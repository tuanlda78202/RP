'''
Idea: For each day, we will assign employees to the night shift such that all the conditions are satisfied, and also
incurs the smallest number of night shifts of employees (thus still optimising the total number of night shifts).
Concretely, we will prioritise employees with minimal number of current night shifts and employees that have off days
on the next day.
'''

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
F = np.pad(F, ((0,0),(0,1)), mode='constant', constant_values=0)  # add another column of 0 for easier index

# print('N =', N)
# print('D =', D)
# print('alpha =', a)
# print('beta =', b)
# print(F)

def select(N, off_today, off_nextday, a, b):
    '''
    :param off_today: number of employees cannot work today
    :param off_nextday: number of employees cannot work on the next day
    :return: z = minimum value of the night shift of an employee
    :return: add = number of employees need to add to suffice the bound
    '''
    z, add = 0, 0
    upper_today = N - off_today - 4*a  # upper bound of the number of employees working today
    lower_today = N - off_today - 4*b

    if upper_today < a or lower_today > b:
        return -1
    else:
        z = max(lower_today, a)

    upper_nextday = N - off_nextday - z - 4*a
    lower_nextday = N - off_nextday - z - 4*b

    if lower_nextday > b:
        z += (lower_nextday - b) # remove redundant employees
    elif upper_nextday < a:
        add = a - upper_nextday  # add employees to suffice the bound
    else:
        add = 0

    if z > b or z < a or add > off_nextday:
        return -1
    else:
        return z, add


def heuristics(N, D, a, b, F):
    num_night = np.full(N, 0)  # number of night shifts of each employee
    global x

    for j in range(D):
        off_today = np.array(F[:, j][:N])
        off_nextday = np.array(F[:, j+1][:N])

        if j != 0:
            for i in range(N):
                if x[i, j-1, 3] == 1:  # if employee i worked at the night shift on the previous day, then rest today
                    off_today[i] = 1

        # Select the possible minimum number of night shift
        if select(N, sum(off_today), sum(off_nextday), a, b) is False:
            print('No optimal solution found.')
            return -1
        else:
            z, add = select(N, sum(off_today), sum(off_nextday), a, b)
        remain = z - add

        # Assign the employee with minimum number of night shift (and absent on the next day) to today's night shift
        emp_off_nextday = np.array([i for i in range(len(off_nextday)) if off_nextday[i] == 1])
        off_night_nextday = np.array([num_night[i] for i in emp_off_nextday])

        while add > 0:
            emp_index = np.argmin(off_night_nextday)
            x[emp_off_nextday[emp_index], j, 3] = 1
            num_night[emp_off_nextday[emp_index]] += 1  # add 1 employee to today's night shift
            off_today[emp_off_nextday[emp_index]] = 1  # avoid working more than one shift in a day
            add -= 1

        # Assign other employees to the night shift if needed (choose among idle employees for today)
        emp_work_today = np.array([i for i in range(len(off_today)) if off_today[i] != 1])
        work_night_today = np.array([num_night[i] for i in emp_work_today])

        while remain > 0:
            emp_index = np.argmin(work_night_today)
            x[emp_work_today[emp_index], j, 3] = 1
            num_night[emp_work_today[emp_index]] += 1
            off_today[emp_work_today[emp_index]] = 1
            remain -= 1

        # Assign other employees to other shifts of today
        i, k = 0, 0
        while i < N and k < 3:
            if off_today[i] == 0:
                x[i, j, k] = 1
                off_today[i] = 1  # avoid assigning the same employee in a day
                k = (k+1) % 3
            i += 1
    return max(num_night)


if __name__ == '__main__':
    x = np.full((N, D, 4), 0)  # solution matrix

    start = time()
    res = heuristics(N, D, a, b, F)
    end = time()
    print('The optimal value is:', res)
    print('The optimal solution is:')

    for i in range(N):
        for j in range(D):
            for k in range(4):
                if x[i, j, k] == 1:
                    print(f'Employee {i+1}: works on day {j+1}, at shift {k+1}')

    # print(x)
    print('Total execution time:', end-start)
