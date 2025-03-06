import board# type: ignore
import sys
import time
from pwmio import PWMOut# type: ignore
import pwmio# type: ignore
import digitalio # type: ignore
from digitalio import DigitalInOut, Direction, Pull # type: ignore
#CT is current time
from time import monotonic as CT  #CT is current time

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

#Rythem LED
ryth1 = DigitalInOut(board.GP5)
ryth1.direction = Direction.OUTPUT
ryth1.value = True

#controls colored LED 1
color1 = pwmio.PWMOut(board.GP16, duty_cycle= 64554)
color2 = pwmio.PWMOut(board.GP17, duty_cycle= 64554)
color3 =  pwmio.PWMOut(board.GP18, duty_cycle= 64554)

#game general
difficulty=1
timeRange = 0.05
gameEnd = False

#input list
inputs=[]

#time management
start = CT()
lastBeat = time.monotonic()
rythemLightDuration = 0.25
pausestart = 0
pause_duration = 4

#Methods
def ResetInputs():
    global NumInputs
    #sets inputs function and rests variables
    if NumInputs==2:
        def NumInputs():
            global inputs
            inputs=[in2.value,in3.value]
        global lastbeats
        lastbeats = [CT,CT]
        global rythem
        rythem = [1,1]
        global success
        success = [False,False]
        global alreadyTrackedInput
        alreadyTrackedInput = [False,False]

    else:
        def NumInputs():
            global inputs
            inputs=[in2.value]
        global rythem
        rythem = [1]
        global lastbeats
        lastbeats = [CT]
        global success
        success = [False]
        global alreadyTrackedInput
        alreadyTrackedInput = [False]



def Timer2(timing, lastBeat):
    fullBeat = (CT()-lastBeat)>=timing
    return fullBeat # returns boolean

def Timer3(timing, lastBeat, range):
    fullBeat = ((CT()-lastBeat) >= (timing-range)) and ((CT()-lastBeat) <= (timing+range))
    return fullBeat # returns boolean


#Extras 
currentInput=0
#run time
while(True):

    timer = Timer2(rythem[0], lastBeat)
    if(timer):
        lastBeat = CT()
#checking inputs
    NumInputs()
    currentInput=0
    for input in inputs:
        currentInput += 1

        if input:
            if alreadyTrackedInput[currentInput]==False:
                success[currentInput] = Timer3(rythem[currentInput],lastbeats[currentInput],timeRange)
            alreadyTrackedInput[currentInput]=True
        else:
            alreadyTrackedInput[currentInput]=False

        if Timer2(rythem[currentInput],lastbeats[currentInput]):
            lastbeats[currentInput] = CT
    
    if Timer2(timer,3):# updating rythem light
        ryth1.value = True
    time.sleep(0.01)