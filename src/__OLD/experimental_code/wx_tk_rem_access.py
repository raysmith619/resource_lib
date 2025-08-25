#tk_rem_access.py   24Jan2024  crs, Author
""" Remote access to tk canvas information
tkinter canvas resides in host process
wxPython AudioDrawWindow instance(s) reside in client
processing is done in threads to avoid locking
"""
import socket as sk
import threading as th
import pickle
import time

from select_trace import SlTrace
class TkRemHost:
    """Host control containing tkinter canvas
    using socket TCP/IP
    """
    
    def __init__(self, canvas_grid, host='', port=50007,
                 max_recv=8192):
        """ Setup cmd interface
        :canvas_grid: tkinter CanvasGrid
        :host: name/id default: '' this machine
        :port: port number default: 50007
        :max_recv: maximum data received length in bytes
                    default: 8192
        """
        self.canvas_grid = canvas_grid
        self.host = host
        self.port = port
        self.max_recv = max_recv
        self.sockobj = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        self.sockobj.bind((host, port))
        self.sockobj.listen(5)
                    
        data_th = th.Thread(target=self.serv_th_proc)
        data_th.start()
        
    def serv_th_proc(self):
        while True:
            self.connection, self.address = self.sockobj.accept()
            SlTrace.lg(f"Got connection: address:{self.address}")
            while True:
                data = self.connection.recv(self.max_recv)
                SlTrace.lg(f"data: {data}")
                if data:
                    self.data_proc(data)
                else:
                    time.sleep(.1)

    def data_proc(self, data):
        """ Process client data/command
        :data: command byte string - pickled command dictionary
                cmd dict:
                    'cmd_name' : command name string
                                'get_cell_specs'
                    
        """
        cmd_dt = pickle.loads(data)
        cmd_name = cmd_dt['cmd_name']
        ret_dt = cmd_dt     # return an augmented dictionary
        if cmd_name == 'get_cell_specs':
            ret = self.get_cell_specs(
                x_min = self.if_attr(cmd_dt, 'x_min'),
                y_min = self.if_attr(cmd_dt, 'y_min'),
                x_max = self.if_attr(cmd_dt, 'x_max'),
                y_max = self.if_attr(cmd_dt, 'y_max'),
                ncols = self.if_attr(cmd_dt, 'ncols'),
                nrows = self.if_attr(cmd_dt, 'nrows'))
        elif cmd_name == 'test_command':
            ret = self.test_command(message=cmd_dt['message'])
        else:
            raise NameError(f"Unrecognized cmd: {cmd_name} in {cmd_dt}")
        
        ret_dt['ret_val'] = ret
        ret_data = pickle.dumps(ret_dt)
        self.connection.send(ret_data)
        
    def if_attr(self, cmd_dt, attr_name):
        """ Return attr value from dict if present else None
        :cmd_dt: command dictionary
        :attr_name: name of attribute
        :returns: attr value from dict iff attr_name present
                    else None
        """
        ret = None      # returned if attr_name not present
        if hasattr(cmd_dt, attr_name):
            ret = cmd_dt[attr_name]
        return ret

    def get_cell_specs(self, 
                        x_min=None, y_min=None,
                        x_max=None, y_max=None,
                        ncols=None, nrows=None):
        """ Get braille cell specifications
        (ix,iy,color) tuple from tk
        canvas items based on selected grid
        :returns: list of (ix,iy,color) tuples
        """
        return self.canvas_grid.get_cell_specs(
                        x_min=None, y_min=None,
                        x_max=None, y_max=None,
                        ncols=None, nrows=None)
    
    def test_command(self, message=)        
        
class TkRemUser:
    """User (remote) control requesting canvas information
    Using socket client
    """
    def __init__(self, host='localhost', port=50007,
                 max_recv=8192, simulated=False):
        """ Handle user (wxPython) side of communications
        :host: host address default: localhost - same machine
        :port: port number default: 50007
        :max_recv: maximum data recieved length in bytes
                    default: 8192
        :simulated: True: simulate tk input default: False
        """
        SlTrace.lg("TkRemUser() __init__() BEGIN")
        self.host = host
        self.port = port
        self.max_recv = max_recv
        self.simulated = simulated
        if self.simulated:
            self.sockobj = None
        else:
            self.sockobj = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
            try:
                self.sockobj.connect((self.host,self.port))
            except:
                SlTrace.lg(f"connect(({self.host},{self.port}) failed")
        SlTrace.lg("TkRemUser() __init__()")
    
    def send_cmd_data(self, data):
        """ Send command(request) to host

        :data: command as byte string
        """
        totalsent = 0
        while totalsent < len(msg):
            sent = self.sockobj.send(data)
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent += sent
            
        
    
    def get_resp_data(self):
        """ Get command response from host
        :returns: response byte data
        """
        data = self.sockobj.recv(self.max_recv)
        return data
    
    def get_cell_specs(self, 
                        x_min=None, y_min=None,
                        x_max=None, y_max=None,
                        ncols=None, nrows=None):
        """ Get cell specs from remote tk canvas
        :returns: list of cell specs (ix,iy,color)
        """        
        if self.simulated:
            return self.simulated_get()
        
        args = locals()
        args['cmd_name'] = "get_braille_cells"
        cmd_data = pickle.dumps(args)
        self.send_cmd_data(cmd_data)
        cmd_resp_data = self.get_resp_data()
        ret_dt = pickle.loads(cmd_resp_data)
        return ret_dt['ret_val']
    
    def test_command(self, 
                        message="Test message"):
        """ Do test message
        :message: test message default:"Test message"
        :returns: "Answer: <message>
        """        
        args = locals()
        args['cmd_name'] = "test_command"
        cmd_data = pickle.dumps(args)
        self.send_cmd_data(cmd_data)
        cmd_resp_data = self.get_resp_data()
        ret_dt = pickle.loads(cmd_resp_data)
        return ret_dt['ret_val']

    def simulated_get(self):
        """ Simulated get cells
        """
        from braille_cell_text import BrailleCellText
        from wx_braille_cell_list import BrailleCellList
        
        spokes_picture="""
        ,,,,,,,,,,,iii
        ,,,,,,,,,,iiiii
        ,,,,,,,,,,iiiii,,,,,,vvv
        ,,,,,,,,,,iiiii,,,,,vvvvv
        ,,,,,,,,,,,,ii,,,,,,vvvvv
        ,,,bb,,,,,,,,i,,,,,,vvvvv
        ,,bbbbb,,,,,,i,,,,,vv
        ,,bbbbb,,,,,,i,,,,vv
        ,,bbbbbbb,,,,ii,,vv
        ,,,,,,,,bbbb,,i,vv,,,,,,,,rr
        ,,,,,,,,,,bbbbivv,,,,,,,,rrrr
        ,,,,,,,,,,,,,bvvrrrrrrrrrrrrr
        ,,,,,,,,,,ggggyoo,,,,,,,,rrrr
        ,,,,,,,,gggg,,y,oo,,,,,,,,rr
        ,,ggggggg,,,,yy,,oo
        ,,ggggg,,,,,,y,,,,oo
        ,,ggggg,,,,,,y,,,,,oo
        ,,,gg,,,,,,,,y,,,,,,ooooo
        ,,,,,,,,,,,,yy,,,,,,ooooo
        ,,,,,,,,,,yyyyy,,,,,ooooo
        ,,,,,,,,,,yyyyy,,,,,,ooo
        ,,,,,,,,,,yyyyy
        ,,,,,,,,,,,yyy
        """
        spokes_bct = BrailleCellText(text=spokes_picture)
        spokes_cells = spokes_bct.get_cells()
        return spokes_cells
