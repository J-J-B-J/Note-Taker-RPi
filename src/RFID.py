"""Contains classes, functions and constants related to the RFID reader."""

if __name__ == "__main__":
    print("You ran the wrong file!!!")
    from sys import exit

    exit()

from Screen import *
from time import sleep
from machine import Pin, SPI
from os import uname

SPI_ID = 1
RST_Pin = 12
SS_Pin = 13
SCK_Pin = 14
MOSI_Pin = 15
MISO_Pin = 8

# Cards = ["1C740DB2","5E07C119",]
Cards = ["1C740DB2", "5E07C119", ]


def tohexstring(v):
    """
    convert a hex value t oa string
    :param v: value
    :return: string value
    """
    s = "["
    for i in v:
        if i != v[0]:
            s += ", "
        s += "0x{:02X}".format(i)
    s += "]"
    return s


class MFRC522:
    """
    Class to manage basic communications with RFID reader
    """
    DEBUG = False
    OK = 0
    NOTAGERR = 1
    ERR = 2

    REQIDL = 0x26
    REQALL = 0x52
    AUTHENT1A = 0x60
    AUTHENT1B = 0x61

    PICC_ANTICOLL1 = 0x93
    PICC_ANTICOLL2 = 0x95
    PICC_ANTICOLL3 = 0x97

    def __init__(self, sck, mosi, miso, rst, cs, baudrate=1000000, spi_id=0):

        self.sck = Pin(sck, Pin.OUT)
        self.mosi = Pin(mosi, Pin.OUT)
        self.miso = Pin(miso)
        self.rst = Pin(rst, Pin.OUT)
        self.cs = Pin(cs, Pin.OUT)

        self.rst.value(0)
        self.cs.value(1)

        board = uname()[0]

        if board == 'WiPy' or board == 'LoPy' or board == 'FiPy':
            self.spi = SPI(0)
            self.spi.init(SPI.MASTER, baudrate=1000000,
                          pins=(self.sck, self.mosi, self.miso))
        elif (board == 'esp8266') or (board == 'esp32'):
            self.spi = SPI(baudrate=100000, polarity=0, phase=0, sck=self.sck,
                           mosi=self.mosi, miso=self.miso)
            self.spi.init()
        elif board == 'rp2':
            self.spi = SPI(spi_id, baudrate=baudrate, sck=self.sck,
                           mosi=self.mosi, miso=self.miso)
        else:
            raise RuntimeError("Unsupported platform")

        self.rst.value(1)
        self.init()

    def _wreg(self, reg, val):

        self.cs.value(0)
        self.spi.write(b'%c' % int(0xff & ((reg << 1) & 0x7e)))
        self.spi.write(b'%c' % int(0xff & val))
        self.cs.value(1)

    def _rreg(self, reg):

        self.cs.value(0)
        self.spi.write(b'%c' % int(0xff & (((reg << 1) & 0x7e) | 0x80)))
        val = self.spi.read(1)
        self.cs.value(1)

        return val[0]

    def _sflags(self, reg, mask):
        self._wreg(reg, self._rreg(reg) | mask)

    def _cflags(self, reg, mask):
        self._wreg(reg, self._rreg(reg) & (~mask))

    def _tocard(self, cmd, send):

        recv = []
        bits = irq_en = wait_irq = 0
        stat = self.ERR

        if cmd == 0x0E:
            irq_en = 0x12
            wait_irq = 0x10
        elif cmd == 0x0C:
            irq_en = 0x77
            wait_irq = 0x30

        self._wreg(0x02, irq_en | 0x80)
        self._cflags(0x04, 0x80)
        self._sflags(0x0A, 0x80)
        self._wreg(0x01, 0x00)

        for c in send:
            self._wreg(0x09, c)
        self._wreg(0x01, cmd)

        if cmd == 0x0C:
            self._sflags(0x0D, 0x80)

        i = 2000
        while True:
            n = self._rreg(0x04)
            i -= 1
            if ~((i != 0) and ~(n & 0x01) and ~(n & wait_irq)):
                break

        self._cflags(0x0D, 0x80)

        if i:
            if (self._rreg(0x06) & 0x1B) == 0x00:
                stat = self.OK

                if n & irq_en & 0x01:
                    stat = self.NOTAGERR
                elif cmd == 0x0C:
                    n = self._rreg(0x0A)
                    lbits = self._rreg(0x0C) & 0x07
                    if lbits != 0:
                        bits = (n - 1) * 8 + lbits
                    else:
                        bits = n * 8

                    if n == 0:
                        n = 1
                    elif n > 16:
                        n = 16

                    for _ in range(n):
                        recv.append(self._rreg(0x09))
            else:
                stat = self.ERR

        return stat, recv, bits

    def _crc(self, data):

        self._cflags(0x05, 0x04)
        self._sflags(0x0A, 0x80)

        for c in data:
            self._wreg(0x09, c)

        self._wreg(0x01, 0x03)

        i = 0xFF
        while True:
            n = self._rreg(0x05)
            i -= 1
            if not ((i != 0) and not (n & 0x04)):
                break

        return [self._rreg(0x22), self._rreg(0x21)]

    def init(self):
        """
        Initiaize variables
        """
        self.reset()
        self._wreg(0x2A, 0x8D)
        self._wreg(0x2B, 0x3E)
        self._wreg(0x2D, 30)
        self._wreg(0x2C, 0)
        self._wreg(0x15, 0x40)
        self._wreg(0x11, 0x3D)
        self.antenna_on()

    def reset(self):
        """
        Reset the RFID Reader
        """
        self._wreg(0x01, 0x0F)

    def antenna_on(self, on=True):
        """
        Tell the reader to turn on/off
        :param on: on or off
        """
        if on and ~(self._rreg(0x14) & 0x03):
            self._sflags(0x14, 0x03)
        else:
            self._cflags(0x14, 0x03)

    def request(self, mode):
        """
        make a request to the RFID reader
        :param mode: mode of the request
        :return: status
        """
        self._wreg(0x0D, 0x07)
        (stat, recv, bits) = self._tocard(0x0C, [mode])

        if (stat != self.OK) | (bits != 0x10):
            stat = self.ERR

        return stat, bits

    def anticoll(self, anticolN):
        """
        Not sure what thus
        """
        ser_chk = 0
        ser = [anticolN, 0x20]

        self._wreg(0x0D, 0x00)
        (stat, recv, bits) = self._tocard(0x0C, ser)

        if stat == self.OK:
            if len(recv) == 5:
                for i in range(4):
                    ser_chk = ser_chk ^ recv[i]
                if ser_chk != recv[4]:
                    stat = self.ERR
            else:
                stat = self.ERR

        return stat, recv

    def PcdSelect(self, serNum, anticolN):
        """
        Select a card
        :param anticolN:
        :param serNum: Serial Number
        :return: Status
        """
        buf = [anticolN, 0x70]
        # i = 0
        # xorsum=0;
        for i in serNum:
            buf.append(i)
        # while i<5:
        #    buf.append(serNum[i])
        #    i = i + 1
        p_out = self._crc(buf)
        buf.append(p_out[0])
        buf.append(p_out[1])
        (status, backData, backLen) = self._tocard(0x0C, buf)
        if (status == self.OK) and (backLen == 0x18):
            return 1
        else:
            return 0

    def SelectTag(self, uid):
        """
        Select a tag to use
        :param uid: tag uid
        :return: status
        """
        byte5 = 0

        # (status,puid)= self.anticoll(self.PICC_ANTICOLL1)
        # print("uid",uid,"puid",puid)
        for i in uid:
            byte5 = byte5 ^ i
        puid = uid + [byte5]

        if self.PcdSelect(puid, self.PICC_ANTICOLL1) == 0:
            return self.ERR, []
        return self.OK, uid

    def SelectTagSN(self):
        """
        Select a tag serial number
        :return: status
        """
        valid_uid = []
        (status, uid) = self.anticoll(self.PICC_ANTICOLL1)
        # print("Select Tag 1:",self.tohexstring(uid))
        if status != self.OK:
            return self.ERR, []

        if self.DEBUG:
            print("anticol(1) {}".format(uid))
        if self.PcdSelect(uid, self.PICC_ANTICOLL1) == 0:
            return self.ERR, []
        if self.DEBUG:
            print("pcdSelect(1) {}".format(uid))

        # check if first byte is 0x88
        if uid[0] == 0x88:
            # ok we have another type of card
            valid_uid.extend(uid[1:4])
            (status, uid) = self.anticoll(self.PICC_ANTICOLL2)
            # print("Select Tag 2:",self.tohexstring(uid))
            if status != self.OK:
                return self.ERR, []
            if self.DEBUG:
                print("Anticol(2) {}".format(uid))
            rtn = self.PcdSelect(uid, self.PICC_ANTICOLL2)
            if self.DEBUG:
                print("pcdSelect(2) return={} uid={}".format(rtn, uid))
            if rtn == 0:
                return self.ERR, []
            if self.DEBUG:
                print("PcdSelect2() {}".format(uid))
            # now check again if uid[0] is 0x88
            if uid[0] == 0x88:
                valid_uid.extend(uid[1:4])
                (status, uid) = self.anticoll(self.PICC_ANTICOLL3)
                # print("Select Tag 3:",self.tohexstring(uid))
                if status != self.OK:
                    return self.ERR, []
                if self.DEBUG:
                    print("Anticol(3) {}".format(uid))
                if self.MFRC522_PcdSelect(uid, self.PICC_ANTICOLL3) == 0:
                    return self.ERR, []
                if self.DEBUG:
                    print("PcdSelect(3) {}".format(uid))
        valid_uid.extend(uid[0:5])
        # if we are here than the uid is ok
        # let's remove the last BYTE whic is the XOR sum

        return self.OK, valid_uid[:len(valid_uid) - 1]
        # return (self.OK , valid_uid)

    def auth(self, mode, addr, sect, ser):
        """
        Authenticate a card
        :param mode: mode
        :param addr: address
        :param sect: section
        :param ser: serial
        :return: authentication
        """
        return self._tocard(0x0E, [mode, addr] + sect + ser[:4])[0]

    def authKeys(self, uid, addr, keyA=None, keyB=None):
        """
        Make authorisation keys
        :param uid: uid
        :param addr: address
        :param keyA: first key
        :param keyB: second key
        :return: status
        """
        status = self.ERR
        if keyA is not None:
            status = self.auth(self.AUTHENT1A, addr, keyA, uid)
        elif keyB is not None:
            status = self.auth(self.AUTHENT1B, addr, keyB, uid)
        return status

    def stop_crypto1(self):
        """
        Stop the encryption.
        """
        self._cflags(0x08, 0x08)

    def read(self, addr):
        """
        Read a card's data
        :param addr: card addrss
        :return: data
        """
        data = [0x30, addr]
        data += self._crc(data)
        (stat, recv, _) = self._tocard(0x0C, data)
        return stat, recv

    def write(self, addr, data):
        """
        write data to a card
        :param addr: card address
        :param data: data t owritw
        :return: status
        """
        buf = [0xA0, addr]
        buf += self._crc(buf)
        (stat, recv, bits) = self._tocard(0x0C, buf)

        if not (stat == self.OK) or not (bits == 4) or not (
                (recv[0] & 0x0F) == 0x0A):
            stat = self.ERR
        else:
            buf = []
            for i in range(16):
                buf.append(data[i])
            buf += self._crc(buf)
            (stat, recv, bits) = self._tocard(0x0C, buf)
            if not (stat == self.OK) or not (bits == 4) or not (
                    (recv[0] & 0x0F) == 0x0A):
                stat = self.ERR
        return stat

    def writeSectorBlock(self, uid, sector, block, data, keyA=None, keyB=None):
        """
        Write a sector block
        :param uid: uid
        :param sector: sector
        :param block: block a or b
        :param data: data to write
        :param keyA: key number 1
        :param keyB: key number 2
        :return: error?
        """
        absolute_block = sector * 4 + (block % 4)
        if absolute_block > 63:
            return self.ERR
        if len(data) != 16:
            return self.ERR
        if self.authKeys(uid, absolute_block, keyA, keyB) != self.ERR:
            return self.write(absolute_block, data)
        return self.ERR

    def readSectorBlock(self, uid, sector, block, keyA=None, keyB=None):
        """
        Read a sector
        :param uid: uid
        :param sector: sector
        :param block: block a or b
        :param keyA: key number 1
        :param keyB: key number 2
        :return: error?
        """
        absolute_block = sector * 4 + (block % 4)
        if absolute_block > 63:
            return self.ERR, None
        if self.authKeys(uid, absolute_block, keyA, keyB) != self.ERR:
            return self.read(absolute_block)
        return self.ERR, None

    def MFRC522_DumpClassic1K(self, uid, Start=0, End=64, keyA=None,
                              keyB=None):
        """
        Dump data to an RFID card
        :param uid: card uid
        :param Start: starting byte
        :param End: ending byte
        :param keyA: key number 1
        :param keyB: key number 2
        :return: status
        """
        status = None
        for absoluteBlock in range(Start, End):
            status = self.authKeys(uid, absoluteBlock, keyA, keyB)
            # Check if authenticated
            print("{:02d} S{:02d} B{:1d}: ".format(absoluteBlock,
                                                   absoluteBlock // 4,
                                                   absoluteBlock % 4), end="")
            if status == self.OK:
                status, block = self.read(absoluteBlock)
                if status == self.ERR:
                    break
                else:
                    for value in block:
                        print("{:02X} ".format(value), end="")
                    print("  ", end="")
                    for value in block:
                        if (value > 0x20) and (value < 0x7f):
                            print(chr(value), end="")
                        else:
                            print('.', end="")
                    print("")
            else:
                break
        if status == self.ERR:
            print("Authentication error")
            return self.ERR
        return self.OK


