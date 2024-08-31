#wx_tk_rem_user.py  08Feb2024  crs, split from wx_tk_rem_access.py
""" Client/User part of wx_tk_rem_host.py, wx_tk_rem_user.py pair
Supporting communication betw
"""
import socket as sk
import threading as th
import queue
import pickle
import time

from select_trace import SlTrace
        
class TkRemUser:
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
        SlTrace.lg("TkRemUser() __init__() BEGIN")
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
        self.host_req_queue = queue.Queue()  # Command queue
        self.host_resp_queue = queue.Queue()  # response queue
        SlTrace.lg("TkRPCUser() __init__()")
        if simulated:
            self.make_simulated(figure=figure)
            return

        
        self.max_recv = max_recv
        self.cmd_time_ms = cmd_time_ms
        self.cmd_in_queue = queue.Queue()
        self.sock_in = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        SlTrace.lg(f"USER: self.sock_in.bind((host={host}, port_in={port_in}))")
        self.sock_in.bind((host, port_in))
        self.sock_in.listen(5)
        
        self.sock_out = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        self.sock_out.connect((self.host,self.port_out))

        cmd_in_th = th.Thread(target=self.cmd_in_th_proc)
        cmd_in_th.start()
        
    def cmd_in_th_proc(self):
        """ Process msgs from host
        """
        while True:
            SlTrace.lg(f"USER: cmd_in_th_proc")
            self.connection, self.address = self.sock_in.accept()
            SlTrace.lg(f"USER:Got connection: address:{self.address}")
            data = self.connection.recv(self.max_recv)
            if len(data) > 0:
                data_dt = pickle.loads(data)
                SlTrace.lg(f"USER: data_dt: {data_dt}", "USER")
                if "__host_req__" in data_dt:
                    self.cmd_proc(data_dt)
                else:
                    self.host_resp_queue.put(data_dt)
            else:
                SlTrace.lg("USER: No data length == 0", "USER")
                continue

    def cmd_proc(cmd_dt):
        """ Process command
        :cmd_dt: command dictionary
        """
        SlTrace.lg(f"cmd_proc: {cmd_dt}")
        SlTrace.lg("TBD implement commands from server")              
        
    def send_cmd(self, args):
        """ Send command(request) to host

        :args: command argument dictionary
        """
        if self.simulated:
            self.simulated_cmd = args
            return

        totalsent = 0
        SlTrace.lg(f"USER: send_cmd: args:{args}")
        data = pickle.dumps(args)
        while totalsent < len(data):
            sent = self.sock_out.send(data)
            SlTrace.lg(f"USER: sent:{sent} data:{data}")
            if sent > 0:
                totalsent += sent
            
            
        
    
    def get_resp_args(self):
        """ Get command response from host
        :returns: response args dictionary
        """
        if self.simulated:
            ret_dt = {}
            ret = "Simulated Response"
            ret_dt['ret_val'] = ret
            self.host_resp_queue.put(ret_dt)
            return self.host_resp_queue.get()
        
        data = self.host_resp_queue.get()
        return data
    
    def get_cell_specs(self, 
                        win_fract=True, 
                        x_min=None, y_min=None,
                        x_max=None, y_max=None,
                        ncols=None, nrows=None):
        """ Get cell specs from remote tk canvas
        :returns: list of cell specs (ix,iy,color)
        """        
        if self.simulated:
            return self.get_cell_specs_simulated(
                        win_fract=win_fract, 
                        x_min=x_min, y_min=y_min,
                        x_max=x_max, y_max=y_max,
                        ncols=ncols, nrows=nrows)
        
        args = locals()
        del(args['self'])
        args['cmd_name'] = 'get_cell_specs'
        self.send_cmd(args)
        ret_dt = self.get_resp_args()
        SlTrace.lg(f"USER: cmd_resp_data: {ret_dt}", "USER:data")
        return ret_dt['ret_val']
    
    def get_cell_specs_simulated(self, 
                        win_fract=True, 
                        x_min=None, y_min=None,
                        x_max=None, y_max=None,
                        ncols=None, nrows=None):
        """ Get cell specs from remote tk canvas
        :returns: list of cell specs (ix,iy,color)
        """        
        return self.sim_cg.get_cell_specs(
                        win_fract=win_fract, 
                        x_min=x_min, y_min=y_min,
                        x_max=x_max, y_max=y_max,
                    n_cols=ncols, n_rows=nrows)


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
                        
        args = locals()
        del(args['self'])
        args['cmd_name'] = 'is_inbounds_ixy'
        self.send_cmd(args)
        ret_dt = self.get_resp_args()
        return ret_dt['ret_val']

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
        
        args = locals()
        del(args['self'])
        args['cmd_name'] = 'get_cell_rect_tur'
        self.send_cmd(args)
        ret_dt = self.get_resp_args()
        SlTrace.lg(f"USER: ret_dt: {ret_dt}", "USER:data")
        return ret_dt['ret_val']
    
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
                        
        args = locals()
        del(args['self'])
        args['cmd_name'] = 'get_canvas_lims'
        self.send_cmd(args)
        ret_dt = self.get_resp_args()
        SlTrace.lg(f"USER: ret_dt: {ret_dt}", "USER:data")
        return ret_dt['ret_val']
    
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
        args = {}        
        args['cmd_name'] = "test_command"
        args['message'] = message
        self.send_cmd(args)
        ret_dt = self.get_resp_args()
        return ret_dt['ret_val']

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
    
    tkr = TkRemUser(simulated=True)
    for msg in ["t1","t2","t3"]:
        SlTrace.lg(f"test_command({msg})")
        res = tkr.test_command(msg)
        SlTrace.lg(f"result: {res}")
    
    if len(sys.argv)  > 1:
        res = tkr.get_cell_specs()
        SlTrace.lg(f"cell_specs: {res}")