import numpy as np
from collections import namedtuple
from random import randint

class Q_table():

    def __init__(self, base):
        self.base = base
        self.q_table = np.zeros([base*base, 3], dtype=np.float64)
        self.learning_rate = 0.1    # Experiment with the learning rate
        self.discount_rate = 0.1    # Should this gradually drop?


    def lookup(self, state, action=None):
        index = self.state_to_index(state)
        if action:
            return self.q_table[index][action]
        else:
            return self.q_table[index]

    # We need to convert the sensor input list to an index for the q_table list.
    # For example, in base 5:
    # An input like 3 3 4 would
    def state_to_index(self, *state):
        temp = 0
        count = 0
        for s in reversed(state):
            temp += s*(self.base*count)
            count += 1
        return temp

    # Every action has an index to correspond the columns in the q_table.
    def get_action_name(self, action):
        actionDict = {0: "left", 1: "forward", 2: "right"}
        return actionDict.get(action)

    # This is the function that applies the Q-function for "learning".
    # It updates the values in the q-table according to the Bellman's equation.
    def update(self, sa_tuple):
        index = self.state_to_index(sa_tuple.state)

        # Bellman's Q-function
        new_value = max(self.lookup(sa_tuple.next_state))*self.discount_rate   # For highest value action in next state
        new_value = sa_tuple.reward + new_value - self.lookup(sa_tuple.state, sa_tuple.action)

        self.q_table[index][sa_tuple.action] += self.learning_rate*new_value

    def get_best_action(self, state):
        index = self.state_to_index(state)
        best_action = self.q_table[index]

    def get_random_action(self):
        return randint(0, 2)
