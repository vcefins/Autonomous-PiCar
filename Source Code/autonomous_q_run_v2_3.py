from picar import front_wheels, back_wheels
from picar.SunFounder_PCA9685 import Servo
import picar
from time import sleep
import numpy as np
from octasonic import Octasonic
import sys
from time import time
import os
from collections import namedtuple
from math import fabs

from Q_table_v2_2 import Q_table
from Q_table_v2_2 import load_table

from actions_v2_2 import servo_install
from actions_v2_2 import get_state
from actions_v2_2 import action_an
from actions_v2_2 import recovery


# Front and Back wheel classes instantiated
bw = back_wheels.Back_Wheels()
fw = front_wheels.Front_Wheels()
picar.setup()

# Front wheel Setup
fw.offset = 0
fw.turn(86.86)

fw_angle = 86.86

octasonic = Octasonic(0)
octasonic.set_sensor_count(8)

crash_dist = 12
epsilon = 0.1   # The randomness of chosen action, used for discovery.

corner_sensor_margin = 5    # Maybe dimming the corner sensors makes movements close to walls more possible.

crash_counter = 0
crash_list = []


def main(q_table):
    global crash_list
    epochs = 0
    
    print "Q-table set."
    
    decay_epsilon = epsilon
    
    start_time = time()
        
    while True:
        print "\n-----\nEpoch: ", epochs + 1, "\n-----"
        crash_report = run(q_table, decay_epsilon, start_time)
        bw.stop()
        crash_list.append(time() - start_time)
        last_actions_list = [sa_t.action for sa_t in crash_report]
        sleep(1)
        recovery(last_actions_list, fw,  bw, octasonic)
        epochs += 1
        sleep(1)
        if decay_epsilon > 0.005:
            decay_epsilon -= 0.001   # decaying epsilon
        print "\n\nvDEBUG Epsilon:", decay_epsilon


# The schedule of a single epoch. This is the core program.
def run(q_table, decay_epsilon, start_time):    
    global crash_counter
    global crash_list
    
    crash = False
    state_action_buffer = []    # Fresh buffer for every epoch

    sa_tuple = namedtuple('sa_tuple', 'state action next_state reward')

    while not crash:
        
        print "---\nCycle\n---"

        current_input = get_state(octasonic)
        print "vDEBUG Raw Sensor Input:", current_input
        # Immediate sensor checks to stop the car in crash situations. 
        if is_crash(current_input[:3]):
            print("\nCrash!\n")
            bw.stop()
            break
        
        current_state = convert_input_to_state(current_input)      
        print "vDEBUG Current state: ", current_state
        
        if np.random.rand() > decay_epsilon:
            print "\nBEST action chosen."
            next_action = q_table.get_best_action(current_state)
        else:
            print "\nRANDOM action chosen."
            next_action = q_table.get_random_action()
            
        print "Action chosen: ", next_action

        action_an(next_action, fw, bw)
        next_input = get_state(octasonic)

        # Immediate sensor checks to stop the car in crash situations. 
        if is_crash(next_input[:3]):
            print("---\nCrash!\n---")
            bw.stop()
            crash = True
        
        next_state = convert_input_to_state(next_input)
        next_reward = calculate_reward(next_state)

        new_sa_tuple = sa_tuple(state=current_state, action=next_action, reward=next_reward, next_state=next_state)
        q_table.update(new_sa_tuple)
        state_action_buffer.append(new_sa_tuple)

    return state_action_buffer[-5:]


# Calculates the reward value that will be used in the q-function.
# Actually, this method of the program directly dictates the policies that the agent is going to inherit.
def calculate_reward(state):
    total_reward = 0
    reward_set = [-100, 5, 15, 25]     # Experiment on the crash state value.
    for s in range(len(state)):
        if s < 3:
            total_reward += reward_set[state[s]+1]
        else:
            if state[s] == 2:
                total_reward += 25
            elif state[s] == 1:
                total_reward += 15
            else:
                total_reward += -20
    return total_reward


# Converts the sensor input that's between 0-255, to limited state-space that's between 0-2
def convert_input_to_state(input):
    state_list = []
    for i in input:
        if i <= crash_dist:
            state_list.append(-1)
        elif crash_dist <= i and i <= 20:
            state_list.append(0)
        elif 21 <= i and i <= 32:
            state_list.append(1)
        elif i > 32:
            state_list.append(2)
    return state_list


def is_crash(state):
    if state[0] <= crash_dist - corner_sensor_margin:
        print "Crash on LEFT corner."
        return True
    elif state[1] <= crash_dist:
        print "Crash up FRONT."
        return True
    elif state[2] <= crash_dist - corner_sensor_margin:
        print "Crash on RIGHT corner."
        return True
    return False


def update_crash_log(crash_list):
    string = "[" + str(crash_list[0])
    
    for item in crash_list[1:]:
        string = string + ", " + str(item)
    string = string + "]\n"
        
    f=open("crash_log.txt", "a+")
    f.write(string)



if __name__ == "__main__":
    save_state = raw_input("Do you want to load from save? (Y/N)\n")
    try:
        q_table = Q_table(3, 5, 3)
        if save_state == 'Y':
            q_table.q_table = load_table()
        main(q_table)
    except KeyboardInterrupt:
        bw.stop()
        save = raw_input("Do you want to save the last session's Q-table? (Y/N)\n")
        if save == 'Y':
            q_table.save_table()
            print "Table saved.\n\n"
        print "This session's crash counting:", str(crash_list)
        save_c = raw_input("\nDo you want to store the crash list in the Crash Log? (Y/N)\n")
        if save_c == 'Y':
            update_crash_log(crash_list)
        print "\nHave a nice day.\n"

