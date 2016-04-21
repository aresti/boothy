import RPi.GPIO as GPIO

class Button():

	def __init__(self, gpio_pin):
		self.gpio_pin = gpio_pin

		GPIO.setmode(GPIO.BCM)
		GPIO.setup(gpio_pin, GPIO.IN)

	def is_pressed(self):
		return GPIO.input(self.gpio_pin)
