#pyttsx_simple_THREADED.py   07Aug2023  crs
""" Simple talk
"""
import time
import threading

import pyttsx3 as pyttsxN

class PyttsxSimple:
    def __init__(self):
        """
        """
            
    def talk(self, text):
        """ Say text
        """
        self.pyt_thread = threading.Thread(target=self.talk_thread_proc,
                                           args = [text])
        self.running = True
        self.pyt_thread.start()
        self.pyt_thread.join()
        
    def talk_thread_proc(self, text):
        engine = pyttsxN.init()
        engine.say(text)
        engine.runAndWait()
    
if __name__ == "__main__":
    print("\nTest Start")
    tt = PyttsxSimple()
    tt.talk("Hello World")
    tt.talk("How are you?")
    tt.talk("How's the weather?")
    tt.talk("Good Bye for now.")
    print("Test End\n")