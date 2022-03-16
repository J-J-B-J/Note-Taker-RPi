if __name__ == "__main__":
    print("You ran the wrong file!!!")
    from sys import exit

    exit()

from time import sleep
from machine import Pin, I2C


def lcdError():
    print("Error! Probable cause: LCD not connected or is not wired properly!")
    from sys import exit
    exit()


RGB1602_SDA = Pin(4)
RGB1602_SCL = Pin(5)

RGB1602_I2C = I2C(0, sda=RGB1602_SDA, scl=RGB1602_SCL, freq=400000)

# Device I2C Arress
LCD_ADDRESS = (0x7c >> 1)
RGB_ADDRESS = (0xc0 >> 1)

# color define

REG_RED = 0x04
REG_GREEN = 0x03
REG_BLUE = 0x02
REG_MODE1 = 0x00
REG_MODE2 = 0x01
REG_OUTPUT = 0x08
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x8DOTS = 0x00


class RGB1602:
    def __init__(self, col, row):
        self._showcontrol = None
        self._currline = None
        self._row = row
        self._col = col

        self._showfunction = LCD_4BITMODE | LCD_1LINE | LCD_5x8DOTS
        self.begin(self._row, self._col)

    def command(self, cmd):
        try:
            RGB1602_I2C.writeto_mem(LCD_ADDRESS, 0x80, chr(cmd))
        except Exception:
            lcdError()

    def write(self, data):
        try:
            RGB1602_I2C.writeto_mem(LCD_ADDRESS, 0x40, chr(data))
        except Exception:
            lcdError()

    def setReg(self, reg, data):
        try:
            RGB1602_I2C.writeto_mem(RGB_ADDRESS, reg, chr(data))
        except Exception:
            lcdError()
            

    def set_rgb(self, r, g, b):
        self.setReg(REG_RED, r)
        self.setReg(REG_GREEN, g)
        self.setReg(REG_BLUE, b)

    def setCursor(self, col, row):
        if (row == 0):
            col |= 0x80
        else:
            col |= 0xc0
        try:
            RGB1602_I2C.writeto(LCD_ADDRESS, bytearray([0x80, col]))
        except Exception:
            lcdError()

    def clear(self):
        self.command(LCD_CLEARDISPLAY)
        sleep(0.002)

    def printout(self, arg):
        if (isinstance(arg, int)):
            arg = str(arg)

        for x in bytearray(arg, 'utf-8'):
            self.write(x)

    def display(self):
        self._showcontrol |= LCD_DISPLAYON
        self.command(LCD_DISPLAYCONTROL | self._showcontrol)

    def begin(self, cols, lines):
        if (lines > 1):
            self._showfunction |= LCD_2LINE
            self._numlines = lines
            self._currline = 0

        sleep(0.05)

        # Send function set command sequence
        self.command(LCD_FUNCTIONSET | self._showfunction)
        # delayMicroseconds(4500);  # wait more than 4.1ms
        sleep(0.005)
        # second try
        self.command(LCD_FUNCTIONSET | self._showfunction)
        # delayMicroseconds(150);
        sleep(0.005)
        # third go
        self.command(LCD_FUNCTIONSET | self._showfunction)
        # finally, set # lines, font size, etc.
        self.command(LCD_FUNCTIONSET | self._showfunction)
        # turn the display on with no cursor or blinking default
        self._showcontrol = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
        self.display()
        # clear it off
        self.clear()
        # Initialize to default text direction (for romance languages)
        self._showmode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
        # set the entry mode
        self.command(LCD_ENTRYMODESET | self._showmode)
        # backlight init
        self.setReg(REG_MODE1, 0)
        # set LEDs controllable by both PWM and GRPPWM registers
        self.setReg(REG_OUTPUT, 0xFF)
        # set MODE2 values
        # 0010 0000 -> 0x20  (DMBLNK to 1, ie blinky mode)
        self.setReg(REG_MODE2, 0x20)


colours = {
    "Red": (255, 0, 0),
    "Orange": (255, 128, 0),
    "Yellow": (255, 255, 0),
    "YellowGreen": (128, 255, 0),
    "Green": (0, 255, 0),
    "GreenLightBlue": (0, 255, 128),
    "LightBlue": (0, 255, 255),
    "Blue": (0, 128, 255),
    "Darkblue": (0, 0, 255),
    "Violet": (128, 0, 255),
    "Pink": (255, 0, 255),
    "Magenta": (255, 0, 128),
    "White": (255, 255, 255),
    "Black": (0, 0, 0),
    "Grey": (128, 128, 128),
    "DarkGrey": (64, 64, 64),
    "LightGrey": (191, 191, 191),
}


class LCD:
    def __init__(self):
        self.lcd = RGB1602(16, 2)
        self.lcd.setCursor(0, 0)

    def show(self, text="Hello, World!", pos=(0, 0), serial=True, clear=True):
        if (clear):
            self.lcd.clear()
        self.lcd.setCursor(pos[0], pos[1])
        if (len(text) <= 16):
            self.lcd.printout(text)
        elif (len(text) > 32):
            self.show("Line Too Long")
            sleep(1)
        else:
            self.lcd.printout(text[:15] + "-")
            if (pos[1] == 0):
                self.lcd.setCursor(0, 1)
                self.lcd.printout(text[15:])
            else:
                self.lcd.setCursor(12, 1)
                self.lcd.printout("...")
        if (serial):
            print(text)

    def clear(self):
        self.lcd.clear()

    def setColour(self, colour):
        colour = colours[colour]
        self.lcd.set_rgb(colour[0], colour[1], colour[2])


lcd = LCD()
