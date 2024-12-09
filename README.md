# CS5002 Final Project (A* search algorithm)
Several implementations of the A* search algorithm. Includes an implementation of maze pathfinding. Also includes Dijkstra and A* implementations of a 15puzzle solver, along with data for evaluating search algorithms.

## Installation

```bash
git clone https://github.com/yu-edwin/CS5002_A_star_algorithm.git
```

Install necessary packages:
```bash
pip install PyQt5 numpy
```

Install optional packages (if you want to look at the results more in depth):
```bash
pip install pandas matplotlib seaborn
```

## Usage

For using the maze pathfinding implementation to start up PyQt program:

```bash
python Astar_visualization.py
```

For constructing 15puzzle:
```python
board = Board()
board.walk(20) # for a 20 move scramble
board.solve("a_star") # takes "a_star" or "dijkstra"
board.reconstruct_path() # displays solve path
```