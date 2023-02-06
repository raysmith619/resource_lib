# sinewave_beep.py    26Jan2023  crs, encapsulate pysinewave
from select_trace import SlTrace
import datetime

try:
    from pysinewave import SineWave
    has_sinewave = True 
except:
    has_sinewave = False 

class PlaySound:
    """ particular sound to be played
    """
    g_psid = 0          # Unique sound id generator
    psid = g_psid       # unique id

    @classmethod
    def pskey(cls, pitch, volume):
        """ Get unique resource key for possible reuse of SineWave
        :pitch: sound pitch
        :volume: sound volume decibel
        :returns: unique resource key
        """
        return (pitch,volume)
    
    def __init__(self, swb, pitch, dur=None,
                 volume=None, pskey=None):
        """ Setup sound to play
        :swb: calling instance of SineWaveBeep
        :pitch: pitch to play
        :dur: duration of play (msec) default:swb.dur_base
        :volume: volume to play (decibels) default:swb.volume_base
        :pskey: unique key  for PlaySound resource default: see pskey()
        """
        PlaySound.g_psid += 1        # Bump generator ??? Why not self.g_psid += q
        self.psid = PlaySound.g_psid # Store unique id
        
        self.swb = swb
        self.pitch = pitch
        self.time_play_start = None      # Play start time, if any 
        self.time_play_stop = None       # Play stop time, if any
        if dur is None:
            dur = swb.dur
        self.dur = dur
        self.volume = volume
        self.sinewave = SineWave(pitch=pitch, decibels=volume)
        if pskey is None:
            pskey = self.pskey(pitch,volume)
        self.pskey = pskey
        SlTrace.lg(f"New PlaySound: {self}", "sound")

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
        self.dur = dur
        self.is_active = True
        if dly is not None and dly != 0:
            SlTrace.lg(f"delaying play: dly:{dly} {self}", "sound")
            self.swb.awin.canvas.after(dly, self.play_sound)
            self.update()
            return
        
        self.play_it()
        
    def play_it(self):
        """ direct play
        """
        SlTrace.lg(f"play( ps:{self}", "sound")
        self.time_play_start = datetime.datetime.now()
        self.time_play_stop = None
        self.sinewave.play()
        self.swb.awin.canvas.after(int(self.dur), self.play_stop)
        self.update()        
        
    def play_sound(self):
        """ Play sound now, possibly delayed
        """
        self.play()
         
    def play_stop(self):
        """ Stop playing - called after duration of play
        """
        if not self.is_active:
            return 
        self.time_play_stop = datetime.datetime.now()
        play_dur = (self.time_play_stop - self.time_play_start).total_seconds()
        SlTrace.lg(f"play_stop play_dur:{play_dur:.3} ps:{self}", "sound")
        self.sinewave.stop()
        self.swb.free_ps(self)     # Release resource - put on available list

    def update(self):
        self.swb.update()
    
    def update_pending(self):
        """ Update pending events
        """
        self.swb.update_pending()
        
