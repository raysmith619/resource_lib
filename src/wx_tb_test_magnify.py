# wx_tb_test_magnify.py 11Jul2024  crs, convert to wx
# AudoDrawWindow Tests
# Test Magnify commands
if __name__ == '__main__':
    import os
    import time

    from format_exception import format_exception
    from select_trace import SlTrace
    from wx_tk_rem_user import TkRemUser
    from wx_braille_display import BrailleDisplay

    from wx_turtle_braille import *
    from wx_adw_play import AdwPlay

    SlTrace.clearFlags()
    #SlTrace.setFlags("slow_key_str")
    test_desc = "No test running"
    test = os.path.basename(__file__)

    silent = True
    silent = False 
    try:
        
        test_desc = "magnify"
        colors = ["red","orange","yellow","green"]
        
        for colr in colors:
            width(40)
            color(colr)
            forward(200)
            right(90)
        #done()            # Complete drawing
            
        tkr = TkRemUser(simulated=True, figure=2)

        bd = BrailleDisplay(tkr=tkr)
        a_bit = 1
        bd.display()        # So we get control
        fte = bd.adw.fte
        adwPlay = AdwPlay(bd=bd, time_inc=0,
                        trace=1,
                        globals={'bd':bd, 'fte':fte, 'a_bit':a_bit,
                                'SlTrace':SlTrace})
        adwPlay.play_pgm(pgm="""
        fte.pause(a_bit)
        fte.speak_text("Select some squares")
        fte.pause(a_bit)
        fte.do_key_str("3;3;3")
        fte.pause(a_bit)
        fte.speak_text("Magnify select")
        fte.do_menu_str("m:s")
        SlTrace.lg("After m:s")
        fte.speak_text("Magnify view")
        SlTrace.lg('after fte.speak_text("Magnify view")')
        fte.do_menu_str("m:v")
        SlTrace.lg("After m:v")
        fte.pause(a_bit)
        #fte.speak_text_stop() 
        SlTrace.lg("Announcing Exiting via File|Exit")
        fte.speak_text("Exiting via File|Exit")
        SlTrace.lg("Ready to do f:x")
        fte.do_menu_str("f:x")
        SlTrace.lg("Testing Passed")
        """)
        SlTrace.lg("After play")

    except AssertionError as err_msg:
        SlTrace.lg(f"Test {test_desc} FAILED: {err_msg}")
    except Exception as e:
        SlTrace.lg(f"Unexpected exception: {e}")
        SlTrace.lg("Printing the full traceback as if we had not caught it here...")
        SlTrace.lg(format_exception(e))
        bd.adw.fte.pgm_exit(1)

    finally:
        SlTrace.lg("Test End", to_stdout=True)
        #fte.pgm_exit()
