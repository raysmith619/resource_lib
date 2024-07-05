#text_to_speech.py  07Jul2023  crs, Author
"""
Text-to-speech
Initially encapusulate pyttsxN text-to-speach
"""
import time
import queue
import threading

from pyttsxN_engine import pyttsxNEngine

from select_trace import SlTrace
from format_exception import format_exception

class TextToSpeechCmd:
    def __init__(self, msg=None, msg_type="REPORT",
                   rate=240, volume=.9, wait=True, cmd_type=None):
        self.msg = msg
        self.msg_type = msg_type
        self.rate = rate
        self.volume = volume
        self.wait = wait
        self.cmd_type = cmd_type

    def __str__(self):
        st = "TextToSpeechCmd:"
        st += self.msg
        st += f" {self.msg_type}"
        st += f" rate={self.rate}"
        st += f" volume={self.volume}"
        st += f" wait={self.wait}"
        st += f" cmd_type={self.cmd_type}"
        return st
    
class TextToSpeechResult:
    RES_OK = "RES_OK"
    RES_ERR = "RES_ERR"
    def __init__(self, msg=None, cmd_type=None,
                 code=None):
        if code is None:
            code = self.RES_OK
        self.msg = msg
        self.cmd_type = cmd_type
        self.code = code
    
class TextToSpeech:
    def __init__(self):
        self.pytt3 = pyttsxNEngine()

                
    def speak_text(self, msg, msg_type="REPORT",
                   rate=240, volume=.9, wait=True):
        """ Speak text, place message into text queue
        to be spoken
        :msg: text of message
        :msg_type: default: REPORT
        :rate: speech rate words per minute
                default: 240
        :volume: volume default: .9
        """
        SlTrace.lg(f"TextToSpeech.speak_text msg:{msg}")
        tts_cmd = TextToSpeechCmd(msg=msg, rate=rate, volume=volume, wait=wait)
        self.speak_text_cmd(tts_cmd)
            
    def clear(self):
        """ Clear queues
        """
        self.pytt3.clear()

    def clear_out_queue(self):
        """ Clear output queue so it can be an indicator
        of speech completion
        """
        while not self.tts_out_queue.empty():
            try:
                self.tts_out_queue.get(block=False)
            except Empty:
                continue


    def ck_queue(self):
        """ Check queue and speak if text available
        """
        if not self.pytt3.is_busy() and self.tts_queue.qsize() > 0:
            cmd = self.tts_queue.get()
            SlTrace.lg(f"ck_queue: cmd: {cmd}", "tts_queue")
            self.pytt3.speak_text_cmd(cmd)
            
            
    def stop():
        """ stop speech/talking
        """
        if self.got_pyttsxN:
            self.pyttsxN_engine.stop()
            
            

    def is_busy(self):
        """ Check if speech is pending or in progress
        :returns: True if busy, False if free
        """
        SlTrace.lg(f"is_busy: pytt3.is_busy():{self.pytt3.is_busy()}")
        return self.pytt3.is_busy()

    def wait_while_busy(self, max_wait=5, wait_proc=time.sleep, inc=.1):
        """ wait till free
        :max_wait: Maximum wait time (seconds) default=5
        :wait_proc: waiting function default: time.sleep
        :inc: wait time (seconds) increment default: .1 sec
        """
        SlTrace.lg("wait_while_busy()")
        self.busy_start_time = time.time()
        while self.is_busy():
            if time.time()-self.busy_start_time > max_wait:
                break
            
            wait_proc(inc)
        
      
    def speak_text_cmd(self, cmd):
        """ speak text command
        :cmd: SpeechTextCmd with speech
        """
        SlTrace.lg(f"speak_text_cmd: {cmd}")
        self.pytt3.put_speech_cmd(cmd)


if __name__ == "__main__":
    tts = TextToSpeech()    
    SlTrace.setFlags("speech,sound_queue")
    SlTrace.lg("\nTest Start")
    tts.speak_text("Hello World!")
    tts.wait_while_busy()
    tts.speak_text("How are you?")
    tts.wait_while_busy()
    tts.speak_text("Hows the weather?")
    tts.wait_while_busy()
    tts.speak_text("What's up?")
    time.sleep(10)
    #tts.clear()
    tts.speak_text("Just cleared")

          