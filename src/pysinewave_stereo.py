# pysinewave_stereo.py
# reuse of SineWave
import time
from turtle_braille_link import *
from sinewave import SineWave

# Combine several sine waves
pitch_base = 6
dur_play = .1
dur_pause = .1
volume_base=0
sinewave_left = SineWave(pitch = pitch_base-3,
                         channels=2, channel_side='l')
sinewave_middle = SineWave(pitch = pitch_base,
                         channels=2, channel_side='lr')
sinewave_right = SineWave(pitch = pitch_base+3,
                         channels=2, channel_side='r')

volume = volume_base
while True:
    volume -= 10
    print(f"volume:{volume}")
    sinewave_left.set_volume(volume)
    sinewave_left.sinewave_generator.set_decibels_per_second(volume/dur_play)
    sinewave_left.play()
    time.sleep(dur_play)
    sinewave_left.stop()
    time.sleep(dur_pause)
    
    sinewave_middle.set_volume(volume)
    sinewave_left.set_decibels_per_second(volume/dur_play)
    sinewave_middle.play()
    time.sleep(dur_play)
    sinewave_middle.stop()
    time.sleep(dur_pause)
    
    sinewave_right.set_volume(volume)
    sinewave_right.set_decibels_per_second(volume/dur_play)
    sinewave_right.play()
    time.sleep(dur_play)
    sinewave_right.stop()
    time.sleep(dur_pause)
