import RPi.GPIO as GPIO
import time

class Lamp():

	def __init__(self, gpio_pins, flash_time='0.1'):
		self.gpio_pins = gpio_pins
		self.flash_time = flash_time

		GPIO.setmode(GPIO.BCM)

		for p in gpio_pins:
			GPIO.setup(p, GPIO.OUT)
			GPIO.output(p, GPIO.HIGH)

	def on(self):
		for p in self.gpio_pins:
			GPIO.output(p, GPIO.LOW)
	
	def off(self):
		for p in self.gpio_pins:
			GPIO.output(p, GPIO.HIGH)
	
	def flash(self):
		for p in self.gpio_pins:
			GPIO.output(p, GPIO.LOW)
		time.sleep(0.2)
		for p in self.gpio_pins:
			GPIO.output(p, GPIO.HIGH)

	def __del__(self):
		GPIO.cleanup()
