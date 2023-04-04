# play_sound_control    31Mar2023  crs
"""
Control sound playing
Soon to be directed to SpeakerControler
"""
from select_trace import SlTrace

from play_sound import PlaySound

class PlaySoundControl:
    
    def __init__(self, win=None, dur=.1, volume=None,):
        """ Setup from sinewave beep
        :swb: SineWaveBeep instance
        """
        self.win = win
        self.dur = dur
        self.volume = volume
        self.g_psid = 0          # Unique sound id generator
        self.play_sound_running = {}     # currently playing by psid
        self.play_sound_available = {}   # free/stopped by pskey - avail lists

    def new_id(self):
        """ Generate unique sound id
        :returns: new id
        """
        self.g_psid += 1
        return self.g_psid

    def play_sound(self,pitch, dur=None, volume=None, dly=None):
        """ Play sound - non-blocking
        :pitch: sound pitch 
        :dur: sound duration default:dur_base (msec)
        :volume: sound volume in decibels default: volume_base
        :dly: delay(silence) before sound
        """
        self.update()
        if volume is None:
            volume = self.volume
        SlTrace.lg(f"play_sound:pitch:{pitch} dur:{dur} volume:{volume} ", "pos_tracking")
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
        ps = PlaySound(self, pitch=pitch,
                          volume=volume, pskey=pskey)
        return ps

        ####### Don't reuse #######
         
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
        """ tkinter update
        """
        if self.win is not None:
            self.win.update()

    def update_pending(self):
        """ Update pending events
        """
        if self.win is not None:
            self.win.update_pending()
