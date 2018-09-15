from picar import front_wheels, back_wheels
from picar.SunFounder_PCA9685 import Servo
import picar
from time import sleep
import numpy as np
from octasonic import Octasonic
import sys
from time import time
from actions import servo_install
import os
from collections import namedtuple

from Q_table import Q_table
from actions import action
from actions import get_state
from actions import action_an
from actions import recovery

import csv

# Front and Back wheel classes instantiated
bw = back_wheels.Back_Wheels()
fw = front_wheels.Front_Wheels()
picar.setup()

# Front wheel Setup
fw.offset = 0
fw.turn(86.86)

bw.speed = 0
fw_angle = 86.86

speed = 75   # Motor Speed Setup

octasonic = Octasonic(0)
octasonic.set_sensor_count(8)

crash_dist = 10
epsilon = 0.1   # The randomness of chosen action, used for discovery.


def main():
    q_table = Q_table(5)
    epochs = 0
    
    decay_epsilon = epsilon
    
    while True:
        print "\n-----\nEpoch: ", epochs + 1, "\n-----"
        crash_report = run(q_table, decay_epsilon, epochs)
        bw.stop()
        last_actions_list = [sa_t.action for sa_t in crash_report]
        sleep(1)
        recovery(last_actions_list, fw,  bw, speed)
        epochs += 1
        sleep(1)
        """if decay_epsilon > 0.001:
            decay_epsilon -= 0.001"""   # decaying epsilon


# The schedule of a single epoch. This is the core program.
def run(q_table, decay_epsilon, epoch):
    crash = False
    state_action_buffer = []    # Fresh buffer for every epoch
    
    # For data collecting purposes
    sensor_input_buffer = [[], []]

    sa_tuple = namedtuple('sa_tuple', 'state action next_state reward')
    
    print epoch
    dir_name = "./epoch_"+str(epoch)
    print "Dir name ", dir_name
    os.mkdir(dir_name)
    
    num_of_actions = 0

    while not crash:
        current_input = get_state(octasonic)
        current_state = convert_input_to_state(current_input)
        
        print "Current state: ", current_state
        r = np.random.rand()
        if r > decay_epsilon:
            next_action = q_table.get_best_action(current_state)
            print "\nBest action chosen."
        else:
            next_action = q_table.get_random_action()
            print "\nRandom action chosen."
            
        print "Action chosen: ", next_action

        action_an(next_action, fw, bw, speed)
        next_input = get_state(octasonic)
        # Crash check immediately after the next state scan to prevent the car crashing an obstacle.
        if is_crash(next_input):
            print("Crash!")
            bw.stop()
            crash = True
        next_state = convert_input_to_state(next_input)
        print "Next state: ", next_state
        next_reward = calculate_reward(next_state)
        print "Calculated reward: ", next_reward

        new_sa_tuple = sa_tuple(state=current_state, action=next_action, reward=next_reward, next_state=next_state)
        q_table.update(new_sa_tuple)
        state_action_buffer.append(new_sa_tuple)
        
        # Saving files
        sensor_input_buffer[0].append(current_input)
        sensor_input_buffer[1].append(next_input)
        q_table_no = dir_name+"/q_table"+str(num_of_actions)+".csv"
        num_of_actions += 1
        
        q_table.save_table(q_table_no)
        print "Q-table saved under name ", q_table_no

    save_sensor_input(sensor_input_buffer, dir_name)
    save_sa_tuples(state_action_buffer, dir_name)
    print "Saved current epoch's (", epoch,") state-action buffer."
    return state_action_buffer[-3:]


# Calculates the reward value that will be used in the q-function.
# Actually, this method of the program directly dictates the policies that the agent is going to inherit.
def calculate_reward(state):
    total_reward = 0
    reward_set = [0, 10, 20, 30, 40]     # Experiment on the crash state value.
    for s in state:
        total_reward += reward_set[s]
    return total_reward


# Converts the sensor input that's between 0-255, to limited state-space that's between 0-4
def convert_input_to_state(input):
    state_list = []
    for i in input:
        if i <= crash_dist:
            state_list.append(0)
        elif i <= 24:
            state_list.append(1)
        elif i <= 48:
            state_list.append(2)
        elif i <= 96:
            state_list.append(3)
        else:
            state_list.append(4)
    return state_list


def is_crash(state):
    if state[0] <= crash_dist-3:
        return True
    elif state[1] <= crash_dist:
        return True
    elif state[2] <= crash_dist-3:
        return True
    return False

# Temporary method to save state-action buffer
def save_sa_tuples(tuple,dirname):
    file_name = dirname + "/state-action-tuple.csv"
    print "\nSaving File: " + file_name
    temp = [[tuple[0].state], [tuple[0].action], [tuple[0].next_state], [tuple[0].reward]]
    print "THE LENGTH: ", len(temp)
    for tup in tuple[1:]:
        temp[0].append(tup.state)
        temp[1].append(tup.action)
        temp[2].append(tup.next_state)
        temp[3].append(tup.reward)
    with open(file_name, 'wb') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(temp)

# Temporary method to save sensory data
def save_sensor_input(input, dirname):
    file_name = dirname + "/raw-sensor-input.csv"
    print "\nSaving File: " + file_name
    with open(file_name, 'wb') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(input)
    


if __name__ == "__main__":
    try:
        main()
    except:
        print "Exception reached."
        bw.stop()