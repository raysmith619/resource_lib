#pyttsx_simple_THREADED_PYT_queued.py   07Aug2023  crs
""" Simple talk
"""
import time
import threading
import queue

import pyttsx3 as pyttsxN

class PyttsxSimple:
    def __init__(self):
        """
        """
        self.running = True
        self.is_talking = False
        self.engine = pyttsxN.init()
        
        # pyttsxN queue thread / and queue
        self.pyt_queue = queue.Queue(10)  # text-to-speech queue 
        self.pyt_thread = threading.Thread(target=self.pyt_thread_proc)
        self.pyt_thread.start()
        
        # talking request queue/thread
        self.talk_queue = queue.Queue(10)  # speech queue of SpeakerControlCmd 
        self.talk_thread = threading.Thread(target=self.talk_thread_proc)
        self.talk_thread.start()
        print("pyt_thread_proc starting")
            
    def talk_thread_proc(self):
        """ Process pending speech requests (SpeakerControlCmd)
        """
        print("talk_thread running")
        while self.running:
            if (self.talk_queue.qsize() > 0
                and not self.is_talking):
                cmd = self.talk_queue.get()
                print(f"talk_queue.get():{cmd}")
                self.do_talk(cmd)
            else:
                time.sleep(.1)
        print("talk_thread returning")
        
    def talk(self, text):
        """ talk - add text to queue
        :text: text to say
        """
        print(f"talk({text})")
        self.talk_queue.put(text)
        
                    
    def do_talk(self, text):
        """ Say text by placing text in pyttsxN queue
        """
        print(f"do_talk({text})")
        self.pyt_queue.put(text)
        
    def pyt_thread_proc(self):
        """ pyttsxN processing thread proc
        """
        while self.running:
            print(f"pyt_thread is_talking:{self.is_talking}")
            if (not self.is_talking
                and self.pyt_queue.qsize() > 0):
                self.is_talking = True
                text = self.pyt_queue.get()
                print(f"pyt_thread_proc say:{text}")
                self.engine.say(text)
                self.engine.runAndWait()
                print(f"AFTER pyt_thread_proc({text})")
                self.is_talking = False
            else:
                time.sleep(.1)

    def is_busy(self):
        if self.talk_queue.qsize() > 0:
            print(f"talk_queue.qsize():{self.talk_queue.qsize()} {self.is_talking}")
            time.sleep(.1)
            return True     # text still in queue
        
        time.sleep(.1)
        print(f"is_talking: {self.is_talking}")        
        return self.is_talking

    def clear(self):
        """ Clear pending talk
        """
        self.talk_queue.empty()
        self.pyt_queue.empty()
        self.engine.stop()      # Stop current
    
    def wait_while_busy(self):
        while self.is_busy():
            print("wait_while_busy")
            time.sleep(.2)

    def quit(self):
        """ Stop talking
        """
        print("quit")
        self.clear()
        self.running = False
        self.talk_thread.join()
        self.pyt_thread.join()
        print("quit end")

            
if __name__ == "__main__":
    print("\nTest Start")
    tt = PyttsxSimple()
    tt.talk("Hello World")
    tt.talk("How are you?")
    tt.wait_while_busy()
    
    nstr = ""
    for ns in range(5, 0, -1):
        nstr += str(ns) + " "
    tt.talk(nstr)
    time.sleep(.1)
    #tt.clear()
    
    tt.talk("How's the weather?")
    tt.talk("Good Bye for now.")
    tt.wait_while_busy()
    
    tt.talk("May here this")
    time.sleep(.1)
    tt.talk("but shouldn't hear this")
    tt.talk("or hear this")
    tt.clear()
    print("but shouldn't here this")
    print("or hear this")
    tt.quit()
    print("Test End\n")