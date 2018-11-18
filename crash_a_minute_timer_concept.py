from time import time
from math import fabs

counter = 0
minute_threshold = 1

start_time = time()

while True:
    cycle_time = time()
    if fabs(start_time - cycle_time) >= minute_threshold*20:
        print(minute_threshold, "minute(s) have passed.\n")
        minute_threshold += 1
