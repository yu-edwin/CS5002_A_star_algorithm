# The 8-puzzle problem 
# Uses A* algorith or
# Dijkstra's algorithm
# 3x3 grid
# By Joe Miller

import heapq

class Node:
    def __init__(self, board, shortest_path_length, previous_node = None):
        self.board = board
        self.shortest_path_length = shortest_path_length
        self.previous_node = previous_node

    def __lt__(self, other):
        return self.shortest_path_length < other.shortest_path_length

class Board:
    GOAL = ((1,2,3),(4,5,6),(7,8,0))
    ROWS = 3
    COLS = 3

    def __init__(self, board):
        self.board = board
        self.coords = self.get_coords()

    def __str__(self):
        board_str = ""
        for row in self.board:
            for col in row:
                board_str += str(col)
            board_str += '\n'
        return f"{board_str}"

    def min_moves(self):
        goal_coord = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2)]
        for i in range(len(self.coords)):
            moves = abs(self.coords[i][0] - goal_coord[i][0])
            moves += abs(self.coords[i][1] - goal_coord[i][1])
        return moves

    def get_coords(self):
        coords = [(r,c) for c in range(self.COLS) for r in range(self.ROWS)]
        for row in range(self.ROWS):
            for col in range(self.COLS):
                element = self.board[row][col]
                coords[element] = (row, col)
        return coords

    def get_neighbors(self):
        neighbors = []
        # find the empty space
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if self.board[row][col] == 0:
                    blank_row = row
                    blank_col = col
        blank_coordinates = (blank_row, blank_col)
        # up 
        if blank_row > 0:
            row = blank_row - 1
            col = blank_col 
            new_board = self.swap((row, col), blank_coordinates)
            neighbors.append(new_board)
        # down
        if blank_row < self.ROWS - 1:
            row = blank_row + 1
            col = blank_col 
            new_board = self.swap((row, col), blank_coordinates)
            neighbors.append(new_board)
        # left 
        if blank_col > 0:
            row = blank_row
            col = blank_col - 1
            new_board = self.swap((row, col), blank_coordinates)
            neighbors.append(new_board)
        # right
        if blank_col < self.COLS - 1:
            row = blank_row
            col = blank_col + 1
            new_board = self.swap((row, col), blank_coordinates)
            neighbors.append(new_board)
        return neighbors

    def swap(self, element_coordinates, blank_coordinates):
        new_board = []
        element_row, element_col = element_coordinates
        element = self.board[element_row][element_col]
        blank_row, blank_col = blank_coordinates
        for row in range(self.ROWS):
            new_row = []
            for col in range(self.COLS):
                if row == blank_row and col == blank_col:
                    new_row.append(element)
                elif row == element_row and col == element_col:
                    new_row.append(0)
                else:
                    new_row.append(self.board[row][col])
            new_board.append(new_row)
        # convert to nested tuples
        x0, y0, z0 = new_board[0][0], new_board[0][1], new_board[0][2]
        x1, y1, z1 = new_board[1][0], new_board[1][1], new_board[1][2]
        x2, y2, z2 = new_board[2][0], new_board[2][1], new_board[2][2]
        tuple_board = ((x0, y0, z0), (x1, y1, z1), (x2, y2, z2))
        return tuple_board

    def solve(self, algorithm = 'd'):
        visited = []
        unvisited = []
        path_length = 0
        start_node = Node(self, path_length)
        heapq.heappush(unvisited, start_node)
        shortest_paths = {self: start_node}
        is_solved = False
        previous_node = None
        boards_checked = 0
        # Search until unvisited list is empty or goal board is found
        while len(unvisited) > 0:
            # visit the unvisited node with the shortest path length first
            node = heapq.heappop(unvisited)
            visited.append(node.board.board)
            boards_checked += 1
            # check neighbors not already visited
            neighbors = node.board.get_neighbors()
            for neighbor_board in neighbors:
                if neighbor_board not in visited:
                    neighbor = Board(neighbor_board)
                    if algorithm == 'a':
                        path_length = node.shortest_path_length + neighbor.min_moves()
                    else:
                        path_length = node.shortest_path_length + 1
                    neighbor_node = Node(neighbor, path_length, node)
                    # put neigbors into list in order of smallest path
                    heapq.heappush(unvisited, neighbor_node)
                    shortest_paths[neighbor_node.board] = neighbor_node
            # Puzzle solved once goal board has been visited
            if self.GOAL in visited:
                is_solved = True
                break
        # don't return shortest paths if solution was not found
        if is_solved:
            goal_node = None
            # find the goal node
            for board in shortest_paths.keys():
                if board.board == self.GOAL:
                    goal_node = shortest_paths[board]
        # return all the goal node
        return (goal_node, boards_checked)


if __name__ == '__main__':
    initial = ((0, 1, 3), (4, 2, 5), (7, 8, 6))
    board = Board(initial)
    # Pass 'a' for A* algorithm or 'd' for Dijkstra's algorithm
    goal_node, boards_checked = board.solve('a')
    print(f"Boards Checked: {boards_checked}")
    if goal_node:
        print("Solved!")
        node = goal_node
        print("Solution Path:")
        solved_path = []
        while node.previous_node:
            solved_path.append(node.board)
            node = node.previous_node
        solved_path.append(node.board)
        l = len(solved_path)
        for i in range(l):
            print(solved_path[(l-1) - i])
    else:
        print("Unsolvable")
    