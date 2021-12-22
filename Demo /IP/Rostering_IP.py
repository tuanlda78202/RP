from ortools.linear_solver import pywraplp
import numpy as np
from time import time


def input(filename):
    with open(filename) as f:
        N, D, a, b = [int(x) for x in f.readline().split()]
        F = [[0 for _ in range(D)] for _ in range(N)]
        for i in range(N):
            d = [int(x) for x in f.readline().split()[:-1]]
            if d:
                F[i][d[0]-1] = 1

    return N, D, a, b, F


filename = 'data.txt'
N, D, a, b, F = input(filename)
F = np.array(F)
# print('N =', N)
# print('D =', D)
# print('alpha =', a)
# print('beta =', b)
# print(F)

solver = pywraplp.Solver('ROSTERING_MIP', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
INF = solver.infinity()


# DECISION VARIABLES
x = {}
for i in range(N):
    for j in range(D):
        for k in range(1, 5):
            x[i, j, k] = solver.IntVar(0, 1, f'x[{i}, {j}, {k}]')

z = solver.IntVar(0, D, 'Z')

# CONSTRAINTS
# Each employee works no more than one shift every day
for i in range(N):
    for j in range(D):
        if F[i][j] == 0:
            cstr = solver.Constraint(-INF, 1)
            for k in range(1, 5):
                cstr.SetCoefficient(x[i, j, k], 1)
            if j != 0:
                cstr.SetCoefficient(x[i, j-1, 4], 1)

# Employees can have a day off after having a night shift on the previous day
for i in range(N):
    for j in range(D):
        if F[i][j] == 0:
            cstr = solver.Constraint(1, 1)
            for k in range(1, 5):
                cstr.SetCoefficient(x[i, j, k], 1)
                if j != 0:
                    cstr.SetCoefficient(x[i, j-1, 4], 1)

# Employees will not work on their off days
for i in range(N):
    for j in range(D):
        if F[i][j] == 1:
            cstr = solver.Constraint(0, 0)
            for k in range(1, 5):
                cstr.SetCoefficient(x[i, j, k], 1)

# Each shift have at least alpha and beta employees at most
for j in range(D):
    for k in range(1, 5):
        cstr = solver.Constraint(a, b)
        for i in range(N):
            cstr.SetCoefficient(x[i, j, k], 1)

# OBJECTIVE FUNCTION
for i in range(N):  # the maximum night shift of any employee is minimised
    obj = solver.Constraint(0, INF)
    for j in range(D):
        obj.SetCoefficient(x[i, j, 4], -1)
        obj.SetCoefficient(z, 1)



if __name__ == '__main__':
    start = time()

    solver.Minimize(z)
    status = solver.Solve()

    end = time()

    if status == pywraplp.Solver.OPTIMAL:
        print('Optimal value:', solver.Objective().Value())
        for i in range(N):
            for j in range(D):
                for k in range(1, 5):
                    if x[i, j, k].solution_value() > 0:
                        print(f'Employee {i+1}: works on day {j+1}, at shift {k}')

    print('Total execution time:', end-start)

