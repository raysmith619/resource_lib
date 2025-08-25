#wx_display_main.py 17Jan2024  crs, Author
""" Startup wxpython display
"""
import argparse
import wx

from select_trace import SlTrace
from wx_braille_display import BrailleDisplay
from wx_tk_rpc_user import TkRPCUser
from wx_braille_cell_list import BrailleCellList

if __name__ == '__main__':      # Required because we use multiprocessing
                                # in some modules e.g. pyttsx_proc.py
                                #
    SlTrace.clearFlags()
    subprocess = False
    id_title = ""       # Identification title
    title = None
    src_file = __file__   # Replaced with remote source file name
    bdlist = None
    host_port = 50040
    host_port = 50020
    port_inc = None
    parser = argparse.ArgumentParser()
    parser.add_argument('--id_title', type=str, dest='id_title', default=id_title)
    parser.add_argument('--title', type=str, dest='title', default=title)
    parser.add_argument('--src_file', type=str, dest='src_file', default=src_file)
    parser.add_argument('--bdlist', type=str, dest='bdlist', default=bdlist)
    parser.add_argument('--host_port', type=int, dest='host_port', default=host_port)
    parser.add_argument('--port_inc', type=int, dest='port_inc', default=port_inc)
    parser.add_argument('--subprocess', action='store_true', dest='subprocess', default=subprocess)
    #parser.add_argument('--ncol=', type=int, dest='ncol', default=ncol)
    args = parser.parse_args()             # or die "Illegal options"
    SlTrace.lg(f"args: {args}\n")
    id_title = args.id_title
    title = args.title
    src_file = args.src_file
    bdlist = args.bdlist
    host_port = args.host_port
    port_inc = args.port_inc
    
    #tkh = TkRPCHost()
    SlTrace.lg(f"wx_display_main.py setting up tk link", "tk_link")
    tkr = TkRPCUser(host_port=host_port)
    SlTrace.lg(f"wx_display_main.py after tk link setup", "tk_link")
    app = wx.App()
    SlTrace.lg(f"wx_display_main.py retrieve cell_specs", "tk_link")
    cells = tkr.get_cell_specs()  # gets (ix,iy,color)*
    SlTrace.lg(f"wx_display_main.py tkr.get_cell_specs() cells: {cells}", "cell_specs")
    cell_list = BrailleCellList(cells)  # converts either to BrailleCell
    bdlist = cell_list.to_string()
    bd = BrailleDisplay(tkr, id_title=id_title, title=title,
                        src_file=src_file, display_list=bdlist)
    bd.display(title=title)
    tkr.setup_from_host_requests()      # Wait till after initial display
    SlTrace.lg("wx_display_main.py after bd.display", "tk_link")
    app.MainLoop()

