#Model Assumptions
#Fitness values range from 0 to 1 (standard assumption)
#Semi-Random seeding of initial pop (Try rand value, if that square is occupied, just take the first open square)
#Birth and Death rate the same and fixed for all cell types
#No mutation (as of yet)

import numpy as np
import random
from enum import Enum
import inspect



def getMooreNeighborhood(grid, i, j):
    neighbors = getVonNeumannNeighborhood(grid, i, j)

    if i-1 < 0 or j+1 >= len(grid[i-1]): #use of grid[i-1] will avoid error in case of a jagged 2d array
        neighbors.append(None)
    else:
        neighbors.append(grid[i-1][j+1]) #Northeast

    if i+1 >= len(grid) or j+1 >= len(grid[i+1]): #use of grid[i+1] will avoid error in case of a jagged 2d array
        neighbors.append(None)
    else:
        neighbors.append(grid[i+1][j+1]) #Southeast

    if i+1 >= len(grid) or j-1 < 0:
        neighbors.append(None)
    else:
        neighbors.append(grid[i+1][j-1]) #Southwest

    if i-1 < 0 or j-1 < 0: #use of grid[i-1] will avoid error in case of a jagged 2d array
        neighbors.append(None)
    else:
        neighbors.append(grid[i-1][j-1]) #Northwest

    return neighbors


def getVonNeumannNeighborhood(grid, i, j):
    neighbors = []
    if i-1 < 0:
        neighbors.append(None)
    else:
        neighbors.append(grid[i-1][j]) #North

    if j+1 >= len(grid[i]):
        neighbors.append(None)
    else:
        neighbors.append(grid[i][j+1]) #East

    if i+1 >= len(grid):
        neighbors.append(None)
    else:
        neighbors.append(grid[i+1][j]) #South

    if j-1 < 0:
        neighbors.append(None)
    else:
        neighbors.append(grid[i][j-1]) #West

    return neighbors

class Strategy(Enum):
    """Strategy is an enum representing how a player will act in the evolution game"""
    COOPERATOR = 1
    DEFECTOR = 2
    TITTAT = 3


b = 0.9 #birth threshold
d = 0.0 #death threshold
coopC = .05
coopB = .1

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

        self.i = i
        self.j = j
        self.fitness = 0.45
        self.strat = strategy
        self.neighbors = []
        self.prevOppMoves = np.zeros(8) #just initialize to 8 to cover largest case # list of the previous moves of each neighbor, neighbor direction is index of move in list
        self.currOppMoves = np.zeros(8)#just initialize to 8 to cover largest case # list of moves of each neighbor in the current grid update

    def setNeighbors(self, grid): #must be called after entire grid is initialized
        self.neighbors = getMooreNeighborhood(grid, self.i, self.j)

    def updateFitnessOwnMove(self):  # 1/2 functions where strategy pays off

        for n in self.neighbors:
            if isinstance(n, Player):
                move = self.chooseMoveDirectReciprocity(self.prevOppMoves[self.neighbors.index(n)])
                if move == Strategy.COOPERATOR.value:
                    self.fitness = self.fitness - coopC  #loses the cost if this player cooperates
                else:
                    self.fitness = self.fitness #no cost if this player defects
                n.currOppMoves[n.neighbors.index(self)] = move

    def updateFitnessDueToOppMoves(self): # should be called after all players have made their currOppMoves - 2/2 functions where strategy pays off
        for n in self.neighbors:
            if isinstance(n, Player):
                m = self.currOppMoves[self.neighbors.index(n)]
                if m == 1:
                    self.fitness = self.fitness + coopB # recieves benefit from neighbor cooperating
                else: #neighbor defected, recieves no benefit
                    self.fitness = self.fitness + 0
        self.prevOppMoves = self.currOppMoves


    def chooseMoveDirectReciprocity(self, opponentLastMove): #returns the strategy for this turn  #where strategy behaviour is executed
        if self.strat == Strategy.COOPERATOR:
            return 1

        elif self.strat == Strategy.TITTAT:
            if opponentLastMove == 0:
                return 1 # cooperates
            else:
                return opponentLastMove   #basically tit for tat, open to change # TODO:
        else:
            return 2


    def shouldDie(self):
        return self.fitness < d

    def shouldGiveBirth(self):
        return self.fitness > b

    def getRandomEmptyNeighbor(self, grid):
        count = random.randint(1, len(self.neighbors)+1)
        origCount = count
        ind = 0
        tries = 0
        while count > 0:

            if ind == NeighborDirection.NORTH:
                res = [self.i-1, self.j]
            elif ind == NeighborDirection.EAST:
                res =  [self.i, self.j + 1]
            elif ind == NeighborDirection.SOUTH:
                res =  [self.i+1, self.j]
            elif ind == NeighborDirection.WEST:
                res = [self.i, self.j-1]
            elif ind == NeighborDirection.NORTHEAST:
                res =  [self.i-1, self.j+1]
            elif ind == NeighborDirection.SOUTHEAST:
                res =  [self.i+1, self.j+1]
            elif ind == NeighborDirection.SOUTHWEST:
                res = [self.i+1, self.j-1]
            else: # direction is NORTHWEST
                res = [self.i-1, self.j-1]

            n = self.neighbors[ind]
            if n is None and not (res[0] < 0 or res[1] < 0 or res[0] >= len(grid) or res[1] >= len(grid[res[0]])):
                count = count - 1
            ind = (ind + 1) % len(self.neighbors)
            tries = tries + 1

            if tries > origCount * len(self.neighbors): # this will occur when there are no valid spots to reproduce
                return [-1,-1]
        return res


    def __repr__(self):
        return '   ' + str(self.strat.value)

    def __str__(self):
        return str(self.strat.value)

