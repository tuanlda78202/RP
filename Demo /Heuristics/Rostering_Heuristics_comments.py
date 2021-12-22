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
F = np.pad(F, ((0,0),(0,1)), mode='constant', constant_values=0)  # add another column of 0s for easier index

# print(F)
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
    # z là số nhân viên đi làm ca đêm vào hôm nay
    # add là số nhân viên cần thêm cho đủ giới hạn
    upper_today = N - off_today - 4*a  # upper bound of the number of employees working in a shift today
    lower_today = N - off_today - 4*b
    # số nhân viên min cần có trong một ca của ngày hôm NAY: tổng nhân viên - số nhân viên không đi làm hôm nay - cận dưới của một ca (có 4 ca nên nhân 4)
    # số nhân viên max cần có trong một ca của ngày hôm NAY: tổng nhân viên - số nhân viên không đi làm hôm nay - cận trên của một ca

    if upper_today < a or lower_today > b:
        return -1
    else:
        z = max(lower_today, a)  # giả sử z (số ca đêm hNAY) nhận giá trị ban đầu chính bằng cận dưới (việc này sẽ đảm bảo được rằng số ca đêm là ít nhất, vì nó chính bằng cận dưới)
        # lower_today có thể nhận giá trị âm, vì vậy lấy max để đảm bảo giới hạn phải là dương


    upper_nextday = N - off_nextday - z - 4*a  # vì có z nhân viên làm ca đêm hôm NAY rồi, nên hôm SAU có z nhân viên được nghỉ
    lower_nextday = N - off_nextday - z - 4*b

    if lower_nextday > b:  # nếu lower bound của ngày hôm sau lớn hơn b (giới hạn của đề bài) thì cắt bớt cho phù hợp
        z += (lower_nextday - b)
    elif upper_nextday < a:  # ngược lại, thấp hơn thì mình cần bổ sung
        add = a - upper_nextday  # add employees to suffice the bound
    else:  # đã đủ nhân viên
        add = 0

    if z > b or z < a or add > off_nextday:  # kiểm tra điều kiện tồn tại nghiệm
        return -1
    else:
        return z, add


def heuristics(N, D, a, b, F):
    num_night = np.full(N, 0)  # number of night shifts of each employee
    global x  # matrix solution

    for j in range(D):
        off_today = np.array(F[:, j][:N])  # binary list, cho biết nhân viên nào đi làm và nghỉ làm hôm NAY
        # ví dụ: [0 0 0 1] tức là nhân viên cuối hôm nay  nghỉ (=1 là nghỉ)
        #print(off_today)
        off_nextday = np.array(F[:, j+1][:N])  # tương tự, nhưng của hôm SAU

        if j != 0:  # nhân viên nào làm ca đêm hôm NAY thì sẽ được chuyển vào danh sách nghỉ của ngày hôm SAU
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
        emp_off_nextday = np.array([i for i in range(len(off_nextday)) if off_nextday[i] == 1]) # chỉ số các nv nghỉ hsau
        # ví dụ: [4] -> hôm sau chỉ có nhân viên số 4 nghỉ
        off_night_nextday = np.array([num_night[i] for i in emp_off_nextday])
        # trong số các nhân viên nghỉ vào ngày hôm sau, trích ra số ca đêm của nhân viên đó

        while add > 0:
            emp_index = np.argmin(off_night_nextday)  # lựa chọn ra nhân viên có số ca đêm ít nhất hiện tại
            x[emp_off_nextday[emp_index], j, 3] = 1  # cho đi làm ca đêm
            num_night[emp_off_nextday[emp_index]] += 1  # add 1 employee to today's night shift
            # sau khi gán xong, mình phải đặt nhân viên này sang trạng thái nghỉ hnay
            off_today[emp_off_nextday[emp_index]] = 1  # avoid working more than one shift in a day
            add -= 1

        # Assign other employees to the night shift if needed (choose among idle employees for today)
        emp_work_today = np.array([i for i in range(len(off_today)) if off_today[i] != 1]) # = 0 : hnay đi làm được
        work_night_today = np.array([num_night[i] for i in emp_work_today])  # số ca đêm của các nhân viên đi làm vào hNAY


        while remain > 0:  # tương tự hàm trên
            emp_index = np.argmin(work_night_today)
            x[emp_work_today[emp_index], j, 3] = 1
            num_night[emp_work_today[emp_index]] += 1
            off_today[emp_work_today[emp_index]] = 1
            remain -= 1

        # Assign other employees to other shifts of today
        i, k = 0, 0  # gán những nhân viên còn lại vào các ca sáng, trưa, và chiều
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

