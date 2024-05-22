#pyttsx_simple.py   07Aug2023  crs
""" Simple talk
"""
import time

import pyttsx3

class PyttsxSimple:
    def __init__(self, wait=False, limit=0):
        """
        :wait: talk, waits till completed
                default: False
        :limit: maximum wait time 0 - no limit
            default: 0 - no limit
        """
        self.is_talking = False
        self.wait = wait
        self.limit = limit
        self.engine = pyttsx3.init()
        self.engine.connect('started-utterance', self.onStart)
        self.engine.connect('finished-utterance', self.onEnd)

    def onStart(self, name):
        print('starting', name)
        #self.is_talking = True
        
    def onWord(self, name, location, length):
        print('word', name, location, length)
        
    def onEnd(self, name, completed):
        print('finishing', name, completed)
        self.is_talking = False
            
    def talk(self, text, wait=None, limit=None):
        """ Say text
        :text: text to speak
        :wait: wait till done
                default: self.wait
        :limit: limit wait
                default: self.limit
        """
        if wait is None:
            wait = self.wait
        if limit is None:
            limit = self.limit
        #self.wait_if_busy(limit=limit)
        if wait:
            self.engine.say(text)
            self.engine.runAndWait()
            self.startup = False
        else:
            self.engine.say(text)
            self.engine.startLoop()

    def wait_if_busy(self, limit=0):
        """ wait if busy talking
        :limit: maximum wait time (sec)
                default: 0 - no limit
        """
        time_start = time.time() 
        while self.is_busy():
            if (limit != 0
                and time.time()-time_start > limit):
                break
            time.sleep(.1)
            
    def is_busy(self):
        """ Return True iff talking
        """
        print(".", end="")
        return self.is_talking
    
if __name__ == "__main__":
    print("\nTest Start")
    wt = False
    #wt = True
    limit = 0
    limit = 3.01
    print("wt:", wt, "limit:", limit)
    tt = PyttsxSimple(wait=wt, limit=limit)
    tt.talk("Hello World")
    tt.talk("How are you?")
    tt.talk("How's the weather?")
    tt.talk("Good Bye for now.")
    print("Test End\n")