def printGrid(grid):
    for row in grid:
        print(row)

def printFitnessGrid(grid):
    for i in np.arange(0, len(grid)):
        line = ' '
        for j in np.arange(0, len(grid[i])):
            if grid[i][j] is not None:
                line = line + f'{grid[i][j].fitness:.2f}' + '  '
            else:
                line = line + '----  '
        print(line)

def avgFitness(grid, strat):
    totalFit = 0
    num = 0
    for i in np.arange(0, len(grid)):
        for j in np.arange(0, len(grid[i])):
            if grid[i][j] is not None and grid[i][j].strat == strat:
                totalFit += grid[i][j].fitness
                num += 1
    if num != 0:
        return totalFit/num
    else:
        return 0

def randomGrid(grid, init_counts):
    count = 0
    ind = []
    while count < init_counts:
        a = random.randint(0,len(grid)-1)
        b = random.randint(0,len(grid[0])-1)
        c = random.randint(0,len(grid)-1)
        d = random.randint(0,len(grid[0])-1)
        e = random.randint(0,len(grid)-1)
        f = random.randint(0,len(grid[0])-1)
        if grid[a][b] is None:
            grid[a][b] = Player(a,b,Strategy.COOPERATOR)
        else:
            for i in np.arange(0,len(grid)):
                for j in np.arange(0,len(grid[i])):
                    if grid[i][j] is None:
                        ind.append([i,j])
            grid[ind[0][0]][ind[0][1]] = Player(ind[0][0],ind[0][1],Strategy.COOPERATOR)
            ind = []
        count+=1

        if grid[c][d] is None:
            grid[c][d] = Player(c,d,Strategy.DEFECTOR)
        else:
            for i in np.arange(0,len(grid)):
                for j in np.arange(0,len(grid[i])):
                    if grid[i][j] is None:
                        ind.append([i,j])
            grid[ind[0][0]][ind[0][1]] = Player(ind[0][0],ind[0][1],Strategy.DEFECTOR)
            ind = []
        count+=1

        if grid[e][f] is None:
            grid[e][f] = Player(e,f,Strategy.DEFECTOR)
        else:
            for i in np.arange(0,len(grid)):
                for j in np.arange(0,len(grid[i])):
                    if grid[i][j] is None:
                        ind.append([i,j])
            grid[ind[0][0]][ind[0][1]] = Player(ind[0][0],ind[0][1],Strategy.TITTAT)
            ind = []
        count+=1

    return grid

def titGrid(grid, init_counts):
    count = 0
    ind = []
    while count < init_counts:

        e = random.randint(0,len(grid)-1)
        f = random.randint(0,len(grid[0])-1)


        if grid[e][f] is None:
            grid[e][f] = Player(e,f,Strategy.DEFECTOR)
        else:
            for i in np.arange(0,len(grid)):
                for j in np.arange(0,len(grid[i])):
                    if grid[i][j] is None:
                        ind.append([i,j])
            grid[ind[0][0]][ind[0][1]] = Player(ind[0][0],ind[0][1],Strategy.TITTAT)
            ind = []
        count+=1

    return grid

def coopGrid(grid, init_counts):
    count = 0
    ind = []
    while count < init_counts:
        a = random.randint(0,len(grid)-1)
        b = random.randint(0,len(grid[0])-1)
        if grid[a][b] is None:
            grid[a][b] = Player(a,b,Strategy.COOPERATOR)
        else:
            for i in np.arange(0,len(grid)):
                for j in np.arange(0,len(grid[i])):
                    if grid[i][j] is None:
                        ind.append([i,j])
            grid[ind[0][0]][ind[0][1]] = Player(ind[0][0],ind[0][1],Strategy.COOPERATOR)
            ind = []
        count+=1

    return grid

