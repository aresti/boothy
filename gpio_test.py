import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
relay_pins = [2, 3, 4, 17]
touch_pin = 14

for p in relay_pins:
	GPIO.setup(p, GPIO.OUT)
	GPIO.output(p, GPIO.HIGH)

GPIO.setup(touch_pin, GPIO.IN)

while True:
	if GPIO.input(touch_pin):
		GPIO.output(2, GPIO.LOW)
	else:
		GPIO.output(2, GPIO.HIGH)
