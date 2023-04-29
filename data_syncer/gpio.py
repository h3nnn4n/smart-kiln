import orangepi.pi3
from OPi import GPIO


channel = 3

GPIO.setmode(orangepi.pi3.BOARD)
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

if GPIO.input(channel):
    print("Input was HIGH")
else:
    print("Input was LOW")
