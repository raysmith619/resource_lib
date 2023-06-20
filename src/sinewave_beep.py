# sinewave_beep.py    26Jan2023  crs, encapsulate pysinewave
from select_trace import SlTrace

from speaker_control import SpeakerControlLocal
        
class SineWaveBeep:
        

    cp = 0      # Base pitch
    cpsp = 3    #  pitch color spacing
    volume_base = -10     # Base volume in decibles
    dur_base = .1      # Base duration (sec)
    dur_other = dur_base*2
    dur_sep = dur_base//3   # between cells
    dur_sep = 50   # between cells
    volume_blank = volume_base - 70
    dur_blank = dur_base
    pitch_on_edge = cp+12
    pitch_warning = cp+13
    
    color_pitches = {
        "SCAN_BLANK": cp-3*cpsp,
        "OTHER" : cp-3*cpsp,
        "red" : cp+1*cpsp,
        "orange" : cp+2*cpsp,
        "yellow" : cp+3*cpsp,
        "green" : cp+4*cpsp,
        "blue" :  cp+5*cpsp,
        "indigo" : cp+6*cpsp,
        "violet" : cp+7*cpsp,
        "black" : cp+8*cpsp,
        "gray" : cp+9*cpsp,
        "white" : cp+10*cpsp,
        "BLANK" : cp+11*cpsp,
        }

    @classmethod
    def color2pitch(cls, color):
        """ Convert color string into pitch
        :color: color string
        """
        if color not in cls.color_pitches:
            return cls.color_pitches["OTHER"]
        
        return cls.color_pitches[color]

    def __init__(self, awin, dur=None, silence_checker=None):
        self.awin = awin
        mw = awin.mw
        self.mw = mw
        if dur is None:
            dur = self.dur_base
        self.dur = dur
        self._silence_checker = silence_checker
        self.speaker_control = SpeakerControlLocal(win=mw)
        

    def announce(self, msg, val=None):
        """ Announce
        """
        SlTrace.lg(f"announce {msg}")
        if msg == "can not do":
            self.play_tone(pitch=self.pitch_warning)
        elif msg == "on edge":
            self.play_tone(pitch=self.pitch_on_edge)


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
        
        self.play_tone(pitch=self.pitch_on_edge) 
        
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

    def announce_next_pcell(self, pc_ixy, volume=None, dur=None, dly=None):
        """ Announce next cell
        :pc_ixy: (ix,iy) of next cell
        """
        if dur is None:
            dur = self.dur_base
        if dly is None:
            dly = self.dur_sep
        self.announce_pcell(pc_ixy=pc_ixy,
                             dur=dur,
                             dly=dly)

    def announce_next_pcells(self, pc_ixys, volume=None, dur=None,
                             dur_sep=None, delay_before=None,
                             ):
        """ Announce next cell
        :pc_ixy: (ix,iy) of next cell
        :volume: sound volume default: self.volume_base
                reduced by 10db each cell
        :dur: length of sound per cell default: self.dur
        :dur_sep: length of silence between cell default: self.dur_sep
        :delay_before: delay before first cell's start(now) in series
                     default: dur+dur_sep (assumes previous cell has same dur)
        """
        if volume is None:
            volume = self.volume_base
        if dur is None:
            dur = self.dur_base
        if dur_sep is None:
            dur_sep = self.dur_sep
        if delay_before is None:
            delay_before = dur + dur_sep

                    
        for idx, pc_ixy in enumerate(pc_ixys):
            ndx = idx+1
            dly = delay_before if idx == 0 else delay_before + idx*(dur_sep+dur)
            self.announce_pcell(pc_ixy=pc_ixy, volume=volume-ndx*10, dur=dur, dly=dly)
        
    def announce_pcell(self, pc_ixy, volume=None, dur=None, dly=None):
        """ Announce cell
        :volume: stereo volume default: calculate based on pc_ixy
        :dly: delay before the sound
        """
        if self.silence():
            return
        
        ix,iy = pc_ixy
        if volume is None:
            volume = self.get_vol(ix=ix, iy=iy)
        if type(volume) != tuple:
            volume = (volume,volume)
        if dur is None:
            dur = self.dur_base
        self.update()
        SlTrace.lg(f"announce_pcell({pc_ixy}, volume={volume} dur={dur}, dly={dly}", "sound")
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
            self.play_tone(pitch=pitch, volume=volume, dur=dur, dly=dly)
            SlTrace.lg(f"in cell: play_tone(pitch={pitch},"
                       f" vol_l={volume[0]:.3f} vol_r={volume[1]:.3f}"
                       f" dur={dur}, dly={dly})"
                       f" cell:{cell} at {pc_ixy}", "pos_tracking")
        elif self.out_of_bounds_check(pc_ixy):
            SlTrace.lg(f"announce_pcell({pc_ixy}) out of bounds", "bounds")
        else:
            SlTrace.lg(f"announce blank: play_blank(dur={self.dur_blank})"
                       f" {cell} at {pc_ixy}", "pos_tracking")
            self.play_blank(ix=ix, iy=iy, dur=self.dur_blank,
                             dly=dly)
            
    def out_of_bounds_check(self, pc_ixy):
        """ Check for out of bounds / illegal location
            and announce
        :pc_ixy: (ix,iy) location
        :returns: True if out of bounds / illegal
        """
        if pc_ixy is None:
            self.play_tone(self.pitch_on_edge)
            return True
        
        ix, iy = pc_ixy
        if ix < self.awin.get_ix_min():
            self.play_tone(self.pitch_on_edge)
            return True
        if ix > self.awin.get_ix_max():
            self.play_tone(self.pitch_on_edge)
            return True
        if iy < self.awin.get_iy_min():
            self.play_tone(self.pitch_on_edge)
            return True
        if iy > self.awin.get_iy_max():
            self.play_tone(self.pitch_on_edge)
            return True

        return False        

    def play_blank(self, ix, iy, dur=None, volume=None, dly=None):
        """ Play sound indicating blank area - non-blocking
        Treat a blank as white (combo of red, green, blue)
        :ix,iy: location
        :dur: sound duration default:dur_blank (msec)
        :volume: (vl,vr) stereo sound volume in decibels
             default: calculated
        :dly: delay(silence) before sound
        """
        if dur is None:
            dur = self.dur_blank
        if volume is None:
            volume = self.get_vol(ix=ix,iy=iy) 
        if type(volume) != tuple:
            volume = (volume,volume)
        vl,vr = volume
        SlTrace.lg(f"play_blank:volume:{vl:.1f},{vr:.1f}", "pos_tracking")
        self.play_tone(pitch=self.color2pitch("BLANK"), dur=self.dur_blank,
                                               volume=volume)

    def play_tones(self,pitches, dur=None, volume=None, dly=None):
        """ Play sound - non-blocking
        :pitches: list of sound pitch 
        :dur: sound duration default:dur_base (msec)
        :volume: sound volume in decibels default: volume_base
        :dly: delay(silence) before sound
        """
        for pitch in pitches:
            self.play_tone(pitch=pitch, dur=dur, volume=volume,dly=dly)

        
    def get_vol(self, ix, iy, eye_ixy_l=None, eye_ixy_r=None):
        """ Get tone volume for cell at ix,iy
        volume(left,right)
        Volume(in decibel): k1*(k2-distance from eye), k1=1, k2=0
        :ix: cell ix
        :iy: cell iy
        :eye_xy_l: left eye/ear at x,y default: self.eye_xy_l
        :eye_xy_r: right eye/ear at x,y  default: self.eye_xy_r
        return: volume(left,right) in decibel
        """
        return self.awin.get_vol(ix=ix, iy=iy, eye_ixy_l=eye_ixy_l,
                                  eye_ixy_r=eye_ixy_r)
       
    def update(self):
        """ Update pending events
        """
        self.awin.update()    

    def update_pending(self):
        """ Update pending events
        """
        self.awin.update_idle()

    """
    ############################################################
                       Links to speaker control
    ############################################################
    """

    def play_tone(self,pitch, dur=None, volume=None, dly=None):
        """ Play sound - non-blocking
        :pitch: sound pitch
        :dur: sound duration default:dur_base (msec)
        :volume: sound volume in decibels default: volume_base
        :dly: delay(silence) before sound
        """
        if not isinstance(volume, tuple):
            volume = (volume,volume)
        vol_adj = self.get_vol_adj()
        if abs(vol_adj) > 1.e-10:  # Only if non-trivial
            vol_left,vol_right = volume
            vol_left += vol_adj
            vol_right += vol_adj
            volume = (vol_left,vol_right)

        self.speaker_control.play_tone(pitch=pitch, dur=dur, volume=volume, dly=dly)


    def get_vol_adj(self):
        """ Get current volume adjustment ??? Thread Safe ???
        :returns: current vol_adjustment in db
        """
        return self.speaker_control.get_vol_adj()
