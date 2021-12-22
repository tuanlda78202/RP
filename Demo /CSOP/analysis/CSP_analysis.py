# Import libraries
import numpy as np
from ortools.sat.python import cp_model
from time import time
import csv

# Read Data
def read_data(file):
    with open(file, 'r') as file:
        # read first line
        n, d, a, b = [int(x) for x in file.readline().split()]

        # Matrix (n,d) full 0, if staff i rest day d(i) -> convert to 1
        F = np.full((n, d), 0)
        for staff in range(n):
            # read each line to end, [:-1] bcs end of each line is -1
            temp = [int(x) for x in file.readline().split()[:-1]]  #check each line from 2 -> i+1
            for day in temp:
                F[staff, day-1] = 1 # day-1 bcs index of list
    return n, d, a, b, F

# Input
def solve(n, d, a, b, F):
# Declare the Model
    model = cp_model.CpModel()

    # Create the Variables
    # X[staff, day, shift] = 1 if staff i work on shift k of day j
    # X[staff, day, shift] = 0, otw
    X = {}
    for staff in range(n):              # check each staff
        for day in range(d):            # check each staff
            for shift in range(1,5):    # check each shift
                X[staff, day, shift] = model.NewIntVar(0,1,"X[{},{},{}]".format(staff,day,shift))

    # Each day, a staff can only work one shift at most
    for staff in range(n):
        for day in range(d):
            if F[staff, day] == 0:
                if day == 0:
                    model.Add(sum([X[staff, day, shift] for shift in range(1,5)]) == 1)
                # If you work the night shift the day before, you can rest the next day
                else:
                    model.Add(sum([X[staff, day, shift] for shift in range(1,5)]) + X[staff, day - 1, 4] == 1)
            else: # F[staff, day] == 1
                model.Add(sum([X[staff, day, shift] for shift in range(1,5)]) == 0)

    # Each shift in each day has at least [a] staffs and at most [b] staffs
    for day in range(d):
        for shift in range(1,5):
            model.Add(sum([X[staff, day, shift] for staff in range(n)]) >= a)
            model.Add(sum([X[staff, day, shift] for staff in range(n)]) <= b)

    # F(i): list of staff rest days i
    # The maximum number of night shifts assigned to a specific staff is the smallest

    max_night_shift = model.NewIntVar(1, int(d/2) + 1, 'max_night_shift') # limit rest day = 1/2 all days
    # for loop add constraint confirm sum of all night shift of staff <= max_night_shift
    for staff in range(n):
        model.Add(sum([X[staff, day, 4] for day in range(d)]) - max_night_shift <= 0)


    # Objective Function
    model.Minimize(max_night_shift)

    # Solver
    solver = cp_model.CpSolver()
    status = solver.Solve(model)


res_10_100_30 = []
for i in range(10, 16, 5):
    N, D, a, b, F = read_data(f'data/data-30/dataN{i}D30.txt')
    start = time()
    solve(N, D, a, b, F)
    end = time()
    res_10_100_30.append(end-start)

res_110_300_30 = []
for i in range(110, 301, 10):
    N, D, a, b, F = read_data(f'data/data-30/dataN{i}D30.txt')
    start = time()
    solve(N, D, a, b, F)
    end = time()
    res_110_300_30.append(end-start)

res_10_100_180 = []
for i in range(10, 101, 2):
    N, D, a, b, F = read_data(f'data/data-30/dataN{i}D30.txt')
    start = time()
    solve(N, D, a, b, F)
    end = time()
    res_10_100_180.append(end-start)

res_10_50_365 = []
for i in range(10, 51, 1):
    N, D, a, b, F = read_data(f'data/data-30/dataN{i}D30.txt')
    start = time()
    solve(N, D, a, b, F)
    end = time()
    res_10_50_365.append(end-start)


print('res_10_100_30 =', res_10_100_30)
print('res_110_300_30 =', res_110_300_30)
print('res_10_100_180 =', res_10_100_180)
print('res_10_50_365 =', res_10_50_365)

# write to file
header30_csp = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300]
data30_csp = res_10_100_30 + res_110_300_30

with open('CSP_d30.csv', 'w') as f1:
    writer = csv.writer(f1)
    writer.writerow(header30_csp)
    writer.writerow(data30_csp)

header180_csp = [i for i in range(10, 101, 2)]
data180_csp = res_10_100_180

with open('CSP_d180.csv', 'w') as f2:
    writer = csv.writer(f2)
    writer.writerow(header180_csp)
    writer.writerow(data180_csp)

header365_csp = [i for i in range(10, 50, 1)]
data365_csp = res_10_50_365

with open('CSP_d365.csv', 'w') as f3:
    writer = csv.writer(f3)
    writer.writerow(header365_csp)
    writer.writerow(data365_csp)