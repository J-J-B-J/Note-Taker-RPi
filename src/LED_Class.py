class Led:
	def __init__(self, pin):
		self.pin = pin
		self.led = Pin(self.pin, Pin.OUT)
	
	def on(self):
		self.led.value(1)
	
	def off(self):
		self.led.value(0)
