# The 8-puzzle problem using Dijkstra's algorithm
# 3x3 grid
# By Joe Miller

class Position:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __str__(self):
        return f"({self.row},{self.col})"

class Tile:
    def __init__(self, element, position, goal_position):
        self.element = element
        self.position = position
        self.goal_position = goal_position
        self.distance = self.get_distance()

    def __str__(self):
        return f"{self.element}({self.position.row},{self.position.col}) distance:{self.distance}"

    def get_distance(self):
        distance_row = abs(self.position.row - self.goal_position.row)
        distance_col = abs(self.position.col - self.goal_position.col)
        min_moves = distance_row + distance_col
        return min_moves

class Board:
    ROWS = 3
    COLS = 3
    goal_tiles = [
    [1, 2, 3], 
    [4, 5, 6], 
    [7, 8, 0]]
    goal_coordinates = {
    1: Position(0,0),
    2: Position(0,1),
    3: Position(0,2),
    4: Position(1,0),
    5: Position(1,1),
    6: Position(1,2),
    7: Position(2,0),
    8: Position(2,1),
    0: Position(2,2)
    }
    # minimum moves needed to solve board (each swap is 2 moves)
    min_moves = 0

    def __init__(self, tile_array):
        self.tile_array = tile_array
        self.tiles = self.make_tiles()
        self.coordinates = self.get_coordinates()
        self.distances = self.get_distances()

    def __str__(self):
        return f"{self.tile_array} min moves:{self.min_moves}"

    def solve(self, solution = []):
        if self.min_moves == 0:
            return solution
        if self.tile_array == Board.goal_tiles:
            return solution
        next_boards = self.get_moves()
        # find the best next move
        closest = self
        for board in next_boards:
            if board.min_moves < closest.min_moves:
                closest = board
        if closest == self:
            return []
        solution.append(closest)
        closest.solve(solution)
        return solution

    def get_coordinates(self):
        coordinates = {}
        for row in range(len(self.tile_array)):
            for col in range(len(self.tile_array[row])):
                element = self.tile_array[row][col]
                coordinates[element] = Position(row, col)
        return coordinates

    def make_tiles(self):
        tiles = {}
        for row in range(len(self.tile_array)):
            for col in range(len(self.tile_array[row])):
                element = self.tile_array[row][col]
                goal_position = self.goal_coordinates[element]
                position = Position(row, col)
                tile = Tile(element, position, goal_position)
                tiles[element] = tile
        return tiles

    def get_tile(self, position):
        element = self.tile_array[position.row][position.col]
        tile = self.tiles[element]
        return tile

    def get_distances(self):
        total = 0
        distances = {}
        for element in self.coordinates:
            distance = self.tiles[element].distance
            total += distance
            distances[element] = distance
        self.min_moves = total
        return distances

    def get_moves(self):
        row = self.coordinates[0].row
        col = self.coordinates[0].col
        goal_position = self.goal_coordinates[0]
        tile_0 = Tile(0, Position(row, col), goal_position)
        next_boards = []

        # check top tile exists
        if (row > 0):
            upper_tile = self.get_tile(Position(row-1, col))
            upper_board = self.swap_tiles(tile_0, upper_tile)
            next_boards.append(upper_board)
        # check bottom tile exists
        if (row < self.ROWS-1):
            lower_tile = self.get_tile(Position(row+1, col))
            lower_board = self.swap_tiles(tile_0, lower_tile)
            next_boards.append(lower_board)
        # check left tile exists
        if (col > 0):
            left_tile = self.get_tile(Position(row, col-1))
            left_board = self.swap_tiles(tile_0, left_tile)
            next_boards.append(left_board)
        # check right tile exists
        if (col < self.COLS-1):
            right_tile = self.get_tile(Position(row, col+1))
            right_board = self.swap_tiles(tile_0, right_tile)
            next_boards.append(right_board)

        return next_boards

    # returns a new board with the 2 tiles switched from this board
    def swap_tiles(self, tile_a, tile_b):
        # copy tile array
        new_tile_array = []
        for r in range(self.ROWS):
            new_row = []
            for c in range(self.COLS):
                new_row.append(self.tile_array[r][c])
            new_tile_array.append(new_row)
        # then swap tiles
        new_tile_array[tile_a.position.row][tile_a.position.col] = tile_b.element
        new_tile_array[tile_b.position.row][tile_b.position.col] = tile_a.element
        # create a new board with the new tiles
        new_board = Board(new_tile_array)
        return new_board


if __name__ == '__main__':
    initial = [[0, 1, 3], [4, 2, 5], [7, 8, 6]]
    # impossible =  [[1,2,3],[4,5,6],[8,7,0]]
    board = Board(initial)
    print(board)
    solution = board.solve()
    if solution == []:
        print("Unsolvable")
    else:
        for board in solution:
            print(board)
