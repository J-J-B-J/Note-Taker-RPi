from machine import Pin
from Screen import *
from time import sleep

dtpin = 18
clkpin = 19

typepin = 2
modepin = 3

num_of_modes = 3
modes = ["Letters","Numbers","Symbols"]

kb1_size = 29
kb_1 = ["A","B","C","D","E","F","G","H","I","J","K","L","M",
        "N","O","P","Q","R","S","T","U","V","W","X","Y","Z",
        "r","d"," "]

kb2_size = 13
kb_2 = ["1","2","3","4","5","6","7","8","9","0","RE","DL"," "]

kb3_size = 33
kb_3 = ["!","@","#","$","%","^","&","*","(",")","-","_","=",
        "+","[","]","{","}","\\","|","`","~",";",":",",",".",
        "<",">","/","?","r","d"," "]


class Rotary:
    def __init__(self):
        self.position = 0
        self.previousValue = True
        self.dirPin = Pin(dtpin, Pin.IN, Pin.PULL_UP)
        self.stepPin = Pin(clkpin, Pin.IN, Pin.PULL_UP)
        self.typePin = Pin(typepin, Pin.IN, Pin.PULL_UP)
        self.modePin = Pin(modepin, Pin.IN, Pin.PULL_UP)
        self.mode = 0
        self.oldRotaryLetters = ""
        self.text = "-"
        self.oldMode = 0
    
    def updateEncoder(self):
        step = self.stepPin.value()
        drct = self.dirPin.value()
        if self.previousValue != step:
            if step == False:
                if drct == False:
                    self.position += 1
                else:
                    self.position -= 1
                
                max_letters = 1
                if self.mode == 0:
                    max_letters = kb1_size
                elif self.mode == 1:
                    max_letters = kb2_size
                elif self.mode == 2:
                    max_letters = kb3_size
                
                if self.position < 0:
                    self.position = max_letters-1
                elif self.position >= max_letters:
                    self.position = 0
            
            self.previousValue = step

    def getMode(self):
        return modes[self.mode]

    def appendToText(self, appending_text):
        if (appending_text == "d"):
            old_text = self.text
            old_text_length = len(old_text)
            self.text = old_text[0:old_text_length-1]
        elif (appending_text == "r"):
            self.text += "\n-"
            self.mode = 0  # When new line, set kb to letters
        else:
            self.text += appending_text
        self.print_info()

    def getRotaryLetters(self):
        kb_value = ""
        if self.mode == 0:
            kb_value = kb_1[self.position]
        elif self.mode == 1:
            kb_value = kb_2[self.position]
        elif self.mode == 2:
            kb_value = kb_3[self.position]
        return kb_value


    def updateButtons(self):
        if self.typePin.value() == 0:
            if self.mode == 0:
                self.appendToText(kb_1[self.getRotary()])
            elif self.mode == 1:
                self.appendToText(kb_2[self.getRotary()])
            elif self.mode == 2:
                self.appendToText(kb_3[self.getRotary()])
            while self.typePin.value() == 0:
                pass
            
        elif self.modePin.value() == 0:
            self.mode += 1
            if self.mode >= num_of_modes:
                self.mode = 0
            while self.modePin.value() == 0:
                pass
    
    def print_mode(self):
        lcd.show("Mode: ")
        lcd.show(modes[self.mode], (6, 0), clear=False)
        sleep(1)

    def print_info(self):
        lcd.show(self.getRotaryLetters(), (15,1))
        lcd.show(self.text, clear=False)


    def getTypedLetters(self):
        self.print_mode()
        done = False
        while done == False:
            self.updateEncoder()
            self.updateButtons()
            
            newRotaryLetters = self.getRotaryLetters()
            if self.oldRotaryLetters != newRotaryLetters:
                self.print_info()
                self.oldRotaryLetters = newRotaryLetters
            
            
            if self.oldMode != self.mode:
                self.print_mode()
                self.oldMode = self.mode


rotary = Rotary()
