from RFID_Class import *
from Rotary_Class import *


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


RFID.readCard()
