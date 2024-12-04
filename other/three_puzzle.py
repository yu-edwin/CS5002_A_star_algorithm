# Simple puzzle problem to figure out Dijkstra's algorithm
# Same rules as the 15 puzzle, or the 8 puzzle, but only 3
# 2x2 grid
# Has 4! = 24 max possible board states
# By Joe Miller

import heapq

class Board:
    GOAL = ((1,2),(3,0))
    ROWS = 2
    COLS = 2

    def __init__(self, board):
        self.board = board

    def __str__(self):
        board_str = ""
        for row in self.board:
            for col in row:
                board_str += str(col)
            board_str += '\n'
        return f"{board_str}"

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
        if blank_row < 1:
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
        if blank_col < 1:
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
        x0, y0 = new_board[0][0], new_board[0][1]
        x1, y1 = new_board[1][0], new_board[1][1]
        tuple_board = ((x0, y0), (x1, y1))
        return tuple_board

class Node:
    def __init__(self, board, shortest_path_length, previous_node = None):
        self.board = board
        self.shortest_path_length = shortest_path_length
        self.previous_node = previous_node

    def __lt__(self, other):
        return self.shortest_path_length < other.shortest_path_length


def solve(start_board):
    visited = []
    unvisited = []
    path_length = 0
    # create node for 1st board
    node = Node(start_board, path_length)
    GOAL = node.board.GOAL
    # put start board in unvisited
    heapq.heappush(unvisited, node)
    shortest_paths = {start_board: node}
    is_solved = False
    previous_node = None
    # quit searching when unvisited list is empty
    while len(unvisited) > 0:
        # get the unvisited node with the shortest path length
        node = heapq.heappop(unvisited)
        
        # increase path length and check neighbors
        path_length = node.shortest_path_length + 1
        # print(f"path length: {path_length}")
        # next node to check is unvisited node with shortest path
        # get neigbors (not already in visited)
        neighbors = node.board.get_neighbors()
        # add board to visited boards
        visited.append(node.board.board)
        for neighbor_board in neighbors:
            # print(neighbor_board)
            if neighbor_board not in visited:
                neighbor = Board(neighbor_board)
                neighbor_node = Node(neighbor, path_length, node)
                # put neigbors into list in order of smallest path
                heapq.heappush(unvisited, neighbor_node)
                shortest_paths[neighbor_node.board] = neighbor_node
        
        # Puzzle solved once goal board has been visited
        # quit searching when goal board is in visited list
        if GOAL in visited:
            is_solved = True
            break
    return shortest_paths

def find_goal_node(nodes, goal_board):
    for board in nodes.keys():
        if board.board == goal_board:
            return nodes[board]
    return None


if __name__ == '__main__':
    board = Board(((3,0),(2,1)))
    print(board)
    shortest_paths = solve(board)
    goal_node = find_goal_node(shortest_paths, board.GOAL)
    node = goal_node
    solved_path = []
    while node.previous_node:
        solved_path.append(node.board)
        node = node.previous_node
    solved_path.append(node.board)
    l = len(solved_path)
    for i in range(l):
        print(solved_path[(l-1) - i])
