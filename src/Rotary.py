"""Contains classes, functions and constants related to the rotary encoder,
the buttons and typing."""

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
modes = ["Letters", "Numbers", "Symbols"]

kb1_size = 29
kb_1 = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
        "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
        "r", "d", " "]

kb2_size = 13
kb_2 = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "RE", "DL", " "]

kb3_size = 33
kb_3 = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "=",
        "+", "[", "]", "{", "}", "\\", "|", "`", "~", ";", ":", ",", ".",
        "<", ">", "/", "?", "r", "d", " "]


def title(sen):
    """
    Turn text into title case.
    :param sen: Text to convert
    :return: Converted text
    """
    new_text = ""
    for i in range(0, len(sen)):
        if i == 1:
            new_text += sen[i].upper()
            continue

        if sen[i - 1] == " ":
            new_text += sen[i].upper()
            continue

        new_text += sen[i].lower()
    return new_text


class Rotary:
    """
    Class to manage typing, the rotary encoder and buttons
    """
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
        """
        Get the text data from the .json file and save it to Rotary().text
        """
        try:
            with open('Text.json', 'r') as textFile:
                old_text = load(textFile)
                for text in old_text:
                    self.text.append(title(text))
        except Exception as e:
            self.postText()
            print(e)

    def postText(self):
        """
        Update the .json text file
        """
        with open('Text.json', 'w') as textFile:
            dump(self.text, textFile)

    def updateEncoder(self):
        """
        Update the position of the rotary encoder.
        i.e. check if it has been turned
        """
        step = self.stepPin.value()
        drct = self.dirPin.value()
        if self.previousValue != step:
            if not step:
                if not drct:
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
                    self.position = max_letters - 1
                elif self.position >= max_letters:
                    self.position = 0

            self.previousValue = step

    def getMode(self):
        """
        Get the current mode
        :return: the current mode
        """
        return modes[self.mode]

    def append_to_text(self, appending_text):
        """
        Append a string to the text.
        :param appending_text: text to append to current text.
        """
        if appending_text == "d":
            if self.text[-1] == "-":
                del self.text[-1]
            else:
                old_text = self.text[-1]
                old_text_length = len(old_text)
                self.text[-1] = old_text[0:old_text_length - 1]
        elif appending_text == "r":
            self.text.append("-")
            self.mode = 0  # When new line, set kb to letters and char to A
            self.position = 0
        else:
            self.text[-1] += appending_text

        new_text = []
        for text in self.text:
            new_text.append(title(text))
        self.text = new_text

        self.postText()
        self.print_info()

    def get_rotary_letters(self):
        """
        Get the letter the rotary encoder has selected.
        :return: the letter selected
        """
        kb_value = ""
        if self.mode == 0:
            kb_value = kb_1[self.position]
        elif self.mode == 1:
            kb_value = kb_2[self.position]
        elif self.mode == 2:
            kb_value = kb_3[self.position]
        return kb_value

    def update_buttons(self):
        """
        Check if a button has been pressed
        """
        if self.typePin.value() == 0:
            self.append_to_text(self.get_rotary_letters())
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
        """
        Show what mode is selected on the screen.
        """
        lcd.show("Mode: ")
        lcd.show(modes[self.mode], (6, 0), clear=False)
        sleep(0.5)
        self.print_info()

    def print_info(self):
        """
        Print the letters and typed text to the screen.
        """
        lcd.show(self.get_rotary_letters(), (15, 1))
        good_line = lcd.show(self.text[-1], clear=False)
        if not good_line:
            sleep(1)
            old_text = self.text[-1]
            old_text_length = len(old_text)
            self.text[-1] = old_text[0:old_text_length - 1]

    def get_typed_letters(self):
        """
        Type into the notepad. This is the main loop for the program.
        """
        lcd.setColour("Darkblue")
        self.print_mode()
        done = False
        while not done:
            self.updateEncoder()
            self.update_buttons()

            new_letters = self.get_rotary_letters()
            new_text = self.text[-1]
            if self.oldRotaryLetters != new_letters or self.oldText != \
                    new_text:
                self.print_info()
                self.oldRotaryLetters = new_letters
                self.oldText = new_text

            if self.oldMode != self.mode:
                self.print_mode()
                self.oldMode = self.mode


rotary = Rotary()
