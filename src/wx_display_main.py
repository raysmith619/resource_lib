#wx_display_main.py 17Jan2024  crs, Author
""" Startup wxpython display
"""
import argparse
import wx

from select_trace import SlTrace
from wx_braille_display import BrailleDisplay
from wx_tk_rem_host import TkRemUser

if __name__ == '__main__':      # Required because we use multiprocessing
                                # in some modules e.g. pyttsx_proc.py
                                #                      
    SlTrace.clearFlags()
    subprocess = False
    bdlist = "(1,1,red) (2,2) (3,3) (4,4,green) (4,3) (4,2,blue)"
    parser = argparse.ArgumentParser()
    parser.add_argument('--bdlist', type=str, dest='bdlist', default=bdlist)
    parser.add_argument('--subprocess', action='store_true', dest='subprocess', default=subprocess)
    #parser.add_argument('--ncol=', type=int, dest='ncol', default=ncol)
    args = parser.parse_args()             # or die "Illegal options"
    SlTrace.lg(f"args: {args}\n")
    tkr = TkRemUser()
    app = wx.App()
    bd = BrailleDisplay(tkr,display_list=args.bdlist)
    bd.display()
    SlTrace.lg("wx_display_main.py after bd.display")
    app.MainLoop()

