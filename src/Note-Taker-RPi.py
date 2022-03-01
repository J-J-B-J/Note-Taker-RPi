from machine import Pin
from RFID_Class import RFID_Reader
from LED_Class import Led

typepin = 2
modepin = 3


# Pin layout and valid card UIDs for RFID Reader can be changed in RFID_Class.py
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

LedGreenPin = 16
LedYellowPin = 17
LedRedPin = 18

num_of_modes = 3
modes = ["Letters","Numbers","Symbols"]

kb1_size = 29
kb_1 = ["A","B","C","D","E","F","G","H","I","J","K","L","M",
		"N","O","P","Q","R","S","T","U","V","W","X","Y","Z",
		"RE","BS"," "]
kb2_size = 13
kb_2 = ["1","2","3","4","5","6","7","8","9","0","RE","BS"," "]
kb3_size = 33
kb_3 = ["!","@","#","$","%","^","&","*","(",")","-","_","=",
		"+","[","]","{","}","\\","|","`","~",";",":",",",".",
		"<",">","/","?","RE","BS"," "]


RFID_Reader().readCard()