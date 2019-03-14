# !/usr/bin/env python3
'''COM2009-3009 EV3DEV TEST PROGRAM'''

# Connect left motor to Output C and right motor to Output B
# Connect an ultrasonic sensor to Input 3

import os
import sys
import time
import ev3dev.ev3 as ev3
import math
from time import sleep, time


# state constants
ON = True
OFF = False
m_n = 0
m_oldM = 0
m_newM = 0
m_oldS = 0
m_newS = 0

# Calculation for standard deviation, variance and mean


def push(value):
    global m_n
    global m_oldM
    global m_newM
    global m_oldS
    global m_newS

    m_n = m_n + 1

    if(m_n == 1):
        m_oldM = m_newM
        m_newM = value
        m_oldS = 0.0
    else:
        m_newM = m_oldM + (value-m_oldM)/m_n
        m_newS = m_oldS + (value-m_oldM)*(value-m_newM)
        # Set up for next iteraction
        m_oldM = m_newM
        m_old = m_newS


def mean():
    global m_n
    if (m_n > 0):
        return m_newM
    else:
        return 0.0


def variance():
    global m_newS
    global m_n
    if (m_n > 1):
        return m_newS/(m_n-1)
    else:
        return 0.00


def standard_deviation():
    return math.sqrt(variance())


def debug_print(*args, **kwargs):
    '''Print debug messages to stderr.
    This shows up in the output panel in VS Code.
    '''
    print(*args, **kwargs, file=sys.stderr)


def reset_console():
    '''Resets the console to the default state'''
    print('\x1Bc', end='')


def set_cursor(state):
    '''Turn the cursor on or off'''
    if state:
        print('\x1B[?25h', end='')
    else:
        print('\x1B[?25l', end='')


def set_font(name):
    '''Sets the console font
    A full list of fonts can be found with `ls /usr/share/consolefonts`
    '''
    os.system('setfont ' + name)


def main():
    '''The main function of our program'''

    # set the console just how we want it
    reset_console()
    set_cursor(OFF)
    set_font('Lat15-Terminus24x12')

    # display something on the screen of the device
    # print('Hello World!')

    # print something to the output panel in VS Code
    debug_print('Hello VS Code!')

    # announce program start
    # ev3.Sound.speak('Test program starting!').wait()

    # set the motor variables
    mb = ev3.LargeMotor('outB')
    mc = ev3.LargeMotor('outC')
    sp = 30
    delta = 30
    # set the ultrasonic sensor variable
    us3 = ev3.UltrasonicSensor('in3')

    # # program loop
    # for x in range (1, 5):

    # display the distance on the screen of the device
    # print('Distance =',ds)

    # print the distance to the output panel in VS Code
    # debug_print('Distance =',ds)
    # ds = us3.value()
    # announce the distance
    # ev3.Sound.speak(ds).wait()

    # move
    # mb.run_direct(duty_cycle_sp=sp)
    # mc.run_direct(duty_cycle_sp=sp)
    # time.sleep(0.)
    # for x in range(1, 1000):
    #     time.sleep(0.01)
    #     ds = us3.value()
    #     # debug_print('Distance =',ds)
    #     push(ds)
    #     mean_current = mean()
    #     variance_current = variance()
    #     stdev = standard_deviation()
    #     debug_print("Distance", ds)
    #     debug_print("Mean", mean_current)
    #     debug_print("Variance", variance_current)
    #     debug_print("Standar Deviation", stdev)

    # mb.run_timed(time_sp=1, speed_sp=1000)
    # mc.run_timed(time_sp=200000, speed_sp=1000)
    # mb.run_direct(duty_cycle_sp=60)
    # mc.run_direct(duty_cycle_sp=60)
    # time.sleep(2.5)
    # mb.run_direct(duty_cycle_sp=10)
    # time.sleep(2)
    # mb.run_direct(duty_cycle_sp=0)
    # mc.run_direct(duty_cycle_sp=0)

    # question 4 open loop
    # for x in range(1,4):
    #     mb.run_direct(duty_cycle_sp=60)
    #     mc.run_direct(duty_cycle_sp=60)
    #     time.sleep(2.5)
    #     mb.run_direct(duty_cycle_sp=10)
    #     time.sleep(2)
    #     # stop
    # mb.run_direct(duty_cycle_sp=0)
    # mc.run_direct(duty_cycle_sp=0)

    #     # reverse direction
    #     sp = -sp
    Kp = 50
    Ki = 0
    Kd = 0
    r = 500
    Tp = 25
    integral = 0
    lastError = 0
    derivative = 0
    b = ev3.UltrasonicSensor('in3')
    rafa = 0
    error = r - (b.value())

    startTime = time()
    while rafa == 0:
        debug_print(round((time() - startTime) % 20))
        if round((time() - startTime) % 20) == 0:
            r = 500
        elif round((time() - startTime) % 10) == 0:
            r = 300
        integral = integral + error
        derivative = error - lastError
        Turn = Kp*error + Ki*integral + Kd*derivative
        Turn = Turn/100
        powerB = Tp + Turn
        powerC = Tp + Turn
        error = r - (b.value())
        debug_print(error)
        debug_print("Value of b", b.value())

        if error > 0:
            mb.run_direct(duty_cycle_sp=-(powerB))
            mc.run_direct(duty_cycle_sp=-(powerC))
        else:
            mb.run_direct(duty_cycle_sp=(powerB))
            mc.run_direct(duty_cycle_sp=(powerC))

            # integral = integral + error
            # derivative = error - lastError
            # Turn = Kp*error + Ki*integral + Kd*derivative
            # Turn = Turn/100
            # powerB = Tp + Turn
            # powerC = Tp + Turn
            # error = r - (b.value())
            # debug_print (error)
            # debug_print ("Value of b",b.value())

            # if error > 0:
            #     mb.run_direct(duty_cycle_sp=-(powerB))
            #     mc.run_direct(duty_cycle_sp=-(powerC))
            # else:
            #     mb.run_direct(duty_cycle_sp=(powerB))
            #     mc.run_direct(duty_cycle_sp=(powerC))
        # if error == 0:
        #     mb.run_direct(duty_cycle_sp=0)
        #     mc.run_direct(duty_cycle_sp=0)
        # else:
        #     mb.run_direct(duty_cycle_sp=powerB)
        #     mc.run_direct(duty_cycle_sp=powerC)
        #     debug_print("PowerB", powerB)
        #     debug_print("PowerB", powerC)

        # time.sleep(10)

    # lastError = error
    # # announce program end
    # ev3.Sound.speak('Test program ending').wait()
    # push(17.0)
    # push(18.0)
    # push(5.0)
    # mean_current = mean()
    # variance_current = variance()
    # stdev = standard_deviation()
    # debug_print (mean_current)
    # debug_print (variance_current)
    # debug_print(stdev)
    # debug_print(m_n)
if __name__ == '__main__':
    main()
