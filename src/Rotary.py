if __name__ == "__main__":
    print("You ran the wrong file!!!")
    from sys import exit

    exit()

from machine import Pin
from Screen import *
from time import sleep
from json import dump, load

dtpin = 18
clkpin = 19

typepin = 17
modepin = 16

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
        self.text = ["-"]
        self.oldMode = 0
        self.oldText = ""
        self.getText()
    
    def getText(self):
        try:
            with open('Text.json', 'r') as textFile:
                self.text = load(textFile)
        except Exception as e:
            self.postText()
            print(e)
    
    def postText(self):
        with open('Text.json', 'w') as textFile:
                dump(self.text, textFile)
    
    def title(self, sen):
        newText = ""
        for i in range(0, len(sen)):
            if i == 0:
                newText += sen[i].upper()
                continue
            
            if sen[i-1] == " ":
                newText += sen[i].upper()
                continue
            
            newText += sen[i].lower()
        return newText
    
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
            if self.text[-1] == "-":
                del self.text[-1]
            else:
                old_text = self.text[-1]
                old_text_length = len(old_text)
                self.text[-1] = old_text[0:old_text_length-1]
        elif (appending_text == "r"):
            self.text.append("-")
            self.mode = 0  # When new line, set kb to letters and char to A
            self.position = 0
        else:
            self.text[-1] += appending_text
        for text in self.text:
            text = self.title(text)
        self.postText()
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
            self.appendToText(self.getRotaryLetters())
            while self.typePin.value() == 0:
                pass
            
        elif self.modePin.value() == 0:
            self.mode += 1
            if self.mode >= num_of_modes:
                self.mode = 0
            self.position = 0
            while self.modePin.value() == 0:
                pass
            sleep(0.1)
    
    def print_mode(self):
        lcd.show("Mode: ")
        lcd.show(modes[self.mode], (6, 0), clear=False)
        sleep(0.5)
        self.print_info()

    def print_info(self):
        lcd.show(self.getRotaryLetters(), (15,1))
        lcd.show(self.text[-1], clear=False)


    def getTypedLetters(self):
        lcd.setColour("Darkblue")
        self.print_mode()
        done = False
        while done == False:
            self.updateEncoder()
            self.updateButtons()
            
            newLetters = self.getRotaryLetters()
            newText = self.text[-1]
            if self.oldRotaryLetters != newLetters or self.oldText != newText:
                self.print_info()
                self.oldRotaryLetters = newLetters
                self.oldText = newText
            
            
            if self.oldMode != self.mode:
                self.print_mode()
                self.oldMode = self.mode


rotary = Rotary()
