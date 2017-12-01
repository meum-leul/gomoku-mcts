from math import *
import random
import copy


iternum = 10000 # iternum >= 10000 is recommanded.
sidesize = 17 # sidesize >= 5

mapsize = sidesize * sidesize

# containing recommanded points by CNN
recom = []


def cal_winlist(n):
    win_state_list = []

    for i in range(n):
        for j in range(n):
            # case -
            if j <= n - 5:
                tar0 = i * n + (j + 0)
                tar1 = i * n + (j + 1)
                tar2 = i * n + (j + 2)
                tar3 = i * n + (j + 3)
                tar4 = i * n + (j + 4)

                win_state_list.append((tar0, tar1, tar2, tar3, tar4))

            # case |
            if i <= n - 5:
                tar0 = (i + 0) * n + j
                tar1 = (i + 1) * n + j
                tar2 = (i + 2) * n + j
                tar3 = (i + 3) * n + j
                tar4 = (i + 4) * n + j

                win_state_list.append((tar0, tar1, tar2, tar3, tar4))

            # case \
            if i <= n - 5 and j <= n - 5:
                tar0 = (i + 0) * n + (j + 0)
                tar1 = (i + 1) * n + (j + 1)
                tar2 = (i + 2) * n + (j + 2)
                tar3 = (i + 3) * n + (j + 3)
                tar4 = (i + 4) * n + (j + 4)

                win_state_list.append((tar0, tar1, tar2, tar3, tar4))

            # case /
            if i >= 4 and j <= n - 5:
                tar0 = (i - 0) * n + (j + 0)
                tar1 = (i - 1) * n + (j + 1)
                tar2 = (i - 2) * n + (j + 2)
                tar3 = (i - 3) * n + (j + 3)
                tar4 = (i - 4) * n + (j + 4)

                win_state_list.append((tar0, tar1, tar2, tar3, tar4))

    return win_state_list

def cal_maplist(n):
    map_dot_list = []
    for i in range(n):
        map_dot_list.append(0)

    return map_dot_list


maplist = cal_maplist(mapsize)
winlist = cal_winlist(sidesize)


class GoMoKu:
    def __init__(self, state = maplist):
        self.playerJustMoved = 2
        self.state = state
        
    def Clone(self):
        state = GoMoKu()
        state.state = self.state[:]
        state.playerJustMoved = self.playerJustMoved
        return state
    
    def DoMove(self, move):
        assert move >= 0 and move <= mapsize - 1 and self.state[move] == 0
        self.playerJustMoved = 3 - self.playerJustMoved
        self.state[move] = self.playerJustMoved
        
        
    def GetMoves(self):      
        if self.checkState() != 0:
            return []
        
        else:
            moves = []
            for i in range(mapsize):
                #if self.state[i] == 0:
                if self.state[i] == 0 and recom.count(i) != 0:
                    moves.append(i)
                    
            return moves
        
    def GetResult(self, playerjm):
        result = self.checkState()
        assert result != 0
        if result == -1:
            return 0.5
        
        elif result == playerjm:
            return 1.0
        else:
            return 0.0
        
        
    def checkState(self):
        for (v,w,x,y,z) in winlist:
            if self.state[v] == self.state[w] ==  self.state[x] == self.state[y] == self.state[z]:
                if self.state[v] == 1:
                    return 1
                elif self.state[v] == 2:
                    return 2
               
        if [i for i in range(mapsize) if self.state[i] == 0] == []:
            return -1
        return 0
    
    def __repr__(self):
        s = ""
        for i in range(mapsize):
            s += ".0X"[self.state[i]]
            if i % sidesize == sidesize - 1:
                s += "\n"
        return s
        
class Node:
    def __init__(self, move = None, parent = None, state = None):
        self.move = move
        self.parentNode = parent
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.untriedMoves = state.GetMoves()
        self.playerJustMoved = state.playerJustMoved
        
    def UCTSelectChild(self):
        s = sorted(self.childNodes, key = lambda c: c.wins/c.visits + sqrt(2 * log(self.visits) / c.visits))
        return s[-1]
    
    def AddChild(self, m ,s):
        n = Node(move = m, parent = self, state = copy.deepcopy(s))
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n
    
    def Update(self, result):
        self.visits += 1
        self.wins += result
        
    def __repr__(self):
        return "[M" + str(self.move) + " W/V " + str(self.wins) + "/" + str(self.visits) + " U" + str(self.untriedMoves) + "]"
    
    def ChildrenToString(self):
        s =""
        for c in self.childNodes:
            s += str(c) + "\n"
        return s
    
    
def UCT(recommanded_state, rootstate, itermax):
    rootnode = Node(state=rootstate)
    
    # by CNN
    recom = recommanded_state
    
    for i in range(itermax):
        node = rootnode
        state = copy.deepcopy(rootstate)
        
        # selection
        while node.untriedMoves == [] and node.childNodes != []:
            node = node.UCTSelectChild()
            state.DoMove(node.move)
        
        # expansion
        if node.untriedMoves != []:
            m = random.choice(node.untriedMoves)
            state.DoMove(m)
            node = node.AddChild(m, state)
        
        # simulation
        while state.GetMoves() != []:
            state.DoMove(random.choice(state.GetMoves()))
        
        # BackPropagation
        while node != None:
            node.Update(state.GetResult(node.playerJustMoved))
            node = node.parentNode
            
    print(rootnode.ChildrenToString())
    
    s = sorted(rootnode.childNodes, key = lambda c: c.wins/c.visits)
    return sorted(s, key = lambda c: c.visits)[-1].move
    
        
def UCTPlayGame(recommanded_state):
    state = GoMoKu()
    while state.GetMoves() != []:
        if state.playerJustMoved == 2:
            rootstate = copy.deepcopy(state)
            m = UCT(recommanded_state, rootstate, itermax = iternum)
        else:
            m, n = input("which Do you want? : ").split()
            m = int(m); m -= 1
            n = int(n); n -= 1
            m = m * sidesize + n
        # print("Best Move : " + str(m) + "\n")
        state.DoMove(m)
        print(str(state))
        
    if state.GetResult(state.playerJustMoved) == 1.0:
        print("Player " + str(state.playerJustMoved) + " Wins!!")
 
    elif state.GetResult(state.playerJustMoved) == 0.0:
        print("Payer " + str(3 - state.playerJustMoved) + " Wins!!")

    else: print("Draw!!")
    
    
if __name__ == "__main__":
    # get recommanded_state
    # ...
    UCTPlayGame(recommanded_state) 
