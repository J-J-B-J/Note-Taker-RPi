from machine import Pin

LedGreenPin = 16
LedYellowPin = 17
LedRedPin = 18


class Led:
	def __init__(self, pin):
		self.pin = pin
		self.led = Pin(self.pin, Pin.OUT)
		self.off()
	
	def on(self):
		self.led.value(1)
	
	def off(self):
		self.led.value(0)


class Leds:
	def __init__(self):
		self.Green_LED = Led(LedGreenPin)
		self.Yellow_LED = Led(LedYellowPin)
		self.Red_LED = Led(LedRedPin)
	
	def Green(self):
		self.Green_LED.on()
		self.Yellow_LED.off()
		self.Red_LED.off()
		
	def Yellow(self):
		self.Green_LED.off()
		self.Yellow_LED.on()
		self.Red_LED.off()
		
	def Red(self):
		self.Green_LED.off()
		self.Yellow_LED.off()
		self.Red_LED.on()
		
	def Off(self):
		self.Green_LED.off()
		self.Yellow_LED.off()
		self.Red_LED.off()

leds = Leds()
