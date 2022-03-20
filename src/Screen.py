"""Classes, functions and constants related to the screen"""

if __name__ == "__main__":
    print("You ran the wrong file!!!")
    from sys import exit

    exit()

from time import sleep
from machine import Pin, I2C


def lcdError():
    """
    Print a problem with the LCD to the console/REPL
    """
    print("Error! Probable cause: LCD not connected or is not wired properly!")
    from sys import exit
    exit()


RGB1602_SDA = Pin(4)
RGB1602_SCL = Pin(5)


class RGB1602:
    """
    Class to manage basic LCD functioality.
    """

    def __init__(self, col: int, row: int):
        self._showmode = None
        self._numlines = None
        self.RGB1602_I2C = I2C(0, sda=RGB1602_SDA, scl=RGB1602_SCL,
                               freq=400000)

        # Device I2C Arress
        self.LCD_ADDRESS = (0x7c >> 1)
        self.RGB_ADDRESS = (0xc0 >> 1)

        # color define

        self.REG_RED = 0x04
        self.REG_GREEN = 0x03
        self.REG_BLUE = 0x02
        self.REG_MODE1 = 0x00
        self.REG_MODE2 = 0x01
        self.REG_OUTPUT = 0x08
        self.LCD_CLEARDISPLAY = 0x01
        self.LCD_RETURNHOME = 0x02
        self.LCD_ENTRYMODESET = 0x04
        self.LCD_DISPLAYCONTROL = 0x08
        self.LCD_CURSORSHIFT = 0x10
        self.LCD_FUNCTIONSET = 0x20
        self.LCD_SETCGRAMADDR = 0x40
        self.LCD_SETDDRAMADDR = 0x80

        # flags for display entry mode
        self.LCD_ENTRYRIGHT = 0x00
        self.LCD_ENTRYLEFT = 0x02
        self.LCD_ENTRYSHIFTINCREMENT = 0x01
        self.LCD_ENTRYSHIFTDECREMENT = 0x00

        # flags for display on/off control
        self.LCD_DISPLAYON = 0x04
        self.LCD_DISPLAYOFF = 0x00
        self.LCD_CURSORON = 0x02
        self.LCD_CURSOROFF = 0x00
        self.LCD_BLINKON = 0x01
        self.LCD_BLINKOFF = 0x00

        # flags for display/cursor shift
        self.LCD_DISPLAYMOVE = 0x08
        self.LCD_CURSORMOVE = 0x00
        self.LCD_MOVERIGHT = 0x04
        self.LCD_MOVELEFT = 0x00

        # flags for function set
        self.LCD_8BITMODE = 0x10
        self.LCD_4BITMODE = 0x00
        self.LCD_2LINE = 0x08
        self.LCD_1LINE = 0x00
        self.LCD_5x8DOTS = 0x00

        self._showcontrol = None
        self._currline = None
        self._row = row
        self._col = col

        self._showfunction = self.LCD_4BITMODE | self.LCD_1LINE | \
                             self.LCD_5x8DOTS
        self.begin(self._col)

    def command(self, cmd: chr):
        """
        Send a command to the LCD
        :param cmd: command to send
        """
        try:
            self.RGB1602_I2C.writeto_mem(self.LCD_ADDRESS, 0x80, chr(cmd))
        except Exception:
            lcdError()

    def write(self, data: chr):
        """
        Send data to the LCD
        :param data: data to send
        """
        try:
            self.RGB1602_I2C.writeto_mem(self.LCD_ADDRESS, 0x40, chr(data))
        except Exception:
            lcdError()

    def setReg(self, reg, data: chr):
        """
        Set the registration of the LCD
        :param reg: registration
        :param data: data
        """
        try:
            self.RGB1602_I2C.writeto_mem(self.RGB_ADDRESS, reg, chr(data))
        except Exception:
            lcdError()

    def set_rgb(self, r: int, g: int, b: int):
        """

        :param r:
        :param g:
        :param b:
        """
        self.setReg(self.REG_RED, r)
        self.setReg(self.REG_GREEN, g)
        self.setReg(self.REG_BLUE, b)

    def setCursor(self, col: int, row: int):
        """
        Set the location of the cursor on the screen
        :param col: column
        :param row: row
        """
        if row == 0:
            col |= 0x80
        else:
            col |= 0xc0
        try:
            self.RGB1602_I2C.writeto(self.LCD_ADDRESS, bytearray([0x80, col]))
        except Exception:
            lcdError()

    def clear(self):
        """
        Clear the screen
        """
        self.command(self.LCD_CLEARDISPLAY)
        sleep(0.002)

    def printout(self, arg: str):
        """
        print something to the screen
        :param arg: argument
        """

        for x in bytearray(arg, 'utf-8'):
            self.write(x)

    def display(self):
        """
        Control the display
        """
        self._showcontrol |= self.LCD_DISPLAYON
        self.command(self.LCD_DISPLAYCONTROL | self._showcontrol)

    def begin(self, lines: int):
        """
        Start up thr LCD
        :param lines: number of lines on the LCD
        """
        if lines > 1:
            self._showfunction |= self.LCD_2LINE
            self._numlines = lines
            self._currline = 0

        sleep(0.05)

        # Send function set command sequence
        self.command(self.LCD_FUNCTIONSET | self._showfunction)
        # delayMicroseconds(4500);  # wait more than 4.1ms
        sleep(0.005)
        # second try
        self.command(self.LCD_FUNCTIONSET | self._showfunction)
        # delayMicroseconds(150);
        sleep(0.005)
        # third go
        self.command(self.LCD_FUNCTIONSET | self._showfunction)
        # finally, set # lines, font size, etc.
        self.command(self.LCD_FUNCTIONSET | self._showfunction)
        # turn the display on with no cursor or blinking default
        self._showcontrol = self.LCD_DISPLAYON | self.LCD_CURSOROFF | \
                            self.LCD_BLINKOFF
        self.display()
        # clear it off
        self.clear()
        # Initialize to default text direction (for romance languages)
        self._showmode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
        # set the entry mode
        self.command(self.LCD_ENTRYMODESET | self._showmode)
        # backlight init
        self.setReg(self.REG_MODE1, 0)
        # set LEDs controllable by both PWM and GRPPWM registers
        self.setReg(self.REG_OUTPUT, 0xFF)
        # set MODE2 values
        # 0010 0000 -> 0x20  (DMBLNK to 1, ie blinky mode)
        self.setReg(self.REG_MODE2, 0x20)


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
    """
    Class to control more advanced functionality of the LCD
    """

    def __init__(self):
        self.lcd = RGB1602(16, 2)
        self.lcd.setCursor(0, 0)

    def show(self, text: str, pos: tuple = (0, 0), serial: bool = True,
             clear: bool = True):
        """
        Show something on the LCD
        :param text: Text to show
        :param pos: text location (top left is (0,0), top right is (15,0))
        :param serial: also print the text to the serial monitor/console/REPL
        :param clear: clear the display before printing the text
        :return: status
        """
        if clear:
            self.lcd.clear()
        self.lcd.setCursor(pos[0], pos[1])
        if len(text) <= 16:
            self.lcd.printout(text)
        elif len(text) > 29:
            self.show("Line Too Long")
            return False
        else:
            self.lcd.printout(text[:15] + "-")
            if pos[1] == 0:
                self.lcd.setCursor(0, 1)
                self.lcd.printout(text[15:])
            else:
                self.lcd.setCursor(12, 1)
                self.lcd.printout("...")
        if serial:
            print(text)
        return True

    def setColour(self, colour: tuple[2]):
        """
        Set the background colour of the LCD
        :param colour: rgb value as tuple
        """
        colour = colours[colour]
        self.lcd.set_rgb(colour[0], colour[1], colour[2])


lcd = LCD()
