#pyttsx_proc_1.py   19Sep2023  crs
""" simple text string version
pyttsxN ecapuslated in a Process
    Facilitates stopping talking mid-utterance
"""
import multiprocessing as mp

import pyttsx3

#from select_trace import SlTrace
class SlTrace:
    def __init__(self):
        pass

    @classmethod
    def lg(cls, msg="", trace_flag=None, level=1, to_stdout=None, dp=None):
        """
        Simple print for SlTrace to avoid
        multiprocessing confusion
        """
        print(msg)

class PyttsxProc:
    def __init__(self):
        """ Setup for interprocess communication
        """
        self.pyt_proc = mp.Process(target=self.pyt_proc_proc)
        self.pyt_queue = mp.Queue(10)  # speech queue of SpeakerControlCmd
        self.pyt_busy = False 
        self.pyt_out_queue = mp.Queue(10)
        self.pyt_proc.start()
        
    def pyt_proc_proc(self):
        """ process speech commands
        """    
        self.engine = pyttsx3.init()

        self.running = True
        
        while self.running:
            cmd = self.pyt_queue.get()
            self.do_talk(cmd)

    def clear(self):
        """ Clear current and pending talking
        """
        self.pyt_proc.kill()
        self.pyt_proc.join()
        
                    
    def is_alive(self):
        return self.pyt_proc.is_alive()

    
    def talk(self, text):
        """ Say text
        :text: text to speak
        """
        self.pyt_queue.put(text)
        SlTrace.lg(f"talk - queue size: {self.pyt_queue.qsize()}")
        
    def do_talk(self, text):
        """ do talking, waiting till done
        :text: text to say
        """
        self.engine_runAndWait(text)
        SlTrace.lg("after engine_runAndWait()")
        SlTrace.lg(f"do_talk - queue size: {self.pyt_queue.qsize()}")

    def engine_runAndWait(self, text):
        """ run engine, wait till done
            use cycles in different thread
        """
        self.pyt_out_queue.put(True)
        self.engine.say(text)
        SlTrace.lg(f"After eng.say({text})")
        self.engine.runAndWait()
        SlTrace.lg("after eng.runAndWait()")
        self.pyt_out_queue.put(False)
        
    def wait_while_busy(self):
        while True:
            if self.pyt_queue.qsize()>0:
                continue

            if not self.is_busy():
                break

    def is_busy(self):
        """ Check if busy talking or
        getting ready to talk
        """
        if self.pyt_queue.qsize()>0:
            return True
        
        while self.pyt_out_queue.qsize() > 0:
            out_busy = self.pyt_out_queue.get()
            self.pyt_busy = out_busy
        return self.pyt_busy
        
    
    def quit(self, wait=True):
        """ Quit talking
        :wait: if true wait till talking is done
                default: True - wait
        """
        SlTrace.lg("Quitting")
        if wait:
            self.wait_while_busy()
        SlTrace.lg("kill")
        self.pyt_proc.kill()
        SlTrace.lg("join")
        self.pyt_proc.join()
        SlTrace.lg("After quit")
           
    
if __name__ == "__main__":
    SlTrace.lg("\nTest Start")
    tt = PyttsxProc()
    tt.talk("Hello World")
    tt.talk("How are you?")
    tt.talk("How's the weather?")
    tt.wait_while_busy()
    tt.talk("Good Bye for now.")
    tt.quit()
    SlTrace.lg("Test End\n")