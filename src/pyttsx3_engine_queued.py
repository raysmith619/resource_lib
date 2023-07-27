#pyttsx3_engine.py  07Jul2023  crs, from text_to_speech.py
"""
Encapusuation of pyttsx3

"""
import time
import threading
import queue

import pyttsx3

from select_trace import SlTrace
from format_exception import format_exception

    
class Pyttsx3Engine:
    def __init__(self):
        self.got_pyttsx3 = False
        self.pyts3_que_size = 20      # queue size, till blocking
        self.tts_talking = False
        try:
            import pyttsx3
            self.got_pyttsx3 = True
            SlTrace.lg("pyttsx3 installed")

        except:
            SlTrace.lg("pyttsx3 NOT installed")
        
        self.pyttsx3_engine = None
        if self.got_pyttsx3:
            try:
                self.pyttsx3_engine = pyttsx3.init()
            except:
                SlTrace.lg("Can't init pyttsx3")


        self.pyts3_queue = queue.Queue(self.pyts3_que_size)  # speech queue of SpeakerControlCmd 
        self.pyts3_thread = threading.Thread(target=self.pyts3_proc_thread)
        self.pyts3_thread.start()

                
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
        SlTrace.lg(f"""pyttsx3_engine.speak_text:  speak_text(msg={msg}, msg_type={msg_type},"""
                   f""" rate={rate}, volume={volume})""")
        tts_cmd = TextToSpeechCmd(msg=msg, rate=rate, volume=volume, wait=wait)
        self.pyts3_queue.put(tts_cmd)
            
    def clear(self):
        """ Clear queues
        """
        while not self.pyts3_queue.empty():
            try:
                self.pyts3_queue.get(block=False)
            except Empty:
                continue
            
    def pyts3_proc_thread(self):
        """ Process pending speech requests (SpeakerControlCmd)
        """
        SlTrace.lg("pyts3_proc_thread running")
        while True:
            SlTrace.lg("pyts3 thread loop")
            if self.pyttsx3_engine._inLoop:
                SlTrace.lg("pyts3 thread loop eng _inLoop")
                time.sleep(.1)
                continue
            
            if self.pyts3_queue.qsize() > 0:            
                SlTrace.lg("pyts3_queue.get()")
                cmd = self.pyts3_queue.get()
                SlTrace.lg(f"pyts3_proc_thread: cmd: {cmd}", "pyts3_queue")
                if cmd.cmd_type == "CLEAR":
                    self.pyts3_proc_queue.empty()
                    self.pytt3.clear()
                else:
                    self.speak_text_cmd(cmd)
            else:
                time.sleep(.1)
                
        SlTrace.lg("pyts3_proc_thread returning")

    def stop():
        """ stop speech/talking
        """
        if self.got_pyttsx3:
            self.pyttsx3_engine.stop()
            
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
        self.tts_talking = True
        SlTrace.lg(f"Setting tts_talking")
        msg = cmd.msg
        msg_type = cmd.msg_type
        rate = cmd.rate
        volume = cmd.volume
        wait = cmd.wait
        cmd_type = cmd.cmd_type
        try:                
            if self.pyttsx3_engine._inLoop:
                SlTrace.lg("Pyttsx3Engine.speak_text - in run loop - ignored")
                return
            
                self.pyttsx3_engine.endLoop()
                self.tts_talking = False
                SlTrace.lg(f"Clearing tts_talking")
                return
            
            if msg_type == 'REPORT':
                SlTrace.lg(f"Pyttsx3Engine.speak_text_cmd: speak_text say  msg: {msg}", "speech")
                self.pyttsx3_engine.setProperty('rate', rate)
                self.pyttsx3_engine.setProperty('volume', volume)
                self.pyttsx3_engine.say(msg)
                SlTrace.lg(f"Pyttsx3Engine.speak_text_cmd: AFTER engine.say  msg: {msg}", "speech")
                self.pyttsx3_engine.runAndWait()
                SlTrace.lg("Pyttsx3Engine.speak_text_cmd: AFTER runAndWait")
                time.sleep(.01)
                self.tts_talking = False
                SlTrace.lg(f"Clearing tts_talking")
                time.sleep(.01)
            elif msg_type == "ECHO":
                if self.pyttsx3_engine._inLoop:
                    SlTrace.lg("speak_text ECHO - in run loop - ignored")
                    self.pyttsx3_engine.endLoop()
                    return
                
                self.pyttsx3_engine.say(msg)
                self.pyttsx3_engine.setProperty('rate', 240)
                self.pyttsx3_engine.setProperty('volume', 0.9)
                self.pyttsx3_engine.runAndWait()
                self.tts_talking = False
                SlTrace.lg(f"Clearing tts_talking")
            else:
                raise Exception(f"Unrecognized msg_type"
                                f" {msg_type} {msg}")
        except Exception as e:
            SlTrace.lg("Bust out of speak_text")
            SlTrace.lg(f"Unexpected exception: {e}")
            SlTrace.lg("Printing the full traceback as if we had not caught it here...")
            SlTrace.lg(format_exception(e))

    def is_busy(self):
        time.sleep(.1)
        SlTrace.lg(f"pyttsx3_engine.tts_talking:{self.tts_talking}"
                   f" isBusy(): {self.pyttsx3_engine.isBusy()}")
        if self.tts_talking and self.pyttsx3_engine.isBusy():
            return True
        
        return False
    
    def wait_while_busy(self):
        """ Wait while busy
        """
        ###time.sleep(3)
        ###return
    
        SlTrace.lg("Pyttsx3Engine.wait_while_busy"
                   f" queue:{self.pyts3_queue.qsize()}")
        while self.tts_talking:
            time.sleep(.1)

if __name__ == "__main__":
    SlTrace.setFlags("speech,sound_queue")
    SlTrace.lg("\nStart Test")
    tts = Pyttsx3Engine()    
    tts.speak_text("Hello World!")
    tts.wait_while_busy()
    tts.speak_text("How are you?")
    tts.wait_while_busy()
    tts.speak_text("Hows the weather?")
    tts.wait_while_busy()
    tts.speak_text("What's up?")
    tts.clear()
    tts.speak_text("Just cleared")

          