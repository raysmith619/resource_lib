# speaker_control.py    19Feb2023  crs, Author
"""
Support thread safe non-blocking speaker control:
    1. text to speech encapsulation of pyttsx3 facilitating
     talk from multiple AudioDrawWindow sources
    2. tone playing using SineWaveNumPy, audio-sounddevice
    
"""
import threading
import queue
import sys
import time
import sounddevice as sd

from format_exception import format_exception
from select_trace import SlTrace, SelectError
from play_sound_control import PlaySoundControl
from sinewave_numpy import SineWaveNumPy
from Lib.pickle import TRUE, FALSE

got_pyttsx3 = False
try:
    import pyttsx3
    got_pyttsx3 = True
except:
    SlTrace.lg("No pyttsx3 to be had")




class SpeakerControlError(SelectError):
    pass

class SpeakerControlDelay:
    """ Delay info
    """
    def __init__(self, dur):
        """ Start delay
        :dur: duration seconds
        """
        self.dur = dur
        self.start = time.time()
        self.end = self.start + self.dur
        
    def is_end(self):
        """ Check if time is up
        :returns: True if at or past end
        """
        now = time.time()
        if now > self.end:
            return True 
        
        return False

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


class SpeakerTone:
    """ Tone to emit
    """
    
    def __init__(self, pitch, volume, dur, delay=0):
        """ Setup tone to emit
        :pitch:
        :volume: (v_left, v_right)
        :dur: seconds
        :delay:   delay before start default: no delay
        """
        self.pitch = pitch
        self.volume = volume
        self.dur = dur
        self.delay = delay
    
    def __str__(self):
        st = f"SpeakerTone: pitch={self.pitch}"
        if self.volume is not None:
            v_left,v_right = self.volume
            st += f" vol=({v_left:.1f},{v_right:.1f})"
        if self.dur is None:
            st += " dur=None"
        else:
            st +=  f" dur={self.dur:.3f}"
        if self.delay is not None:
            st += f" delay:{self.delay:.3f}"
        return st

class SpeakerWaveform:
    """ waveform to emit
    """
    
    def __init__(self, ndarr, dur, delay=None, sample_rate=None):
        """ setup waveform
        :ndarr: waveform (SinewaveNumPy stereo_waveform)
        :dur: wave max duration (seconds)
        :dly: delay(seconds) from start default: no delay
        :sample_rate: sample rate fps
        """
        self.ndarr = ndarr
        self.dur = dur
        self.delay = delay
        self.sample_rate = sample_rate
    
    def __str__(self):
        st = f"SpeakerWaveform: dur={self.dur}"
        if self.delay is not None:
            st += f" delay:{self.delay:.3f}"
        return st
    
class SpeakerControlCmd:
    """ Command to execute
    """

    def __init__(self, cmd_type=None, msg=None, msg_type=None,
                 tone=None, waveform=None, win=None, after=None):
        """ Setup command
        :cmd_type: command to execute
                "CMD_MSG" - speak message - msg REQUIRED
                "CMD_TONE" - make tone - tone REQUIRED
                "CMD_WAVEFORM - make wf waveform REQUIRED
                "CLEAR" - clear pending speech/tone
                "QUIT" - quit operation
        :msg: text to speak SpeakText
        :msg_type: type of message
                REPORT: std reporting
                CMD: command
                ECHO: echo of user input
            default: REPORT
        :tone: (SpeakerTone) tone to make
        :waveform: (SpeakerWaveform) waveform to play 
        :win: SpeakerControlLocal's window reference
        :after: function to call after cmd completion
                default: no call
        """
        self.cmd_id = SpeakerControl.new_id()
        self.cmd_type = cmd_type
                
        self.msg = msg
        self.msg_type = msg_type
        self.tone = tone
        self.waveform = waveform
        self.win = win
        self.after = after
        if after is not None:
            if win is None:
                raise SpeakerControlError(f"after missing win cmd:{self}")
        if cmd_type == "CMD_MSG":
            if msg is None:
                raise SpeakerControlError(f"msg missing with type MSG: {self}")
        if cmd_type == "CMD_TONE":
            if tone is None:
                raise SpeakerControlError(f"tone missing with type TONE: {self}")
        if cmd_type == "CMD_WAVEFORM":
            if waveform is None:
                raise SpeakerControlError(f"waveform missing with type WF: {self}")
        

    def __str__(self):
        ret = f"SpeakerControlCmd: {self.cmd_id} {self.cmd_type}"
        if self.msg is not None:
            ret += f" {self.msg}"
        if self.msg_type is not None:
            ret += f" {self.msg_type}"
        if self.tone is not None:
            ret += f" {self.tone}"
        if self.waveform is not None:
            ret += f" {self.waveform}"
        if self.after is not None:
            ret += f" win:{self.win} after:{self.after}"
        
        return ret

        
