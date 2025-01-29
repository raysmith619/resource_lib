# wx_speaker_control.py    24Oct2023  crs, Author
"""
Support thread safe non-blocking speaker control:
    1. text to speech encapsulation of pyttsxN facilitating
     talk from multiple AudioDrawWindow sources
    2. tone playing using SineWaveNumPy, audio-sounddevice
    3. Using wxPython utilities for time control
    4. Using PyttsxProc for speech to text
    
"""
import threading
import queue
import time
import wx

import sounddevice as sd

from format_exception import format_exception
from select_trace import SlTrace, SelectError
from wx_play_sound_control import PlaySoundControl
from sinewave_numpy import SineWaveNumPy

from pyttsx_proc import PyttsxProc
from speech_maker_cmd import SpeechMakerCmd



class SpeakerControlError(SelectError):
    pass

class SpeakerControlDelay:
    """ Delay info
    """
    def __init__(self, sc, dur):
        """ Start delay
        :sc: speaker control instance
        :dur: duration seconds
        """
        self.sc = sc
        self.dur = dur
        self.start = time.time()
        self.end = self.start + self.dur
        self.waiting = True 
        
    def is_end(self):
        """ Check if time is up
        :returns: True if at or past end
        """
        now = time.time()
        if not self.waiting or now > self.end:
            return True 
        
        return False

    def stop(self):
        """ Stop delay (set as over)
        """
        self.waiting = False

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
        if volume is None:
            SlTrace.lg("SpeakerTone volume={volume}, treat as 0,0")
            volume = (0,0)
        self.volume = volume
        if dur is None:
            SlTrace.lg(f"SpeakerTone dur is {dur} treat as .1")
            dur = .1
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
    
    def __init__(self, ndarr, dur,
                 calculate_dur=None, delay=None, sample_rate=None):
        """ setup waveform
        :ndarr: waveform (SinewaveNumPy stereo_waveform)
        :dur: wave max duration (seconds)
        :calculate_dur: calculate duration based on waveform and sample_rate
        :dly: delay(seconds) from start default: no delay
        :sample_rate: sample rate fps
        """
        self.ndarr = ndarr
        self.dur = dur
        self.calculate_dur = calculate_dur
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
                 rate=None, volume=None,
                 tone=None, waveform=None, fr=None, after=None):
        """ Setup command
        :cmd_type: command to execute
                "CMD_MSG" - speak message - msg REQUIRED
                "CMD_SPEAK_TEXT_STOP" - stop current/pending text speech
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
        :rate: speach rate WPM
        :volume: speach volume
        :tone: (SpeakerTone) tone to make
        :waveform: (SpeakerWaveform) waveform to play 
        :fr: SpeakerControlLocal's window reference
        :after: function to call after cmd completion
                default: no call
        """
        self.cmd_id = SpeakerControl.new_id()
        self.cmd_type = cmd_type
                
        self.msg = msg
        self.msg_type = msg_type
        self.rate = rate
        self.volume = volume
        self.tone = tone
        self.waveform = waveform
        self.fr = fr
        self.after = after
        if after is not None:
            if fr is None:
                ###wxport###raise SpeakerControlError(f"after missing fr cmd:{self}")
                pass
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
            ret += f" fr:{self.fr} after:{self.after}"
        
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
        :simple_speaker: For Debugging/Test
                True - avoid multiprocessing/threading to aboid freeze problems
                default: False
        """
        self.pyttsx_proc  = PyttsxProc()
        self.cmds_size = cmds_size
        self.sound_size = sound_size
        self.sample_rate = sample_rate
        self.vol_adj = 0.0      # Central volume adjustment factor
        self.start_control()
        
    def start_control(self):
        """ Start / Restart control
        """
        self._running = True        # Thread functions exit when cleared
        self.sc_busy = False        # True -> control busy
                                    # to replace other busys
        self.forced_clear = False   # set on force_clear, checked on waiting...
        self.sound_busy = False     # Set True if active or pending

        self.psc = PlaySoundControl()
        self.sound_lock = threading.Lock()
        self.cmds_in_progress = {}   # cmd ins process by cmd_id
        self.sc_cmd_queue = queue.Queue(self.cmds_size)  # Command queue of SpeakerControlCmd
        self.sc_cmd_thread = threading.Thread(target=self.sc_cmd_proc_thread)
        self.sc_sound_queue = queue.Queue(self.sound_size)  # speech queue of SpeakerControlCmd 
        self.sc_sound_thread = threading.Thread(target=self.sc_sound_proc_thread)
        self.sc_sound_thread.start()
        self.sc_cmd_thread.start()
        self.sc_tone_busy = False       # True - iff toneing

        
    def sc_cmd_proc_thread(self):
        """ speech maker command processing thread function
        """
        while not self.forced_clear and self._running:            
            cmd = self.sc_cmd_queue.get()
            SlTrace.lg(f"cmd: {cmd}", "speech")
            SlTrace.lg(f"cmd: {cmd}", "sound_queue")
            if cmd.cmd_type == "CMD_MSG":
                SlTrace.lg(f"CMD_MSG: {cmd}", "CMD_MSG")
                self.sc_sound_queue.put(cmd)
            elif cmd.cmd_type == "CMD_STOP_SPEAK_TEXT":
                self.stop_speak_text()            
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

    def get_vol_adj(self):
        """ Get current volume adjustment
        :returns: current vol_adjustment in db
        """
        return self.vol_adj

    def report_vol_adj(self):
        SlTrace.lg(f"vol_adj: {self.vol_adj}")

    def set_vol_adj(self, adj=0.0):
        """ Set volume adjustment
        :adj: db adjustment default:0.0
        """
        self.vol_adj = adj
        self.report_vol_adj()
        
    def clear(self):
        """ Clear queue
        """
        SlTrace.lg("speech clearing")
        sd.stop()
        self.clear_cmd_queue()
        SlTrace.lg(f"self.sc_cmd_queue.qsize(): {self.sc_cmd_queue.qsize()}")
        self.clear_sound_queue()
        SlTrace.lg(f"self.sc_sound_queue.qsize(): {self.sc_sound_queue.qsize()}")
        self.sc_speech_busy = False 
        self.sc_tone_busy = False
        self.sound_busy = False
    
    def stop_scan(self):
        """ Stop current scan
        """
        self.clear()
    
    def stop_speak_text(self):
        """ Stop current and pending text speach
        """
        self.pyttsx_proc.clear()
        

    def clear_cmd_queue(self):
        while self.sc_cmd_queue.qsize() > 0:
            cmd = self.sc_cmd_queue.get()
            SlTrace.lg(f"removing cmd entry: {cmd}")

    def clear_sound_queue(self):
        while self.sc_sound_queue.qsize() > 0:
            cmd = self.sc_sound_queue.get()
            SlTrace.lg(f"removing speech queue entry: {cmd}")
            
    def force_clear(self):
        """ force Clear
        :restart: restart controller after a short wait
        """
        SlTrace.lg("force speech clearing")
        self.clear_cmd_queue()
        SlTrace.lg(f"self.sc_cmd_queue.qsize(): {self.sc_cmd_queue.qsize()}")
        self.clear_sound_queue()
        SlTrace.lg(f"self.sc_sound_queue.qsize(): {self.sc_sound_queue.qsize()}")
        sd.stop()                   # Stop waveform
        self.forced_clear = True        # stoping waits...

        #if self.pyttsxN_engine.isBusy():
        #self.pyttsxN_engine.stop()
        #if self.pyttsxN_engine._inLoop:
        #    self.pyttsxN_engine.endLoop()
        #self.pyttsxN_engine = pyttsxN.init()

        #self.sound_lock.release()
        self.sc_speech_busy = False 
        self.sc_tone_busy = False

    def force_clear_reset(self):
        self.sc_forced_clear = False 

            
    def busy_parts(self):
        """ Check if if busy parts
        """
        if self.pyttsx_proc.is_busy() or self.sc_tone_busy:     # Fast check
            return True
        
        if self.get_cmd_queue_size() > 0:
            return True
         
        if self.get_sound_queue_size() > 0:
            return True
        
        return False

            
    def is_busy(self):
        """ Check if if busy or anything is pending
        """
        if self.sc_busy or self.busy_parts():
            self.sc_busy = self.busy_parts()
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
        SlTrace.lg("sc_sounc_proc_thread running", "sound")
        #while not self.forced_clear and self._running:
        while True:
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
            
            self.sound_busy = True  # Busy till complete
                                    # Avoid hazard of empty queue
                                    # and no active sound        
            cmd = self.sc_sound_queue.get()
            SlTrace.lg(f"speech queue: cmd: {cmd}", "sound_queue")
            if cmd.cmd_type == "CLEAR":
                continue
            elif cmd.cmd_type == "QUIT":
                self.pyttsx_proc.quit()
                break

            elif cmd.cmd_type == "CMD_MSG":
                msg = cmd.msg
                msg_type = cmd.msg_type
                self.speak_text(msg, msg_type=msg_type,
                                rate=cmd.rate, volume=cmd.volume)
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
                if cmd.fr is None:
                    ###wxportraise SpeakerControlError(f"after missing fr in cmd {cmd}")
                    pass
                if cmd_id in self.cmds_in_progress:
                    del self.cmds_in_progress[cmd_id]
                
        SlTrace.lg("sc_sound_proc_thread returning")
            
    def quit(self):
        SlTrace.lg("SpeakerControl quitting")
        self.clear()
        self._running = False       # All our threads watch this
        self.sc_cmd_queue.put(SpeakerControlCmd(cmd_type="QUIT"))   # drop the wait
        self.sc_sound_queue.put(SpeakerControlCmd(cmd_type="QUIT"))   # drop the wait
        SlTrace.lg("Force threads stop")
        #self.sc_sound_thread.join()
        #self.sc_cmd_thread.join()

    def delay_for(self, dur):
        """ Wait for dur seconds
        :dur: duration seconds
        """
        self.delay_start(dur=dur)
        self.delay_wait()
        
    def delay_start(self, dur):
        """ Start delay
        :dur: duration in seconds
        """
        self._delay = SpeakerControlDelay(self, dur=dur)

    def delay_wait(self):
        """ wait till delay end
        """
        while not self._delay.is_end():
            time.sleep(.001) 
        
    def play_tone(self, tone):
        """ Called to play pending tone
        :tone: (SpeakerTone) tuple left,right or monoral
        """
        if type(tone.volume) != tuple:
            tone.volume = (tone.volume,tone.volume)
            
        self.sc_tone_busy = True
        SlTrace.lg(f"play_tone: qsize: {self.get_sound_queue_size()}",
                    "sound_queue")
        try:                
            with self.sound_lock:
                vol_left,vol_right = tone.volume
                self.delay_start(tone.delay)
                stereo_waveform = SineWaveNumPy(pitch = tone.pitch,
                    duration=tone.dur,
                    decibels_left=vol_left,
                    decibels_right=vol_right)
                self.delay_wait()
            stereo_waveform.play()
            self.delay_for(dur=tone.dur)
            stereo_waveform.stop()
            
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
        :sample_rate: sample rate default: waveform.sample_rate,
                                           else: self.sample_rate
        """
        self.sc_tone_busy = True
        dur = waveform.dur
        sample_rate = waveform.sample_rate
        if sample_rate is None:
            sample_rate = self.sample_rate
        if dur is None or waveform.calculate_dur:
            wf_shape = waveform.ndarr.shape
            wf_len = wf_shape[0]
            dur = wf_len/sample_rate
        SlTrace.lg(f"play_waveform: len:{wf_len} dur: {dur}",
                    "sound_time")
        try:                
            with self.sound_lock:
                if waveform.delay is not None:
                    self.delay_for(waveform.delay)
                ts = time.time()
                sd.play(waveform.ndarr, sample_rate)
                self.delay_for(dur=dur)
                sd.stop()
                te = time.time()
                SlTrace.lg(f"play_waveform end tw=({te-ts:.3f})", "sound_time")
        except Exception as e:
            SlTrace.lg("Bust out of play_waveform")
            SlTrace.lg(f"Unexpected exception: {e}")
            SlTrace.lg("Printing the full traceback as if we had not caught it here...")
            SlTrace.lg(format_exception(e))
        self.sc_tone_busy = False
                
    def speak_text(self, msg, msg_type=None,
                   rate=240, volume=.9):
        """ Called to speak pending line
        :msg: text of message
        :mst_type: default: REPORT
        :rate: speech rate words per minute
                default: 240
        :volume: volume default: .9
        
        """
        SlTrace.lg(f"sc: speek_text: qsize: {self.get_sound_queue_size()}",
                    "speech")
        
        if msg_type is None:
            msg_type = "REPORT"
        SlTrace.lg(f"""sc: speak_text(msg={msg}, msg_type={msg_type},"""
                   f""" rate={rate}, volume={volume})""", "speak_text")
        cmd = SpeechMakerCmd(msg=msg, msg_type=msg_type,
                 rate=rate, volume=volume)
        self.pyttsx_proc.make_cmd(cmd)

    def send_cmd(self, cmd_type='speak', msg=None, msg_type=None,
                 rate=None, volume=None, tone=None,
                 waveform=None, fr=None, after=None):
        """ Send cmd to speaker control engine
            storing hash of cmds in process
            Sets self.sc_busy True, which is cleared
            when speech and tone are complete/idle
            and all queues are empty
        :cmd_type: command type
                    'text'        - speak text
                    'tone'        - tone
                    'erase_queue' - erase/cancel pending speech/tones
                    'exit' - erase/cancel pending speech/tones and then stop engine
        :msg: message text, if any
        :msg_type: type of text
                'report'  - standard report
                'command' - a command
        :rate: speaking rate for speech
        :volume: speaking volume for speech
        :tone: SpeakerTone
        :waveform: waveform (SinewaveNumPy.stereo_waveform) NumPy array
        :fr: SpeakerControlLocal's window reference
        :after: function to call after cmd completion
                default: no call
        :returns: cmd, cmd_id, after is needed but cmd is for documentation
        """
        self.sc_busy = True
        SlTrace.lg(f"send_cmd:{cmd_type} msg: {msg} tone: {tone}", "sound_queue")
        cmd = SpeakerControlCmd(cmd_type=cmd_type, msg=msg,
                                 msg_type=msg_type,
                                 rate=rate, volume=volume,
                                 tone=tone, waveform=waveform,
                                 after=after)
        cmd_id = cmd.cmd_id
        self.cmds_in_progress[cmd_id] = cmd
        self.sc_cmd_queue.put(cmd)
        return cmd

