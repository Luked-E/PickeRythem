import board# type: ignore
import time
import pwmio
from digitalio import DigitalInOut, Direction, Pull
from time import monotonic as CT  #CT holds current time
import random
import asyncio
'''
version stuff
import sys
print(sys.version)
'''

#Debugging light
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

#Game LED
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
strikeWithoutSuccessEnable = True
#minimum and maximum times for switching rythems
rythRangeStart = 8
rythRangeEnd =16

#input list
inputs=[]

#time management
start = CT()
lastBeat = time.monotonic()
rythemLightDuration = 0.25
homeRythem = 1
# In game pausing for rythem change
pauseStart = CT()
nextPauseIn = 0
lastPause = 0
pauseDuration = 6


#Methods
def GetInputs():
    global inputs
    inputs=[not in2.value,not in3.value]

def Lights(state):
    correct1.value = state
    false1.value = state
    correct2.value = state
    false2.value = state
    ryth1.value = state

def CorrectLED(state,light):
    global correct1
    global correct2
    if (light==0):
        correct1.value = state
    if (light==1):
        correct2.value = state

def rythemChooser(lastRythem):
    global difficulty
    return (random.randint()/2^(difficulty-1))


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
    return (CT()-lastBeat)>=timing

#timer with range capabilities
def Timer3(timing, lastBeat, range):
    '''each compared to time past: ((above -range+) and (under +range+time)) or ((above zero) 
    and (under range)) '''
    fullBeat = (((CT()-lastBeat)>=(timing-(range/2))) and ((CT()-lastBeat)<=(timing+(range/2)))) or (((CT()-lastBeat)<=range/2) and ((CT()-lastBeat)>=0))
    return fullBeat

#timer with range and offset capabilities
def Timer3Offset(timing, lastBeat, range, offset):
    '''((above -range+) and (under +range+time)) or ((above zero) 
    and (under range)) with offset making the base time shorter
    offset does not work for offsets larger than half the range'''
    fullBeat = (((CT()-lastBeat)>=(timing-(range/2)+offset)) and ((CT()-lastBeat)<=(timing+(range/2)+offset))) or (((CT()-lastBeat)<=range/2+offset) and ((CT()-lastBeat)>=0))
    return fullBeat

def SetDifficultyLight(difficulty):
    if(difficulty==1):
        color1.duty_cycle = 64554
        color2.duty_cycle = 0
        color3.duty_cycle = 64554
    elif(difficulty==2):
        color1.duty_cycle = 0
        color2.duty_cycle = 64554
        color3.duty_cycle = 64554
    elif(difficulty==3):
        color1.duty_cycle = 64554
        color2.duty_cycle = 64554
        color3.duty_cycle = 0

#Extras 
ResetInputs()

#input debugging
def Debug():
    print(f"{in1.value}, {in2.value}, {in3.value}, {in4.value}")


