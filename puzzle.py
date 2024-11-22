from __future__ import annotations
import numpy as np
import itertools
import heapq
import time
import random
# GOAL = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]],dtype=np.int8)
GOAL = [(3,3),(0,0),(0,1),(0,2),(0,3),(1,0),(1,1),(1,2),(1,3),(2,0),(2,1),(2,2),(2,3),(3,0),(3,1),(3,2)]
class Board:
    def __init__(self,state: np.array = None, heuristic = False):
        if state is None:
            self.make_board()
        else:
            self.board = state
            self.bytes = self.board.tobytes()
        
        if heuristic:
            self.heuristic()
        else:
            self.h = -1


    def make_board(self):
        """"""
        b = np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0],dtype=np.int8)
        np.random.shuffle(b)
        b.resize(4,4)
        self.fix()
        self.board = b
        self.bytes = b.tobytes()

    def fix(self):
        """to be implemented
        """
        return
    

    def heuristic(self):
        """Calculates distance heuristic
        """
        self.h = 0
        for idx, i in enumerate(GOAL):
            d1, d2 = i
            row, col = np.where(self.board == idx)
            self.h += abs(d1 - row) + abs(d2 - col)
        self.h = self.h[0]
        return self.h
    
    def get_neighbours(self) -> list[Board]:
        """Gets neighbours in the graph
        Returns:
            list[Board] containing all neighbours
        """
        row, col = np.where(self.board == 0)
        out = []
        if row != 0:
            copy = self.board.copy() # deep
            copy[row,col], copy[row-1,col] = copy[row-1,col], copy[row,col]
            if self.h == -1:
                out.append(Board(state=copy))
            else:
                out.append(Board(state=copy,heuristic=True))
        if row != 3:
            copy = self.board.copy() # deep
            copy[row,col], copy[row+1,col] = copy[row+1,col], copy[row,col]
            if self.h == -1:
                out.append(Board(state=copy))
            else:
                out.append(Board(state=copy,heuristic=True))
        if col != 0:
            copy = self.board.copy() # deep
            copy[row,col], copy[row,col-1] = copy[row,col-1], copy[row,col]
            if self.h == -1:
                out.append(Board(state=copy))
            else:
                out.append(Board(state=copy,heuristic=True))
        if col != 3:
            copy = self.board.copy() # deep
            copy[row,col], copy[row,col+1] = copy[row,col+1], copy[row,col]
            if self.h == -1:
                out.append(Board(state=copy))
            else:
                out.append(Board(state=copy,heuristic=True))
        return out
    
    def walk(self, n: int = 10):
        """Random walk on self.board with n(int) steps.
        Doesn't guarantee shortest path is n.
        """
        row, col = np.where(self.board == 0)
        # print(self.board)
        for i in range(n):
            # print(i)
            possibilites = []
            if row != 0:
                possibilites.append((row-1,col))
            if row != 3:
                possibilites.append([row+1,col])
            if col != 0:
                possibilites.append([row,col-1])
            if col != 3:
                possibilites.append([row,col+1])
            new_row, new_col = random.choice(possibilites)
            # print(f"{[row,col]=}",f"{[new_row,new_col]=}")
            # print(self.board[row,col], self.board[new_row, new_col])
            self.board[row,col], self.board[new_row, new_col] = self.board[new_row, new_col], self.board[row,col]
            row, col = new_row, new_col
            # print(f"{[row,col]=}",f"{[new_row,new_col]=}")
            # print(self.board)



SOLVED = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]],dtype=np.int8).tobytes()
UNSOLVABLE = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,15,14,0]],dtype=np.int8).tobytes()
def dijkstra(board):
    t1 = time.time()
    chart = {board.bytes: [0, None]} # shows all explored states
    counter = itertools.count()
    heap = [(0,next(counter),board)] # priority queue
    stop = False
    while heap and not stop:
        if len(heap) > 10000000:
            # stop search if queue gets too big
            break
        distance, _, node = heapq.heappop(heap)
        neighbours = node.get_neighbours()

        for i in neighbours:
            if i.bytes not in chart:
                heapq.heappush(heap, (distance+1,next(counter),i))
                chart[i.bytes] = [node.h,node.bytes]
            elif i.bytes in chart:
                if distance + 1 < chart[i.bytes][0]: # done for completeness, 15puzzle dijkstra should never hit this
                    chart[i.bytes] = [distance+1, node.bytes]
            

            if i.bytes == SOLVED or i.bytes == UNSOLVABLE:
                # stop search if solved
                stop = True
                break

    if stop:
        print('SOLVED')
    elif len(heap) > 10000000:
        print(f'BIG HEAP, {len(heap)=}')
    total_time = time.time()-t1
    print(f'sampled {len(chart)} states in {total_time:.2f} seconds')

    return chart, heap, total_time

def a_star(board):
    t1 = time.time()
    chart = {board.bytes: [0, None]} # shows all explored states
    counter = itertools.count()
    heap = [(0,next(counter),board)] # priority queue
    stop = False
    while heap and not stop:
        if len(heap) > 10000000:
            # stop search if queue gets too big
            break
        distance, _, node = heapq.heappop(heap)
        neighbours = node.get_neighbours()

        for i in neighbours:
            if i.bytes not in chart:
                heapq.heappush(heap, (i.h,next(counter),i))
                chart[i.bytes] = [node.h,node.bytes]
            elif i.bytes in chart:
                if distance + 1 < chart[i.bytes][0]:
                    chart[i.bytes] = [distance+1, node.bytes]
            
            if i.bytes == SOLVED or i.bytes == UNSOLVABLE:
                stop = True
                break

    if stop:
        print('SOLVED')
    elif len(heap) > 10000000:
        print(f'BIG HEAP, {len(heap)=}')
    total_time = time.time()-t1
    print(f'sampled {len(chart)} states in {total_time:.2f} seconds')

    return chart, heap, total_time

def path(chart: dict[bytes,tuple[int,int,Board]], state: bytes):
    new = chart[state]
    while new[2]:
        print(new[2].board)
        new = chart[new[2].tobytes()]
        
def a_star_mp(n: int):
    """a_star worker function for multiprocessing
    """
    board = Board(state=np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]],dtype=np.int8),heuristic=True)
    board.walk(n)
    chart, heap, total_time = a_star(board)
    return len(chart), len(heap), total_time
