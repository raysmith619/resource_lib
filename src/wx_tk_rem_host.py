#tk_rem_host.py   24Jan2024  crs, renamed from wx_tk_rem_access.py
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

from wx_canvas_grid import CanvasGrid

from select_trace import SlTrace
class TkRemHost:
    """Host control containing tkinter canvas
    using socket TCP/IP
    """
    
    def __init__(self, canvas_grid, host='', port=50007,
                 cmd_time_ms= 500,
                 max_recv=2**16):
        """ Setup cmd interface
        :canvas_grid: tkinter CanvasGrid
        :host: name/id default: '' this machine
        :port: port number default: 50007
        :max_recv: maximum data received length in bytes
                    default: 2**16
        :cmd_time_ms: maximum between cmd check in seconds
                    default: .5 sec
        """
        self.canvas_grid = canvas_grid
        self.host = host
        self.port = port
        self.max_recv = max_recv
        self.cmd_time_ms = cmd_time_ms
        self.cmd_queue = queue.Queue()
        self.sockobj = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        self.sockobj.bind((host, port))
        self.sockobj.listen(5)
        SlTrace.lg("TkRemHost __init__()")            
        data_th = th.Thread(target=self.serv_th_proc)
        data_th.start()
        canvas_grid.base.after(0, self.data_proc)
        
    def serv_th_proc(self):
        while True:
            SlTrace.lg(f"HOST: serv_th_proc", "HOST")
            self.connection, self.address = self.sockobj.accept()
            SlTrace.lg(f"HOST:Got connection: address:{self.address}", "HOST")
            data = self.connection.recv(self.max_recv)
            if len(data) > 0:
                SlTrace.lg(f"HOST: data: {data}", "data", "HOST")
                self.cmd_queue.put(data)
            else:
                SlTrace.lg("HOST: No data length == 0", "HOST")
                break

    def data_proc(self, data=None):
        """ Process client data/command
        :data: command byte string - pickled command dictionary
            default: look at self.cmd_queue
                cmd dict:
                    'cmd_name' : command name string
                                'get_cell_specs'
                    
        """
        SlTrace.lg(f"HOST: data_proc: {data} queue.empty: {self.cmd_queue.empty()}", "HOSTdata_proc")
        if data is None:
            if not self.cmd_queue.empty():
                data = self.cmd_queue.get()
        if data is not None:
            cmd_dt = pickle.loads(data)
            SlTrace.lg(f"HOST: cmd_dt: {cmd_dt}", "HOSTcmds")
            SlTrace.lg(f"HOST: cmd_dt: {cmd_dt}", "HOSTcmds")
            cmd_name = cmd_dt['cmd_name']
            ret_dt = cmd_dt     # return an augmented dictionary
            if cmd_name == 'get_cell_specs':
                ret = self.get_cell_specs(
                    win_fract = self.if_attr(cmd_dt, 'win_fract'),
                    x_min = self.if_attr(cmd_dt, 'x_min'),
                    y_min = self.if_attr(cmd_dt, 'y_min'),
                    x_max = self.if_attr(cmd_dt, 'x_max'),
                    y_max = self.if_attr(cmd_dt, 'y_max'),
                    n_cols = self.if_attr(cmd_dt, 'n_cols'),
                    n_rows = self.if_attr(cmd_dt, 'n_rows'))
            elif cmd_name == 'get_canvas_lims':
                ret = self.get_canvas_lims()
            elif cmd_name == 'get_cell_rect_tur':
                ret = self.get_cell_rect_tur(
                    ix = self.if_attr(cmd_dt, 'ix'),
                    iy = self.if_attr(cmd_dt, 'iy'))
            elif cmd_name == 'test_command':
                ret = self.test_command(message=cmd_dt['message'])
            else:
                raise NameError(f"HOST: Unrecognized cmd: {cmd_name} in {cmd_dt}", "HOSTcmds")
        
            ret_dt['ret_val'] = ret
            SlTrace.lg(f"HOST: ret_dt:{ret_dt}", "HOSTcmds")
            ret_data = pickle.dumps(ret_dt)
            self.connection.send(ret_data)
        if not self.cmd_queue.empty():
            self.canvas_grid.base.after(0, self.data_proc)
        else:
            self.canvas_grid.base.after(self.cmd_time_ms, self.data_proc)

        
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

    def get_cell_specs(self,
                        win_fract=None, 
                        x_min=None, y_min=None,
                        x_max=None, y_max=None,
                        n_cols=None, n_rows=None):
        return self.canvas_grid.get_cell_specs(
                        win_fract=win_fract,
                        x_min=x_min, y_min=y_min,
                        x_max=x_max, y_max=y_max,
                        n_cols=n_cols, n_rows=n_rows)

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
    cvg.create_line(200,300,400,400, width=10, fill="green", tags=["green1","green2"])
    cvg.create_rectangle(200,200,300,300, fill="red")
    cvg.create_oval(100,200,250,300, fill="orange", tags="orange_tag")
    tkh = TkRemHost(cvg)
    cell_specs = tkh.get_cell_specs()
    SlTrace.lg(f"cell_specs: {cell_specs}")
    root.mainloop()
    