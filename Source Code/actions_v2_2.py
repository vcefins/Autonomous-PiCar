from picar import front_wheels, back_wheels
from picar.SunFounder_PCA9685 import Servo
from picar.SunFounder_PCA9685 import PCA9685
import picar
from time import sleep
import numpy as np
import sys
from octasonic import Octasonic
from time import time


optimal_pace = 40   # default pace: 40
speed = 65


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
    distance0 = octasonic.get_sensor_reading(0)   # faced left diagonal
    distance1 = octasonic.get_sensor_reading(1)   # faced front
    distance2 = octasonic.get_sensor_reading(2)   # faced right diagonal
    
    distance3 = octasonic.get_sensor_reading(5) # faced left side
    distance4 = octasonic.get_sensor_reading(4) # faced right side
    
    return distance0, distance1, distance2, distance3, distance4


def get_state_focus(octasonic, f):
    return octasonic.get_sensor_reading(f)


def get_state_rear(octasonic):
    return octasonic.get_sensor_reading(3)
    

def servo_install(angle):
    servo0 = Servo.Servo(0, bus_number=1)
    servo0.write(angle)
    
    print "Servo set to", angle, "degrees.\n"
    
    
def action_an(action_in, fw, bw, reverse=False):
    
    forward_angle = 86.86
    turning_angle = 45
    
    # 0: turn left   1: go forward   2: turn right
    angles = [forward_angle - turning_angle, forward_angle, forward_angle + turning_angle]

    angle = angles[action_in]

    if reverse:
        bw_position = bw.forward
    else:
        bw_position = bw.backward
        
    for i in range(optimal_pace):
        fw.turn(angle)
        bw.speed = speed
        bw_position()   # Because the motor is working in reverse for an unknown reason


def recovery(crash_report, fw, bw, octasonic):
    if crash_report == []:
        crash_report.append(1)
    
    print "\nvDEBUG Recovering"
    for act in reversed(crash_report):
        if get_state_rear(octasonic) > 20:
            action_an(act, fw, bw, True)
