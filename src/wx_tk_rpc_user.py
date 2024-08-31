#wx_tk_rpc_user.py  08Feb2024  crs, split from wx_tk_rem_access.py
""" Client/User part of wx_tk_rem_host.py, wx_tk_rem_user.py pair
Supporting communication betw
"""
import socket as sk
import threading as th
import queue
import pickle
import time
from wx_rpc import RPCClient

from select_trace import SlTrace
        
class TkRPCUser:
    """User (remote) control requesting canvas information
    Using socket client
    """
    def __init__(self, host='localhost',
                 port=None,
                 port_in=None,
                 port_out=None,
                 port_diff=20,
                 port_inc=None,
                 max_recv=2**16, simulated=False,
                 cmd_time_ms= 500,
                 figure=1):
        """ Handle user (wxPython) side of communications
        :host: host address default: localhost - same machine
        :port: shorthand for port_in
        :port_in: port for incoming requests/responses
        :port_out: port for outgoing request/responses
                default: port_in+port_diff
        :port_diff:  diff between port_in and port_out
                default: 20
        :port_inc: port increment default: no increment
        :max_recv: maximum data recieved length in bytes
                    default: 2**16
        :cmd_time_ms: maximum between cmd check in seconds
                    default: .5 sec
        :simulated: True: simulate tk input default: False
        :figure: simulated figure 1 - spokes, 2 - square
                default=1 spokes
        """
        SlTrace.lg("TkRPCUser() __init__() BEGIN")
        self.host = host
        if port is not None:
            port_in = port
        if port_in is None:
            port_in = 50040
        if port_out is None:
            port_out = port_in+port_diff
        if port_inc is not None:
            port_in += port_inc
            port_out += port_inc
        self.port_in = port_in
        self.port_out = port_out
        
        self.max_recv = max_recv
        self.cmd_time_ms = cmd_time_ms
        self.simulated = simulated
        SlTrace.lg("TkRPCUser() __init__()")
        if simulated:
            self.make_simulated(figure=figure)
            return
        
        self.max_recv = max_recv
        self.cmd_time_ms = cmd_time_ms

        self.from_user_client = RPCClient(self.host, self.port_out)
        self.from_user_client.connect()
    
    def get_cell_specs(self, 
                        win_fract=True, 
                        x_min=None, y_min=None,
                        x_max=None, y_max=None,
                        n_cols=None, n_rows=None):
        """ Get cell specs from remote tk canvas
        :returns: list of cell specs (ix,iy,color)
        """        
        if self.simulated:
            return self.get_cell_specs_simulated(
                        x_min=x_min, y_min=y_min,
                        win_fract=win_fract, 
                        x_max=x_max, y_max=y_max,
                        n_cols=n_cols, n_rows=n_rows)
        
        return self.from_user_client.get_cell_specs(
                    win_fract=win_fract, 
                    x_min=x_min, y_min=y_min,
                    x_max=x_max, y_max=y_max,
                    n_cols=n_cols, n_rows=n_rows)
            
    
    def get_cell_specs_simulated(self, 
                        win_fract=True, 
                        x_min=None, y_min=None,
                        x_max=None, y_max=None,
                        n_cols=None, n_rows=None):
        """ Get cell specs from remote tk canvas
        :returns: list of cell specs (ix,iy,color)
        """        
        return self.sim_cg.get_cell_specs(
                        win_fract=win_fract, 
                        x_min=x_min, y_min=y_min,
                        x_max=x_max, y_max=y_max,
                    n_cols=n_cols, n_rows=n_rows)


    def is_inbounds_ixy(self, *ixy):
        """ Check if ixy pair is in bounds
        :ixy: if tuple ix,iy pair default: current location
              else ix,iy indexes
            ix: cell x index default current location
            iy: cell y index default current location
        :returns: True iff in bounds else False
        """
        if self.simulated:
            return self.is_inbounds_ixy_simulated(self, *ixy)
        
        return self.from_user_client.is_inbounds_ixy(*ixy)

    def is_inbounds_ixy_simulated(self, *ixy):
        """ Check if ixy pair is in bounds
        :ixy: if tuple ix,iy pair default: current location
              else ix,iy indexes
            ix: cell x index default current location
            iy: cell y index default current location
        :returns: True iff in bounds else False
        """
    

    def get_cell_rect_tur(self, ix, iy):
        """ Get cell's turtle rectangle x, y  upper left, x,  y lower right
        :ix: cell x index
        :iy: cell's  y index
        :returns: (min_x,max_y, max_x,min_y)
        """
        if self.simulated:
            return self.get_cell_rect_tur_simulated(
                        ix=ix,iy=iy)
        
        return self.from_user_client.get_cell_rect_tur(ix, iy)
    
    def get_cell_rect_tur_simulated(self, 
                        ix,iy):
        """ Get cell rectangle
        :returns: )
        """        
        return self.sim_cg.get_cell_rect_tur(
                        ix,iy)
    
    
    def get_canvas_lims(self, win_fract=True):
        """ Get canvas limits
        :win_fract: True - fractional 0. to 1.
                    False - window coordinates
        :returns: internal (xmin, xmax, ymin, ymax)
        """
        if self.simulated:
            return self.get_canvas_lims_simulated(win_fract=win_fract)
        
        if win_fract:
            return (0.,1., 0., 1.)
        
        return self.from_user_client.get_canvas_lims(win_fract)
                        
    
    def get_canvas_lims_simulated(self, win_fract=True):
        """ Simulate access to canvas info
        :returns: internal (xmin, xmax, ymin, ymax)
        """
        if win_fract:
            return (0.,1.,0.,1.)
        
        winfo_width = self.sc_width
        winfo_height = self.sc_height
        xmax = winfo_width/2
        xmin = -xmax
        ymax = winfo_height/2
        ymin = -ymax
        return (xmin,xmax,ymin,ymax)

    
    def test_command(self, 
                        message="Test message"):
        """ Do test message
        :message: test message default:"Test message"
        :returns: "Answer: <message>
        """
        return self.from_user_client.test_command(message)

    def make_simulated(self, figure=1):
        """ Setup local tkinter canvas + canvas_grid
        to provide direct access for local calls
            get_canvas_specs
            get_canvas_lims
        :figure: simulated tk figure
                0 - empty 
                1 - spokes ( like wx_spokes.py)
                2 - square ( like wx_square_colors.py)
        """
        if figure == 0:
            self.make_simulated_empty()
        elif figure  == 1:
            self.make_simulated_spokes()
        elif figure == 2:
            self.make_simulated_square()
        else:
            raise Exception(f"Unsupported figure: {figure}")

    def make_simulated_spokes(self):
        """ simulate wx_spokes.py
        """
        import turtle as tur
        from wx_canvas_grid import CanvasGrid
        sc_width = 800
        sc_height = 900
        self.sc_width = sc_width
        self.sc_height = sc_height
        screen = tur.Screen()
        screen.setup(sc_width, sc_height)
        tur.speed("fastest")
        colors = ["red","orange","yellow","green",
                  "blue","indigo","violet"]
        sp_len = 250
        dot_size = sp_len/3
        for colr in colors:
            tur.color(colr)
            tur.forward(sp_len)
            tur.dot(100)
            tur.backward(sp_len)
            tur.right(360/len(colors))
        canvas = tur.getcanvas()
        self.sim_cg = CanvasGrid(base=canvas)

    def make_simulated_empty(self):
        """ simulate empty screen
        """
        import turtle as tur
        from wx_canvas_grid import CanvasGrid
        sc_width = 800
        sc_height = 900
        self.sc_width = sc_width
        self.sc_height = sc_height
        screen = tur.Screen()
        screen.setup(sc_width, sc_height)
        canvas = tur.getcanvas()
        self.sim_cg = CanvasGrid(base=canvas)

    def make_simulated_square(self):
        """ simulate wx_square_colors.py
        """
        import turtle as tur
        from wx_canvas_grid import CanvasGrid
        sc_width = 800
        sc_height = 900
        self.sc_width = sc_width
        self.sc_height = sc_height
        screen = tur.Screen()
        screen.setup(sc_width, sc_height)
        tur.speed("fastest")
        colors = ["red","orange","yellow","green"]

        for colr in colors:
            tur.width(40)
            tur.color(colr)
            tur.forward(200)
            tur.right(90)
        canvas = tur.getcanvas()
        self.sim_cg = CanvasGrid(base=canvas)

if __name__ == '__main__':
    import sys
    
    tkr = TkRPCUser(simulated=True)
    for msg in ["t1","t2","t3"]:
        SlTrace.lg(f"test_command({msg})")
        res = tkr.test_command(msg)
        SlTrace.lg(f"result: {res}")
    
    if len(sys.argv)  > 1:
        res = tkr.get_cell_specs()
        SlTrace.lg(f"cell_specs: {res}")