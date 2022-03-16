if __name__ == "__main__":
    print("You ran the wrong file!!!")
    from sys import exit

    exit()

from mfrc522 import MFRC522
from Screen import *
from time import sleep

SPI_ID = 1
RST_Pin = 12
SS_Pin = 13
SCK_Pin = 14
MOSI_Pin = 15
MISO_Pin = 8

# Cards = ["1C740DB2","5E07C119",]
Cards = ["1C740DB2","5E07C119",]


class RFID_Reader:
    def __init__(self):
        self.reader = MFRC522(spi_id=SPI_ID, sck=SCK_Pin,
                              miso=MISO_Pin, mosi=MOSI_Pin, cs=SS_Pin,
                              rst=RST_Pin)

    def uid_to_string(self, uid):
        """

        :param uid: a uid value of a card
        :return: string version of uid param
        """
        string = ""
        for i in uid:
            string = "%02X" % i + string
        return string

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
                (stat, tag_type) = self.reader.request(self.reader.REQIDL)
                (stat, uid) = self.reader.SelectTagSN()
                pin_value = Pin(0, Pin.PULL_UP).value()
                if stat == self.reader.OK or pin_value == 1:
                    card_uid = self.uid_to_string(uid)
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


RFID = RFID_Reader()
