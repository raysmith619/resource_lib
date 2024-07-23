# wx_tb_test_scanning.py 22Jul2024  crs, adapt from:
#               wx_tb_test_magnify + tb_test_scanning
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
        
        test_desc = "scanning"
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
        pt_time = 10
        adwPlay = AdwPlay(bd=bd, time_inc=0,
                        trace=1,
                        globals={'bd':bd, 'fte':fte, 'a_bit':a_bit,
                                'SlTrace':SlTrace,
                                'pt_time':pt_time}
                        )
        adwPlay.play_pgm(pgm="""
            fte.speak_text("Scanning")
            fte.pause(a_bit)
            fte.set_skip_run(val=False)
            fte.set_skip_space(val=False)
            fte.set_combine_wave()
            fte.set_cell_time(.1)
            fte.set_space_time(.05)
            fte.do_menu_str("s:s")
            fte.speak_text(f"Pausing {pt_time} seconds")
            pause(pt_time)
            SlTrace.lg("Stopping scan with s:t")
            fte.do_menu_str("s:t")
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
        fte.pgm_exit()
