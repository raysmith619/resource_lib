#pyttsx_simple_t4.py   10Sep2023  crs
""" Simple
    Only call do_talk if got queued request
    and not currently talking
    Do pyttsxN action within do_talk
    Include onWord to capture stop requests
    to stop current utterance (at word boundary)
    
    Place pyttsxN in own process to support
    stopping during utterance
"""
import time
import queue

from pyttsx_proc import PyttsxProc

from select_trace import SlTrace

class PyttsxSimple:
    def __init__(self):
        """
        """
        self.pyt_proc = None    # pyttsxN process if one
        
    def talk(self, text):
        """ talk - add text to queue
        :text: text to say
        """
        if self.pyt_proc is None or not self.pyt_proc.is_alive():
            self.pyt_proc = PyttsxProc()    # create/restart pyttsxN
        if self.pyt_proc:
            self.pyt_proc.talk(text)
        

    def clear(self):
        """ Clear pending talk
        """
        if self.pyt_proc is not None:
            self.pyt_proc.clear()
    
    def wait_while_busy(self, busy_fun=None):
        """ wait while bysy
        :busy_fun: function to call while busy
                default: no call
        """
        SlTrace.lg("wait_while_busy", "talk_busy")
        if self.pyt_proc is None:
            return
        
        while self.pyt_proc.is_busy():
            if busy_fun:
                busy_fun()

    def quit(self):
        """ Stop talking
        """
        SlTrace.lg("quit", "talk_quit")
        if self.pyt_proc is not None:
            self.pyt_proc.quit()
            self.pyt_proc = None
        

            
if __name__ == "__main__":
    SlTrace.setFlags("stdouthasts=0")
    SlTrace.setFlags("talk_word")
    SlTrace.setFlags("talk,talk_thread=False")
    SlTrace.setFlags("talk_busy=False")
    
    def busy_fun():
        print(".", end="")
        time.sleep(.2)
        
    SlTrace.lg("\nTest Start")
    tt = PyttsxSimple()
    #tt.talk(" ".join([str(n) for n in range(5)]))
    #tt.clear()
    tt.talk("Hello World")
    tt.talk("How are you?")
    tt.wait_while_busy(busy_fun=busy_fun)
    
    nstr = ""
    for n in range(5, 0, -1):
        tt.talk(str(n))
    #time.sleep(.1)
    tt.clear()
    
    tt.talk("How's the weather?")
    tt.talk("Good Bye for now.")
    tt.wait_while_busy(busy_fun=busy_fun)
    
    tt.talk("May here this")
    tt.wait_while_busy()
    tt.talk("but shouldn't hear this")
    tt.talk("or hear this")
    tt.clear()
    tt.talk("After clear()")
    tt.wait_while_busy()
    tt.quit()
    SlTrace.lg("Test End\n")