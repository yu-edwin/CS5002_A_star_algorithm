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
import argparse

# GOAL = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]],dtype=np.int8)
SOLVED_PUZZLE = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]],dtype=np.int8)
SOLVED = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]],dtype=np.int8).tobytes()
UNSOLVABLE = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,15,14,0]],dtype=np.int8).tobytes()
GOAL = [(3,3),(0,0),(0,1),(0,2),(0,3),(1,0),(1,1),(1,2),(1,3),(2,0),(2,1),(2,2),(2,3),(3,0),(3,1),(3,2)]

class Board:
    def __init__(self,state: np.array = None, method = None):
        self.board = SOLVED_PUZZLE.copy() if state is None else state # sets inital board state if given, otherwise set as solved board
        # self.h = heuristic # determines if heurstic is needed for this board

        self.scramble_path = []
        self.solve_path = []
        self.method = method

    @property
    def bytes(self):
        return self.board.tobytes()

    @property
    def solved(self):
        return self.bytes == SOLVED
    
    @property
    def scrambled(self):
        return self.bytes != SOLVED


    @property
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
        if self.method != "a_star":
            return 0
        heuristic = 0
        for idx, i in enumerate(GOAL):
            d1, d2 = i
            row, col = np.where(self.board == idx)
            heuristic += abs(d1 - row) + abs(d2 - col)
        return heuristic[0]
    

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
            out.append(Board(state=copy,method=self.method))
        if row != 3:
            copy = self.board.copy()
            copy[row,col], copy[row+1,col] = copy[row+1,col], copy[row,col]
            out.append(Board(state=copy,method=self.method))
        if col != 0:
            copy = self.board.copy()
            copy[row,col], copy[row,col-1] = copy[row,col-1], copy[row,col]
            out.append(Board(state=copy,method=self.method))
        if col != 3:
            copy = self.board.copy()
            copy[row,col], copy[row,col+1] = copy[row,col+1], copy[row,col]
            out.append(Board(state=copy,method=self.method))
        return out

    def __repr__(self) -> str:
        return f"{self.board}"

    def walk(self, n: int = 10):
        """scrambles self.board with n steps.
        Random walk won't walk back onto a visited state *
        Does not guarantee shortest path is n moves away.

        Changes self.board to the scramble
        sets self.scramble_path
        """
        row, col = np.where(self.board == 0)
        visited = set([self.bytes])
        path = []
        for i in range(n): 
            possibilites = []
            if row != 0: # swap with up
                possibilites.append("U")
            if row != 3: # swap with down
                possibilites.append("D")
            if col != 0: # swap with left
                possibilites.append("L")
            if col != 3: # swap with right
                possibilites.append("R")

            random.shuffle(possibilites)
            while possibilites: # prevent walking back to visited state
                swap = possibilites.pop()
                if swap == "U":
                    new_row, new_col = row-1, col
                elif swap == "D":
                    new_row, new_col = row+1,col
                elif swap == "L":
                    new_row, new_col = row, col-1
                elif swap == "R":
                    new_row, new_col = row, col+1
                self.board[row,col], self.board[new_row, new_col] = self.board[new_row, new_col], self.board[row,col]

                if self.bytes not in visited:
                    path.append(swap)
                    visited.add(self.bytes)
                    row, col = new_row, new_col # new location of 0
                    break
                else:
                    self.board[row,col], self.board[new_row, new_col] = self.board[new_row, new_col], self.board[row,col]
            else: # got stuck in a corner and I'm too lazy to fix it for real (recursively calls until it works):
                new = Board()
                path = new.walk(n)
                self.board = new.board
                return path
        self.scramble_path = path
        return path

    def solve(self, method = "a_star"):
        # bookkeeping
        self.method = method
        t1 = time.time()
        counter = itertools.count() 
        stop  = False

        # set up dictionary and heap
        visited = {self.bytes: [0, None]}
        unvisited = [(0,next(counter),self)]
        while unvisited and not stop:
            # ways to exit search
            if len(visited) > 10000000 and time.time() - t1 > 60:
                print(f"TOO SLOW, {len(visited) = }, {time.time() - t1:.2f} seconds")
                break
            distance, _, node = heapq.heappop(unvisited)
            neighbours = node.get_neighbours()
            for i in neighbours:
                new_distance = distance+1+i.heuristic
                if i.bytes not in visited:
                    heapq.heappush(unvisited, (new_distance,next(counter),i))
                    visited[i.bytes] = [new_distance,node.bytes]
                elif i.bytes in visited:
                    if new_distance < visited[i.bytes][0]:
                        visited[i.bytes] = [new_distance, node.bytes]

                if i.solved:
                    stop = True
                    break

        total_time = time.time() - t1
        print(f'sampled {len(visited)} states in {total_time:.2f} seconds')
        return len(visited), len(unvisited), total_time


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input file: data/...")
    parser.add_argument("-m", "--method", help="Solve method: a_star, dijkstra, bfs, dfs, bidirectional")
    args = parser.parse_args()


    with open(args.input, "rb") as fp:
        board = pickle.load(fp)

    results = board.solve(args.method)

    with open(f"results/{args.method}/{args.input.split('/')[-2]}.csv","a") as f:
        f.write(f"{results[0]},{results[1]},{results[2]}\n")