def defectGrid(grid, init_counts):
    count = 0
    ind = []
    while count < init_counts:
        c = random.randint(0,len(grid)-1)
        d = random.randint(0,len(grid[0])-1)

        if grid[c][d] is None:
            grid[c][d] = Player(c,d,Strategy.DEFECTOR)
        else:
            for i in np.arange(0,len(grid)):
                for j in np.arange(0,len(grid[i])):
                    if grid[i][j] is None:
                        ind.append([i,j])
            grid[ind[0][0]][ind[0][1]] = Player(ind[0][0],ind[0][1],Strategy.DEFECTOR)
            ind = []
        count+=1

    return grid


def main():
    #Set Initial Parameters

    K = 5 #size of grid ie carrying capacity
    C0 = 3 #labled as 1
    D0 = 3 #labled as 2
    T0 = 4

    init_counts = C0+D0+T0
    grid = [[None for s in range(K)] for t in range(K)]

    grid = randomGrid(grid, init_counts)
    #grid = coopGrid(grid, init_counts)
    #grid = defectGrid(grid, init_counts)
    #grid = titGrid(grid, init_counts)

    #success counters
    CoopBirths = 0
    DefectBirths = 0
    TitBirths = 0
    CoopDeaths = 0
    DefectDeaths = 0
    TitDeaths = 0



    print('Initial population: ')
    printGrid(grid)
    print('\n Corresponding Fitness:')
    printFitnessGrid(grid)
    print(' ')

    b = 0.9 #birth threshold
    d = 0.0 #death threshold
    #Run CA
    #Check neighbors and updates fit according to payoff matrix, using standard payoff matrix
    timesteps = 5
    while timesteps > 0:
        for i in np.arange(0, K):
            for j in np.arange(0, K):
                if grid[i][j] is not None:
                    # prepare all neighbors
                    grid[i][j].setNeighbors(grid)
        for i in np.arange(0, K):
            for j in np.arange(0, K):
                if grid[i][j] is not None:
                    # this is where we update fitness based on own moves this turn
                    grid[i][j].updateFitnessOwnMove()
        for i in np.arange(0, K):
            for j in np.arange(0, K):
                if grid[i][j] is not None:
                    # this is where we update fitness based on neighbors' moves this turn
                    grid[i][j].updateFitnessDueToOppMoves()
        for i in np.arange(0, K):
            for j in np.arange(0, K):
                if grid[i][j] is not None:

                    if grid[i][j].shouldDie():  #will defectors ever die?
                        if grid[i][j].strat == Strategy.COOPERATOR:
                            CoopDeaths += 1
                        elif grid[i][j].strat == Strategy.TITTAT:
                            TitDeaths += 1
                        else:
                            DefectDeaths += 1
                        grid[i][j] = None
                    if grid[i][j] is not None and grid[i][j].shouldGiveBirth():
                        birthCoord = grid[i][j].getRandomEmptyNeighbor(grid)
                        if birthCoord != [-1,-1]:
                            grid[birthCoord[0]][birthCoord[1]] = Player(birthCoord[0], birthCoord[1], grid[i][j].strat)
                            grid[i][j].fitness = grid[i][j].fitness - .45 # subtract 45 to not alter avg fitness
                            if grid[i][j].strat == Strategy.COOPERATOR:
                                CoopBirths = CoopBirths + 1
                            elif grid[i][j].strat == Strategy.TITTAT:
                                TitBirths = TitBirths + 1
                            else:
                                DefectBirths = DefectBirths + 1
        timesteps -=1
    print('Final Population: ')
    printGrid(grid)
    print('Corresponding Fitness: ')
    printFitnessGrid(grid)

    print(f'COOPERATOR Births: {CoopBirths}')
    print(f'DEFECTOR Births: {DefectBirths}')
    print(f'TITTAT Births: {TitBirths}')
    print(f'COOPERATOR Deaths: {CoopDeaths}')
    print(f'DEFECTOR Deaths: {DefectDeaths}')
    print(f'TITTAT Deaths: {TitDeaths}')
    print(f'COOPERATOR Average fitness: {avgFitness(grid, Strategy.COOPERATOR)}')
    print(f'DEFECTOR Average fitness: {avgFitness(grid, Strategy.DEFECTOR)}')
    print(f'TITTAT Average fitness: {avgFitness(grid, Strategy.TITTAT)}')



if __name__ == "__main__":
    main()
