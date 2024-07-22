#pyttsx_simple_THREADED.py   07Aug2023  crs
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
        self.is_talking = False
        self.talk_queue = queue.Queue(10)  # speech queue of SpeakerControlCmd 
        self.talk_thread = threading.Thread(target=self.talk_thread_proc)
        self.running = True
        self.talk_thread.start()
            
    def talk_thread_proc(self):
        """ Process pending speech requests (SpeakerControlCmd)
        """
        print("talk_thread running")
        while self.running:
            if self.talk_queue.qsize() > 0:
                cmd = self.talk_queue.get()
                print(f"talk_queue.get():{cmd}")
                self.do_talk(cmd)
        print("talk_thread returning")
        
    def talk(self, text):
        """ talk - add text to queue
        :text: text to say
        """
        self.talk_queue.put(text)
        
                    
    def do_talk(self, text):
        """ Say text
        """
        self.pyt_thread = threading.Thread(target=self.pyt_thread_proc,
                                           args = [text])
        self.running = True
        self.pyt_thread.start()
        self.pyt_thread.join()
        
    def pyt_thread_proc(self, text):
        self.is_talking = True
        print(f"pyt_thread_proc({text})")
        engine = pyttsxN.init()
        engine.say(text)
        engine.runAndWait()
        print(f"AFTER pyt_thread_proc({text})")
        self.is_talking = False

    def is_busy(self):
        if self.talk_queue.qsize() > 0:
            print(f"talk_queue.qsize():{self.talk_queue.qsize()} {self.is_talking}")
            return True     # text still in queue
        
        return self.is_talking

    def clear(self):
        """ Clear pending talk
        """
        self.talk_queue.empty()
    
    def wait_while_busy(self):
            while self.is_busy():
                print("wait_while_busy")
                time.sleep(.1)

    def quit(self):
        """ Stop talking
        """
        print("quit")
        self.running = False
        self.talk_queue.empty()
        self.talk_thread.join()
        self.pyt_thread.join()
        print("quit end")

            
if __name__ == "__main__":
    print("\nTest Start")
    tt = PyttsxSimple()
    tt.talk("Hello World")
    tt.talk("How are you?")
    tt.wait_while_busy()
    
    tt.talk("How's the weather?")
    tt.talk("Good Bye for now.")
    tt.wait_while_busy()
    
    tt.talk("May here this")
    tt.talk("but shouldn't hear this")
    tt.talk("or hear this")
    tt.clear()
    print("but shouldn't here this")
    print("or hear this")
    tt.quit()
    print("Test End\n")