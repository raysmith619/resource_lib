#wx_to_tk.py    01Jan2024  crs Author
""" 
Communication between turtle/tkinter window display and
wxPython AudioDisplayWindow(s)
"""
import time
import multiprocessing as mp

class WxToTk:
    def __init__(self, base_obj):
        """ Setup communication between base process and
        new process.
        base_obj.new_proc is the callable target in the new process
            wxCommand requests from wx process to tk display
            wxCommandResp responses to wx command requests
            :base_obj: base process obj
        """
        qlen = 4
        self.base_obj = base_obj
        self.proc = mp.Process(target=self.base_obj.new_proc)
        self.cmd_queue = mp.Queue(qlen)      # Commands from new process
        self.cmd_resp_queue = mp.Queue(qlen)
        self.proc.start()


if __name__ == "__main__":
    import time

    class BaseObj:
        def new_proc():
            while True:
                print("Hi from new_proc")
                time.sleep(.5)
    
    base_obj = BaseObj()
    print("Starting WxTk")        
    nP = WxToTk(base_obj=base_obj)
    time.sleep(5)
    while True:
        print("Hi from base process")
        time.sleep(.3)