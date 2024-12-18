# CS5002 Final Project (A* search algorithm)
Dijkstra and A* implementations of a 15puzzle solver, along with data for evaluating search algorithms.

## Installation

```bash
git clone https://github.com/yu-edwin/CS5002_A_star_algorithm.git
```

Install necessary packages:
```bash
pip install numpy
```

Install optional packages (if you want to look at the results more in depth):
```bash
pip install pandas matplotlib seaborn
```

## Usage

For constructing 15puzzle:
```python
board = Board()
board.walk(20) # for a 20 move scramble
board.solve(method = "a_star", pattern = True) # solves with "dijkstra" or "a_star, also optional pattern database
board.reconstruct_path() # displays solve path
```