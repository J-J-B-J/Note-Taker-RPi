# Pin layout and other settings for specific modules can be changed in their specific programs

# ------------------------
# MFRC522      Raspberry
# Reader/PCD   Pi Pico
# Pin          Pin
# ------------------------
# RST          GP0
# SDA(SS)      GP1
# SCK          GP2
# MOSI         GP3
# MISO         GP4

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


try:
	if __name__ == "__main__":
		main()

except Exception as e:
	print(e)
	from time import sleep
	from machine import Pin
	while True:
		Pin(25, Pin.OUT).value(1)
		sleep(0.25)
		Pin(25, Pin.OUT).value(0)
		sleep(0.25)
