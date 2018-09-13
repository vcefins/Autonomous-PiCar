import numpy as np
from collections import namedtuple

class Q_table():

    def __init__(self, base):
        self.q_table = np.zeros([125, 3], dtype=np.float64)
        self.base = base
        self.learning_rate = 0.1    # Experiment with the learning rate
        self.discount_rate = 0.1    # Should this gradually drop?


    def lookup(self, state, action=None):
        index = self.state_to_index(state)
        if action:
            return self.q_table[index][self.get_action_index(action)]
        else:
            return self.q_table[index]

    def state_to_index(self, *state):
        temp = 0
        count = 0
        for s in state:
            temp += s*(self.base*count)
            count += 1
        return temp

    def get_action_index(self, action):
        actionDict = {"left": 0, "forward": 1, "right": 2}
        return actionDict.get(action)

    def update(self, sa_tuple):
        index = self.state_to_index(sa_tuple.state)

        # Bellman's Q-function
        new_value = max(self.lookup(sa_tuple.next_state))*self.discount_rate   # For highest value action in next state
        new_value = sa_tuple.reward + new_value - self.lookup(sa_tuple.state, sa_tuple.action)

        self.q_table[index][self.get_action_index(sa_tuple.action)] += self.learning_rate*new_value