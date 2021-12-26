import numpy as np
import random
N = int(input())
D = int(input())
S = []
for i in range (1,N+1):
    S.append(i)
bound =[]
Nightshift = np.full((N,D),1)
F=[]
def solution(j,S):
    if j == D :
        return Nightshift,bound
    for k in range(1,5):                         
        lowerbound = random.randint(1, N // 4)
        upperbound = lowerbound + random.randint(1, N//4)
        bound.append(lowerbound)
        bound.append(upperbound)
        for i in range (lowerbound,upperbound):       
            '''         h = random.randrange(len(S)) # get random index
            S[h], S[-1] = S[-1], S[h]    # swap with the last element
            x = S.pop()
            '''
            random.shuffle(S)

            while S:
                x = S.pop()
            if k == 4 :
                Nightshift[x-1,j] = 0
    S = []
    for i in range (N):
        if Nightshift[i,j] == 1 :
            S.append(i)
    return solution(j+1,S)
solution(0,S)
a = min(bound)
b = max(bound)
for i in range(N):
    for j in range(D):
        if j == D-1:
            break
        if Nightshift[i,j] == 0 :
            F.append(j+2)
    F.append(-1)
First = [a,b,N,D]

with open(f'data/dataN{N}D{D}.txt', 'w') as f:
    for i in First:
        f.write(str(i)+" ")
    f.write('\n')
    for k in F:
        f.write(str(k)+" ")
        if k == -1 :
            f.write("\n")
