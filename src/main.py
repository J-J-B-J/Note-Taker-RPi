"""Main program file"""

# Pin layout and other settings for specific modules can be changed in their
# specific programs

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
# LCD          Raspberry
# Screen       Pi Pico
# Pin          Pin
# ------------------------
# SDA          GP4
# SCL          GP5

# ------------------------
# Rotary       Raspberry
# Encoder      Pi Pico
# Pin          Pin
# ------------------------
# DT           GP18
# CLK          GP19

# ------------------------
# Button       Raspberry
# Pin          Pi Pico
#              Pin
# ------------------------
# modePin      16
# typePin      17

from RFID import *
from Rotary import *
from sys import exit
from time import sleep


def main():
    """
    Run the program
    """
    unlocked = RFID.read_card()
    if unlocked:
        lcd.show("Welcome, Josh!")
        sleep(1)
    else:
        lcd.show("Goodbye, Intruder...")
        for _ in range(0, 10):
            lcd.setColour("Darkblue")
            sleep(0.3)
            lcd.setColour("Red")
            sleep(0.3)
        exit()

    rotary.get_typed_letters()


if __name__ == "__main__":
    main()
