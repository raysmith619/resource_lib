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

from wx_canvas_grid import CanvasGrid

from select_trace import SlTrace
class TkRPCHost:
    """Host control containing tkinter canvas
    using socket TCP/IP
    """
    
    def __init__(self, canvas_grid, host='',
                 port=None,
                 port_in=None,
                 port_out=None,
                 port_diff=20,
                 port_inc=None,
                 cmd_time_ms= 500,
                 max_recv=2**16):
        """ Setup cmd interface
        :canvas_grid: tkinter CanvasGrid
        :host: name/id default: '' this machine
        :port_diff:  diff between port_in and port_out
                default: 20
        :port: shorthand for port_in
        :port_in: port number where we accept unsolicited input
                        default: 50020
        :port_out: port number we send unsolicited output
                        default: port_in+port_diff
        :port_inc: increment to port_in, port_out
                        default: no change
        :max_recv: maximum data received length in bytes
                    default: 2**16
        :cmd_time_ms: maximum between cmd check in seconds
                    default: .5 sec
        """
        self.sock_out = None    #  setup once connection is establised 
        self.canvas_grid = canvas_grid
        self.host = host
        if port is not None:
            port_in = port
        if port_in is None:
            port_in = 50020
        if port_out is None:
            port_out = port_in+port_diff
        if port_inc is not None:
            port_in += port_inc
            port_out += port_inc
        self.port_in = port_in
        self.port_out = port_out
        
        self.max_recv = max_recv
        self.cmd_time_ms = cmd_time_ms
        
        self.to_host_server = RPCServer(self.host, self.port_in)

        self.to_host_server.registerMethod(self.get_canvas_lims)
        self.to_host_server.registerMethod(self.get_cell_rect_tur)
        self.to_host_server.registerMethod(self.get_cell_specs)

        server_host_th = th.Thread(target=self.cmd_in_th_proc)
        server_host_th.start()
        SlTrace.lg("TkRPCHost __init__()")            
        
    def cmd_in_th_proc(self):
        SlTrace.lg(f"HOST: server_host_th_proc", "HOST")
        self.to_host_server.run()
 
    def host_req(self, req_dict):
        """ Request from host, e.g. snapshot
        :req_dict: request dictionary
        """
        req_dict["__host_request__"] = "HOST_REQUEST"
        req_data = pickle.dumps(req_dict)
        self.sock_out.connect((self.host, self.port_out))
        self.sock_out.send(req_data)
        req_resp_data = self.sock_out.recv(self.max_recv)
        #TBD

    def snapshot(self, title=None, bdlist=None):
        """ Create display snapshot
        :title: display title
        :bdlist: braill display list text string
        """
        host_req_dict = {"title": title,
                         "bdlist":bdlist}
        self.host_req(req_dict=host_req_dict)

        
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
    cvg.show_canvas()
    cvg.create_line(200,300,400,400, width=10, fill="green", tags=["green1","green2"])
    cvg.create_rectangle(200,200,300,300, fill="red")
    cvg.create_oval(100,200,250,300, fill="orange", tags="orange_tag")
    port = 50007+2
    tkh = TkRPCHost(cvg, port=port)
    cell_specs = tkh.get_cell_specs()
    SlTrace.lg(f"cell_specs: {cell_specs}")
    '''
    '''
    root.mainloop()
    