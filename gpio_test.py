import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)

GPIO.setup(7, GPIO.OUT)

for i in range(5):
    GPIO.output(7, False)
    sleep(2)
    GPIO.output(7, True)
    sleep(2)

GPIO.cleanup()
