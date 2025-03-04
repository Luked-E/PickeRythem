
import board
import sys
import time
from pwmio import PWMOut
import pwmio
import digitalio # type: ignore
from digitalio import DigitalInOut, Direction, Pull # type: ignore

# Button inputs 1-4
in1 = DigitalInOut(board.GP0)
in1.direction = Direction.INPUT
in1.pull = Pull.UP

in2 = DigitalInOut(board.GP1)
in2.direction = Direction.INPUT
in2.pull = Pull.UP

in3 = DigitalInOut(board.GP2)
in3.direction = Direction.INPUT
in3.pull = Pull.UP

in4 = DigitalInOut(board.GP3)
in4.direction = Direction.INPUT
in4.pull = Pull.UP

#controls colored LED 1
color1 = pwmio.PWMOut(board.GP16, duty_cycle= 1)

color2 = pwmio.PWMOut(board.GP17, duty_cycle= 12)

color3 =  pwmio.PWMOut(board.GP18, duty_cycle= 2)

#starting pause config 
pause = False
pause_duration = 4

#time stuff
start_time = time.monotonic()
current_time = time.monotonic()
last_beat = time.monotonic()
print(start_time)

#run time
while(True):
    current_time = time.monotonic()

    time.sleep(0.01)
