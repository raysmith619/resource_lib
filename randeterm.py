# randeterm.py    26Mar2020  crs
"""
Simple deterministic random number generation
For testing with repeatable results import randeterm as random
"""
import random

rand = random.Random()
rand.seed(1)

def randint(*args, **kwargs):
    return rand.randint(*args, **kwargs)
