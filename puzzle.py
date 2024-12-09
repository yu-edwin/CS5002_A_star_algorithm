from __future__ import annotations
import numpy as np
import itertools
import heapq
import time
import random
import pickle
import argparse
import os


SOLVED_PUZZLE = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]],dtype=np.int8)
SOLVED = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]],dtype=np.int8).tobytes()
GOAL = [(3,3),(0,0),(0,1),(0,2),(0,3),(1,0),(1,1),(1,2),(1,3),(2,0),(2,1),(2,2),(2,3),(3,0),(3,1),(3,2)]
class Board:
    def __init__(self,state: np.array = None, method = None):
        self.board = SOLVED_PUZZLE.copy() if state is None else state # sets inital board state if given, otherwise set as solved board
        self.scramble_path = []
        self.solve_path = []
        self.method = method

    def __repr__(self) -> str:
        return f"{self.board}"

    @property
    def bytes(self):
        return self.board.tobytes()

    @property
    def solved(self):
        return self.bytes == SOLVED

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

    def solve(self, method = "a_star", pattern = False):
        """ Search Algorithms: a_star and dijkstra
        """
        # bookkeeping
        self.method = method
        t1 = time.time()
        counter = itertools.count() 
        if pattern:
            with open("precompute.pickle","rb") as fp:
                check = pickle.load(fp)
        else:
            check = set([SOLVED])
        stop = self.bytes in check

        # set up dictionary and heap
        space = 0
        visited = {self.bytes: [0, None]}
        unvisited = [(self.heuristic,next(counter),self)]
        while unvisited and not stop:
            # ways to exit search
            if len(visited) > 1000000 and len(unvisited) > 1000000 and time.time() - t1 > 60:
                print(f"TOO SLOW, {len(visited) = }, {len(unvisited) = }, {time.time() - t1:.2f} seconds")
                break
            distance, _, node = heapq.heappop(unvisited)
            neighbours = node.get_neighbours()
            for i in neighbours:
                
                new_distance = distance+1+i.heuristic-node.heuristic
                if i.bytes not in visited or new_distance < visited[i.bytes][0]:
                    heapq.heappush(unvisited, (new_distance,next(counter),i))
                    visited[i.bytes] = [new_distance,node.bytes]
                if i.bytes in check:
                    print('solved!!')
                    stop = True
                    break
            space = max(space, len(unvisited))

        total_time = time.time() - t1
        print(f'sampled {len(visited)} states in {total_time:.2f} seconds ({len(unvisited)=})')
        self.visited = visited
        return len(visited), space, total_time

    def reconstruct_path(self):
        """Reconstructs solve path from self.visited dictionary
        """
        byte_path = []
        node = SOLVED
        array_path = [np.frombuffer(SOLVED, dtype=np.int8).reshape(4,4)]
        while node:
            byte_path.append(node)
            _, node = self.visited[node]
            if node:
                array_path.append(np.frombuffer(node, dtype=np.int8).reshape(4,4))
        self.byte_path = byte_path
        self.array_path = array_path
        self.distance = len(array_path) - 1
        self.array_path.reverse()
        for i in self.array_path:
            print(i,end="\r\033[3A")
            time.sleep(0.5)
        print("\033[4B")





if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input file: data/5/0.pickle ...")
    parser.add_argument("-m", "--method", help="Solve method: a_star, dijkstra")
    parser.add_argument("-p", "--pattern", action="store_true",  help="Optional pattern database")
    args = parser.parse_args()

    with open(args.input, "rb") as fp:
        board = pickle.load(fp)
    results = board.solve(args.method, pattern=args.pattern)

    folder = f"results/{'pattern' if args.pattern else 'no_pattern'}/{args.method}"
    with open(f"{folder}/{args.input.split('/')[-2]}.csv","a") as f:
        f.write(f"{args.input.removeprefix('data/')},{results[0]},{results[1]},{results[2]}\n")