def uid_to_string(uid):
    """
    Convert a UID to a printable string
    :param uid: an uid value of a card
    :return: string version of uid param
    """
    string = ""
    for i in uid:
        string = "%02X" % i + string
    return string


class RFIDReader:
    """
    Class to control the RFID reader.
    """

    def __init__(self):
        self.reader = MFRC522(spi_id=SPI_ID, sck=SCK_Pin,
                              miso=MISO_Pin, mosi=MOSI_Pin, cs=SS_Pin,
                              rst=RST_Pin)

    def read_card(self):
        """
        Find a card and get it's uid
        :return: Weather or not the correct card was entered
        """
        lcd.setColour("Orange")
        lcd.show("Preparing reader...")
        sleep(1)

        self.reader.init()
        stat = self.reader.request(self.reader.REQIDL)

        if stat == self.reader.OK:
            lcd.show("Tap card or connect wire to unlock!")
            while True:
                (stat, uid) = self.reader.SelectTagSN()
                pin_value = Pin(0, Pin.PULL_UP).value()
                if stat == self.reader.OK or pin_value == 1:
                    card_uid = uid_to_string(uid)
                    if card_uid in Cards or pin_value == 1:
                        lcd.setColour("Green")
                        lcd.show("Correct Card!")
                        sleep(1)
                        return True
                    else:
                        lcd.setColour("Red")
                        lcd.show("Incorrect Card!")
                        sleep(1)
                        return False
        else:
            lcd.show("Connect wire to unlock!")
            while True:
                if Pin(0, Pin.PULL_UP).value() == 1:
                    lcd.setColour("Green")
                    lcd.show("Correct Pin!")
                    sleep(1)
                    return True


RFID = RFIDReader()
