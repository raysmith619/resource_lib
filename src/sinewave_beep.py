# sinewave_beep.py    26Jan2023  crs, encapsulate pysinewave
from select_trace import SlTrace
try:
    from pysinewave import SineWave
    has_sinewave = True 
except:
    has_sinewave = False 

class PlaySound:
    """ particular sound to be played
    """
    def __init__(self, swb, pitch, dur=None, volume=None):
        """ Setup sound to play
        :swb: calling instance of SineWaveBeep
        :pitch: pitch to play
        :dur: duration of play (msec) default:swb.dur_base
        :volume: volume to play (decibels) default:swb.volume_base
        """
        self.swb = swb
        self.pitch = pitch
        self.dur = dur
        self.volume = volume
        self.sinewave = SineWave(pitch=pitch)
        
    def play(self, dur=None, volume=None, dly=None):
        """ Play/replay sound for duration
        :dur: play duration default: initial duration (msec)
        :dly: delay (silence) before sound
        """
        if dly is not None:
            if dur is not None:     # Setup for delayed
                self.dur = dur
            if volume is not None:
                self.volume = volume
            SlTrace.lg(f"delayed: play(pitch: {self.pitch} dly:{dly}", "sound")
            self.is_active = True
            self.swb.awin.canvas.after(dly, self.play_sound)
            return
            
        if dur is None:
            dur = self.dur
        if volume is None:
            volume = self.volume
        self.sinewave.set_volume(volume)
        self.sinewave.play()
        self.is_active = True
        SlTrace.lg(f"play(pitch:{self.pitch} dur={dur} volume:{volume}", "sound")
        self.swb.awin.canvas.after(dur, self.play_stop)

    def play_sound(self):
        """ Play sound now, possibly delayed
        """
        self.play()
         
    def play_stop(self):
        """ Stop playing - called after duration of play
        """
        if not self.is_active:
            return 
        
        self.sinewave.stop()
        SlTrace.lg(f"play_stop pitch={self.pitch}", "sound")
        self.is_active = False 
        
