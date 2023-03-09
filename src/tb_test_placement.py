# tb_test_placement.py
# AudoDrawWindow Tests
# Test visual placement - INTERACTIVE

import os
import traceback
import sys

from format_exception import format_exception
from select_trace import SlTrace

from braille_display import BrailleDisplay
SlTrace.clearFlags()
test_desc = "No test running"
test = os.path.basename(__file__)
bd = BrailleDisplay(title=f"Test: {test}")
bd.display()
aw = bd.aud_win
fte = aw.ftend        # menu/keyboard/mouse control

try:
    
    test_desc = "place center"
    x,y = 0,0
    fte.move_to(x,y)
    ix,iy = fte.get_ixy_at()
    ixc,iyc = aw.grid_width//2, aw.grid_height//2
    SlTrace.lg(f"x:{x} y:{y} x_min:{fte.get_x_min()} y_min:{fte.get_y_min()}"
          f" ix:{ix}, iy:{iy}")
    assert ix == ixc, f"ix should be {ixc} was {ix}"
    assert iy == iyc,  f"iy should be {iyc} was {iy}"
    cell = fte.create_cell(cell_ixy=(ix,iy), color="blue")
    fte.display_cell(cell=cell)
    
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
    