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

        self.pyt_queue = queue.Queue(10)  # speech queue of SpeakerControlCmd 
        self.pyt_thread = threading.Thread(target=self.pyt_proc_thread)
        self.running = True
        self.pyt_thread.start()

        self.pyt_queue2 = queue.Queue(10)  # speech queue of SpeakerControlCmd 
        self.pyt_thread2 = threading.Thread(target=self.pyt_proc_thread2)
        self.running2 = True
        self.pyt_thread2.start()

            
    def pyt_proc_thread(self):
        """ Process pending speech requests (SpeakerControlCmd)
        """
        SlTrace.lg("pyt_proc_thread2 running")
        while self.running:
            cmd = self.pyt_queue.get()
            SlTrace.lg(f"pyts3_queue.get():{cmd}")
            self.pyt_queue2.put(cmd)
        SlTrace.lg("pyts3_proc_thread2 returning")
            
    def pyt_proc_thread2(self):
        """ Process pending speech requests (SpeakerControlCmd)
        """
        SlTrace.lg("pyt_proc_thread running2")
        while self.running2:
            cmd = self.pyt_queue2.get()
            SlTrace.lg(f"pyts3_queue2.get():{cmd}")
            self.do_talk(cmd)
        SlTrace.lg("pyts3_proc_thread returning")
            
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
        self.run_and_wait_thread.start()
        SlTrace.lg("AFTER thread start()")
        self.run_and_wait_thread.join()
        SlTrace.lg("AFTER thread join()")
        
    def run_and_wait_thread_proc(self, text):
        SlTrace.lg("starting run_and_wait_thread_proc")
        eng = pyttsx3.init()
        eng.say(text)
        SlTrace.lg(f"After eng.say({text})")
        eng.runAndWait()
        SlTrace.lg("after eng.runAndWait()")
    
if __name__ == "__main__":
    print("\nTest Start")
    tt = PyttsxQueued()
    tt.talk("Hello World")
    tt.talk("How are you?")
    tt.talk("How's the weather?")
    tt.talk("Good Bye for now.")
    tt.wait_while_busy()
    print("Test End\n")