#pyttsx_voices.py   06Aug2023  crs
""" Test voices
"""
import pyttsx3 as pyttsxN

engine = pyttsxN.init()
voices = engine.getProperty('voices')
for voice in voices:
   engine.setProperty('voice', voice.id)
   engine.say('The quick brown fox jumped over the lazy dog.')
engine.runAndWait()
