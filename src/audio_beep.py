# audio_beep.py    25Nov2022  crs,
""" 
Audio Support for audio_window
"""
import winsound
from select_trace import SlTrace
from sinewave_beep import SineWaveBeep

class AudioBeep:
    beep_dur = 200      # Default beep duration
    color_fm = 1000     # Color frequency multiplier
    other_freq = color_fm//4
    other_dur = beep_dur*2
    blank_freq = color_fm//3
    blank_dur = beep_dur*2
    
    color_freqs = {
        "OTHER" : other_freq,
        "BLANK" : blank_freq,
        "red" : 1*color_fm,
        "orange" : 2*color_fm,
        "yellow" : 3*color_fm,
        "green" : 4*color_fm,
        "blue" :  5*color_fm,
        "indigo" : 6*color_fm,
        "violet" : 7*color_fm,
        "black" : 8*color_fm,
        "white" : 9*color_fm,
        "gray" : 10*color_fm,
        }
    
    def __init__(self, awin, silence_checker=None):
        """ Setup audio sound support
        :awin: instance of AudioWindow
        :silence_checker: function to check if we should
                        go silent
        """
        self.awin = awin
        self._silence_checker = silence_checker
        self.sinewave_beep = SineWaveBeep(awin, silence_checker=silence_checker)
        self.has_sinewave = True        # TEMP - push checking deeper

    def announce_can_not_do(self, msg=None, val=None):
        """ Announce we can't do something
        """
        SlTrace.lg("announce_can_not_do()", "bounds")
        if self.has_sinewave:
            self.sinewave_beep.announce("can_not_do")
        else:    
            winsound.Beep(frequency=self.color_fm//5, duration=self.beep_dur//3)


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
        if self.has_sinewave:
            self.sinewave_beep.announce("on_edge")
        else:
            winsound.Beep(200, 500) 
        
    def announce_pcells(self, pc_ixys, dur=None):
        """ Anounce what we're up against
        200 ms first cell, 100 ms second cell 50 ms
        :pc_ixys: list of possible cells ixy
        :dur: max duration of beep default: 200 
        """
        if self.has_sinewave:
            self.sinewave_beep.announce_pcells(pc_ixys, dur)
        else:
            if dur is None:
                dur = self.beep_dur
            for pc_ixy in pc_ixys:
                self.announce_pcell(pc_ixy, dur)
                dur //= 2
        
    def announce_next_pcells(self, pc_ixys, dur=None):
        """ Announce what we're up against
        200 ms first cell, 100 ms second cell 50 ms
        :pc_ixys: list of possible cells ixy
        :dur: max duration of beep default: 200 
        """
        if self.has_sinewave:
            self.sinewave_beep.announce_next_pcells(pc_ixys, dur)
        else:
            if dur is None:
                dur = self.beep_dur
            for pc_ixy in pc_ixys:
                self.announce_pcell(pc_ixy, dur)
                dur //= 2

    def announce_next_pcell(self, pc_ixy):
        """ Announce next cell
        :pc_ixy: (ix,iy) of next cell
        """
        if self.has_sinewave:
            self.sinewave_beep.announce_next_pcell(pc_ixy=pc_ixy)
        else:    
            self.announce_pcell(pc_ixy=pc_ixy,
                                 dur=int(self.beep_dur*.5))
        
    def announce_pcell(self, pc_ixy, dur=None, dly=None):
        """ Announce cell
        :pc_ixy: ix,iy indexes
        :dur: duration default: pass on down
        :dly: delay before the sound default: pass on down
        """
        if self.silence():
            return
        
        if self.has_sinewave:
            self.sinewave_beep.announce_pcell(pc_ixy, dur=dur, dly=dly)
        else:
            if dur is None:
                dur = self.beep_dur
            cell = self.awin.get_cell_at_ixy(pc_ixy)
            if cell is not None:
                color = cell._color
                if color not in self.color_freqs:
                    freq = self.color_freqs["OTHER"]
                    dur = self.other_dur
                    SlTrace.lg(f"color:{color} freq:{freq} dur:{dur}",
                                "pos_tracking")
                else:
                    freq = self.color_freqs[color]
                winsound.Beep(freq, dur)
                SlTrace.lg(f"in cell: winsound.Beep({freq},{dur})"
                           f" cell:{cell} at {pc_ixy}", "pos_tracking")
            elif self.out_of_bounds_check(pc_ixy):
                SlTrace.lg(f"announce_pcell({pc_ixy}) out of bounds", "bounds")
            else:
                winsound.Beep(frequency=self.blank_freq, duration=self.blank_dur)
                SlTrace.lg(f"blank: winsound.Beep({self.blank_freq},{self.blank_dur})"
                           f" {cell} at {pc_ixy}", "pos_tracking")
            
    def out_of_bounds_check(self, pc_ixy):
        """ Check for out of bounds / illegal location
            and announce
        :pc_ixy: (ix,iy) location
        :returns: True if out of bounds / illegal
        """
        if pc_ixy is None:
            self.announce_can_not_do()
            return True
        
        ix, iy = pc_ixy
        if ix < self.awin.get_ix_min():
            self.announce_can_not_do()
            return True
        if ix > self.awin.get_ix_max():
            self.announce_can_not_do()
            return True
        if iy < self.awin.get_iy_min():
            self.announce_can_not_do()
            return True
        if iy > self.awin.get_iy_max():
            self.announce_can_not_do()
            return True

        return False