#pyttsx_proc.py   19Sep2023  crs
""" pyttsxN ecapuslated in a separate process
    Supports
        1. queued requests
        2. clearing pending and current requests
"""
import multiprocessing as mp

from speech_maker_cmd import SpeechMakerCmd
import pyttsx4 as pyttsxN    # Can use pyttsx4 instead

from select_trace import SlTrace

class PyttsxProc:
    def __init__(self, qlen=10):
        """ Setup for interprocess communication
        :qlen: input/output queue length
                default: 10
        """
        self.qlen = qlen
        self.setup_proc()       # setup incase
                                # is_busy called
                                # before talk
    def pyt_proc_proc(self):
        """ process speech commands
            process's processing procedure
        """    
        self.engine = pyttsxN.init()

        while True:
            cmd = self.pyt_queue.get()
            self.do_cmd(cmd)

    def setup_proc(self):
        """ Setup procesing process
        """
        self.pyt_busy = False   # Updated with status 
        self.pyt_proc = mp.Process(target=self.pyt_proc_proc)
        self.pyt_queue = mp.Queue(self.qlen)  # speech queue of SpeakerControlCmd
        self.pyt_out_queue = mp.Queue(self.qlen)
        self.pyt_proc.start()
        
    def clear(self):
        """ Clear current and pending talking
        """
        if self.pyt_proc is None:
            return      # clear or unset
        
        self.pyt_proc.kill()
        self.pyt_proc.join()
        self.pyt_proc = None    # Forces talk to re-setup
        
                    
    def is_alive(self):
        """ Check if speech processing is going
        """
        if self.pyt_proc is None:
            return False    # inactive
        
        return self.pyt_proc.is_alive()

    
    def talk(self, text, rate=None, volume=None):
        """ Say text
        Starts process if inactive
        :text: text to speak
        """
        cmd = SpeechMakerCmd(msg=text, rate=rate,
                             volume=volume)
        self.make_cmd(cmd)
    
    def make_cmd(self, cmd):
        """Make speech command
        :cmd: SpeechMakerCmd
            QUIT - clear pending and current speech
        """
        if self.pyt_proc is None:
            self.setup_proc()
            
        if cmd.cmd_type == "QUIT":
            self.quit()
            return
        
        self.pyt_queue.put(cmd)
        SlTrace.lg(f"make_cmd - queue size: {self.pyt_queue.qsize()}", "talk_cmd")
            
    def do_cmd(self, cmd):
        """ do talking, waiting till done
        :cmd: SpeechMakerCmd
        """
        self.engine_runAndWait(cmd)
        SlTrace.lg("after engine_runAndWait()", "talk_cmd")
        SlTrace.lg(f"do_cmd - queue size: {self.pyt_queue.qsize()}", "talk_cmd")

    def engine_runAndWait(self, cmd):
        """ run engine, wait till done
        """
        self.pyt_out_queue.put(True)    # Set as busy
        if cmd.rate is not None:
            self.engine.setProperty('rate', cmd.rate)
        if cmd.volume is not None:
            self.engine.setProperty('volume', cmd.volume)
        if cmd.msg is not None:
            self.engine.say(cmd.msg)
            SlTrace.lg(f"After eng.say({cmd.msg})", "talk_cmd")
            self.engine.runAndWait()
        SlTrace.lg("after eng.runAndWait()", "talk_cmd")
        self.pyt_out_queue.put(False)
        
    def wait_while_busy(self):
        while True:
            if not self.is_busy():
                break

    def is_busy(self):
        """ Check if busy talking or
        getting ready to talk
        """
        if self.pyt_queue.qsize()>0:
            return True
        
        while self.pyt_out_queue.qsize() > 0:
            self.pyt_busy = self.pyt_out_queue.get()
        return self.pyt_busy
        
    
    def quit(self, wait=True):
        """ Quit talking
        :wait: if true wait till talking is done
                default: True - wait
        """
        SlTrace.lg("Quitting", "talk_cmd")
        if wait:
            self.wait_while_busy()
        SlTrace.lg("kill", "talk_cmd")
        self.pyt_proc.kill()
        SlTrace.lg("join", "talk_cmd")
        self.pyt_proc.join()
        SlTrace.lg("After quit", "talk_cmd")
           
    
if __name__ == "__main__":
    import time
    
    SlTrace.clearFlags()
    SlTrace.setFlags("talk_cmd")
    
    SlTrace.lg("\nTest Start")
    tt = PyttsxProc()
    tt.talk("Hello World")
    tt.talk(" ".join([str(i) for i in range(100,0,-1)]))
    time.sleep(4)
    tt.clear()
    tt.talk("How are you?", volume=.5)
    tt.talk("How's the weather?", rate=120)
    tt.wait_while_busy()
    tt.talk("Good Bye for now.", volume=.99)
    tt.quit()
    SlTrace.lg("Test End\n")