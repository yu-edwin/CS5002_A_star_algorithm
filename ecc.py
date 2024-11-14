import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass


def show(message: list[int], base: int = 2):
    if base not in {2,10,16}:
        raise ValueError('bro why')
    b2 = ''.join([str(i) for i in message])
    match base:
        case 2:
            print(b2)
        case 8:
            print(format(int(b2,2),'o'))
        case 10:
            print(int(b2,2))
        case 16:
            print(format(int(b2,2),'x'))
            

def message(n = 0) -> list[int]:
    return [random.choice([0,1]) for _ in range(n)]

class hamming_7_4:
    @staticmethod
    def encode(message: list[int]):
        """Adding redundancy into original message
        """
        encoded_message = []
        while message:
            a,b,c,d, *message = message
            p1 = a^b^d
            p2 = a^c^d
            p3 = b^c^d
            encoded_message += [p1,p2,a,p3,b,c,d]
        return encoded_message

    @staticmethod
    def decode(message: list[int]) -> list[int]:
        """Checks for error, the convert back to original message
        """
        parity_check = hamming_7_4.check(message)
        original = []
        if any(parity_check):
            for idx, i in enumerate(parity_check):
                if i:
                    message[idx] ^= 1
        while message:
            p1,p2,a,p3,b,c,d, *message = message
            original += [a,b,c,d]
        return original

    @staticmethod
    def error(message: list[int], n: int = 1) -> list[int]:
        """induces n errors, up to 1 error per block if n > number of blocks
        """
        num_blocks = [i for i in range(0,len(message),7)]
        while num_blocks and n:
            n -= 1
            idx = random.choice(num_blocks)
            num_blocks.remove(idx)
            idx += random.randint(0,6)
            message[idx] ^= 1
        return message
            
    @staticmethod
    def check(message: list[int]) -> list[int]:
        """checks each block of code
        indices of 1 in blocks indicate error bits
        """
        blocks = []
        for i in range(0,len(message),7):
            blocks.extend(hamming_7_4.check_block(message[i:i+7]))
        return blocks
    
    @staticmethod
    def check_block(block: list[int]) -> list[int]:
        """performs check an individual block of code
        """
        check_matrix = np.array([
            [0, 0, 0, 1, 1, 1, 1],
            [0, 1, 1, 0, 0, 1, 1],
            [1, 0, 1, 0, 1, 0, 1]
        ])
        block = np.array(block)
        result = np.dot(check_matrix, block) % 2
        match list(result):
            case 1,1,1:
                return [0,0,0,0,0,0,1]
            case 1,1,0:
                return [0,0,0,0,0,1,0]
            case 1,0,1:
                return [0,0,0,0,1,0,0]
            case 1,0,0:
                return [0,0,0,1,0,0,0]
            case 0,1,1:
                return [0,0,1,0,0,0,0]
            case 0,1,0:
                return [0,1,0,0,0,0,0]
            case 0,0,1:
                return [1,0,0,0,0,0,0]
            case 0,0,0:
                return [0,0,0,0,0,0,0]

