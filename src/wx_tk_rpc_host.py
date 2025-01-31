#wx_tk_rpc_host.py   24Jan2024  crs, renamed from wx_tk_rem_access.py
""" Remote access to tk canvas information
tkinter canvas resides in host process
wxPython AudioDrawWindow instance(s) reside in client
processing is done in threads to avoid locking
"""
import tkinter as tk
import socket as sk
#from wx_tk_rpc_server import TkRPCServer
import queue
import pickle
import time
import threading as th
import copy

#from wx_rpc import RPCServer
from wx_bg_rpc import RPCServer
from wx_rpc import RPCClient

from wx_canvas_grid import CanvasGrid

from select_trace import SlTrace
from wx_tk_bg_call import TkBgCall

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
        self.canvas_grid_snapshots = []     # Snapshots, if any
        self.root = root
        self.host_name = host_name
        if host_port is None:
            host_port = TkRPCHost.HOST_PORT
        self.host_port = host_port
        self.max_recv = max_recv
        self.cmd_time_ms = cmd_time_ms
        self.user_is_ready = False      # Set True when user is ready to accept calls
        self.snapshot_is_complete = True    # Set if no waiting required

        self.bg = TkBgCall(root, canvas_grid=self.canvas_grid,
                canvas_grid_snapshots=self.canvas_grid_snapshots)
        SlTrace.lg(f"self.to_host_server ="
                   f" TkRPCServer({self.host_name}, {self.host_port})", "HOST")
        self.to_host_server = RPCServer(self.bg, self.host_name, self.host_port)

        self.to_host_server.registerMethod(self.setup_calling_user)
        self.to_host_server.registerMethod(self.get_canvas_lims)
        self.to_host_server.registerMethod(self.get_cell_rect_tur)
        self.to_host_server.registerMethod(self.get_cell_specs)
        self.to_host_server.registerMethod(self.snapshot_complete)
        self.to_host_server.registerMethod(self.test_dummy)
        self.to_host_server.registerMethod(self.get_ret)
        th.Thread(target=self.cmd_in_th_proc).start()

        
        
        SlTrace.lg("TkRPCHost __init__()", "HOST")            

    def test_dummy(self, *args, **kwargs):
        """ dummy test function
        """
        SlTrace.lg(f"test_dummy({args}, {kwargs})", "HOST")
        return ""
                                  
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
                   f" RPCClient({user_name}, {user_port})", "HOST")
        self.from_host_client = RPCClient(user_name, user_port)
        self.from_host_client.connect()
        self.user_is_ready = True
        SlTrace.lg("User is ready to accept calls", "HOST")
    
    def wait_for_user(self):
        """ Wait till user is ready
        """
        while not self.user_is_ready:
            self.tk_event_check()
    
    def wait_for_snapshot(self):
        """ Wait till snapshot is ready
        """
        while not self.snapshot_complete:
            self.tk_event_check()
            
    def tk_event_check(self):
        """ Allow tk event processing
        """                        
        self.root.update_idletasks()
        self.root.update()
        
    def snapshot(self, title=None):
        """ Create display snapshot
        :title: display title
        """
        self.wait_for_user()
        self.wait_for_snapshot()    # incase double snapshot
        # must call from main thread
        self.snapshot_is_complete = False
        SlTrace.lg(f"self.from_host_client.snapshot({title})", "snapshot")
        ###snapshot = copy.deepcopy(self.canvas_grid)   # fails
        snapshot = self.canvas_grid.copy()
        snapshot_str = snapshot.canvas_show_items()
        sno = len(self.canvas_grid_snapshots)+1
        SlTrace.lg(f"\nsnapshot[{sno}]: {snapshot_str}", "snapshot")
        self.canvas_grid_snapshots.append(snapshot)
        self.from_host_client.snapshot(f"{sno}: {title}",
                        snapshot_num=sno)
        self.wait_for_snapshot()    # Block till completed

    def snapshot_complete(self):
        """ Signal snapshot process has completed
        """        
        self.snapshot_is_complete = True
        
        
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

    def get_ret(self, call_num):
        """ Get return value from call if availaible, None if not
        :call_num: unique call number
        """
        return self.bg.get_ret(call_num)
            
    def get_cell_specs(self,
                        snapshot_num=None,
                        win_fract=None, 
                        x_min=None, y_min=None,
                        x_max=None, y_max=None,
                        n_cols=None, n_rows=None):

        cell_specs = self.canvas_grid.get_cell_specs()
        SlTrace.lg(f"\nTkRPCHost:canvas_grid.get_cell_specs cell_specs(): {cell_specs}", "HOST")
        if snapshot_num is None or snapshot_num == 0:
            canvas_grid = self.canvas_grid
        else:
            canvas_grid = self.canvas_grid_snapshots
        ret = canvas_grid.get_cell_specs(
                        win_fract=win_fract, 
                        x_min=x_min, y_min=y_min,
                        x_max=x_max, y_max=y_max,
                        n_cols=n_cols, n_rows=n_rows)
        SlTrace.lg(f"""nTkRPCHost: canvas_grid.get_cell_specs(win_fract={win_fract}, 
                        x_min={x_min}, y_min={y_min},
                        x_max={x_max}, y_max={y_max},
                        n_cols={n_cols}, n_rows={n_rows})
                    ret : {ret}
                    """, "cell_specs")        
        return ret
        #return cell_specs   # TFD return strait from grid
    '''        
    def get_cell_specs_set(self,
                        win_fract=None, 
                        x_min=None, y_min=None,
                        x_max=None, y_max=None,
                        n_cols=None, n_rows=None):
        call_num = self.bg.set_call(self.get_cell_specs,
                        win_fract=win_fract, 
                        x_min=x_min, y_min=y_min,
                        x_max=x_max, y_max=y_max,
                        n_cols=n_cols, n_rows=n_rows)
        ret = self.get_ret(call_num)
        return ret
    '''    

    def get_cell_rect_tur(self,
                        ix=None, 
                        iy=None):

        ret = self.canvas_grid.get_cell_rect_tur(
                        ix,iy)
        SlTrace.lg(f"\nTkRPCHost:get_cell_rect_tur({ix},{iy}) ret: {ret}", "cell_specs")
        return ret     # TFD
            

    def get_canvas_lims(self):
        """ Get canvas limits - internal values, to which
        self.base.find_overlapping(cx1,cy1,cx2,cy2) obeys.
        NOTE: These values, despite some vague documentation, may be negative
              to adhere to turtle coordinate settings.
        
        :returns: internal (xmin, xmax, ymin, ymax)
        """
        ret = self.canvas_grid.get_canvas_lims()
        return ret
        
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
    SlTrace.lg(f"cell_specs: {cell_specs}", "cell_specs")
    '''
    '''
    root.mainloop()
    