class SpeakerControl(Singleton):
    CMDS_SIZE = 150
    SOUND_SIZE = 150
    #SOUND_SIZE = 30        # To force filling
    cmd_id = 0
    
    @classmethod
    def new_id(cls):        # Thread safe ???  TBD
        cls.cmd_id += 1
        return cls.cmd_id
    
    def __init__(self, cmds_size=CMDS_SIZE, sound_size=SOUND_SIZE,
                 sample_rate=44100):
        """ Setup speaker control
        :cmds_size: general command queue size
        :sounc_size: pending sounds queue size
        :sample_rate: waveform presentation sample_rate
                    default: 44100 per second
        """
        self.cmds_size = cmds_size
        self.sound_size = sound_size
        self.sample_rate = sample_rate
        self._running = True        # Thread functions exit when cleared

        if got_pyttsx3:
            self.pyttsx3_engine = pyttsx3.init()
        else:
            SlTrace.lg("Can't init pyttsx3")

        self.psc = PlaySoundControl()
        self.sound_lock = threading.Lock()
        self.cmds_in_progress = {}   # cmd ins process by cmd_id
        self.sc_cmd_queue = queue.Queue(cmds_size)  # Command queue of SpeakerControlCmd
        self.sc_cmd_thread = threading.Thread(target=self.sc_cmd_proc_thread)
        self.sc_sound_queue = queue.Queue(sound_size)  # speech queue of SpeakerControlCmd 
        self.sc_sound_thread = threading.Thread(target=self.sc_sound_proc_thread)
        self.sc_sound_thread.start()
        self.sc_cmd_thread.start()
        self.sc_speech_busy = False     # True - iff speeking
        self.sc_tone_busy = False       # True - iff toneing

        
    def sc_cmd_proc_thread(self):
        """ speech maker command processing thread function
        """
        while self._running:
            
            cmd = self.sc_cmd_queue.get()
            SlTrace.lg(f"cmd: {cmd}", "speech")
            SlTrace.lg(f"cmd: {cmd}", "sound_queue")
            if cmd.cmd_type == "CMD_MSG":
                self.sc_sound_queue.put(cmd)
            elif cmd.cmd_type == "CMD_TONE":
                self.sc_sound_queue.put(cmd)
            elif cmd.cmd_type == "CMD_WAVEFORM":
                self.sc_sound_queue.put(cmd)
            elif cmd.cmd_type == "CLEAR":
                SlTrace.lg("Clearing speech")
                self.clear()
            elif cmd.cmd_type == "QUIT":
                self.clear()
                self.sc_sound_queue.put(cmd)
                self.quit()
            else:
                raise SpeakerControlError(f"Unrecognized SpeakerControl command {cmd}")
        SlTrace.lg("sc_cmd_proc_thread returning")

    def get_cmd_queue_size(self):
        """ Get current number of entries
        :returns: number of entries
        """
        return self.sc_cmd_queue.qsize()

    def get_sound_queue_max(self):
        """ Get current number of entries
        :returns: number of entries
        """
        return self.self.sound_size

    def get_sound_queue_size(self):
        """ Get current number of entries
        :returns: number of entries
        """
        return self.sc_sound_queue.qsize()
        
    def clear(self):
        """ Clear queue
        """
        SlTrace.lg("speech clearing")
        with self.sc_cmd_queue.mutex:
            self.sc_cmd_queue.queue.clear()
        SlTrace.lg(f"self.sc_cmd_queue.qsize(): {self.sc_cmd_queue.qsize()}")
        with self.sc_sound_queue.mutex:
            self.sc_sound_queue.queue.clear()
        SlTrace.lg(f"self.sc_sound_queue.qsize(): {self.sc_sound_queue.qsize()}")

    def clear_cmd_queue(self):
        while self.sc_cmd_queue.qsize() > 0:
            cmd = self.sc_cmd_queue.get()
            SlTrace.lg(f"removing cmd entry: {cmd}")

    def clear_sound_queue(self):
        while self.sc_sound_queue.qsize() > 0:
            cmd = self.sc_sound_queue.get()
            SlTrace.lg(f"removing speech queue entry: {cmd}")
            
    def force_clear(self):
        """ force Clear queue
        """
        SlTrace.lg("force speech clearing")
        self.clear_cmd_queue()
        SlTrace.lg(f"self.sc_cmd_queue.qsize(): {self.sc_cmd_queue.qsize()}")
        self.clear_sound_queue()
        SlTrace.lg(f"self.sc_sound_queue.qsize(): {self.sc_sound_queue.qsize()}")
        
        #if self.pyttsx3_engine.isBusy():
        #self.pyttsx3_engine.stop()
        #if self.pyttsx3_engine._inLoop:
        #    self.pyttsx3_engine.endLoop()
        #self.pyttsx3_engine = pyttsx3.init()

        #self.sound_lock.release()
    
    def is_busy(self):
        """ Check if if busy or anything is pending
        """
        
        if self.sc_speech_busy or self.sc_tone_busy:     # Fast check
            return True
        
        if self.get_cmd_queue_size() > 0:
            return True 

        if self.get_sound_queue_size() > 0:
            return True

        if self.sc_speech_busy or self.sc_tone_busy:     # Final check
            return True
        
        return False

    def is_in_progress(self, cmd_id):
        """ Check if cmd is still in progress
        :cmd_id: command  id
        """
        if cmd_id in self.cmds_in_progress:
            return True 
        
        return False 
    
    def sc_sound_proc_thread(self):
        """ Process pending speech requests (SpeakerControlCmd)
        """
        SlTrace.lg("sc_sounc_proc_thread running")
        while self._running:
            qsize = self.sc_sound_queue.qsize()
            SlTrace.lg(f"sound_queue {qsize}: BEFORE sc_sound_queue.get()", "sound_queue")
            buffer = 10
            space_left = self.sound_size - qsize
            if space_left < buffer:
                SlTrace.lg(f"Speech queue filling qsize:{qsize}"
                           f" of {self.sound_size}")
                while True:
                    qsize = self.sc_sound_queue.qsize()
                    space_left = self.sound_size - qsize
                    if space_left < 2*buffer:
                        cmd = self.sc_sound_queue.get()
                        SlTrace.lg(f"dropping {cmd}")
                    else:
                        break
                    
            cmd = self.sc_sound_queue.get()
            SlTrace.lg(f"speech queue: cmd: {cmd}", "sound_queue")
            if cmd.cmd_type == "CLEAR":
                continue
            elif cmd.cmd_type == "QUIT":
                self.pyttsx3_engine.stop()
                break

            elif cmd.cmd_type == "CMD_MSG":
                msg = cmd.msg
                msg_type = cmd.msg_type
                self.speak_text(msg, msg_type=msg_type)
                SlTrace.lg(f"sound_queue: cmd: {cmd} AFTER speak_text", "sound_queue")
            elif cmd.cmd_type == "CMD_TONE":
                self.play_tone(cmd.tone)
                SlTrace.lg(f"sound_queue: cmd: {cmd} AFTER play_tone", "sound_queue")
            elif cmd.cmd_type == "CMD_WAVEFORM":
                self.play_waveform(cmd.waveform)
                SlTrace.lg(f"sound_queue: cmd: {cmd} AFTER play_waveform", "sound_queue")
            else:
                raise SpeakerControlError(f"Unrecognized speaker cmd type:{cmd.cmd_type} in {cmd}")
            if cmd.after is not None:
                cmd_id = cmd.cmd_id
                if cmd.win is None:
                    raise SpeakerControlError(f"after missing win in cmd {cmd}")
                if cmd_id in self.cmds_in_progress:
                    del self.cmds_in_progress[cmd_id]
                
        SlTrace.lg("sc_sound_proc_thread returning")
            
    def quit(self):
        SlTrace.lg("SpeachMaker quitting")
        self.clear()
        self._running = False       # All our threads watch this
        self.sc_cmd_queue.put(SpeakerControlCmd(cmd_type="QUIT"))   # drop the wait
        self.sc_sound_queue.put(SpeakerControlCmd(cmd_type="QUIT"))   # drop the wait
        SlTrace.lg("Force threads stop")
        #self.sc_sound_thread.join()
        #self.sc_cmd_thread.join()

    def delay(self, dur):
        """ Wait for dur seconds
        :dur: duration seconds
        """
        self.delay_start(dur=dur)
        self.delay_wait()
        
    def delay_start(self, dur):
        """ Start delay
        :dur: duration in seconds
        """
        self._delay = SpeakerControlDelay(dur=dur)

    def delay_wait(self):
        """ wait till delay end
        """
        while not self._delay.is_end():
            time.sleep(.001) 
        
    def play_tone(self, tone):
        """ Called to play pending tone
        :tone: (SpeakerTone)
        """
        self.sc_tone_busy = True
        SlTrace.lg(f"play_tone: qsize: {self.get_sound_queue_size()}",
                    "sound_queue")
        try:                
            with self.sound_lock:
                vol_left,vol_right = tone.volume
                self.delay_start(tone.delay)
                sinewave_stereo = SineWaveNumPy(pitch = tone.pitch,
                    duration_s=tone.dur,
                    decibels_left=vol_left,
                    decibels_right=vol_right)
                self.delay_wait()
            sinewave_stereo.play()
            self.delay(dur=tone.dur)
            sinewave_stereo.stop()
            
        except Exception as e:
            SlTrace.lg("Bust out of play_tone")
            SlTrace.lg(f"Unexpected exception: {e}")
            SlTrace.lg("Printing the full traceback as if we had not caught it here...")
            SlTrace.lg(format_exception(e))
        self.sc_tone_busy = False
        
    def play_waveform(self, waveform):
        """ Called to play pending waveform
        :waveform: (SpeakerWaveform) waveform to play
        :dur: duration default: waveform.dur
        :sample_rate: sample rate default self.sample_rate
        """
        self.sc_tone_busy = True
        dur = waveform.dur
        sample_rate = waveform.sample_rate
        if sample_rate is None:
            sample_rate = self.sample_rate
        SlTrace.lg(f"play_waveform: qsize: {self.get_sound_queue_size()}",
                    "sound_queue")
        try:                
            with self.sound_lock:
                if waveform.delay is not None:
                    self.delay(waveform.delay)
                ts = time.time()
                sd.play(waveform.ndarr, sample_rate)
                self.delay(dur=dur)
                sd.stop()
                te = time.time()
                SlTrace.lg(f"play_waveform end tw=({te-ts:.3f})", "sound_time")
        except Exception as e:
            SlTrace.lg("Bust out of play_waveform")
            SlTrace.lg(f"Unexpected exception: {e}")
            SlTrace.lg("Printing the full traceback as if we had not caught it here...")
            SlTrace.lg(format_exception(e))
        self.sc_tone_busy = False
                
    def speak_text(self, msg, msg_type=None):
        """ Called to speak pending line
        
        """
        self.sc_speech_busy = True
        SlTrace.lg(f"speek_text: qsize: {self.get_sound_queue_size()}",
                    "speech")
        try:                
            with self.sound_lock:
                if self.pyttsx3_engine._inLoop:
                    SlTrace.lg("speak_text - in run loop - ignored")
                    self.pyttsx3_engine.endLoop()
                    self.sc_speech_busy = False
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
                        self.sc_speech_busy = False
                        return
                    
                    self.pyttsx3_engine.say(msg)
                    self.pyttsx3_engine.setProperty('rate', 240)
                    self.pyttsx3_engine.setProperty('volume', 0.9)
                    self.pyttsx3_engine.runAndWait()
                else:
                    raise SpeakerControlError(f"Unrecognized speech_type"
                                    f" {msg_type} {msg}")
        except:
            SlTrace.lg("Bust out of speak_text")
        self.sc_speech_busy = False

    def send_cmd(self, cmd_type='speak', msg=None, msg_type=None, tone=None,
                 waveform=None, win=None, after=None):
        """ Send cmd to speaker control engine
            storing hash of cmds in process
        :cmd_type: command type
                    'text'        - speak text
                    'tone'        - tone
                    'erase_queue' - erase/cancel pending speech/tones
                    'exit' - erase/cancel pending speech/tones and then stop engine
        :msg: message text, if any
        :msg_type: type of text
                'report'  - standard report
                'command' - a command
        :tone: SpeakerTone
        :waveform: waveform (SinewaveNumPy.stereo_waveform) NumPy array
        :win: SpeakerControlLocal's window reference
        :after: function to call after cmd completion
                default: no call
        :returns: cmd, cmd_id, after is needed but cmd is for documentation
        """
        SlTrace.lg(f"send_cmd:{cmd_type} msg: {msg} tone: {tone}", "sound_queue")
        cmd = SpeakerControlCmd(cmd_type=cmd_type, msg=msg, msg_type=msg_type,
                                 tone=tone, waveform=waveform,
                                 win=win, after=after)
        cmd_id = cmd.cmd_id
        self.cmds_in_progress[cmd_id] = cmd
        self.sc_cmd_queue.put(cmd)
        return cmd

            
