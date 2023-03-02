# speech_maker.py    19Feb2023  crs, Author
"""
Support thread safe non-blocking text to speach encapsulation of pyttsx3
facilitating talk from multiple AudioDrawWindow sources
"""
import threading
import queue
import sys
import time

from select_trace import SlTrace, SelectError


class SpeechMakerError(SelectError):
    pass


class Singleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None: 
            with cls._lock:
                # Another thread could have created the instance
                # before we acquired the lock. So check that the
                # instance is still nonexistent.
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance


class SpeechMakerCmd:
    """ Command to execute
    """

    def __init__(self, cmd_type=None, msg=None, msg_type=None):
        """ Setup command
        :cmd_type: command to execute
                "MSG" - speak message
                "CLEAR" - clear pending speech
                "QUIT" - quit operation
        :msg: text to speak SpeakText
        :msg_type: type of message
                REPORT: std reporting
                CMD: command
                ECHO: echo of user input
            default: REPORT
        """
        self.cmd_type = cmd_type
        self.msg = msg
        self.msg_type = msg_type

    def __str__(self):
        ret = f"SpeechMakerCmd {self.cmd_type}"
        if self.msg is not None:
            ret += f" {self.msg}"
        if self.msg_type is not None:
            ret += f" {self.msg_type}"
        return ret

        
class SpeechMaker(Singleton):
    CMDS_SIZE = 20
    SPEECH_SIZE = 20

    def __init__(self, cmds_size=CMDS_SIZE, speech_size=SPEECH_SIZE):
        self.cmds_size = cmds_size
        self.speech_size = speech_size
        self._running = True        # Thread functions exit when cleared

        try:
            import pyttsx3
            self.pyttsx3_engine = pyttsx3.init()
        except:
            self.pyttsx3_engine = None 


        self.speech_lock = threading.Lock()
        self.sm_cmd_queue = queue.Queue(cmds_size)  # Command queue of SpeechMakerCmd
        self.sm_cmd_thread = threading.Thread(target=self.sm_cmd_proc_thread)
        self.sm_speech_queue = queue.Queue(speech_size)  # speech queue of SpeechMakerCmd 
        self.sm_speech_thread = threading.Thread(target=self.sm_speech_proc_thread)
        self.sm_speech_thread.start()
        self.sm_cmd_thread.start()
        
    def sm_cmd_proc_thread(self):
        """ speech maker command processing thread function
        """
        while self._running:
            cmd = self.sm_cmd_queue.get()
            SlTrace.lg(f"cmd: {cmd}", "speech")
            if cmd.cmd_type == "MSG":
                self.sm_speech_queue.put(cmd)
            elif cmd.cmd_type == "CLEAR":
                SlTrace.lg("Clearing speech")
                self.clear()
            elif cmd.cmd_type == "QUIT":
                self.clear()
                self.sm_speech_queue.put(cmd)
                self.quit()
            else:
                raise SpeechMakerError(f"Unrecognized SpeechMaker command {cmd}")
        SlTrace.lg("sm_cmd_proc_thread returning")

    def clear(self):
        """ Clear queue
        """
        SlTrace.lg("speech clearing")
        with self.sm_cmd_queue.mutex:
            self.sm_cmd_queue.queue.clear()
        SlTrace.lg(f"self.sm_cmd_queue.qsize(): {self.sm_cmd_queue.qsize()}")
        with self.sm_speech_queue.mutex:
            self.sm_speech_queue.queue.clear()
        SlTrace.lg(f"self.sm_speech_queue.qsize(): {self.sm_speech_queue.qsize()}")

    def clear_cmd_queue(self):
        while self.sm_cmd_queue.qsize() > 0:
            cmd = self.sm_cmd_queue.get()
            SlTrace.lg(f"removing cmd entry: {cmd}")

    def clear_speech_queue(self):
        while self.sm_speech_queue.qsize() > 0:
            cmd = self.sm_speech_queue.get()
            SlTrace.lg(f"removing speech queue entry: {cmd}")
            
    def force_clear(self):
        """ force Clear queue
        """
        SlTrace.lg("force speech clearing")
        self.clear_cmd_queue()
        SlTrace.lg(f"self.sm_cmd_queue.qsize(): {self.sm_cmd_queue.qsize()}")
        self.clear_speech_queue()
        SlTrace.lg(f"self.sm_speech_queue.qsize(): {self.sm_speech_queue.qsize()}")
        #if self.pyttsx3_engine.isBusy():
        #    self.pyttsx3_engine.stop()

        #if self.pyttsx3_engine._inLoop:
        #    self.pyttsx3_engine.endLoop()
        #self.speech_lock.release()
        
    def sm_speech_proc_thread(self):
        """ Process pending speech requests (SpeechMakerCmd)
        """
        
        while self._running:
            cmd = self.sm_speech_queue.get()
            SlTrace.lg(f"speech queue: cmd: {cmd}", "speech")
            if cmd.cmd_type == "CLEAR":
                continue
            elif cmd.cmd_type == "QUIT":
                self.pyttsx3_engine.stop()
                break
            
            msg = cmd.msg
            msg_type = cmd.msg_type
            self.speak_text(msg, msg_type=msg_type)
            SlTrace.lg(f"speech queue: cmd: {cmd} AFTER speak_text", "speech")
        SlTrace.lg("sm_speech_proc_thread returning")
            
    def quit(self):
        SlTrace.lg("SpeachMaker quitting")
        self.clear()
        self._running = False       # All our threads watch this
        self.sm_cmd_queue.put(SpeechMakerCmd(cmd_type="QUIT"))   # drop the wait
        self.sm_speech_queue.put(SpeechMakerCmd(cmd_type="QUIT"))   # drop the wait
        SlTrace.lg("Force threads stop")
        #self.sm_speech_thread.join()
        #self.sm_cmd_thread.join()
                
    def speak_text(self, msg, msg_type=None):
        """ Called to speak pending line
        
        """
        try:                
            with self.speech_lock:
                if self.pyttsx3_engine._inLoop:
                    SlTrace.lg("speak_text - in run loop - ignored")
                    self.pyttsx3_engine.endLoop()
                    return
                
                if msg_type == 'REPORT':
                    self.pyttsx3_engine.say(msg)
                    self.pyttsx3_engine.setProperty('rate', 240)
                    self.pyttsx3_engine.setProperty('volume', 0.9)
                    self.pyttsx3_engine.runAndWait()
                    SlTrace.lg(f"speak_text  msg: {msg} AFTER runAndWait", "speech")
                elif msg_type == "ECHO":
                    if self.pyttsx3_engine._inLoop:
                        SlTrace.lg("speak_text ECHO - in run loop - ignored")
                        self.pyttsx3_engine.endLoop()
                        return
                    
                    self.pyttsx3_engine.say(msg)
                    self.pyttsx3_engine.setProperty('rate', 240)
                    self.pyttsx3_engine.setProperty('volume', 0.9)
                    self.pyttsx3_engine.runAndWait()
                else:
                    raise SpeechMakerError(f"Unrecognized speech_type"
                                    f" {msg_type} {msg}")
        except:
            SlTrace.lg("Bust out of speak_text")

    def send_cmd(self, cmd_type='speak', msg=None, msg_type=None):
        """ Send cmd to speach engine
        :cmd_type: command type
                    'text'        - speak text
                    'erase_queue' - erase/cancel pending speech
                    'exit' - erase/cancel pending speech and then stop engine
        :msg: message text, if any
        :msg_type: type of text
                'report'  - standard report
                'command' - a command
        """
        SlTrace.lg(f"send_cmd:{cmd_type} msg: {msg}")
        cmd = SpeechMakerCmd(cmd_type=cmd_type, msg=msg, msg_type=msg_type)
        self.sm_cmd_queue.put(cmd)

            
