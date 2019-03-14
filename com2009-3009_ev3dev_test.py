#!/usr/bin/env python3
'''COM2009-3009 EV3DEV TEST PROGRAM'''

# Connect left motor to Output C and right motor to Output B
# Connect an ultrasonic sensor to Input 3

import os
import sys
import time
import ev3dev.ev3 as ev3
import math
# import random
# import matplotlib.pyplot as plt
# from matplotlib import style
# import time
# import numpy as np


# Global Variables
ON = True
OFF = False
m_n = 0
m_oldM = 0
m_newM = 0
m_oldS = 0
m_newS = 0
integral_left = 0
integral_right = 0
last_error_left = 0
last_error_right = 0
derivative_left = 0
derivative_right = 0
# start_time = time.time()
# end_time = time.time()


class RunningStats:
    # The following are to calculate the running stats
    m_n = 0
    m_oldM = 0
    m_newM = 0
    m_oldS = 0
    m_newS = 0

    # @staticmethod
    def push(self, x):
        global m_n, m_oldM, m_newM, m_oldS, m_newS
        m_n = m_n + 1

        if (m_n == 1):
            # Double check it
            # TODO
            m_newM = x
            m_oldM = x
            m_oldS = 0.0
        else:
            m_newM = m_oldM + (x - m_oldM)/m_n
            m_newS = m_oldS + (x - m_oldM)*(x - m_newM)
            # set up for next iteration
            m_oldM = m_newM
            m_oldS = m_newS

    # Calculates the running variance
    @staticmethod
    def variance():
        global m_n, m_oldM, m_newM, m_oldS, m_newS
        # Changed to greater or equals to make sure that the value will
        # be different than 0
        # When the variable is greater, returns the equation
        if (m_n >= 1):
            return (m_newS)/(m_n-1)
        else:
            return 0.0

    # Calculates the running standard deviation

    def standard_deviation(self):
        global m_n, m_oldM, m_newM, m_oldS, m_newS
        return math.sqrt(RunningStats.variance())

    # Calculates the running mean
    def mean(self):
        global m_n, m_oldM, m_newM, m_oldS, m_newS
        # Changed to greater or equals to make sure that the value will be
        # different than 0
        if (m_n >= 1):
            return m_newM
        else:
            return 0.0


# Professors Code >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

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


def select_controller(mode):
    # Using Ku to get a better integral
    Ku = 6
    Tu = 0.3
    if mode == "P":
        print("Running in P mode")
        # Mulitply Kp by 100 to use decimal points
        Kp = 0.6*100
        # Proportional for the Integral
        Ki = 0
        # Proportional for the derivative
        Kd = 0
        return Kp, Ki, Kd
    elif mode == "PI":
        print("Running in PI mode")
        # Mulitply Kp by 100 to use decimal points
        Kp = 0.45*100*Ku
        # Proportional for the Integral
        Ki = (0.54*Ku)/Tu
        # Proportional for the derivative
        Kd = 0
        return Kp, Ki, Kd
    elif mode == "PID":
        print("Running in PID mode")
        # Mulitply Kp by 100 to use decimal points
        Kp = 0.6*100*Ku
        # Proportional for the Integral
        Ki = (1.2*Ku)/Tu
        # Proportional for the derivative
        Kd = (3*Ku*Tu)
        return Kp, Ki, Kd

    # Calculates the PID, sets Ki, Kd = 0 if you would like to use only P and so on


def calculate_pid(left_sensor, right_sensor, mode):
    global integral_left, integral_right, last_error_left, last_error_right, derivative_left, derivative_right
    Kp, Ki, Kd = select_controller(mode)
    # In words our conversion is "for every 1
    # unit change in the error we will increase the
    # power of one motor by 10"

    # The value that would be right
    left_sensor = left_sensor/10
    right_sensor = right_sensor/10

    offset = (left_sensor + right_sensor)/2

    # The target power, when the error is 0 the motors will run in this power
    # The target point for when the value is == to the offset value can be
    # higher
    # Therefore, it would be good to have an if statement checking it
    # If the line is pretty straight you can use a large Tp to get the
    # robot running at high speed and a small Kp so the
    # turns (corrections) are gentle.
    Tp = 50

    # This has to read from the robot's left sensor
    error_left = left_sensor - offset
    # This has to read from the robot's left sensor
    error_right = right_sensor - offset
    # It will increase or decrease the error conform the "size" of the integral
    # variable, giving the controller a method to reduce errors over time
    # Another way to don't make the integral to get too big is to do times
    # 2/3, making the integral forget about long term errors
    integral_left = (integral_left) + error_left
    integral_right = (integral_right) + error_right
    # The derivative that tries to see the future error
    derivative_left = error_left - last_error_left
    derivative_right = error_right - last_error_right
    # This is the P, therefore, how much we want to change the velocity
    # of the motor
    # Divide velocity by 100 to decrease from the Kp from before
    velocity_p_left = ((error_left*Kp)+(integral_left*Ki)+(derivative_left*Kd))/100
    velocity_p_right = ((error_right*Kp)+(integral_right*Ki)+(derivative_right*Kd))/100
    # Those are the powers that will be suplied to the motors
    power_right = velocity_p_right + Tp
    power_left = velocity_p_left + Tp

    # Save the last error to be the next error
    last_error_left = error_left
    last_error_right = error_right

    # Check the maximum and minimum power that can be sent to the robot
    # Also check if the motor can receive a negative power
    # Also double check by how far both motors go from a 100
    # If it goes too far, better changing some Tune like Kp or Tp
    if power_left > 100:
        power_left = 100
    elif power_left < -100:
        power_left = -100

    if power_right > 100:
        power_right = 100
    elif power_right < -100:
        power_right = -100

    # Sets the integral to zero when the error is zero
    # That is to make sure that the integral does not get too big
    # if error == 0:
    #     integral = 0
    # debug_print(error)
    # error =

    # Return the powers of the robots
    if (error_left <= 3 and error_left >= -3) and (error_right <= 3 and error_right >= -3):
        debug_print("Full speed")

        return 90, 90
    else:
        return power_left, power_right


def main():
    '''The main function of our program'''

    # set the console just how we want it
    reset_console()
    set_cursor(OFF)
    set_font('Lat15-Terminus24x12')

    # display something on the screen of the device
    print('Best Robot 2019')

    # print something to the output panel in VS Code
    debug_print('Good evening')

    # announce program start
    ev3.Sound.speak('Program Starting').wait()

    # set the motor variables
    mb = ev3.LargeMotor('outB')
    mc = ev3.LargeMotor('outD')

    # set the ultrasonic sensor variable
    left_sensor = ev3.UltrasonicSensor('in1')
    right_sensor = ev3.UltrasonicSensor('in4')

    while True:
        time.sleep(0.005)
        power_left, power_right = calculate_pid(left_sensor.value(), right_sensor.value(), "P")
        # Give power to the motors
        debug_print("Power Left="+str(power_left) + "Power Right="+str(power_right))
        mb.run_direct(duty_cycle_sp=(power_left))
        mc.run_direct(duty_cycle_sp=(power_right))


if __name__ == '__main__':
    main()
