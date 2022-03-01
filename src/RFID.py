from mfrc522 import MFRC522
from LED import *

SPI_ID = 1
RST_Pin = 12
SS_Pin = 13
SCK_Pin = 14
MOSI_Pin = 15
MISO_Pin = 8

Cards = ["1C740DB2","5E07C119",]

class RFID_Reader:
	def __init__(self):
		self.reader = reader = MFRC522(spi_id=SPI_ID,sck=SCK_Pin,miso=MISO_Pin,mosi=MOSI_Pin,cs=SS_Pin,rst=RST_Pin)
	
	def uidToString(self, uid):
		mystring = ""
		for i in uid:
			mystring = "%02X" % i + mystring
		return mystring
	
	def readCard(self):
		leds.Yellow()
		print("Tap card to unlock.")
		done = False
		while done == False:
		 	self.reader.init()
			(stat, tag_type) = self.reader.request(self.reader.REQIDL)
			if stat == self.reader.OK:
				(stat, uid) = self.reader.SelectTagSN()
				if stat == self.reader.OK:
					card_uid = self.uidToString(uid)
					if card_uid in Cards:
						leds.Green()
						print("Correct Card!")
					else:
						leds.Red()
						print("Incorrect Card!")
					done = True
				else:
					pass


RFID = RFID_Reader()
