from picar import front_wheels, back_wheels
from picar.SunFounder_PCA9685 import Servo
import picar
from time import sleep
import numpy as np
from octasonic import Octasonic
import sys
from time import time
from actions import servo_install

from actions import action
from actions import get_state
from actions import action_an


front_wheels_enable = True
rear_wheels_enable = True


# Front and Backwheel classes assigned
bw = back_wheels.Back_Wheels()
fw = front_wheels.Front_Wheels()
picar.setup()

# Front wheel Setup
fw.offset = 0
fw.turn(90)

bw.speed = 0
fw_angle = 90

motor_speed = 70   # Speed Setup 




def main():
    
    angle = 86.9
    
    servo_install(90)
    
    while True:
    
        action_an(angle, fw, bw, motor_speed)


    
    """octasonic = Octasonic(0)
    octasonic.set_sensor_count(8)
    
    crash = False
    
    action_list = ['forward', 'left', 'right', 'forward', 'left', 'forward']
    
    
    for act in action_list:
        action(act, fw, bw, motor_speed)
    
    bw.speed = 0
    sleep(1)
    
    for act in reversed(action_list):
        action(act, fw, bw, motor_speed, True)"""

    
    bw.stop()
    #action("forward", fw, bw, motor_speed)




    

def simple_logic_machine_follows_least_obstructed_path(octasonic, fw, bw, motor_speed):

    while not crash:
        state_current = get_state(octasonic)
        temp = 0
        for distance in state_current[:-1]:
            if distance > temp:
                temp = distance
        index = state_current.index(temp)
        
        take_action = {0: 'straight', 1: 'right', 2: 'left'}
        action(take_action.get(index), fw, bw, motor_speed)
        state_next = get_state(octasonic)
        
        print "\n-\nInitial State: ", str(state_current)
        print "Action Taken: ", take_action.get(index)
        print "Next State: ", str(state_next), "\n-\n"
        



if __name__ == "__main__":
    main()
        