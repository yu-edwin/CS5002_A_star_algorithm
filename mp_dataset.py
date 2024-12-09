import multiprocessing as mp
import subprocess
import os
import random

if __name__ == "__main__":
    commands = []
    for move in range(100,101,5):
        for i in range(100):
            commands.append(["python","puzzle.py","-i",f"data/{move}/{i}.pickle","-m","a_star"])
            commands.append(["python","puzzle.py","-i",f"data/{move}/{i}.pickle","-m","a_star","-p"])
            commands.append(["python","puzzle.py","-i",f"data/{move}/{i}.pickle","-m","dijkstra"])
            commands.append(["python","puzzle.py","-i",f"data/{move}/{i}.pickle","-m","dijkstra","-p"])
    random.shuffle(commands)

    with mp.get_context("spawn").Pool(processes=12,maxtasksperchild=1) as pool:
        pool.map(subprocess.run, commands)