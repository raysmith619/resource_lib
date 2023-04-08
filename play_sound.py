# play_sound.py    31Mar2023  crs, extract to move to speaker_control

import datetime
from select_trace import SlTrace
try:
    from sinewave_numpy import SineWaveNumPy
    has_sinewave = True 
except:
    has_sinewave = False 

class PlaySound:
    """ particular sound to be played
    """

    @classmethod
    def pskey(cls, pitch, volume):
        """ Get unique resource key for possible reuse of SineWaveNumPy still needed???
        :pitch: sound pitch
        :volume: sound volume decibel if  not tuple then (volume,volume)
        :returns: unique resource key
        """
        if type(volume) != tuple:
            volume = (volume,volume)
        return (pitch,volume)
    
    def __init__(self, psc, pitch, dur=None,
                 volume=None, pskey=None):
        """ Setup sound to play
        :psc: controler
        :pitch: pitch to play
        :dur: duration of play (msec) default:psc.dur_base
        :volume: stereo volume to play (decibels) default:psc.volume_base
        :pskey: unique key  for PlaySound resource default: see pskey()
        """
        self.psid = psc.new_id() # Store unique id
        
        if volume is None:
            volume = psc.volume 
        if dur is None:
            dur = psc.dur
        self.psc = psc
        self.pitch = pitch
        self.time_play_start = None      # Play start time, if any 
        self.time_play_stop = None       # Play stop time, if any
        if dur is None:
            dur = psc.dur
        self.dur = dur
        if not isinstance(dur, (int, float)):
            SlTrace.lg(f"bad type for dur {self.dur}:{type(self.dur)}")
            dur  = .2
        if type(volume) != tuple:
            volume = (volume,volume)
        self.volume = volume
        volume_left,volume_right = volume
        self.waveform_stereo = SineWaveNumPy(pitch=pitch, decibels_left=volume_left,
                                      decibels_right=volume_right)
        if pskey is None:
            pskey = self.pskey(pitch,volume)
        self.pskey = pskey
        SlTrace.lg(f"New : {self}", "sound")

    def __str__(self):
        """ String instance for pretty printing
        """
        st = f"PlaySound[{self.psid}]:"
        st += f" pitch:{self.pitch}" 
        st += f" dur:{self.dur}"
        st += f" volume:{self.volume}"
        st += f" pskey:{self.pskey}"
        return st 

    def update_id(self):
        """ Update id for reuse
        """
        PlaySound.g_psid += 1
        self.psid = self.g_psid
        SlTrace.lg(f"Reusing PlaySound: {self}")
          
    def play(self, dur=None, dly=None):
        """ Play/replay sound for duration
        :dur: play duration default: initial duration (msec)
        :dly: delay (silence) before sound
        """
        self.update()
        if dur is None:     # Setup for delayed
            dur = self.dur
        if not isinstance(dur, (int, float)):
            self.waveform_stereo.stop()
            SlTrace.lg(f"bad type for dur {self.dur}:{type(self.dur)}")
            pass
        self.dur = dur
        self.is_active = True
        if dly is not None and dly != 0:
            SlTrace.lg(f"delaying play: dly:{dly} {self}", "sound")
            self.psc.awin.canvas.after(dly, self.play_sound)
            self.update()
            return
        
        self.play_it()
        
    def play_it(self):
        """ direct play
        """
        SlTrace.lg(f"play( ps:{self}", "sound")
        self.time_play_start = datetime.datetime.now()
        self.time_play_stop = None
        self.waveform_stereo.play()
        if not isinstance(self.dur, (int, float)):
            SlTrace.lg(f"bad type for self.dur {self.dur}:{type(self.dur)}")
            self.waveform_stereo.stop()
            return
        
        
        self.update()        
        
    def play_sound(self):
        """ Play sound now, possibly delayed
        """
        self.play_it()
         
    def play_stop(self):
        """ Stop playing - called after duration of play
        """
        if not self.is_active:
            return 
        self.time_play_stop = datetime.datetime.now()
        play_dur = (self.time_play_stop - self.time_play_start).total_seconds()
        SlTrace.lg(f"play_stop play_dur:{play_dur:.3} ps:{self}", "sound")
        self.waveform_stereo.stop()
        self.psc.free_ps(self)     # Release resource - put on available list

    def update(self):
        self.psc.update()
    
    def update_pending(self):
        """ Update pending events
        """
        self.psc.update_pending()