class SineWaveBeep:
        

    cp = 0      # Base pitch
    cpsp = 3    #  pitch color spacing
    dur_base = 200  # Base duration (msec)
    dly_between = dur_base//3   # between cells
    dur_blank = dur_base
    pitch_blank = cp-1
    pitch_on_edge = cp+12
    pitch_warning = cp+13
    volume_base = 0     # Base volume in decibles
    
    color_pitches = {
        "OTHER" : cp-2*cpsp,
        "BLANK" : cp-2*cpsp,
        "red" : cp+1*cpsp,
        "orange" : cp+2*cpsp,
        "yellow" : cp+3*cpsp,
        "green" : cp+4*cpsp,
        "blue" :  cp+5*cpsp,
        "indigo" : cp+6*cpsp,
        "violet" : cp+7*cpsp,
        "black" : cp+8*cpsp,
        "white" : cp+9*cpsp,
        "gray" : cp+10*cpsp,
        }



    def __init__(self, awin, silence_checker=None):
        self.awin = awin
        self._silence_checker = silence_checker
        self.has_sinewave = has_sinewave
        self.play_sound_running = {}     # currently playing
        self.play_sound_available = {}   # stopped - avail
        if not self.has_sinewave:
            SlTrace.lg("pysinewave not present - use winsound")
            return
        
        self.sinewave_warn = SineWave(pitch=self.pitch_warning)
        

    def announce(self, msg, val=None):
        """ Announce
        """
        SlTrace.lg(f"announce {msg}")
        if msg == "can not do":
            self.play_sound(pitch=self.pitch_warning)
        elif msg == "on edge":
            self.play_sound(pitch=self.pitch_on_edge)


    def silence(self):
        """ Check if we are silenced
        """
        if self._silence_checker is None:
            return False 
        
        if self._silence_checker():
            return True    # We're silent
       
        return False    # We make noise 
            
    def on_edge(self):
        if self.silence():
            return
        
        self.play_sound(pitch=self.pitch_on_edge) 
        
    def announce_pcells(self, pc_ixys, dur=None):
        """ Anounce what we're up against
        200 ms first cell, 100 ms second cell 50 ms
        :pc_ixys: list of possible cells ixy
        :dur: max duration of beep default: 200 
        """
        if dur is None:
            dur = self.dur_base
        for pc_ixy in pc_ixys:
            self.announce_pcell(pc_ixy, dur)
            ###dur //= 2

    def announce_next_pcell(self, pc_ixy,dur=None, dly=None):
        """ Announce next cell
        :pc_ixy: (ix,iy) of next cell
        """
        if dur is None:
            dur = self.dur_base
        if dly is None:
            dly = self.dly_between
        self.announce_pcell(pc_ixy=pc_ixy,
                             dur=dur,
                             dly=dly)

    def announce_next_pcells(self, pc_ixys, dur=None, dly=None):
        """ Announce next cell
        :pc_ixy: (ix,iy) of next cell
        :dly: delay before each cell default: self.dly_between
        """
        if dur is None:
            dur = self.dur_base
        if dly is None:
            dly = self.dly_between
        for pc_ixy in pc_ixys:
            self.announce_pcell(pc_ixy=pc_ixy,
                                 dur=dur,
                                 dly=dly)
        
    def announce_pcell(self, pc_ixy, dur=None, dly=None):
        """ Announce cell
        :dly: delay before the sound
        """
        if self.silence():
            return
        if dur is None:
            dur = self.dur_base
        cell = self.awin.get_cell_at_ixy(pc_ixy)
        if cell is not None:
            color = cell._color
            if color not in self.color_pitches:
                pitch = self.color_pitches["OTHER"]
                dur = self.dur_other
                SlTrace.lg(f"color:{color} pitch:{pitch} dur:{dur}",
                            "pos_tracking")
            else:
                pitch = self.color_pitches[color]
            self.play_sound(pitch=pitch, dur=dur, dly=dly)
            SlTrace.lg(f"in cell: winsound.Beep({pitch},{dur})"
                       f" cell:{cell} at {pc_ixy}", "pos_tracking")
        elif self.out_of_bounds_check(pc_ixy):
            SlTrace.lg(f"announce_pcell({pc_ixy}) out of bounds", "bounds")
        else:
            self.play_sound(pitch=self.pitch_blank,
                             dur=self.dur_blank,
                             dly=dly)
            SlTrace.lg(f"blank: play_sound({self.pitch_blank},{self.dur_blank})"
                       f" {cell} at {pc_ixy}", "pos_tracking")
            
    def out_of_bounds_check(self, pc_ixy):
        """ Check for out of bounds / illegal location
            and announce
        :pc_ixy: (ix,iy) location
        :returns: True if out of bounds / illegal
        """
        if pc_ixy is None:
            self.play_sound(self.pitch_on_edge)
            return True
        
        ix, iy = pc_ixy
        if ix < self.awin.get_ix_min():
            self.play_sound(self.pitch_on_edge)
            return True
        if ix > self.awin.get_ix_max():
            self.play_sound(self.pitch_on_edge)
            return True
        if iy < self.awin.get_iy_min():
            self.play_sound(self.pitch_on_edge)
            return True
        if iy > self.awin.get_iy_max():
            self.play_sound(self.pitch_on_edge)
            return True

        return False        

    def play_sound(self,pitch, dur=None, volume=None, dly=None):
        """ Play sound - non-blocking
        :pitch: sound pitch 
        :dur: sound duration default:dur_base (msec)
        :volume: sound volume in decibels default: volume_base
        :dly: delay(silence) before sound
        """
        ps = self.get_sound(pitch, dur=dur, volume=volume)
        ps.play(dly=dly)

    def get_sound(self, pitch, dur=None, volume=None):
        """ get or create PlaySound instance
        :pitch, dur, volume: see PlaySound
        :returns: PlaySound 
        """
        if dur is None:
            dur = self.dur_base
        if volume is None:
            volume = self.volume_base 
        ps_key = (pitch,dur,volume)
        if ps_key in self.play_sound_available:
            return self.play_sound_available[ps_key]
        
        return PlaySound(self, pitch=pitch, dur=dur,
                          volume=volume)