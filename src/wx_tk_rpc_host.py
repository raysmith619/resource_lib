#wx_tk_rpc_host.py   24Jan2024  crs, renamed from wx_tk_rem_access.py
""" Remote access to tk canvas information
tkinter canvas resides in host process
wxPython AudioDrawWindow instance(s) reside in client
processing is done in threads to avoid locking
"""
import tkinter as tk
import socket as sk
import threading as th
import queue
import pickle
import time

from wx_rpc import RPCServer
from wx_rpc import RPCClient

from wx_canvas_grid import CanvasGrid

from select_trace import SlTrace
from tk_bg_call import TkBgCall

class TkRPCHost:
    HOST_PORT = 50010
    """Host control containing tkinter canvas
    using socket TCP/IP
    """
    
    def __init__(self, canvas_grid, root=None, host_name='localhost',
                 host_port=None,
                 cmd_time_ms= 500,
                 max_recv=2**16):
        """ Setup cmd interface
        :canvas_grid: tkinter CanvasGrid
        :root: tkinter main window, used for update() calls
        :host_name: name/id default: '' this machine
        :host_port: port number where we accept unsolicited input
                        default: 50020
        :max_recv: maximum data received length in bytes
                    default: 2**16
        :cmd_time_ms: maximum between cmd check in seconds
                    default: .5 sec
        """
        self.sock_out = None    #  setup once connection is establised 
        self.canvas_grid = canvas_grid
        self.root = root
        self.host_name = host_name
        if host_port is None:
            host_port = TkRPCHost.HOST_PORT
        self.host_port = host_port
        self.max_recv = max_recv
        self.cmd_time_ms = cmd_time_ms
        self.user_is_ready = False      # Set True when user is ready to accept calls
        SlTrace.lg(f"self.to_host_server ="
                   f" RPCServer({self.host_name}, {self.host_port})")
        self.to_host_server = RPCServer(self.host_name, self.host_port)

        self.to_host_server.registerMethod(self.setup_calling_user)
        self.to_host_server.registerMethod(self.get_canvas_lims)
        self.to_host_server.registerMethod(self.get_cell_rect_tur)
        self.to_host_server.registerMethod(self.get_cell_specs)

        th.Thread(target=self.cmd_in_th_proc).start()
        
        
        SlTrace.lg("TkRPCHost __init__()")            
        
    def cmd_in_th_proc(self):
        SlTrace.lg(f"HOST: server_host_th_proc", "HOST")
        self.to_host_server.run()

    def setup_calling_user(self, user_name=None, user_port=None):
        """ Setup calling user - indicate user is ready to be called
        :user_name: user name default: our host name
        :user_port: user port default: generated from input port
        """
        if user_name is None:
            user_name = self.host_name
        if user_port is None:
            user_port = self.host_port+1
        SlTrace.lg(f"self.from_host_client ="
                   f" RPCClient({user_name}, {user_port})")
        self.from_host_client = RPCClient(user_name, user_port)
        self.from_host_client.connect()
        self.user_is_ready = True
        SlTrace.lg("User is ready to accept calls")
    
    def wait_for_user(self):
        """ Wait till user is ready
        """
        while not self.user_is_ready:
            self.root.update()
                        
    def snapshot(self, title=None):
        """ Create display snapshot
        :title: display title
        """
        self.wait_for_user()
        # must call from main thread
        SlTrace.lg(f"self.root.after(0, self.from_host_client.snapshot, {title})")
        self.root.after(0, self.from_host_client.snapshot, title)
        

        
    def if_attr(self, cmd_dt, attr_name):
        """ Return attr value from dict if present else None
        :cmd_dt: command dictionary
        :attr_name: name of attribute
        :returns: attr value from dict iff attr_name present
                    else None
        """
        ret = None      # returned if attr_name not present
        if attr_name in cmd_dt:
            ret = cmd_dt[attr_name]
        return ret

    def make_bg_call(self, call_name):
        """ Invoke call to be waited on
        """
        bg = TkBgCall(call_name)
        
        self.root.after(0, bg.args)
        
    def get_cell_specs(self,
                        win_fract=None, 
                        x_min=None, y_min=None,
                        x_max=None, y_max=None,
                        n_cols=None, n_rows=None):
        bg = TkBgCall(self.root)
        ret = bg.call(self.canvas_grid.get_cell_specs,
                        win_fract=win_fract, 
                        x_min=x_min, y_min=y_min,
                        x_max=x_max, y_max=y_max,
                        n_cols=n_cols, n_rows=n_rows)
        return ret
        

    def get_cell_rect_tur(self,
                        ix=None, 
                        iy=None):
        return self.canvas_grid.get_cell_rect_tur(
                        ix=ix,
                        iy=iy)
            

    def get_canvas_lims(self):
        """ Get canvas limits - internal values, to which
        self.base.find_overlapping(cx1,cy1,cx2,cy2) obeys.
        NOTE: These values, despite some vague documentation, may be negative
              to adhere to turtle coordinate settings.
        
        :returns: internal (xmin, xmax, ymin, ymax)
        """
        return self.canvas_grid.get_canvas_lims()
        
    def test_command(self, message="No Message Sent"):
        """ Do server test command
        :message: test message default: "No Message Sent"
        :returns: Answer: <message>
        """
        return "Answer: " + message       

if __name__ == '__main__':

    import tkinter as tk
    root = tk.Tk()

    cvg = CanvasGrid(root, height=450, width=450)
    cvg.create_line(0,0,200,300, width=10, fill="blue", tags="blue_tag")
    cvg.show_canvas()
    cvg.create_line(200,300,400,400, width=10, fill="green", tags=["green1","green2"])
    cvg.create_rectangle(200,200,300,300, fill="red")
    cvg.create_oval(100,200,250,300, fill="orange", tags="orange_tag")
    port = None
    tkh = TkRPCHost(cvg)
    cell_specs = tkh.get_cell_specs()
    SlTrace.lg(f"cell_specs: {cell_specs}")
    '''
    '''
    root.mainloop()
    