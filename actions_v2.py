from picar import front_wheels, back_wheels
from picar.SunFounder_PCA9685 import Servo
from picar.SunFounder_PCA9685 import PCA9685
import picar
from time import sleep
import numpy as np
import sys
from octasonic import Octasonic
from time import time


optimal_pace = 40
speed = 45


def action(action_in, fw, bw, reverse=None):
    
    fw_possible_actions = {'0': fw.turn_right, '1': fw.turn_straight, '2': fw.turn_left}
    fw_position = fw_possible_actions.get(action_in)

    bw_position = bw.backward

    if reverse and not action == 'backward':
        bw_position = bw.forward
    elif not reverse and action == 'backward':
        bw_position = bw.forward

    print action
        
    for i in range(optimal_pace):
        fw_position()
        bw.speed = speed
        bw_position()   # Because the motor is working in reverse for an unknown reason
        
        
def get_state(octasonic):
    distance1 = octasonic.get_sensor_reading(2)   # faced front
    distance2 = octasonic.get_sensor_reading(1)   # faced right
    distance0 = octasonic.get_sensor_reading(7)   # faced left
    # distance3 = octasonic.get_sensor_reading(0)   # faced backward
    
    return distance0, distance1, distance2#, distance3


def servo_install(angle):
    servo0 = Servo.Servo(0, bus_number=1)
    servo1 = Servo.Servo(1, bus_number=1)
    servo2 = Servo.Servo(2, bus_number=1)
    servo0.write(angle)
    servo1.write(angle)
    servo2.write(angle)
    
    print "Servo set to", angle, "degrees.\n"
    
    
def action_an(action_in, fw, bw, reverse=False):
    
    angles = {0: 61.86, 1: 86.86, 2: 111.86}

    angle = angles.get(action_in)

    if reverse:
        bw_position = bw.forward
        print "--- Recovering ---"
    else:
        bw_position = bw.backward
        
    for i in range(optimal_pace):
        fw.turn(angle)
        bw.speed = speed
        bw_position()   # Because the motor is working in reverse for an unknown reason


def recovery(crash_report, fw, bw):
    print "\nRecovery mode reached. Actions to be taken: ", crash_report
    for act in reversed(crash_report):
        action_an(act, fw, bw, True)
