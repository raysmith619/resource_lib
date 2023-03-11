# tb_test_keyboard.py
# AudoDrawWindow Tests
# Test keyboard commands

import os


from format_exception import format_exception
from select_trace import SlTrace

from braille_display import BrailleDisplay

SlTrace.clearFlags()
#SlTrace.setFlags("slow_key_str")
test_desc = "No test running"
test = os.path.basename(__file__)

silent = True
silent = False 

bd = BrailleDisplay(title=f"Test: {test}", silent=silent)
bd.display(silent=silent)
aw = bd.aud_win
fte = aw.fte        # menu/keyboard/mouse control

try:
    
    test_desc = "keyboard"
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
    key_str = (
                "d"
                ";c;g;9;9;9;9"
                ";c;r;7;7;7;7"
                ";c;v;2;2;2;2;c;r;2;2;c;o;2;2;2"
                  ";u;8;8;8;8;8;8;8;8;d"
                ";c;o;1;1;1;1"
                ";c;b;3;3;3;3"
                ";c;g;6;6;c;i;6;6;6;c;v;6;6;6"
                ";w"
            )
    '''
    key_str = (
            "d"
            ";c;g;9;9;9;9"
            )
    '''
    fte.do_key_str("d")
    for _ in range(3):
        fte.do_key_str("c;b;Right")
        fte.do_key_str("c;r;Right")
    fte.do_key_str("Escape")
    fte.do_key_str(key_str)
    fte.do_key_str("Escape")
    
    fte.do_key_str("h;Escape;Up;Down;Left;Right")
    fte.do_key_str("d")      # Lower pen
    fte.do_key_str("c;r;Down")
    fte.do_key_str("1;2;3;4;5;6;7;8;9;0")
    fte.do_key_str("r;a;b")
    fte.do_key_str("c;o;Up")
    fte.do_key_str("w")
    SlTrace.lg(f"speech cmd queue size:{fte.get_cmd_queue_size()}")
    SlTrace.lg(f"speech speech queue size:{fte.get_speech_queue_size()}")
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
    