class SpeakerControlLocal:
    """ Localinstance of SpeakerControl
    """

    def __init__(self, win, logging_sound=False):
        self.cmds_awaiting_after = {} # dictionary by cmd_id awaiting after
        self.awaiting_loop_ms = 1      # Awaiting loop
        self.awaiting_loop_going = False    # Checking loop in progress
        self.sc = SpeakerControl()
        self.win = win
        self.logging_sound = logging_sound
        self.make_silent(False)

    def get_sound_queue_max(self):
        """ Get current number of entries
        :returns: number of entries
        """
        return self.sc.get_sound_queue_max()

    def get_sound_queue_size(self):
        """ Get current number of entries
        :returns: number of entries
        """
        return self.sc.get_sound_queue_size()

    def make_silent(self, val=True):
        self._silent = val

    def clear(self):
        """ Clear pending output
        """
        self.sc.clear()

    def get_cmd_queue_size(self):
        """ Get current number of entries
        :returns: number of entries
        """
        return self.sc.get_cmd_queue_size()

    def get_sound_queue_size(self):
        """ Get current number of entries
        :returns: number of entries
        """
        return self.sc.get_sound_queue_size()

    def is_busy(self):
        """ Check if if busy or anything is pending
        """
        return self.sc.is_busy()

    def wait_while_busy(self):
        while self.is_busy():
            self.win.update()
                    
    def quit(self):    
        self.sc.quit()

    def play_tone(self, pitch, dur=None, volume=None, dly=None):
        """ play tone
        :pitch: tone pitch
        :dur: tone duration
        :volume: (left,right) decibels
        :dly: delay(seconds) from start default: no delay
        """
        tone = SpeakerTone(pitch=pitch, dur=dur, volume=volume)
        SlTrace.lg(f"play_tone tone: {tone}")
        self.sc.send_cmd(cmd_type="CMD_TONE", tone=tone)
        
    def play_waveform(self, ndarr, dur=None, dly=None,
                               sample_rate=None,
                               after=None):
        """ play waveform
        :ndarr: waveform (SinewaveNumPy stereo_waveform)
        :dur: wave max duration (seconds)
        :dly: delay(seconds) from start default: no delay
        :sample_rate: sample rate fps
        :after: function to call after play completes
                 (self.win.after(0,after)
                default: no call
        """
        waveform = SpeakerWaveform(ndarr=ndarr, dur=dur, delay=dly,
                              sample_rate=sample_rate)
        SlTrace.lg(f"play_waveform waveform: {waveform}", "sound_queue")
        cmd = self.sc.send_cmd(cmd_type="CMD_WAVEFORM", waveform=waveform,
                         win=self.win, after=after)
        if after is not None:
            self.add_awaiting(cmd)

    def add_awaiting(self, cmd):
        """ Add cmds awaiting after calls
            start waiting loop if necessary
        :cmd: cmd sent
        """
        self.cmds_awaiting_after[cmd.cmd_id] = cmd
        if not self.awaiting_loop_going:
            self.awaiting_loop_going = True
            self.win.after(0, self.awaiting_after_ck)

    def awaiting_after_ck(self):
        """ Check cmds awaiting for after cking
        """
        self.awaiting_loop_going = False    # Set True if more needed
                                            # Delete in order
        cmd_ids  = sorted(list(self.cmds_awaiting_after))   # So we can delete in loop
        for cmd_id in cmd_ids:
            if cmd_id in self.cmds_awaiting_after:
                cmd = self.cmds_awaiting_after[cmd_id]
                if not self.sc.is_in_progress(cmd_id):
                    SlTrace.lg(f"{cmd_id}: after_called for {cmd}", "sound_queue")
                    self.win.after(0, cmd.after)
                    del self.cmds_awaiting_after[cmd_id]
        if len(self.cmds_awaiting_after) > 0:
            self.awaiting_loop_going = True
            self.win.after(self.awaiting_loop_ms, self.awaiting_after_ck)
                
    def speak_text(self, msg, dup_stdout=True,
                   msg_type="REPORT"):
        """ Speak text, if possible else write to stdout
        :msg: text message, iff speech
        :dup_stdout: duplicate to stdout default: True
        :nsg_type: type of speech default: 'REPORT'
            REPORT - standard reporting
            CMD    - command
            ECHO - echo user input
        """
        if self.logging_sound:
            SlTrace.lg(msg)
        text_lines = msg.split("\n")
        for text_line in text_lines:
            if not self._silent:
                self.sc.send_cmd(cmd_type="CMD_MSG", msg=text_line, msg_type=msg_type)
        if dup_stdout and not self.logging_sound:
            SlTrace.lg(msg)

    def speak_text_stop(self):
        """ Stop pending speech
        """
        self.sc.force_clear()
        
            
if __name__ == "__main__":
    from audio_draw_window import AudioDrawWindow
    
    SlTrace.setFlags("speech")
    awin = AudioDrawWindow()
    scl = SpeakerControlLocal(win=awin)
    scl.speak_text("Hello World!")
    scl.speak_text("How are you?")
    scl.speak_text("Hows the weather?")
    scl.speak_text("What's up?")
    time.sleep(3)
    scl.clear()
    scl.speak_text("Just cleared")
    time.sleep(10)
    awin.mainloop()
    time.sleep(4)
