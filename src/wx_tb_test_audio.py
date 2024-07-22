# wx_tb_test_audio.py   11Jul2024  crs, convert to wx
# AudoDrawWindow Tests
# Test audio tonal responses

import os


from format_exception import format_exception
from select_trace import SlTrace

from wx_braille_display import BrailleDisplay
from wx_speaker_control import SpeakerControlLocal
from wx_tk_rem_user import TkRemUser

SlTrace.clearFlags()
#SlTrace.setFlags("slow_key_str")
test_desc = "No test running"
test = os.path.basename(__file__)

silent = True
silent = False 

try:
    tkr = TkRemUser(simulated=True)
    # suppress speach to avoid multiprocessing
    speaker_control = SpeakerControlLocal(simple_speaker=True)
    bd = BrailleDisplay(tkr=tkr, title=f"Test: {test}",
                        speaker_control=speaker_control)
    bd.display(silent=silent)
    aw = bd.adw
    fte = aw.fte        # menu/keyboard/mouse control
    
    test_desc = "audio bell"
    x,y = 0,0
    fte.move_to(x,y)
    ix,iy = fte.get_ixy_at()
    ixc,iyc = aw.grid_width//2, aw.grid_height//2
    SlTrace.lg(f"x:{x} y:{y} x_min:{fte.get_x_min()} y_min:{fte.get_y_min()}"
          f" ix:{ix}, iy:{iy}")
    ###???assert ix == ixc, f"ix should be {ixc} was {ix}"
    ###???assert iy == iyc,  f"iy should be {iyc} was {iy}"
    cell = fte.create_cell(cell_ixy=(ix,iy), color="blue")
    fte.display_cell(cell=cell)
    down_key_str = "d"
    up_key_str = "u"
    first_str = ("c;g;9;9;9;9"
                ";c;r;7;7;7;7"
                ";c;v;2;2;2;2;c;r;2;2;c;o;2;2;2"
                  ";u;8;8;8;8;8;8;8;8;d"
                ";c;o;1;1;1;1"
                ";c;b;3;3;3;3"
                ";c;g;6;6;c;i;6;6;6;c;v;6;6;6"
                ";w"
            )
    fte.do_key_str(down_key_str + ";" + first_str)

    ### Too disruptive SlTrace.setFlags("slow_key_str")    # Slow things down
    SlTrace.lg("Retrace steps with audio beep mode on")
    fte.do_menu_str("n:n;n:u")    
    fte.do_key_str(up_key_str)
    fte.move_to(x,y)
    fte.do_key_str(first_str)   # Retrace steps
    
    #fte.do_menu_str("n:")
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
    