# tb_test_scanning.py
# AudoDrawWindow Tests
# Test Scan commands

import os
import time

from format_exception import format_exception
from select_trace import SlTrace

from turtle_braille_link import *

# Test programs with done removed

def square_loop_colors():
    test_desc = "scanning"
    colors = ["red","orange","yellow","green"]
    
    for colr in colors:
        width(40)
        color(colr)
        forward(200)
        right(90)
    #done()            # Complete drawing

def spokes():
    # spokes.py
    # Display a star with spokes
    
    #from turtle_braille_link import *        # Set link to library
    ##from turtle import *    # Bring in turtle graphic functions
    speed("fastest")
    for i in range(7):      # Do things 7 times
        if i == 0:
            color("red")
        elif i == 1:
            color("orange")
        elif i == 2:
            color("yellow")
        elif i == 3:
            color("green")
        elif i == 4:
            color("blue")
        elif i == 5:
            color("indigo")
        else:
            color("violet")
        forward(300)
        dot(100)
        backward(300)
        right(360/7)
    #done()

    
SlTrace.clearFlags()
#SlTrace.setFlags("sound_queue,decpl")
SlTrace.setFlags("sound_time,decpl,scanning")
test_desc = "No test running"
test = os.path.basename(__file__)

test_function = square_loop_colors
test_function = spokes

silent = True
silent = False
pt_time = 160
pt_time = 10 
try:
    test_function()
    bd.display()        # So we get control
    a_bit = 2
    fte = bd.aud_win.fte
    fte.speak_text("Scanning")
    fte.pause(a_bit)
    fte.set_skip_run(val=False)
    fte.set_skip_space(val=False)
    fte.set_combine_wave()
    fte.set_cell_time(.1)
    fte.set_space_time(.05)
    fte.do_menu_str("s:s")
    fte.speak_text(f"Pausing {pt_time} seconds")
    fte.pause(pt_time)
    SlTrace.lg("Stopping scan with s:t")
    fte.do_menu_str("s:t")
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
    