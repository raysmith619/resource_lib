#pyttsx_proc.py   19Sep2023  crs
""" pyttsxN ecapuslated in a Process
    Facilitates stopping talking mid-utterance
"""
import multiprocessing as mp

from speech_maker_cmd import SpeechMakerCmd
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
        self.pyt_proc = None    # Set when ready
        
    def pyt_proc_proc(self):
        """ process speech commands
        """    
        self.engine = pyttsx3.init()

        self.running = True
        
        while self.running:
            cmd = self.pyt_queue.get()
            self.do_cmd(cmd)

    def setup_proc(self):
        """ Setup procesing process
        """
        self.pyt_proc = mp.Process(target=self.pyt_proc_proc)
        self.pyt_queue = mp.Queue(10)  # speech queue of SpeakerControlCmd
        self.pyt_busy = False 
        self.pyt_out_queue = mp.Queue(10)
        self.pyt_proc.start()
        
    def clear(self):
        """ Clear current and pending talking
        """
        if self.pyt_proc is None:
            return      # clear or unset
        
        self.pyt_proc.kill()
        self.pyt_proc.join()
        self.pyt_proc = None
        
                    
    def is_alive(self):
        """ Check if speech processing is going
        """
        if self.pyt_proc is None:
            return False
        
        return self.pyt_proc.is_alive()

    
    def talk(self, text, rate=None, volume=None):
        """ Say text
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
        SlTrace.lg(f"make_cmd - queue size: {self.pyt_queue.qsize()}")
            
    def do_cmd(self, cmd):
        """ do talking, waiting till done
        :cmd: SpeechMakerCmd
        """
        self.engine_runAndWait(cmd)
        SlTrace.lg("after engine_runAndWait()")
        SlTrace.lg(f"do_cmd - queue size: {self.pyt_queue.qsize()}")

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
            SlTrace.lg(f"After eng.say({cmd.msg})")
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
    import time
    
    SlTrace.lg("\nTest Start")
    tt = PyttsxProc()
    tt.talk("Hello World")
    tt.talk(" ".join([str(i) for i in range(100,0,-1)]))
    time.sleep(5)
    tt.clear()
    tt.talk("How are you?", volume=.5)
    tt.talk("How's the weather?", rate=120)
    tt.wait_while_busy()
    tt.talk("Good Bye for now.", volume=.99)
    tt.quit()
    SlTrace.lg("Test End\n")