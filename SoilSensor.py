import RPi.GPIO as GPIO
import time

# GPIO SETUP
channel = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)

def callback(channel):
	if GPIO.input(channel):
		print("No Water Detected!")
	else:
		print("Water Detected!")

# Detect changes in the state of GPIO pins.
GPIO.add_event_detect(channel,GPIO.BOTH,bouncetime=300)
GPIO.add_event_callback(channel, callback)
# Infinite loop to keep the program running.
while True:
	time.sleep(0)