class SineWaveBeep:
        

    cp = 0      # Base pitch
    cpsp = 3    #  pitch color spacing
    volume_base = -10     # Base volume in decibles
    dur_base = 500      # Base duration (msec)
    dur_sep = dur_base//3   # between cells
    dur_sep = 50   # between cells
    volume_blank = volume_base - 70
    dur_blank = dur_base//2
    pitch_on_edge = cp+12
    pitch_warning = cp+13
    
    color_pitches = {
        "OTHER" : cp-3*cpsp,
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



    def __init__(self, awin, dur=None, silence_checker=None):
        self.awin = awin
        if dur is None:
            dur = self.dur_base
        self.dur = dur
        self._silence_checker = silence_checker
        self.has_sinewave = has_sinewave
        self.play_sound_running = {}     # currently playing by psid
        self.play_sound_available = {}   # free/stopped by pskey - avail lists
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
        :dly: delay before the sound
        """
        if self.silence():
            return
        
        if volume is None:
            volume = self.volume_base
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
            self.play_sound(pitch=pitch, volume=volume, dur=dur, dly=dly)
            SlTrace.lg(f"in cell: play_sound(pitch={pitch}, dur={dur}, dly={dly})"
                       f" cell:{cell} at {pc_ixy}", "pos_tracking")
        elif self.out_of_bounds_check(pc_ixy):
            SlTrace.lg(f"announce_pcell({pc_ixy}) out of bounds", "bounds")
        else:
            SlTrace.lg(f"announce blank: play_blank(dur={self.dur_blank})"
                       f" {cell} at {pc_ixy}", "pos_tracking")
            self.play_blank(dur=self.dur_blank,
                             dly=dly)
            
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

    def play_blank(self, dur=None, volume=None, dly=None):
        """ Play sound indicating blank area - non-blocking
        Treat a blank as white (combo of red, green, blue)
        :dur: sound duration default:dur_blank (msec)
        :volume: sound volume in decibels default: volume_blank
        :dly: delay(silence) before sound
        """
        if dur is None:
            dur = self.dur_blank
        if volume is None:
            volume = self.volume_blank
        SlTrace.lg(f"play_blank:volume:{volume}", "sound")
        pitches = []
        for color in ["white","gray","black"]:
            pitches.append(self.color_pitches[color])
        self.play_sounds(pitches=pitches, dur=dur, volume=volume, dly=dly)

    def play_sound(self,pitch, dur=None, volume=None, dly=None):
        """ Play sound - non-blocking
        :pitch: sound pitch 
        :dur: sound duration default:dur_base (msec)
        :volume: sound volume in decibels default: volume_base
        :dly: delay(silence) before sound
        """
        self.update()
        SlTrace.lg(f"play_sound:pitch:{pitch} dur:{dur} volume:{volume} ", "sound")
        ps = self.get_sound(pitch, volume=volume)
        SlTrace.lg(f"    ps:{ps}", "sound")
        self.add_ps_to_run(ps)        # Show who's running
        ps.play(dly=dly, dur=dur)

    def play_sounds(self,pitches, dur=None, volume=None, dly=None):
        """ Play sound - non-blocking
        :pitches: list of sound pitch 
        :dur: sound duration default:dur_base (msec)
        :volume: sound volume in decibels default: volume_base
        :dly: delay(silence) before sound
        """
        self.update()
        SlTrace.lg(f"play_sounds:pitches:{pitches} dur:{dur} volume:{volume} ", "sound")
        ps_list = []
        for pitch in pitches:
            ps = self.get_sound(pitch, volume=volume)
            SlTrace.lg(f"    ps:{ps}", "sound")
            ps_list.append(ps)
        for ps in ps_list:
            self.add_ps_to_run(ps)        # Show who's running
            ps.play(dly=dly, dur=dur)

    def add_ps_to_run(self, ps):
        """ Add PlaySound instance to runing list
        :ps: PlaySound instance
        """
        if ps.psid in self.play_sound_running:
            SlTrace.lg(f"Attempted adding of running PlaySound[{ps.psid}] - {ps}")
            return
        
        self.play_sound_running[ps.psid] = ps
        

    def free_ps(self, ps):
        """ Free PlaySound resource for possible reuse
        :ps: PlaySound instance
        """
        self.update_pending()
        if ps.psid not in self.play_sound_running:
            SlTrace.lg(f"Attempted freeing of non-running PlaySound[{ps.psid}] - {ps}")
            return
        
        if ps.pskey in self.play_sound_available:
            psavails = self.play_sound_available[ps.pskey]
        else:
            psavails = self.play_sound_available[ps.pskey] = []
        psavails.append(ps)
        del(self.play_sound_running[ps.psid])
         
        
    def get_sound(self, pitch, volume=None):
        """ get or create PlaySound instance
        :pitch, volume: see PlaySound
        :returns: PlaySound 
        """
        self.update_pending()
        if volume is None:
            volume = self.volume_base 
        pskey = PlaySound.pskey(pitch=pitch,volume=volume)
        if pskey in self.play_sound_available:
            psavails = self.play_sound_available[pskey]
            psavail = psavails.pop()
            SlTrace.lg(f"get_sound reusing: {psavail}", "sound")
            if len(psavails) == 0:
                del(self.play_sound_available[pskey]) 
            return psavail
        
        ps = PlaySound(self, pitch=pitch,
                          volume=volume, pskey=pskey)
        return ps
       
    def update(self):
        """ Update pending events
        """
        self.awin.update()    

    def update_pending(self):
        """ Update pending events
        """
        self.awin.update_idle()
     