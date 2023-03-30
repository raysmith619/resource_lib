#sinewave_numpy.py    29Mar2023  crs
""" Lower level substitute for pysinewave
    Not a direct substitute but for lower level operations
"""
import time
import numpy as np
import sounddevice as sd
from pysinewave import utilities

class SineWaveNumPy:
    """ Gathers and plays stereo sine wave
    """
    def __init__(self, pitch=0, decibels_left=0, decibels_right=0,
                sample_rate=44100, duration_s=1.):
        """ Setup waves
        :pitch: user tone level default: 0
        :decibels_left: left volume in decibels default: 0
        :decibels_right: right volume in decibels default: 0
        :samplerate: samples per second default: 44100
        :duration: stored duration default:1
        """
        freq_hz = utilities.pitch_to_frequency(pitch)
        atten_left = utilities.decibels_to_amplitude_ratio(decibels_left) 
        atten_right = utilities.decibels_to_amplitude_ratio(decibels_right) 
        self.sample_rate = sample_rate
        
        # NumpPy magic to calculate the waveform
        each_sample_number = np.arange(duration_s * sample_rate)
        base_waveform = np.sin(2 * np.pi * each_sample_number * freq_hz / sample_rate)
        left_waveform = base_waveform.reshape(-1,1)*atten_left
        right_waveform = base_waveform.reshape(-1,1)*atten_right
        stereo_waveform = np.hstack((left_waveform, right_waveform))
        self.stereo_waveform = stereo_waveform
        
    def play(self):
        """ Start playing tone
        """
        sd.play(self.stereo_waveform, self.sample_rate)
        
        
    def stop(self):
        """ Stop playing tone
        """
        sd.stop()

if __name__ == "__main__":
    pitch = 2
    pitch_sep = 2
    decibels_sep = 50
    decibels_left = -50
    decibels_right = decibels_left + decibels_sep
    duration_s = 2
    sw1 = SineWaveNumPy(pitch=pitch, decibels_left=decibels_left,
                       decibels_right=decibels_right,
                       duration_s=duration_s)
    sw2 = SineWaveNumPy(pitch=pitch+pitch_sep, decibels_left=decibels_right,
                       decibels_right=decibels_left,
                       duration_s=duration_s)
    print(f"Starting with pitch:{pitch} duration:{duration_s} sec")
    sw1.play()
    time.sleep(duration_s)
    sw1.stop()
    print("End of sw1")
    time.sleep(1)
    sw2.play()
    time.sleep(duration_s)
    sw2.stop()
    print("End of sw2")