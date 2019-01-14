import numpy as np
from collections import namedtuple
from random import randint
from random import sample
from math import pow

class Q_table():

    # base to the power of sensor_num gives the number of total possible states, which determines the number of rows in Q-table
    # action_num determines the number of columns in Q-table
    def __init__(self, base, sensor_num, action_num):
        self.base = base
        dim1 = int(pow(base, sensor_num))
        self.q_table = np.zeros([dim1, action_num], dtype=np.float64)

        self.learning_rate = 0.01    # Experiment with the learning rate
        self.discount_rate = 0.3    # Should this gradually drop?


    def lookup(self, state, action=None):
        index = self.state_to_index(state)
        if type(action) == int:
            return self.q_table[index][action]
        else:
            return self.q_table[index]


    # We need to convert the sensor input list to an index for the q_table list.
    # For example, in base 5:
    # E.g 3 3 4 --> 4 + 3*5 + 3 *25 = 94
    def state_to_index(self, state):
        for f in range(len(state)):
            if state[f] == -1:
                state[f] = 0
        
        temp = 0
        count = 0
        for s in reversed(state):
            temp += s*(pow(self.base, count))
            count += 1
        return int(temp)


    def print_table(self):
        print "---\nQ-table\n---\n"
        for row in self.q_table:
            print row
        print "---\n"
        
    
    # This is the function that applies the Q-function for "learning".
    # It updates the values in the q-table according to the Bellman's equation.
    def update(self, sa_tuple):
        table_index = self.state_to_index(sa_tuple.state)
        print "\nUpdating State", str(table_index), "\n"

        # Bellman's Q-function
        future_value = max(self.lookup(sa_tuple.next_state))*self.discount_rate   # For highest value in next state
        new_value = sa_tuple.reward + future_value - self.lookup(sa_tuple.state, sa_tuple.action)

        self.q_table[table_index][sa_tuple.action] += self.learning_rate*new_value


    # If the epsilon decides on not doing discovery, this function is called for action decision.
    def get_best_action(self, state):
        # print "vDEBUG get best action reached."
        table_index = self.state_to_index(state)
        
        a = self.q_table[table_index]
        print "\nvDEBUG: Q-table row: ", a
        temp = a.tolist()        

        max_value = max(temp)
        # print "vDEBUG Highest value", max_value
        
        occurences = [i for i, x in enumerate(temp) if x == max_value]
        # print "vDEBUG: Value", max_value, "occurs in that row", len(occurences), "times."
        # print "vDEBUG Contents of 'occurences':", str(occurences)
        
        if len(occurences) == 1:
            action = occurences[0]
        elif len(occurences) == 2:
            sample_act = sample(occurences, 1)
            action = sample_act[0]
        else:
            action = self.get_random_action()
        return int(action)

    # If the epsilon decides on discovery, this function is called for action decision.
    def get_random_action(self):
        return randint(0, 2)
    
    def save_table(self):
        np.savetxt("Saved Q-table", self.q_table)
        
        
def load_table():
    return np.loadtxt("Saved Q-table")
        
