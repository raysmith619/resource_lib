#pyttsx_queued.py   13Aug2023  crs
""" Simple queued
"""
import time
import queue
import threading

import pyttsx3

from select_trace import SlTrace

class PyttsxQueued:
    def __init__(self):
        """ Setup for queued talking
        """
        self.engine = pyttsx3.init()
        
        self.engine.connect('started-utterance', self.onStart)
        self.engine.connect('finished-utterance', self.onEnd)

        self.pyt_queue = queue.Queue(10)  # speech queue of SpeakerControlCmd 
        self.pyt_thread = threading.Thread(target=self.pyt_proc_thread)
        self.running = True
        self.pyt_thread.start()

        self.busy_thread = threading.Thread(target=self.busy_proc_thread)
        self.busy_thread.start()

            
    def pyt_proc_thread(self):
        """ Process pending speech requests (SpeakerControlCmd)
        """
        SlTrace.lg("pyt_proc_thread running")
        while self.running:
            cmd = self.pyt_queue.get()
            SlTrace.lg(f"pyts3_queue.get():{cmd}")
            self.do_talk(cmd)
        SlTrace.lg("pyts3_proc_thread returning")
            
    def busy_proc_thread(self):
        """ checking for engine busy
        """
        SlTrace.lg("busy_proc_thread running")
        while self.running:
            self.is_busy = self.engine.isBusy()
            time.sleep(.1)
        SlTrace.lg("busy_proc_thread returning")


    def onStart(self, name):
        print('starting', name)
        #self.is_talking = True
        
    def onWord(self, name, location, length):
        print('word', name, location, length)
        
    def onEnd(self, name, completed):
        print('finishing', name, completed)
        self.is_talking = False
            
    def talk(self, text):
        """ Say text
        :text: text to speak
        """
        self.pyt_queue.put(text)
        
    def do_talk(self, text):
        """ do talking, waiting till done
        :text: text to say
        """
        self.engine_runAndWait(text)
        SlTrace.lg("after engine_runAndWait()")

    def engine_runAndWait(self, text):
        """ run engine, wait till done
            use cycles in different thread
        """
        self.run_and_wait_thread = threading.Thread(
                        target=self.run_and_wait_thread_proc,
                        args=[text])
        self.run_and_wait_thread.run()
        #self.run_and_wait_thread.join()
        
    def run_and_wait_thread_proc(self, text):
        SlTrace.lg("starting run_and_wait_thread_proc")
        self.engine.say(text)
        SlTrace.lg(f"After engine.say({text})")
        self.engine.runAndWait()
        SlTrace.lg("after engine.runAndWait()")
                    
    def wait_while_busy(self):
        while not self.ck_busy():
            time.sleep(.1)
        return
                    
    def ck_busy(self):
        """ Return True iff talking
        """
        print(".", end="")
        return self.pyt_queue.qsize() > 0
    
        time.wait(.001) # Give time to start
        return self.is_busy()
    
if __name__ == "__main__":
    print("\nTest Start")
    wt = False
    #wt = True
    limit = 0
    limit = 3.01
    print("wt:", wt, "limit:", limit)
    tt = PyttsxQueued()
    tt.talk("Hello World")
    tt.talk("How are you?")
    tt.talk("How's the weather?")
    tt.talk("Good Bye for now.")
    tt.wait_while_busy()
    print("Test End\n")