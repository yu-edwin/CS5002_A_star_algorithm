from __future__ import annotations
import numpy as np
import itertools
import heapq
import time

class Board:
    def __init__(self,state: np.array = None):
        if state is None:
            self.make_board()
        else:
            self.board = state
            self.bytes = self.board.tobytes()

    def make_board(self):
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
        """Calculates manhattan distance heuristic
        """
        self.h = 0
        for i in self.goal:
            d1 = self.board.index(i)
            d2 = i - 1 if i else 15
            self.h += abs(d1//4 - d2//4) + abs(d1%4 - d2%4)
        return self.h
    
    def get_neighbours(self) -> list[Board]:
        row, col = np.where(self.board == 0)
        out = []
        if row != 0:
            copy = self.board.copy() # deep
            copy[row,col], copy[row-1,col] = copy[row-1,col], copy[row,col]
            out.append(Board(state=copy))
        if row != 3:
            copy = self.board.copy() # deep
            copy[row,col], copy[row+1,col] = copy[row+1,col], copy[row,col]
            out.append(Board(state=copy))
        if col != 0:
            copy = self.board.copy() # deep
            copy[row,col], copy[row,col-1] = copy[row,col-1], copy[row,col]
            out.append(Board(state=copy))
        if col != 3:
            copy = self.board.copy() # deep
            copy[row,col], copy[row,col+1] = copy[row,col+1], copy[row,col]
            out.append(Board(state=copy))
        return out


SOLVED = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]],dtype=np.int8).tobytes()
UNSOLVABLE = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,15,14,0]],dtype=np.int8).tobytes()
def dijkstra(board):
    # print(board.board)
    t1 = time.time()
    chart = {board.bytes: [0, None]}
    counter = itertools.count()
    heap = [(0,next(counter),board)]
    stop = False
    while heap and not stop:
        if len(heap) > 10000000: # stop it if it gets too big
            break
        distance, _, node = heapq.heappop(heap)
        neighbours = node.get_neighbours()

        # print(f"{len(neighbours)=}")
        for i in neighbours:
            # print(i.board)
            if i.bytes not in chart:
                # print(f'not in chart {i.bytes=}')
                heapq.heappush(heap, (distance+1,next(counter),i)) # push to queue
                chart[i.bytes] = [distance+1,node.bytes] # add to explored
            elif i.bytes in chart:
                # print(f'in chart {i.bytes=}')
                if distance + 1 < chart[i.bytes][0]: # update if shorter, for 15 puzzle in pure dijkstra it should never hit this, done for completeness
                    chart[i.bytes] = [distance+1, node.bytes]
            

            #check if it's the solution
            if i.bytes == SOLVED or i.bytes == UNSOLVABLE:
                stop = True
                break

    if stop:
        print('SOLVED')
    elif len(heap) > 10000000:
        print(f'BIG HEAP, {len(heap)=}')
    print(f'sampled {len(chart)} states in {time.time()-t1:.2f} seconds')

    return chart, heap

def path(chart: dict[bytes,tuple[int,int,Board]], state: bytes):
    new = chart[state]
    while new[2]:
        print(new[2].board)
        new = chart[new[2].tobytes()]
        
