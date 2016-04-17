import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
relay_pins = [2, 3, 4, 17]
touch_pins = [14,24]

for p in relay_pins:
	GPIO.setup(p, GPIO.OUT)
	GPIO.output(p, GPIO.HIGH)

for p in touch_pins:
	GPIO.setup(p, GPIO.IN)

while True:
	if GPIO.input(touch_pins[0]):
		GPIO.output(relay_pins[0], GPIO.LOW)
	elif GPIO.input(touch_pins[1]):
		GPIO.output(relay_pins[1], GPIO.LOW)
	else:
		GPIO.output(relay_pins[0], GPIO.HIGH)
		GPIO.output(relay_pins[1], GPIO.HIGH)
