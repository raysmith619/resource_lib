# pyttsx_startLoop.py   25Aug2023  crs
""" Exercise pyttsxN startLoop()
"""
import time

import pyttsx3 as pyttsxN

engine = pyttsxN.init()

engine.say("First line")
engine.say("Second line")
engine.startLoop()
engine.say("Third line")
engine.startLoop()
engine.endLoop()
