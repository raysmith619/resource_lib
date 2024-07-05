#pyttsxN_engine.py  07Jul2023  crs, from text_to_speech.py
"""
Encapusulation of pyttsxN including queued requests

"""
import time
import threading
import queue

from text_to_speech_cmd import TextToSpeechCmd
from pyttsxN_engine import pyttsxNEngine

from select_trace import SlTrace
from format_exception import format_exception

    
class pyttsxNEngineQueued:
    def __init__(self):
        self.pyt = pyttsxNEngine()
        self.pyts3_que_size = 20      # queue size, till blocking
        self.running = True
        self.text_cmd = None            # Current cmd

        self.pyt_queue = queue.Queue(self.pyts3_que_size)  # speech queue of SpeakerControlCmd 
        self.pyt_thread = threading.Thread(target=self.pyt_proc_thread)
        self.pyt_thread.start()

                
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
        if msg_type is None:
            msg_type = "REPORT"
        SlTrace.lg(f"""pyttsxN_engine.speak_text:  speak_text(msg={msg}, msg_type={msg_type},"""
                   f""" rate={rate}, volume={volume})""")
        tts_cmd = TextToSpeechCmd(msg=msg, rate=rate, volume=volume, wait=wait)
        self.pyt_queue.put(tts_cmd)
            
    def clear(self):
        """ Clear queues
        """
        while not self.pyt_queue.empty():
            try:
                self.pyt_queue.get(block=False)
            except Empty:
                continue
            
    def pyt_proc_thread(self):
        """ Process pending speech requests (SpeakerControlCmd)
        """
        SlTrace.lg("pyts3_proc_thread running")
        while self.running:
            SlTrace.lg("pyt thread loop")
            if self.pyt.is_busy():
                SlTrace.lg("pyt isBusy")
                time.sleep(.1)
                continue
            
            if self.pyt_queue.qsize() > 0:            
                cmd = self.pyt_queue.get()
                SlTrace.lg(f"pyts3_queue.get():{cmd}")
                SlTrace.lg(f"pyt_proc_thread: cmd: {cmd}", "pyts3_queue")
                if cmd.cmd_type == "CLEAR":
                    self.clear()
                    self.pyt.clear()
                else:
                    self.speak_text_cmd(cmd)
            else:
                time.sleep(.1)
                
        SlTrace.lg("pyts3_proc_thread returning")

    def stop(self):
        """ stop speech/talking
        """
        self.running = False    # Stop queue thread
        self.clear()
        self.pyt.stop()
            
    def put_speech_cmd(self, cmd):
        """ Add speech command
        :cmd: speach command(TextToSpeechCmd)
        """
        self.tts_talking = True
        self.pyts3_queue.put(cmd)            
        
      
    def speak_text_cmd(self, cmd):
        """ speak text command
        :cmd: SpeechTextCmd with speech
        """
        self.text_cmd = cmd
        self.pyt.speak_text_cmd(cmd=cmd)

    def is_busy(self):
        if self.pyt_queue.qsize() > 0:
            return True
        
    
        return self.pyt.is_busy()
    
    def wait_while_busy(self):
        """ Wait while busy
        """
        SlTrace.lg("pyttsxNEngineQueued.wait_while_busy"
                   f" queue:{self.pyt_queue.qsize()}")
    
        while self.is_busy():
            time.sleep(.1)

if __name__ == "__main__":
    SlTrace.setFlags("speech,sound_queue")
    SlTrace.lg("\nStart Test")
    tts = pyttsxNEngineQueued()    
    tts.speak_text("Hello World!")
    tts.speak_text("How are you?")
    tts.wait_while_busy()

    tts.speak_text("Hows the weather?")
    tts.wait_while_busy()
    tts.speak_text("What's up?")
    tts.stop()
    tts.speak_text("Just stopped")
    SlTrace.lg("Test End")

          