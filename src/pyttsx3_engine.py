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

from text_to_speech_cmd import TextToSpeechCmd
class Pyttsx3Engine:
    def __init__(self):
        self.got_pyttsx3 = False
        self.eng_talking = False
        self.eng_queue_size = 3
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
                self.got_pyttsx3 = False
                self.pyttsx3_engine = None

        self.running = True
        self.eng_queue = queue.Queue(self.eng_queue_size)  # speech queue of SpeakerControlCmd 
        self.eng_thread = threading.Thread(target=self.eng_proc_thread)
        self.eng_thread.start()

            
    def eng_proc_thread(self):
        """ Process pending engine requests (SpeakerControlCmd)
        """
        SlTrace.lg("engine_proc_thread running")
        while self.running:
            SlTrace.lg("engine thread loop")
            if self.is_busy():
                SlTrace.lg("engine isBusy")
                time.sleep(.1)
                continue
            
            if self.eng_queue.qsize() > 0:            
                cmd = self.eng_queue.get()
                SlTrace.lg(f"eng_queue.get():{cmd}")
                SlTrace.lg(f"eng_proc_thread: cmd: {cmd}", "eng_queue")
                if cmd.cmd_type == "CLEAR":
                    self.clear()
                    self.pyt.clear()
                else:
                    self.speak_text_cmd_do(cmd)
            else:
                time.sleep(.1)
                
        SlTrace.lg("eng_proc_thread returning")

                
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
        self.speak_text_cmd(tts_cmd)

    def clear(self):
        """ Clear out pending/present speech
        """
        if self.got_pyttsx3:
            self.pyttsx3_engine.stop()
        
        
    def stop(self):
        """ stop speech/talking
        """
        self.running = False
        self.clear()

    def speak_text_cmd(self, cmd):
        """ Send text command to speaker queue
        to be spoken at next opportunity
        """
        self.eng_queue.put(cmd)        
      
    def speak_text_cmd_do(self, cmd):
        """ speak text command
        :cmd: SpeechTextCmd with speech
        """
        self.eng_talking = True
        SlTrace.lg(f"Setting eng_talking")
        msg = cmd.msg
        msg_type = cmd.msg_type
        rate = cmd.rate
        volume = cmd.volume
        wait = cmd.wait
        cmd_type = cmd.cmd_type
        if not self.got_pyttsx3:
            return
        
        try:                
            if self.pyttsx3_engine._inLoop:
                SlTrace.lg("Pyttsx3Engine.speak_text - in run loop - ignored")
                return
            
                self.pyttsx3_engine.endLoop()
                self.eng_talking = False
                SlTrace.lg(f"Clearing eng_talking")
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
                self.eng_talking = False
                SlTrace.lg(f"Clearing eng_talking")
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
                self.eng_talking = False
                SlTrace.lg(f"Clearing eng_talking")
            else:
                raise Exception(f"Unrecognized msg_type"
                                f" {msg_type} {msg}")
        except Exception as e:
            SlTrace.lg("Bust out of speak_text")
            SlTrace.lg(f"Unexpected exception: {e}")
            SlTrace.lg("Printing the full traceback as if we had not caught it here...")
            SlTrace.lg(format_exception(e))

    def is_busy(self):
        return False    # TFD
        return self.eng_talking

    
    def wait_while_busy(self):
        """ Wait while busy
        """
        SlTrace.lg("Pyttsx3Engine.wait_while_busy")
        return  # TFD
    
        while self.is_busy():
            time.sleep(.1)

if __name__ == "__main__":
    SlTrace.setFlags("speech,sound_queue")
    SlTrace.lg("\nStart Test")
    tts = Pyttsx3Engine()    
    tts.speak_text("Hello World!"*2)
    tts.wait_while_busy()
    tts.speak_text("How are you?")
    tts.wait_while_busy()
    tts.speak_text("Hows the weather?")
    tts.wait_while_busy()
    tts.speak_text("What's up?")
    time.sleep(20)
    tts.clear()
    tts.speak_text("Just cleared")

          