#pyttsx_simple_t2.py   07Aug2023  crs
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
        self.engine = pyttsxN.init()
        self.is_talking = False
        
        # pyttsxN queue thread / and queue
        self.pyt_queue = queue.Queue(10)  # text-to-speech queue 
        self.pyt_thread = threading.Thread(target=self.pyt_thread_proc)
        self.pyt_thread.start()
        
        # talking request queue/thread
        self.talk_queue = queue.Queue(10)  # speech queue of SpeakerControlCmd 
        self.talk_thread = threading.Thread(target=self.talk_thread_proc)
        self.running = True
        self.talk_thread.start()
            
        time.sleep(1)

    def talk_thread_proc(self):
        """ Process pending speech requests (SpeakerControlCmd)
        """
        print("talk_thread running")
        while self.running:
            time.sleep(0)
            if self.talk_queue.qsize() > 0:
                cmd = self.talk_queue.get()
                print(f"talk_queue.get():{cmd}")
                self.do_talk(cmd)
        print("talk_thread returning")
        
    def talk(self, text):
        """ talk - add text to queue
        :text: text to say
        """
        time.sleep(0)
        print(f"talk({text})")
        self.talk_queue.put(text)
        
                    
    def do_talk(self, text):
        """ Say text by placing text in pyttsxN queue
        """
        time.sleep(0)
        print(f"do_talk({text})")
        self.pyt_queue.put(text)
        
    def pyt_thread_proc(self):
        """ pyttsxN processing thread proc
        """
        print("pyt_thread_proc starting")
        #self.engine = pyttsxN.init()
        
        while self.running:
            time.sleep(0)
            print(f"pyt_thread is_talking"
                f" pyt_queue_qsize(): {self.pyt_queue.qsize()}"
                f" is_talking: {self.is_talking}")
            if (not self.is_talking
                and self.pyt_queue.qsize() > 0):
                self.is_talking = True
                text = self.pyt_queue.get()
                print(f"pyt_thread text: {text}"
                    f" pyt_queue_qsize(): {self.pyt_queue.qsize()}"
                    f" is_talking: {self.is_talking}")
                print(f"pyt_thread_proc say:{text}")
                self.engine.say(text)
                self.engine.runAndWait()
                print(f"AFTER pyt_thread_proc({text})")
                self.is_talking = False

    def is_busy(self):
        time.sleep(0)
        print(f"talk_queue.qsize():{self.talk_queue.qsize()}"
              f" pyt_queue.qsize():{self.pyt_queue.qsize()}"
              f" talking:{self.is_talking}")
        return (self.pyt_queue.qsize() > 0
                or self.talk_queue.qsize() > 0
                or self.is_talking)

    def clear(self):
        """ Clear pending talk
        """
        self.talk_queue.empty()
        self.pyt_queue.empty()
        self.engine.stop()      # Stop current
        print("After clear() call")
    
    def wait_while_busy(self):
        print("wait_while_busy")
        while self.is_busy():
            time.sleep(.1)

    def quit(self):
        """ Stop talking
        """
        print("quit")
        self.clear()
        self.running = False
        self.pyt_thread.join()
        print("quit end")

            
if __name__ == "__main__":
    print("\nTest Start")
    tt = PyttsxSimple()
    tt.talk("Hello World")
    tt.talk("How are you?")
    tt.wait_while_busy()
    
    nstr = ""
    for n in range(5, 0, -1):
        tt.talk(str(n))
    time.sleep(.1)
    tt.clear()
    
    tt.talk("How's the weather?")
    tt.talk("Good Bye for now.")
    tt.wait_while_busy()
    
    tt.talk("May here this")
    time.sleep(.01)
    tt.talk("but shouldn't hear this")
    tt.talk("or hear this")
    tt.clear()
    tt.talk("After clear()")
    tt.wait_while_busy()
    tt.quit()
    print("Test End\n")