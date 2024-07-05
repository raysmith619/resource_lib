#pyttsx_simple.py   07Aug2023  crs
""" Simple talk
"""
import time

import pyttsx4 as pyttsxN

class PyttsxSimple:
    def __init__(self):
        """
        """
        self.engine = pyttsxN.init()
            
    def talk(self, text):
        """ Say text
        """
        self.engine.say(text)
        self.engine.runAndWait()
    
if __name__ == "__main__":
    print("\nTest Start")
    tt = PyttsxSimple()
    tt.talk("Hello World")
    tt.talk("How are you?")
    tt.talk("How's the weather?")
    tt.talk("Good Bye for now.")
    print("Test End\n")