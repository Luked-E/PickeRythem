import board# type: ignore
import sys
import time
from pwmio import PWMOut# type: ignore
import pwmio# type: ignore
import digitalio # type: ignore
from digitalio import DigitalInOut, Direction, Pull # type: ignore
#CT is current time
from time import monotonic as CT  #CT is current time

led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT

# Button inputs 1-4
in1 = DigitalInOut(board.GP0)
in1.direction = Direction.INPUT
in1.pull = Pull.UP

in2 = DigitalInOut(board.GP3)
in2.direction = Direction.INPUT
in2.pull = Pull.UP

in3 = DigitalInOut(board.GP8)
in3.direction = Direction.INPUT
in3.pull = Pull.UP

in4 = DigitalInOut(board.GP11)
in4.direction = Direction.INPUT
in4.pull = Pull.UP

#Rythem LED
ryth1 = DigitalInOut(board.GP5)
ryth1.direction = Direction.OUTPUT
ryth1.value = True

false1= DigitalInOut(board.GP4)
false1.direction = Direction.OUTPUT

false2= DigitalInOut(board.GP6)
false2.direction = Direction.OUTPUT

correct1= DigitalInOut(board.GP1)
correct1.direction = Direction.OUTPUT

correct2= DigitalInOut(board.GP10)
correct2.direction = Direction.OUTPUT

#controls colored LED 1
color1 = pwmio.PWMOut(board.GP16, duty_cycle= 64554)
color2 = pwmio.PWMOut(board.GP17, duty_cycle= 64554)
color3 =  pwmio.PWMOut(board.GP18, duty_cycle= 64555)

#game general
difficulty=1
timeRange = 0.3
strikes=0
score=0
inGame = True
inMenu = True

#input list
inputs=[]

#time management
start = CT()
lastBeat = time.monotonic()
rythemLightDuration = 0.25
pausestart = 0
pause_duration = 4
homeRythem = 1


#Methods
def GetInputs():
    global inputs
    inputs=[not in2.value,not in3.value]

def CorrectLED(state,light):
    global correct1
    global correct2
    if (light==0):
        correct1.value = state
    if (light==1):
        correct2.value = state

def FalseLED(state,light):
    global false1
    global false2
    if (light==0):
        false1.value = state
    if (light==1):
        false2.value = state

def ResetInputs():
    ct = CT()
    global lastBeats
    lastBeats = [ct,ct]
    global rythem
    rythem = [1,1]
    global alreadyTrackedInput
    alreadyTrackedInput = [False,False]
    global success
    success = [0,0]
    global successNotReset
    successNotReset = [True,True]


def Timer2(timing, lastBeat): #gives if the range of lastbeat and currentbeat is greater than the timing
    fullBeat = (CT()-lastBeat)>=timing
    return fullBeat

def Timer3(timing, lastBeat, range):
    '''each compared to time past: ((above -range+) and (under +range+time)) or ((above zero) 
    and (under range)) '''
    fullBeat = (((CT()-lastBeat)>=(timing-(range/2))) and ((CT()-lastBeat)<=(timing+(range/2)))) or (((CT()-lastBeat)<=range/2) and ((CT()-lastBeat)>=0))
    return fullBeat

def Timer3Offset(timing, lastBeat, range, offset):
    '''((above -range+) and (under +range+time)) or ((above zero) 
    and (under range)) with offset making the base time shorter
    offset does not work for offsets larger than half the range'''
    fullBeat = (((CT()-lastBeat)>=(timing-(range/2)+offset)) and ((CT()-lastBeat)<=(timing+(range/2)+offset))) or (((CT()-lastBeat)<=range/2+offset) and ((CT()-lastBeat)>=0))
    return fullBeat

#Extras 
currentInput=0

ResetInputs()
#run time
while(True):

    while(inMenu):
        if(not in4.value):
            break
    print("get ready")
    time.sleep(2)
    print("out")
    while(inGame):
        if(not in1.value):
            break

        if(Timer2(homeRythem, lastBeat)):
            lastBeat = CT()


        #checking inputs
        GetInputs()
        currentInput=0
        for input in inputs:

            #rests 
            if ((successNotReset[currentInput]) and (Timer2(rythem[currentInput],lastBeats[currentInput]-(timeRange/2)))):
                success[currentInput] = False
                successNotReset[currentInput] = False
                FalseLED(False,currentInput)
                CorrectLED(False,currentInput)
                print("success: reset")

                
            if Timer2(rythem[currentInput],lastBeats[currentInput]):#resets the last beat 
                successNotReset[currentInput] = True
                lastBeats[currentInput] = CT()
                '''if not success[currentInput]:
                    strikes += 1'''
                print("lastBeat: reset, Strikes: "+str(strikes) )
            
            led.value = input
            if (input):
                if (not alreadyTrackedInput[currentInput]):
                    print("(")
                    alreadyTrackedInput[currentInput]=True
                    #adds strikes for pressing after a succes and pressing outside of acceptable zone
                    if (not Timer3(rythem[currentInput],lastBeats[currentInput],timeRange)):
                        strikes += 1
                        FalseLED(True,currentInput)
                        print("Strikes   __1__   :"+str(strikes))
                    elif (success[currentInput]):
                        strikes += 1
                        FalseLED(True,currentInput)
                        print("Strikes   __2__   :"+str(strikes))
                    else:
                        success[currentInput] = True
                        score += 1
                        CorrectLED(True,currentInput)
                        print("Score: "+str(score))

            else:   # One registered press per on/off cycle
                if(alreadyTrackedInput[currentInput]):
                    print(")")
                alreadyTrackedInput[currentInput]=False 
            currentInput += 1


        if Timer3Offset(homeRythem,lastBeat,0.1,-timeRange/4):# Updating rythem light
            ryth1.value = True
        else:
            ryth1.value = False
        if strikes >= 300:
            inGame = False
        time.sleep(0.001)