class SimpleSpeakerControl():
    """ Simple speaker control for distributed operation
    Mostly for debugging/testing
    """

    def __init__(self):
        self.simple_speaker = True

    def get_cmd_queue_size(self):
        return 0
        
    def is_busy(self):
        return False
    
    def quit(self):
        return
    
    def clear(self):
        return
    
    def send_cmd(self, cmd_type='speak', msg=None, msg_type=None,
                 rate=None, volume=None, tone=None,
                 waveform=None, fr=None, after=None):
        """ Stub out major cmd processing
        """

    def get_sound_queue_size(self):
        return 0
        
    def get_vol_adj(self):
        return 0
    
    def busy_parts(self):
        return False

    def get_sound_queue_size(self):
        """ Get current number of entries
        :returns: number of entries
        """
        return self.sc.get_sound_queue_size()
    
    

            
            
class SpeakerControlLocal:
    """ Localinstance of SpeakerControl
    """

    def __init__(self, logging_sound=False, simple_speaker=False):
        self.make_silent(False)
        self.logging_sound = logging_sound
        self.simple_speaker = simple_speaker
        if simple_speaker:
            self.sc = SimpleSpeakerControl()
            return
        
        self.cmds_awaiting_after = {} # dictionary by cmd_id awaiting after
        self.awaiting_loop_ms = 1      # Awaiting loop
        self.awaiting_loop_going = False    # Checking loop in progress
        self.sc = SpeakerControl()      # NOTE: no simple_speaker arg

    def get_sound_queue_max(self):
        """ Get maximum number of entries
        :returns: max number of entries
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
        self.clear_awaiting()

    def force_clear(self, restart=False):
        """ Clear pending output
        """
        SlTrace.lg("force_clear")
        self.sc.force_clear()
        rwait = 2000
        if restart:
            SlTrace.lg(f"Waiting {rwait} msec")
            wx.CallLater(rwait, self.sc.start_control)

    def get_cmd_queue_size(self):
        """ Get current number of entries
        :returns: number of entries
        """
        return self.sc.get_cmd_queue_size()

    def get_vol_adj(self):
        """ Get current volume adjustment ??? Thread Safe ???
        :returns: current vol_adjustment in db
        """
        return self.sc.get_vol_adj()

    def is_busy(self):
        """ Check if if busy or anything is pending
        """
        return self.sc.is_busy()

    def wait_while_busy(self):
        while self.sc.busy_parts():
            pass    ###wxport###
            
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
        SlTrace.lg(f"play_tone tone: {tone}", "play_tone")
        self.sc.send_cmd(cmd_type="CMD_TONE", tone=tone)
        
    def play_waveform(self, ndarr, dur=None, dly=None,
                               sample_rate=None,
                               calculate_dur=False,
                               after=None):
        """ play waveform
        :ndarr: waveform (SinewaveNumPy stereo_waveform)
        :dur: wave max duration (seconds)
        :dly: delay(seconds) from start default: no delay
        :sample_rate: sample rate fps
        :calculate_dur:    # calculate duration based on waveform, sample_rate
        :after: function to call after play completes
                 (self.wx_win.after(0,after)
                default: no call
        """
        waveform = SpeakerWaveform(ndarr=ndarr, dur=dur, delay=dly,
                                   calculate_dur=calculate_dur,
                                   sample_rate=sample_rate)
        SlTrace.lg(f"play_waveform waveform: {waveform}", "sound_queue")
        cmd = self.sc.send_cmd(cmd_type="CMD_WAVEFORM", waveform=waveform,
                         after=after)
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
            wx.CallAfter(self.awaiting_after_ck)

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
                    wx.CallAfter(cmd.after)
                    del self.cmds_awaiting_after[cmd_id]
        if len(self.cmds_awaiting_after) > 0:
            self.awaiting_loop_going = True
            wx.CallLater(self.awaiting_loop_ms, self.awaiting_after_ck)

    def clear_awaiting(self):
        """ Clear out awaiting, calling all awaiting
        """
        self.awaiting_loop_going = False
        if self.simple_speaker:
            return
        
        cmd_ids  = sorted(list(self.cmds_awaiting_after))   # So we can delete in loop
        for cmd_id in cmd_ids:
            if cmd_id in self.cmds_awaiting_after:
                cmd = self.cmds_awaiting_after[cmd_id]
                SlTrace.lg(f"{cmd_id}: after_called for {cmd}", "sound_queue")
                wx.CallAfter(cmd.after)
                del self.cmds_awaiting_after[cmd_id]
                        
    def speak_text(self, msg, dup_stdout=True,
                   msg_type=None,
                   rate=None, volume=None):
        """ Speak text, if possible else write to stdout
        :msg: text message, iff speech
        :dup_stdout: duplicate to stdout default: True
        :msg_type: type of speech default: 'REPORT'
            REPORT - standard reporting
            CMD    - command
            ECHO - echo user input
        :rate: speech rate words per minute
                default: 240
        :volume: volume default: .9
            
        """
        if msg_type is None:
            msg_type = "REPORT"
        if self.logging_sound:
            SlTrace.lg(msg)
        text_lines = msg.split("\n")
        for text_line in text_lines:
            if not self._silent:
                self.sc.send_cmd(cmd_type="CMD_MSG", msg=text_line,
                                  msg_type=msg_type,
                                  rate=rate, volume=volume)
        if dup_stdout and not self.logging_sound:
            SlTrace.lg(msg)

    def stop_speak_text(self):
        """ Stop pending speech
        """
        self.sc.send_cmd(cmd_type="CMD_STOP_SPEAK_TEXT")

    def stop_scan(self):
        """ Stop current scan
        """
        self.sc.stop_scan()
        self.stop_speak_text()    

if __name__ == "__main__":
    import os
    import time
    import multiprocessing
    multiprocessing.freeze_support()
    from wx_win import WxWin
    adw = None
    wx_win = WxWin(adw, "wx_speaker_control Self Test")
    for simple_speaker in [True, False]:
        SlTrace.lg(f"simple_speaker: {simple_speaker}")
        SlTrace.setFlags("speech,sound_queue")
        scl = SpeakerControlLocal(simple_speaker=simple_speaker)
        scl.wait_while_busy()
        long_msg = """
        line one
        line two
        line three
        line four
        line five
        line six
        line seven
        line eight
        line nine
        line ten
        """
        long_msg_group = long_msg.split("\n")
        for msg in ["one"]:
            scl.speak_text(msg)
            time.sleep(1)
            scl.wait_while_busy()

            scl.speak_text(long_msg)
            scl.wait_while_busy()
            
            scl.speak_text("Hello World!")
            scl.wait_while_busy()
            scl.speak_text("How are you?")
            scl.wait_while_busy()
            scl.speak_text("Hows the weather?")
            scl.wait_while_busy()
            scl.speak_text("What's up?")
            time.sleep(3)
            scl.clear()
            scl.speak_text("Just cleared")
            time.sleep(2)
            scl.wait_while_busy()
