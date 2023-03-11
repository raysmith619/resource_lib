# tb_test_goto.py
# AudoDrawWindow Tests
# Test positioning

import os
import traceback
import sys

from format_exception import format_exception

from select_trace import SlTrace

from braille_display import BrailleDisplay
SlTrace.clearFlags()
test_desc = "No test running"

try:
    test = os.path.basename(__file__)
    bd = BrailleDisplay(title=f"Test: {test}")
    bd.display()
    aw = bd.aud_win
    fte = aw.fte        # menu/keyboard/mouse control
    
    test_desc = "move_to"
    x,y = fte.get_x_min(),fte.get_y_min()
    fte.move_to(x,y)
    ix,iy = fte.get_ixy_at()
    SlTrace.lg(f"x:{x} y:{y} x_min:{fte.get_x_min()} y_min:{fte.get_y_min()}"
          f" ix:{ix}, iy:{iy}")
    assert ix == 0, f"ix should be 0 was {ix}"
    assert iy == 0,  f"ix should be 0 was {iy}"
    
    test_desc = "cursor_down"
    x,y = fte.get_x_min(),fte.get_y_min()
    ix,iy = fte.get_ixy_at()
    fte.key_down()
    x2,y2 = fte.get_xy()
    ix2,iy2 = fte.get_ixy_at()
    SlTrace.lg(f"x:{x} y:{y} ix:{ix} iy:{iy} x2:{x2} y2{y2}"
               f" ix2:{ix2}, iy:{iy2}")
    assert ix2 == ix, f"ix2 should be {ix} is {ix2}"
    assert iy2 == iy+1,  f"iy should be {iy+1} is {iy}"
    
    
    test_desc = "place cell"
    x,y = 0,0
    fte.move_to(x,y)
    ix,iy = fte.get_ixy_at()
    ixc,iyc = aw.grid_width//2, aw.grid_height//2
    SlTrace.lg(f"x:{x} y:{y} x_min:{fte.get_x_min()} y_min:{fte.get_y_min()}"
          f" ix:{ix}, iy:{iy}")
    assert ix == ixc, f"ix should be {ixc} was {ix}"
    assert iy == iyc,  f"iy should be {iyc} was {iy}"
    
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
    