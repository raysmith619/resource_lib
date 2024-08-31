# wx_tb_test_scanning_timing.py 22Jul2024  crs, adapt from:
#               wx_tb_test_scanning + tb_test_scanning_timinig
# AudoDrawWindow Tests
# Test Magnify commands
if __name__ == '__main__':
    import os
    import time

    from format_exception import format_exception
    from select_trace import SlTrace
    from wx_tk_rpc_user import TkRPCUser
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
        
        test_desc = "scanning timing"
            
        tkr = TkRPCUser(simulated=True, figure=0)

        bd = BrailleDisplay(tkr=tkr)
        a_bit = 1
        bd.display()        # So we get control
        adw = bd.adw
        fte = adw.fte
        pt_time = 120
        sq_side = 20     # square side n = sq_side*sq_side
        #sq_side = 5
        ###sq_side = 2     # TFD
        total_cells = sq_side*sq_side
        colors = ["red","orange","yellow",
                "green", "blue", "indigo", "violet"]
        adwPlay = AdwPlay(bd=bd, time_inc=0,
                        trace=1,
                        globals={'bd':bd, 'adw':adw, 'fte':fte,
                                'a_bit':a_bit,
                                'SlTrace':SlTrace,
                                'pt_time':pt_time,
                                'sq_side':sq_side,
                                'total_cells':total_cells,
                                'colors':colors,                               
                                }
                        )
        adwPlay.play_pgm(pgm="""
            sq_side = 20
            fte.set_skip_space(False)
            fte.set_skip_run(False)
            fte.set_profile_running()       # Start profiling
            ~
            for ix in range(sq_side):
                for iy in range(sq_side):
                    cell_color = colors[int(ix/5+iy)%len(colors)]
                    bc = adw.create_cell((ix,iy), color=cell_color)
                    adw.display_cell(bc)
            ~
            fte.set_scan_len(total_cells//sq_side)
            SlTrace.lg(f"Setup: scan_len:{total_cells}")
            fte.start_scanning()
            SlTrace.lg("Scanning setup finished")
            pause(pt_time)
            SlTrace.lg("Stopping scanning")
            fte.do_menu_str("s:t")
            SlTrace.lg("Exiting via f:x")
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
        fte.pgm_exit()
