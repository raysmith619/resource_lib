# wx_tb_test_audio_1.py 11Jul2024  crs, Convert to wx
# AudoDrawWindow Tests
# Test audio simplest

import os


from format_exception import format_exception
from select_trace import SlTrace

from wx_braille_display import BrailleDisplay
from wx_speaker_control import SpeakerControlLocal
from wx_tk_rem_user import TkRemUser

SlTrace.clearFlags()
SlTrace.setFlags("sound_queue")
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
    bd.display()
    aw = bd.adw
    fte = aw.fte        # menu/keyboard/mouse control
    
    test_desc = "audio bell 1"
    down_key_str = "d"
    up_key_str = "u"
    
    SlTrace.lg("Waiting for window")
    fte.wait_on_output()
    SlTrace.lg("Window beginning output should be done")
    x,y = 0,0
    fte.move_to(x,y)
    ix,iy = fte.get_ixy_at()
    fte.wait_on_output()
    colors = ["red", "orange", "yellow"]
    for i in range(len(colors)):
        c_ixy = (ix+i, iy)
        color = colors[i%len(colors)]
        SlTrace.lg(f"Going to {c_ixy}")
        cell = fte.create_cell(cell_ixy=c_ixy, color=color)
        fte.display_cell(cell=cell)
        fte.wait_on_output()
    
    ix -= 1     # to left of cells
    fte.speak_text(f"Moving to {ix},{iy}")
    fte.wait_on_output()
    fte.move_to_ixy(ix=ix, iy=iy)
    fte.wait_on_output()
    fte.do_menu_str("n:u")      # Turn on audio beep
    for _ in range(len(colors)+2):  # One past to space
        fte.do_key_str("6")     # To right
    fte.wait_on_output()
    fte.speak_text("After going though cells with audio beep")
    fte.wait_on_output()
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
    