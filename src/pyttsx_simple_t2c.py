#pyttsx_simple_t2c.py   24Aug2023  crs
""" Simple talk
    Only call do_talk if got queued request
    and not currently talking
    Do pyttsxN action within do_talk
"""
import time
import threading
import queue

import pyttsx3

from select_trace import SlTrace

class PyttsxSimple:
    def __init__(self):
        """
        """
        self.is_talking = False
        
        # talking request queue/thread
        self.talk_queue = queue.Queue(10)  # speech queue of SpeakerControlCmd 
        self.talk_thread = threading.Thread(target=self.talk_thread_proc)
        self.running = True
        self.talk_thread.start()
            
        time.sleep(1)

    def talk_thread_proc(self):
        """ Process pending speech requests (SpeakerControlCmd)
        """
        SlTrace.lg("talk_thread running")
        while self.running:
            time.sleep(0)
            if (self.talk_queue.qsize() > 0
                and not self.is_talking):
                cmd = self.talk_queue.get()
                SlTrace.lg(f"talk_queue.get():{cmd}")
                self.do_talk(cmd)
        SlTrace.lg("talk_thread returning")
        
    def talk(self, text):
        """ talk - add text to queue
        :text: text to say
        """
        SlTrace.lg(f"talk({text})")
        self.talk_queue.put(text)
        
                    
    def do_talk(self, text):
        """ Say text, returning when done
        """
        self.engine = pyttsx3.init()
        self.is_talking = True
        SlTrace.lg(f"do_talk({text})")
        self.engine.say(text)
        self.engine.runAndWait()
        self.is_talking = False
        
                 
    def is_busy(self):
        time.sleep(0)
        #SlTrace.lg(f"talk_queue.qsize():{self.talk_queue.qsize()}"
        #      f" talking:{self.is_talking}")
        return (self.talk_queue.qsize() > 0
                or self.is_talking)

    def clear(self):
        """ Clear pending talk
        """
        self.talk_queue.empty()
        self.engine.stop()      # Stop current
        SlTrace.lg("After clear() call")
    
    def wait_while_busy(self, busy_fun=None):
        """ wait while bysy
        :busy_fun: function to call while busy
                default: no call
        """
        SlTrace.lg("wait_while_busy")
        while self.is_busy():
            if busy_fun:
                busy_fun()

    def quit(self):
        """ Stop talking
        """
        SlTrace.lg("quit")
        self.clear()
        self.running = False
        SlTrace.lg("quit end")

            
if __name__ == "__main__":
    #SlTrace.setFlags("stdouthasts=0")
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
    tt.talk("but shouldn't hear this")
    tt.talk("or hear this")
    tt.clear()
    tt.talk("After clear()")
    tt.wait_while_busy()
    tt.quit()
    SlTrace.lg("Test End\n")