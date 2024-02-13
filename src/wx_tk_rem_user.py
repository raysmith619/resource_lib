#wx_tk_rem_user.py  08Feb2024  crs, split from wx_tk_rem_access.py
""" Client/User part of wx_tk_rem_host.py, wx_tk_rem_user.py pair
Supporting communication betw
"""
import socket as sk
import threading as th
import pickle
import time

from select_trace import SlTrace
        
class TkRemUser:
    """User (remote) control requesting canvas information
    Using socket client
    """
    def __init__(self, host='localhost', port=50007,
                 max_recv=2**16, simulated=False):
        """ Handle user (wxPython) side of communications
        :host: host address default: localhost - same machine
        :port: port number default: 50007
        :max_recv: maximum data recieved length in bytes
                    default: 2**16
        :simulated: True: simulate tk input default: False
        """
        SlTrace.lg("TkRemUser() __init__() BEGIN")
        self.host = host
        self.port = port
        self.max_recv = max_recv
        self.simulated = simulated
        SlTrace.lg("TkRemUser() __init__()")
    
    def send_cmd_data(self, data):
        """ Send command(request) to host

        :data: command as byte string
        """
        if self.simulated:
            return
        self.sockobj = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        try:
            SlTrace.lg(f"sockobj.connect(({self.host},{self.port}))")
            self.sockobj.connect((self.host,self.port))
        except:
            SlTrace.lg(f"connect(({self.host},{self.port}) failed")
        totalsent = 0
        while totalsent < len(data):
            sent = self.sockobj.send(data)
            SlTrace.lg(f"sent:{sent} data:{data}", "data")
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
        args['self'] = None
        args['cmd_name'] = 'get_cell_specs'
        SlTrace.lg(f"args:{args}")
        cmd_data = pickle.dumps(args)
        self.send_cmd_data(cmd_data)
        cmd_resp_data = self.get_resp_data()
        SlTrace.lg(f"cmd_resp_data: {cmd_resp_data}", "data")
        ret_dt = pickle.loads(cmd_resp_data)
        return ret_dt['ret_val']
    
    def test_command(self, 
                        message="Test message"):
        """ Do test message
        :message: test message default:"Test message"
        :returns: "Answer: <message>
        """
        args = {}        
        args['cmd_name'] = "test_command"
        args['message'] = message
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

if __name__ == '__main__':
    import sys
    
    tkr = TkRemUser()
    for msg in ["t1","t2","t3"]:
        SlTrace.lg(f"test_command({msg})")
        res = tkr.test_command(msg)
        SlTrace.lg(f"result: {res}")
    
    if len(sys.argv)  > 1:
        res = tkr.get_cell_specs()
        SlTrace.lg(f"cell_specs: {res}")