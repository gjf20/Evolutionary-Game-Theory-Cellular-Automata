#Model Assumptions
#Fitness values range from 0 to 1 (standard assumption)
#Semi-Random seeding of initial pop (Try rand value, if that square is occupied, just take the first open square)
#Birth and Death rate the same and fixed for all cell types
#No mutation (as of yet)

import numpy as np
import random

#Set Initial Parameters
ben = 0.15 #benefit of interacting with a C
cost = 0.2 #cost of interacting with a D
b = 0.9 #birth threshold
d = 0.1 #death threshold
K = 5 #size of grid ie carrying capacity
C0 = 5 #labled as 1
D0 = 5 #labled as 2
Cfit0 = 0.5 #initial fitness of cell type C
Dfit0 = 0.5 #initial fitness of cell type D
Cfit = np.repeat(Cfit0,K)
Dfit = np.repeat(Dfit0,K)
init_counts = C0+D0
grid = np.zeros((K,K))

#Seed C0,D0
count = 0
C_ind = [] #ignore for now
D_ind = []
ind = []
while count< init_counts:
    a = random.randint(0,K-1)
    b = random.randint(0,K-1)
    c = random.randint(0,K-1)
    d = random.randint(0,K-1)
    if grid[a,b] == 0:
        grid[a,b] = 1
        C_ind.append([a,b])
    else:
        for i in np.arange(0,K-1):
            for j in np.arange(0,K-1):
                if grid[i,j] ==0:
                    ind.append([i,j])
        grid[ind[0][0],ind[0][1]] = 1
        C_ind.append([ind[0][0],ind[0][1]])
        ind = []
    count+=1

    if grid[c,d] == 0:
        grid[c,d] = 2
        D_ind.append([c,d])
    else:
        for i in np.arange(0,K-1):
            for j in np.arange(0,K-1):
                if grid[i,j] ==0:
                    ind.append([i,j])
        grid[ind[0][0],ind[0][1]] = 2
        D_ind.append([ind[0][0],ind[0][1]])
        ind = []
    count+=1
print(grid)
print(C_ind)
print(D_ind)

#Run CA
#Check neighbors and updates fit according to payoff matrix, using standard payoff matrix
count = 0
while count<K:
    for i in np.arange(0,K-2):
        for j in np.arange(0,K-1):
            if grid[i,j]==1:
                if grid[i+1,j]==1:
                    Cfit[count] = Cfit[count]+(ben-cost)
                    if Cfit[count] < d:
                        dies = C_ind[count]
                        grid[dies[0],dies[1]] = 0
                    elif Cfit[count] > b: #need a check on prolif, cc or stasis threshold
                        prolif = C_ind[count]
                        if grid[prolif[0]+1,prolif[1]] == 0 & prolif[0]+1<K-1:
                            grid[prolif[0]+1,prolif[1]] = 1
                elif grid[i+1,j]==2:
                    Cfit[count] = Cfit[count]-cost
                    if Cfit[count] < d:
                        dies = C_ind[count]
                        grid[dies[0],dies[1]] = 0
                    elif Cfit[count] > b: #need a check on prolif, cc or stasis threshold
                        prolif = C_ind[count]
                        if grid[prolif[0]+1,prolif[1]] ==0 & prolif[0]+1<K-1:
                            grid[prolif[0]+1,prolif[1]] = 1
                count+=1



print(grid)
