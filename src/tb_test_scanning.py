# tb_test_scanning.py
# AudoDrawWindow Tests
# Test Scan commands

import os
import time

from format_exception import format_exception
from select_trace import SlTrace

from turtle_braille_link import *

SlTrace.clearFlags()
#SlTrace.setFlags("sound_queue,decpl")
SlTrace.setFlags("sound_time,decpl,scanning")
test_desc = "No test running"
test = os.path.basename(__file__)

silent = True
silent = False 
try:
    
    test_desc = "scanning"
    colors = ["red","orange","yellow","green"]
    
    for colr in colors:
        width(40)
        color(colr)
        forward(200)
        right(90)
    #done()            # Complete drawing
    bd.display()        # So we get control
    a_bit = 2
    fte = bd.aud_win.fte
    fte.speak_text("Scanning")
    fte.pause(a_bit)
    fte.set_skip_space(val=True)
    fte.do_menu_str("s:s")
    pt_time = 160
    fte.speak_text(f"Pausing {pt_time} seconds")
    fte.pause(pt_time)
    SlTrace.lg("Testing Passed")


except AssertionError as err_msg:
    SlTrace.lg(f"Test {test_desc} FAILED: {err_msg}")
except Exception as e:
    SlTrace.lg(f"Unexpected exception: {e}")
    SlTrace.lg("Printing the full traceback as if we had not caught it here...")
    SlTrace.lg(format_exception(e))
    fte.pgm_exit(1)

finally:
    SlTrace.lg("Test End")
    fte.pgm_exit()
    