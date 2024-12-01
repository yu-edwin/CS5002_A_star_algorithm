from __future__ import annotations
import numpy as np
import itertools
import heapq
import time
import random
import copy
from collections import deque
import multiprocessing as mp
import pandas as pd
import pickle

# GOAL = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]],dtype=np.int8)
SOLVED_PUZZLE = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]],dtype=np.int8)
SOLVED = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]],dtype=np.int8).tobytes()
UNSOLVABLE = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,15,14,0]],dtype=np.int8).tobytes()
GOAL = [(3,3),(0,0),(0,1),(0,2),(0,3),(1,0),(1,1),(1,2),(1,3),(2,0),(2,1),(2,2),(2,3),(3,0),(3,1),(3,2)]

class Board:
    def __init__(self,state: np.array = None, heuristic = None):
        self.board = state if state else SOLVED_PUZZLE # sets inital board state if given, otherwise set as solved board
        self.h = self.heuristic() if heuristic else -1 # calls function to calculate heuristic, otherwise -1

    @property
    def bytes(self):
        return self.board.tobytes()
    
    # don't use this, use self.walk() instead
    # def make_board(self):
    #     b = np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0],dtype=np.int8)
    #     np.random.shuffle(b)
    #     b.resize(4,4)
    #     self.fix()
    #     self.board = b
    #     self.bytes = b.tobytes()

    def heuristic(self):
        """Calculates distance heuristic.
        Sum of differences of the indices 
        Example:
            [[ 1  2  3  4]
             [ 5  6  7  8]
             [ 9 10 11 12]
             [13 14 15  0]] heuristic 0

            [[ 1  2  3  4]
             [ 5  6  7  8]
             [ 9 10 11  0]
             [13 14 15 12]] heuristic 2
            
            [[ 1  2  3  4]
             [ 5  0  7  8]
             [ 9  6 10 11]
             [13 14 15 12]] heuristic 8
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
            copy = self.board.copy()
            copy[row,col], copy[row-1,col] = copy[row-1,col], copy[row,col]
            if self.h == -1:
                out.append(Board(state=copy))
            else:
                out.append(Board(state=copy,heuristic=True))
        if row != 3:
            copy = self.board.copy()
            copy[row,col], copy[row+1,col] = copy[row+1,col], copy[row,col]
            if self.h == -1:
                out.append(Board(state=copy))
            else:
                out.append(Board(state=copy,heuristic=True))
        if col != 0:
            copy = self.board.copy()
            copy[row,col], copy[row,col-1] = copy[row,col-1], copy[row,col]
            if self.h == -1:
                out.append(Board(state=copy))
            else:
                out.append(Board(state=copy,heuristic=True))
        if col != 3:
            copy = self.board.copy()
            copy[row,col], copy[row,col+1] = copy[row,col+1], copy[row,col]
            if self.h == -1:
                out.append(Board(state=copy))
            else:
                out.append(Board(state=copy,heuristic=True))
        return out

    def __repr__(self) -> str:
        return f"{self.board}"
    
    def walk(self, n: int = 10):
        """Random walk on self.board with n steps.
        Random walk won't walk back onto a visited state *
        Doesn't guarantee shortest path is n.
        """
        row, col = np.where(self.board == 0)
        visited = set([self.bytes])
        for i in range(n): 
            possibilites = []
            if row != 0:
                possibilites.append((row-1,col))
            if row != 3:
                possibilites.append([row+1,col])
            if col != 0:
                possibilites.append([row,col-1])
            if col != 3:
                possibilites.append([row,col+1])
            random.shuffle(possibilites)
            while possibilites: # prevent walking back to visited state
                new_row, new_col = possibilites.pop()
                self.board[row,col], self.board[new_row, new_col] = self.board[new_row, new_col], self.board[row,col]
                if self.bytes not in visited:
                    visited.add(self.bytes)
                    row, col = new_row, new_col # new location of 0
                    break
                else:
                    self.board[row,col], self.board[new_row, new_col] = self.board[new_row, new_col], self.board[row,col]
            else: # got stuck in a corner and I'm too lazy to fix it for real (recursively calls until it works):
                print('recursing',n)
                new = Board()
                new.walk(n)
                self.board = new.board
                return


def bfs(board):
    t1 = time.time()
    chart = {board.bytes: [0, None]} # shows all explored states, visited
    counter = itertools.count()
    queue = deque([board]) # queue, "unvisited"
    stop = False
    while queue and not stop:
        if len(queue) > 10000000:
            # stop search if queue gets too big
            break
        node = queue.popleft()
        neighbours = node.get_neighbours()

        for i in neighbours:
            if i.bytes not in chart:
                queue.append(i)
                chart[i.bytes] = [node.bytes]
            elif i.bytes in chart:
                continue
            

            if i.bytes == SOLVED or i.bytes == UNSOLVABLE:
                # stop search if solved
                stop = True
                break

    if stop:
        # print('SOLVED')
        pass
    elif len(queue) > 10000000:
        print(f'BIG HEAP, {len(queue)=}')
    total_time = time.time()-t1
    print(f'sampled {len(chart)} states in {total_time:.2f} seconds')

    return len(chart), len(queue), total_time

def dfs(board):
    t1 = time.time()
    chart = {board.bytes: [0, None]} # shows all explored states, visited
    counter = itertools.count()
    stack = [board] # queue, "unvisited"
    stop = False
    while stack and not stop:
        if len(stack) > 10000000:
            # stop search if queue gets too big
            break
        node = stack.pop()
        neighbours = node.get_neighbours()

        for i in neighbours:
            if i.bytes not in chart:
                stack.append(i)
                chart[i.bytes] = [node.bytes]
            elif i.bytes in chart:
                continue
            

            if i.bytes == SOLVED or i.bytes == UNSOLVABLE:
                # stop search if solved
                stop = True
                break

    if stop:
        # print('SOLVED')
        pass
    elif len(stack) > 10000000:
        print(f'BIG HEAP, {len(stack)=}')
    total_time = time.time()-t1
    print(f'sampled {len(chart)} states in {total_time:.2f} seconds')

    return len(chart), len(stack), total_time

def dijkstra(board):
    t1 = time.time()
    chart = {board.bytes: [0, None]} # shows all explored states, visited
    counter = itertools.count()
    heap = [(0,next(counter),board)] # priority queue, "unvisited"
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
                chart[i.bytes] = [distance+1,node.bytes]
            elif i.bytes in chart:
                if distance + 1 < chart[i.bytes][0]: # done for completeness, 15puzzle dijkstra should never hit this
                    chart[i.bytes] = [distance+1, node.bytes]
            

            if i.bytes == SOLVED or i.bytes == UNSOLVABLE:
                # stop search if solved
                stop = True
                break

    if stop:
        # print('SOLVED')
        pass
    elif len(heap) > 10000000:
        print(f'BIG HEAP, {len(heap)=}')
    total_time = time.time()-t1
    print(f'sampled {len(chart)} states in {total_time:.2f} seconds')

    return len(chart), len(heap), total_time

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
            new_distance = node.h + distance + 1
            if i.bytes not in chart:
                heapq.heappush(heap, (i.h,next(counter),i))
                chart[i.bytes] = [new_distance, node.bytes]
            elif i.bytes in chart:
                if new_distance < chart[i.bytes][0]:
                    chart[i.bytes] = [new_distance, node.bytes]
            
            if i.bytes == SOLVED or i.bytes == UNSOLVABLE:
                stop = True
                break

    if stop:
        # print('SOLVED')
        pass
    elif len(heap) > 10000000:
        print(f'BIG HEAP, {len(heap)=}')
    total_time = time.time()-t1
    print(f'sampled {len(chart)} states in {total_time:.2f} seconds')

    return len(chart), len(heap), total_time

def path(chart: dict[bytes,tuple[int,int,Board]], state: bytes):
    new = chart[state]
    while new[2]:
        print(new[2].board)
        new = chart[new[2].tobytes()]
        
def a_star_mp(board: Board):
    """a_star worker function for multiprocessing
    """
    board.heuristic()
    chart_size, heap_size, total_time = a_star(board)
    return chart_size, heap_size, total_time

def dijkstra_mp(board: Board):
    """dijkstra worker function for multiprocessing
    """
    chart_size, heap_size, total_time = dijkstra(board)
    return chart_size, heap_size, total_time

def bfs_mp(board: Board):
    """bfs worker function for multiprocessing
    """
    chart_size, queue_size, total_time = bfs(board)
    return chart_size, queue_size, total_time

def dfs_mp(board: Board):
    """dfs worker function for multiprocessing
    """
    chart_size, stack_size, total_time = dfs(board)
    return chart_size, stack_size, total_time


# def compare_methods(n: int, methods = [a_star, dijkstra]):
#     original = Board(state=np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]],dtype=np.int8),heuristic=False)
#     original.walk(n)
    
#     out = {}
#     for i in methods:
#         board = Board(state=original.board, heuristic=i.__name__)
#         chart, heap, total_time = i(board)
#         out[f"{i.__name__}_states"] = len(chart)
#         out[f"{i.__name__}_heap"] = len(heap)
#         out[f"{i.__name__}_time"] = total_time

#     return out