#run time
while(True):

    '''
    menu setup
    '''
    ResetInputs()
    ryth1.value = True
    print("-------------\nIn Menu\n------------\n")


    '''
    In Menu
    '''
    while(True):
        Lights(True)
        GetInputs()
        currentInput=0
        for input in inputs:
            if(input):
                if (not alreadyTrackedInput[currentInput]):
                    alreadyTrackedInput[currentInput] = True
                    #change this if there are not two inputs
                    difficulty += (-1 + (2 * currentInput))
                    #change if adding game difficulties
                    if(difficulty==4):
                        difficulty = 3
                    elif(difficulty==0):
                        difficulty = 1

            else:
                alreadyTrackedInput[currentInput] = False

            currentInput += 1
        SetDifficultyLight(difficulty)
        # Debug()
        if (not in1.value):
            break
        time.sleep(0.02)


    '''
    game setup
    '''
    Lights(False)
    ResetInputs()
    time.sleep(2)

    print("-------------\nIn Game\n------------\n")
    lastPause = CT()
    nextPause = random.randrange(rythRangeStart,rythRangeEnd)
    '''




    Game Round:

    '''
    while(True):
        # exit game
        if(not in4.value):
            break
        
        # Rythem switching
        if(Timer2(nextPauseIn,lastPause)):
            print("----------")
            # flash warning
            Lights(True)
            time.sleep(0.2)
            Lights(False)
            
            # chooses new light
            chosenLight = random.randint(0,len(inputs)-1)
            print(f"Chosen Light: {chosenLight}")

            # chooses new rythem
            nextRythem = rythem[chosenLight]
            while (nextRythem == rythem[chosenLight]):
                nextRythem = (2**(random.randint(-difficulty,1)))
            print(f"light {chosenLight} has been changed from {rythem[chosenLight]} to {nextRythem}")
            rythem[chosenLight] = nextRythem

            # presentation of new rythem
            lastPause = CT()
            tempLastBeat = CT()
            while(not Timer2(pauseDuration, lastPause)):

                # last beat and rythem light while inside loop
                if(Timer2(homeRythem, lastBeat)):
                    lastBeat = CT()
                if Timer3Offset(homeRythem,lastBeat,0.1,-timeRange/4):# Updating rythem light
                    ryth1.value = True
                else:
                    ryth1.value = False
                
                # last temp beat and new rythem while inside loop
                if(Timer2(nextRythem, tempLastBeat)):
                    tempLastBeat = CT()
                if Timer3Offset(nextRythem,tempLastBeat,0.1,-timeRange/4):
                    CorrectLED(True,chosenLight)
                else:
                    CorrectLED(False,chosenLight)

                time.sleep(0.001)

            # Post change cleanup and reset
            nextPauseIn = random.randint(rythRangeStart,rythRangeEnd)
            lastPause = CT()
            for beats in range(0,len(inputs)):
                lastBeats[beats] = CT()


        # last beat and rythem light
        if(Timer2(homeRythem, lastBeat)):
            lastBeat = CT()
        if Timer3Offset(homeRythem,lastBeat,0.1,-timeRange/4):# Updating rythem light
            ryth1.value = True
        else:
            ryth1.value = False


        #checking inputs
        GetInputs()
        currentInput=0
        for input in inputs:

            # resets success
            if ((successNotReset[currentInput]) and (Timer2(rythem[currentInput],lastBeats[currentInput]-(timeRange/2)))):
                success[currentInput] = False
                successNotReset[currentInput] = False
                FalseLED(False,currentInput)
                CorrectLED(False,currentInput)
                print(f"{currentInput}: success: reset")

            #resets the last beat 
            if Timer2(rythem[currentInput],lastBeats[currentInput]):
                successNotReset[currentInput] = True
                lastBeats[currentInput] = CT()
                if (not success[currentInput] and strikeWithoutSuccessEnable):
                    strikes += 1
                    print(f"{currentInput}: Strikes   __3__   :{strikes}")
                print(f"{currentInput}: lastBeat reset")
            
            led.value = input
            if (input):
                if (not alreadyTrackedInput[currentInput]):
                    print(f"{currentInput}: (")
                    alreadyTrackedInput[currentInput]=True

                    #adds strikes for pressing after a succes and pressing outside of acceptable zone
                    if ((not success[currentInput])and(not Timer3(rythem[currentInput],lastBeats[currentInput],timeRange))):
                        strikes += 1
                        FalseLED(True,currentInput)
                        print(f"{currentInput}: Strikes   __1__   :{strikes}")
                    elif (success[currentInput]):
                        strikes += 1
                        FalseLED(True,currentInput)
                        print(f"{currentInput}: Strikes   __2__   :{strikes}")
                    else:
                        score += 1
                        CorrectLED(True,currentInput)
                        print(f"{currentInput}: Score: "+str(score))
                    success[currentInput] = True

            else:   # One registered press per on/off cycle
                if(alreadyTrackedInput[currentInput]):
                    print(f"{currentInput}: )")
                alreadyTrackedInput[currentInput]=False 
            currentInput += 1

        
        if strikes >= 100:
            break
        time.sleep(0.001)
    Lights(True)
    time.sleep(0.2)
    Lights(False)