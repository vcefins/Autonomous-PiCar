from picar import front_wheels, back_wheels
from picar.SunFounder_PCA9685 import Servo
import picar
from time import sleep
import numpy as np
from octasonic import Octasonic
import sys
from time import time
from actions import servo_install

from collections import namedtuple

from Q_table import Q_table
from actions import action
from actions import get_state
from actions import action_an
from actions import recovery


# Front and Back wheel classes instantiated
bw = back_wheels.Back_Wheels()
fw = front_wheels.Front_Wheels()
picar.setup()

# Front wheel Setup
fw.offset = 0
fw.turn(86.86)

bw.speed = 0
fw_angle = 86.86

speed = 70   # Motor Speed Setup

octasonic = Octasonic(0)
octasonic.set_sensor_count(8)

crash_dist = 12
epsilon = 0.1   # The randomness of chosen action, used for discovery.


def main():
    q_table = Q_table(5)
    epochs = 0

    while True:
        print "\n\nEpoch: ", epochs + 1, "\n"
        crash_report = run(q_table)
        bw.stop()
        last_actions_list = [sa_t.action for sa_t in crash_report]
        print last_actions_list
        recovery(last_actions_list, bw, fw, speed)
        epochs += 1
        sleep(2)


# The schedule of a single epoch. This is the core program.
def run(q_table):
    crash = False
    state_action_buffer = []    # Fresh buffer for every epoch

    sa_tuple = namedtuple('sa_tuple', 'state action next_state reward')

    while not crash:
        current_input = get_state(octasonic)
        current_state = convert_input_to_state(current_input)

        if np.random.rand() > epsilon:
            next_action = q_table.get_best_action(current_state)
        else:
            next_action = q_table.get_random_action()

        action_an(next_action, fw, bw, speed)
        next_input = get_state(octasonic)
        # Crash check immediately after the next state scan to prevent the car crashing an obstacle.
        if is_crash(next_input):
            bw.stop()
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
    reward_set = [-30, 3, 6, 9, 12]     # Experiment on the crash state value.
    for s in state:
        total_reward += reward_set[s]
    return total_reward


# Converts the sensor input that's between 0-255, to limited state-space that's between 0-4
def convert_input_to_state(input):
    state_list = []
    for i in input:
        if i <= crash_dist:
            state_list.append(0)
        elif i <= 40:
            state_list.append(1)
        elif i <= 80:
            state_list.append(2)
        elif i <= 160:
            state_list.append(3)
        else:
            state_list.append(4)
    return state_list


def is_crash(state):
    for i in state:
        if i <= crash_dist:
            return True
    return False



if __name__ == "__main__":
    main()