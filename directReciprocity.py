#Model Assumptions
#Fitness values range from 0 to 1 (standard assumption)
#Semi-Random seeding of initial pop (Try rand value, if that square is occupied, just take the first open square)
#Birth and Death rate the same and fixed for all cell types
#No mutation (as of yet)

import numpy as np
import random
from enum import Enum
import inspect



def getMooreNeighborhood(self, grid, i, j):
    neighbors = getVonNeumannNeighborhood(grid, i, j)

    if i-1 < 0 or j+1 >= len(grid[i-1]): #use of grid[i-1] will avoid error in case of a jagged 2d array
        neighbors.append(self.EMPTY)
    else:
        neighbors.append(grid[i-1,j+1]) #Northeast

    if i+1 >= len(grid) or j+1 >= len(grid[i+1]): #use of grid[i+1] will avoid error in case of a jagged 2d array
        neighbors.append(self.EMPTY)
    else:
        neighbors.append(grid[i+1,j+1]) #Southeast

    if i+1 >= len(grid) or j-1 < 0:
        neighbors.append(self.EMPTY)
    else:
        neighbors.append(grid[i+1,j-1]) #Southwest

    if i-1 < 0 or j-1 < 0: #use of grid[i-1] will avoid error in case of a jagged 2d array
        neighbors.append(self.EMPTY)
    else:
        neighbors.append(grid[i-1,j-1]) #Northwest

    return neighbors


def getVonNeumannNeighborhood(self, grid, i, j):
    neighbors = []
    if i-1 < 0:
        neighbors.append(self.EMPTY)
    else:
        neighbors.append(grid[i-1,j]) #North

    if j+1 >= len(grid[i]):
        neighbors.append(self.EMPTY)
    else:
        neighbors.append(grid[i, j+1]) #East

    if i+1 >= len(grid):
        neighbors.append(self.EMPTY)
    else:
        neighbors.append(grid[i+1,j]) #South

    if j-1 < 0:
        neighbors.append(self.EMPTY)
    else:
        neighbors.append(grid[i, j-1]) #West

    return neighbors

class Strategy(Enum):
    """Strategy is an enum representing how a player will act in the evolution game"""
    COOPERATOR = 1
    DEFECTOR = 2




coopC = .25
coopB = .3

class NeighborDirection(Enum):
    """The indicies of each direction in the neighbor list"""
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
    NORTHEAST = 4
    SOUTHEAST = 5
    SOUTHWEST = 6
    NORTHWEST = 7

class Player(object):
    """Player represents a player of the evolution game, it has grid coordinates, fitness level, and a strategy for playing the game"""

    def __init__(self, i, j, strategy):

        self.i = i #may not need these
        self.j = j
        self.fitness = 0
        self.strat = strategy
        self.neighbors = []
        self.prevOppMoves = np.zeros(8) #just initialize to 8 to cover largest case # list of the previous moves of each neighbor, neighbor direction is index of move in list
        self.currOppMoves = np.zeros(8) #just initialize to 8 to cover largest case # list of moves of each neighbor in the current grid update

    def setNeighbors(self, grid): #must be called after entire grid is initialized
        self.neighbors = getMooreNeighborhood(grid, self.i, self.j)

    def updateFitnessOwnMove(self):  # 1/2 functions where strategy pays off

        for n in self.neighbors:
            if isinstance(n, Player):
                move = self.chooseMoveDirectReciprocity(self.prevOppMoves[self.neighbors.index(n)])
                if move == Strategy.COOPERATOR:
                    self.fitness = self.fitness - coopC  #loses the cost if this player cooperates
                else:
                    self.fitness = self.fitness - 0 #no cost if this player defects

                n.currOppMoves[n.neighbors.index(self)] = move

    def updateFitnessDueToOppMoves(self): # should be called after all players have made their currOppMoves - 2/2 functions where strategy pays off
        for m in self.currOppMoves:
            if m == 1:
                self.fitness = self.fitness + coopB # recieves benefit from neighbor cooperating
            else: #neighbor defected, recieves no benefit
                self.fitness = self.fitness + 0
        self.prevOppMoves = self.currOppMoves


    def chooseMoveDirectReciprocity(self, opponentLastMove): #returns the strategy for this turn  #where strategy behaviour is executed
        if self.strat == Strategy.COOPERATOR:
            if opponentLastMove == 0:
                return 1 # cooperates
            else:
                return opponentLastMove   #basically tit for tat, open to change # TODO:
        else:
            if opponentLastMove == 0:
                return 2 #defects
            else:
                return opponentLastMove  #tit for tat with start on defect, open to change:

    def __repr__(self):
        if self.strat == Strategy.COOPERATOR:
            return str(1)
        else: #DEFECTOR
            return str(2)

    def __str__(self):
        if self.strat == Strategy.COOPERATOR:
            return str(1)
        else: #DEFECTOR
            return str(2)

def main():
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

    #success counters?
    CoopBirths = 0
    DefectBirths = 0

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
            grid[a,b] = Player(a,b,Strategy.COOPERATOR)
            C_ind.append(grid[a,b])
        else:
            for i in np.arange(0,K-1):
                for j in np.arange(0,K-1):
                    if grid[i,j] ==0:
                        ind.append([i,j])
            grid[ind[0][0],ind[0][1]] = Player(a,b,Strategy.COOPERATOR)
            C_ind.append(grid[ind[0][0],ind[0][1]])
            ind = []
        count+=1

        if grid[c,d] == 0:
            grid[c,d] = Player(c,d,Strategy.DEFECTOR)
            D_ind.append(grid[c,d])
        else:
            for i in np.arange(0,K-1):
                for j in np.arange(0,K-1):
                    if grid[i,j] ==0:
                        ind.append([i,j])
            grid[ind[0][0],ind[0][1]] = Player(c,d,Strategy.DEFECTOR)
            D_ind.append(grid[ind[0][0],ind[0][1]])
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
                            if grid[prolif[0]+1,prolif[1]] == 0 & prolif[0]+1<K-1:  #TODO this condition seems like it is in the wrong order
                                # TODO why do we make sure not to have prolif[0]+1 = k-1? wont we ignore a row of grid?
                                grid[prolif[0]+1,prolif[1]] = 1
                    elif grid[i+1,j]==2:
                        Cfit[count] = Cfit[count]-cost
                        if Cfit[count] < d:
                            dies = C_ind[count]
                            grid[dies[0],dies[1]] = 0
                        elif Cfit[count] > b: #need a check on prolif, cc or stasis threshold
                            prolif = C_ind[count]
                            if grid[prolif[0]+1,prolif[1]] ==0 & prolif[0]+1<K-1: #TODO this condition seems like it is in the wrong order
                                # TODO why do we make sure not to have prolif[0]+1 = k-1? wont we ignore a row of grid?
                                grid[prolif[0]+1,prolif[1]] = 1
                    count+=1



    print(grid)


if __name__ == "__main__":
    main()
