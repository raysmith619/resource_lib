#wx_tk_rpc_user.py  08Feb2024  crs, split from wx_tk_rem_access.py
""" Client/User part of wx_tk_rem_host.py, wx_tk_rem_user.py pair
Supporting communication betw
"""
import socket as sk
import threading as th
import queue
import pickle
import time
import wx

from wx_rpc import RPCClient
from wx_rpc import RPCServer


from select_trace import SlTrace

        
class TkRPCUser:
    """User (remote) control requesting canvas information
    Using socket client
    """
    def __init__(self, host_name='localhost',
                 host_port=None,
                 max_recv=2**16, simulated=False,
                 cmd_time_ms= 500,
                 figure=1):
        """ Handle user (wxPython) side of communications
        :host_name: servere host name default: localhost - same machine
        :host_port: port to send server requests
        :max_recv: maximum data recieved length in bytes
                    default: 2**16
        :cmd_time_ms: maximum between cmd check in seconds
                    default: .5 sec
        :simulated: True: simulate tk input default: False
        :figure: simulated figure 1 - spokes, 2 - square
                default=1 spokes
        """
        SlTrace.lg("TkRPCUser() __init__() BEGIN")
        self.adw = None         # Set when ready
        self.snapshots = []     # snapshot adw, if any

        self.host_name = host_name
        if host_port is None:
           raise Exception("server port is not specified") 
        self.host_port = host_port
        self.user_port = host_port+1        # ??? better choice?
        
        self.max_recv = max_recv
        self.cmd_time_ms = cmd_time_ms
        self.simulated = simulated
        SlTrace.lg("TkRPCUser() __init__()")
        if simulated:
            self.make_simulated(figure=figure)
            return

        self.to_host = RPCClient(self.host_name, self.host_port)
        self.to_host.connect()

        #self.setup_from_host_requests()
        
    def setup_from_host_requests(self):           
        self.from_host_server = RPCServer(self.host_name, self.user_port)

        self.from_host_server.registerMethod(self.snapshot)

        th.Thread(target=self.cmd_in_th_proc).start()
        self.to_host.setup_calling_user()  # enable req from host
        
    def cmd_in_th_proc(self):
        SlTrace.lg(f"USER: server_host_th_proc")
        self.from_host_server.run()

    """
    User based functions
    remotely requested from the host  
    """
    
    def snapshot(self, title=None):
        """ Create display snapshot
        :title: display title
        """
    
        SlTrace.lg(f"USER: snapshot(self, title={title})")
        SlTrace.lg(f"wx.CallAfter(self.snapshot_direct, title={title}")
        wx.CallAfter(self.snapshot_direct, title=title)
        #self.snapshot_direct(title=title)

    def snapshot_direct(self, title=None):
        """ Direct call, from event processor
        :title: display title
        """
        
        SlTrace.lg(f"USER: snapshot_direct(self, title={title}) direct call")
        if self.adw is None:
            SlTrace.lg("USER: AudioDrawWindow not set - snapshot ignored")
            return
        
        adw = self.adw.create_audio_window(title=title)
        self.snapshots.append(adw)
            
    def get_cell_specs(self,
                        win_fract=True, 
                        x_min=None, y_min=None,
                        x_max=None, y_max=None,
                        n_cols=None, n_rows=None):
        """ Get cell specs from remote tk canvas
        :returns: list of cell specs (ix,iy,color)
        """
        SlTrace.lg(f"""TkRPCUser:get_cell_specs(win_fract={win_fract}, 
                        x_min={x_min}, y_min={y_min},
                        x_max={x_max}, y_max={y_max},
                        n_cols={n_cols}, n_rows={n_rows})
                        """)        
        if self.simulated:
            return self.get_cell_specs_simulated(
                        x_min=x_min, y_min=y_min,
                        win_fract=win_fract, 
                        x_max=x_max, y_max=y_max,
                        n_cols=n_cols, n_rows=n_rows)
        
        call_num = self.to_host.get_cell_specs(
                    TK_EXECUTE_IN_MAIN_THREAD=True,
                    x_min=x_min, y_min=y_min,
                    x_max=x_max, y_max=y_max,
                    n_cols=n_cols, n_rows=n_rows)
        SlTrace.lg(f"TkRPCUser:get_cell_specs call_num:{call_num}")
        while True:
            ret = self.to_host.get_ret(call_num)
            if ret is not None:
                break
        SlTrace.lg(f"TkRPCUser:get_cell_specs[{call_num}] ret:{ret}")
        return ret    
    
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
        
        return self.to_host.is_inbounds_ixy(*ixy)

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
        
        call_num = self.to_host.get_cell_rect_tur(ix, iy,
                    TK_EXECUTE_IN_MAIN_THREAD=True)
        while True:
            ret = self.to_host.get_ret(call_num)
            if ret is not None:
                break
        SlTrace.lg(f"get_cell_rect_tur ret:{ret}")
        return ret    
    
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
        
        #return self.to_host.get_canvas_lims(win_fract)
        
        call_num = self.to_host.get_canvas_lims(win_fract,
                    TK_EXECUTE_IN_MAIN_THREAD=True)
        while True:
            ret = self.to_host.get_canvas_lims(call_num)
            if ret is not None:
                break
        SlTrace.lg(f"get_canvas_lims ret:{ret}")
        return ret    
                        
    
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
        return self.to_host.test_command(message)

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

    def set_adw(self, adw):
        """ Setup AudioDrawWindow, to support snapshot
            only first instance
        :adw: AudioWindow reference
        """
        SlTrace.lg(f"set_adw:{adw}")
        if self.adw is None:
            SlTrace.lg(f"set_adw({adw} first)")
            self.adw = adw
        
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