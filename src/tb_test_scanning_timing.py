# tb_test_scanning_timing.py
# Timing setup and execution
#

import os
import time

from format_exception import format_exception
from select_trace import SlTrace
from audio_draw_window import AudioDrawWindow
from braille_cell import BrailleCell 

SlTrace.clearFlags()

test_desc = "scanning timing"
test = os.path.basename(__file__)

sq_side = 20     # square side n = sq_side*sq_side
###sq_side = 2     # TFD
total_cells = sq_side*sq_side
colors = ["red","orange","yellow",
          "green", "blue", "indigo", "violet"]
fte = None
try:
    adw = AudioDrawWindow()
    fte = adw.fte
    fte.set_skip_space(False)
    fte.set_skip_run(False)
    fte.set_profile_running()       # Start profiling
    for ix in range(sq_side):
        for iy in range(sq_side):
            cell_color = colors[int(ix/5+iy)%len(colors)]
            bc = adw.create_cell((ix,iy), color=cell_color)
            adw.display_cell(bc)
    fte.set_scan_len(total_cells//sq_side)
    SlTrace.lg(f"Setup: scan_len:{total_cells}")
    fte.start_scanning()
    fte.pause(320)
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
    