# pyttsx_startLoop.py   25Aug2023  crs
""" Exercise pyttsx3 startLoop()
"""
import time

import pyttsx3

engine = pyttsx3.init()

engine.say("First line")
engine.say("Second line")
engine.startLoop()
engine.say("Third line")
engine.startLoop()
engine.endLoop()