class SpeechMakerLocal:
    """ Localinstance of SpeechMaker
    """

    def __init__(self, win=None, logging_speech=False):
        self.sm = SpeechMaker()
        self.win = win
        self.logging_speech = logging_speech
        self.make_silent(False)

    def make_silent(self, val=True):
        self._silent = val

    def clear(self):
        """ Clear pending output
        """
        self.sm.clear()
        
    def quit(self):    
        self.sm.quit()

        
    def speak_text(self, msg, dup_stdout=True,
                   msg_type="REPORT"):
        """ Speak text, if possible else write to stdout
        :msg: text message
        :dup_stdout: duplicate to stdout default: True
        :nsg_type: type of speech default: 'REPORT'
            REPORT - standard reporting
            CMD    - command
            ECHO - echo user input
        """
        if self.logging_speech:
            SlTrace.lg(msg)
        if self.win is not None:
            self.win_print(msg)
        text_lines = msg.split("\n")
        for text_line in text_lines:
            if not self._silent:
                self.sm.send_cmd(cmd_type="MSG", msg=text_line, msg_type=msg_type)
        if dup_stdout and not self.logging_speech:
            SlTrace.lg(msg)

    def speak_text_stop(self):
        """ Stop pending speech
        """
        self.sm.force_clear()
        
            
if __name__ == "__main__":
    
    sml = SpeechMakerLocal()
    sml.speak_text("Hello World!")
    sml.speak_text("How are you?")
    sml.speak_text("Hows the weather?")
    sml.speak_text("What's up?")
    time.sleep(3)
    sml.clear()
    sml.speak_text("Just cleared")
    time.sleep(4)
