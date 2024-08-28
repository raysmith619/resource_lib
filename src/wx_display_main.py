#wx_display_main.py 17Jan2024  crs, Author
""" Startup wxpython display
"""
import argparse
import wx

from select_trace import SlTrace
from wx_braille_display import BrailleDisplay
from wx_tk_rem_user import TkRemUser


if __name__ == '__main__':      # Required because we use multiprocessing
                                # in some modules e.g. pyttsx_proc.py
                                #
    SlTrace.clearFlags()
    subprocess = False
    bdlist = None
    port_in = 50040
    port_out = 50020
    port_inc = None
    parser = argparse.ArgumentParser()
    parser.add_argument('--bdlist', type=str, dest='bdlist', default=bdlist)
    parser.add_argument('--port_in', type=int, dest='port_in', default=port_in)
    parser.add_argument('--port_out', type=int, dest='port_out', default=port_out)
    parser.add_argument('--port_inc', type=int, dest='port_inc', default=port_inc)
    parser.add_argument('--subprocess', action='store_true', dest='subprocess', default=subprocess)
    #parser.add_argument('--ncol=', type=int, dest='ncol', default=ncol)
    args = parser.parse_args()             # or die "Illegal options"
    SlTrace.lg(f"args: {args}\n")
    bdlist = args.bdlist
    port_in = args.port_in
    port_out = args.port_out
    port_inc = args.port_inc
    
    #tkh = TkRemHost()
    tkr = TkRemUser(port_in=port_in, port_out=port_out, port_inc=port_inc)
    app = wx.App()
    bd = BrailleDisplay(tkr, display_list=bdlist)
    bd.display()
    SlTrace.lg("wx_display_main.py after bd.display")
    app.MainLoop()

