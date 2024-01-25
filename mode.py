import RPi.GPIO as GPIO

M0_pin = 5
M1_pin = 6

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# set output
GPIO.setup(M0_pin, GPIO.OUT)
GPIO.setup(M1_pin, GPIO.OUT)


def toMode0():
    # set M0=high,M1=high
    GPIO.output(M0_pin, False)
    GPIO.output(M1_pin, False)

def toMode1():
    # set M0=high,M1=high
    GPIO.output(M0_pin, True)
    GPIO.output(M1_pin, False)

def toMode2():
    # set M0=high,M1=high
    GPIO.output(M0_pin, False)
    GPIO.output(M1_pin, True)

def toMode3():
    # set M0=high,M1=high
    GPIO.output(M0_pin, True)
    GPIO.output(M1_pin, True)

