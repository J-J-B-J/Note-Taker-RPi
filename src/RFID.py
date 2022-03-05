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
        lcd.show("Tap card to unlock!")
        while True:
            self.reader.init()
            (stat, tag_type) = self.reader.request(self.reader.REQIDL)
            if stat == self.reader.OK:
                (stat, uid) = self.reader.SelectTagSN()
                if stat == self.reader.OK:
                    card_uid = self.uid_to_string(uid)
                    if card_uid in Cards:
                        lcd.setColour("Green")
                        lcd.show("Correct Card!")
                        sleep(1)
                        return True
                    else:
                        lcd.setColour("Red")
                        lcd.show("Incorrect Card!")
                        sleep(1)
                        return False


RFID = RFID_Reader()
