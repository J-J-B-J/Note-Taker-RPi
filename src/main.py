# Pin layout and other settings for specific modules can be changed in their specific programs

# ------------------------
# MFRC522      Raspberry
# Reader/PCD   Pi Pico
# Pin          Pin
# ------------------------
# RST          GP12
# SDA(SS)      GP13
# SCK          GP14
# MOSI         GP15
# MISO         GP8

# ------------------------
# LED          Raspberry
# Colour       Pi Pico
#              Pin
# ------------------------
# Green        GP16
# Yellow       GP17
# Red          GP18

from RFID import *
from Rotary import *


def main():
	RFID.readCard()


if __name__ == "__main__":
	main()
