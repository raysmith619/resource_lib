#wx_tk_bg_call.py 20Sep2024  crs
""" 
Background caller to facilitate calling functions from within tkinter's main thread
Tkinter requires that some functions be executed in the main thread
"""
import queue
import tkinter as tk
import copy

from select_trace import SlTrace

""" call entry """
class BgCallEntry:
    def __init__(self, bg_call, function, args, kwargs,
                 root=None, call_num=None, ret=None):
        """ Setup call entry
        :bg_call: reference to caller (TgBgCall)
        :function: function to be called from main thread
        :args: pocition args
        :kwargs: key word args
        :call_num: unique call number default: generated
        :ret: function return
        """
        self.bg_call = bg_call
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.root = root
        call_num = bg_call.next_call_num(call_num)
        self.call_num = call_num
        self.ret = ret
        self.done = False       # Set when call complete

    def get_name(self):
        """ Get function name
        """
        return self.function.__name__
       
    def __str__(self):
        st = f"BgCallEntry[{self.call_num}]: {self.get_name()} {self.args} {self.kwargs}"
        return st
        
class TkBgCall:
    
    def __init__(self, root, canvas_grid=None,
                 canvas_grid_snapshots = [], check_queue_int=10):
        """ Setup for background call in which runctions are called
        :root: root (root) object
        :canvas_grid: base canvas
        :check_int: queue check interval (msec)
        """
        self.root = root
        self.canvas_grid = canvas_grid
        self.canvas_grid_snapshots = canvas_grid_snapshots
        self.check_queue_int = check_queue_int
        self.call_num = 0               # Unique call #
        self.call_entry_d = {}          # dictionary of pending calls
        self.call_rets = {}             # Dictionary by call_num of pending call returns
        self.call_queue = queue.Queue()
        self.call_ret_queue = queue.Queue()
        cell_specs = self.canvas_grid.get_cell_specs()
        SlTrace.lg(f"TkBgCall: cell_specs: {cell_specs}")
        SlTrace.lg()
        self.set_check_queue()

    def set_check_queue(self):
        """Set check interval"
        """
        self.root.after(self.check_queue_int, self.check_queue)
                
    def check_queue(self):
        """ check for and process any pending commands for background
        """
        SlTrace.lg("check_queue", "check_queue")
        if not self.call_queue.empty():
            call_entry = self.call_queue.get()
            SlTrace.lg(f"check_queue call_entry:{call_entry}", "check_queue")
            self.bg_caller(call_entry)
        self.set_check_queue()    
            

    def next_call_num(self, call_num=None):
        """ Get/adjust next call number
        :call_num: next call number
            default: increase number by one
        :returns: updated call number
        """
        if call_num is None:
            call_num = self.call_num + 1
        self.call_num = call_num
        return self.call_num


    
    def bg_caller(self, call_entry):
        """ Calls function.  Signals when call is complete
        MUST BE CALLED FROM MAIN THREAD
        :call_num: index in self.call_entry_d of function entry 
        """
        SlTrace.lg(f"bg_caller calling {call_entry}")
        name = call_entry.get_name()
        if name == "get_cell_specs":
            cell_specs = self.canvas_grid.get_cell_specs()
            SlTrace.lg(f"\nTkBgCall:bg_caller cell_specs: {cell_specs}")
            SlTrace.lg()
            if "snapshot_num" in call_entry.kwargs:
                snapshot_num = call_entry.kwargs["snapshot_num"]                
                del call_entry.kwargs["snapshot_num"]
                if snapshot_num is not None and snapshot_num > 0:
                    canvas_grid = self.canvas_grid_snapshots[snapshot_num-1]
                else:
                    canvas_grid = self.canvas_grid
            else:
                canvas_grid = self.canvas_grid
            retorig = canvas_grid.get_cell_specs(*call_entry.args,
                                                      **call_entry.kwargs)
        elif name == "get_rect_tur":
            rect_tur = self.canvas_grid.get_cell_rect_tur()
            SlTrace.lg(f"\nTkBgCall:bg_caller rec_tur: {rect_tur}")
            SlTrace.lg()
            retorig = rec_tur
        else:
            retorig = call_entry.function(*call_entry.args, **call_entry.kwargs)
            SlTrace.lg(f"""\n TkBgCall::bg_caller: call_entry: {call_entry}
                        \n retorig: {retorig}
                    """)
            
        SlTrace.lg(f"TkBgCall.bg_caller: retorig:{retorig}")
        ret = copy.copy(retorig)
        SlTrace.lg(f"TkBgCall:bg_caller ret: {ret}")
        self.call_rets[call_entry.call_num] = ret
        call_entry.ret = ret     # Save function return for delayed return
        call_entry.done = True   # Set call completion indicator
        self.call_ret_queue.put(call_entry)
    
    def set_call(self, function, *args, **kwargs):
        """ Setup call function and args in dictionary to be called in the future in bacground
            Do background till function completes
            Return function's return value
        :function: function to call
        :args: positional args
        :kwargs: keyword args
        :returns: unique call nunber
        """
        call_entry = BgCallEntry(self, function, args, kwargs, root=self.root)
        SlTrace.lg(f"call_queue.put {call_entry}")
        self.call_queue.put(call_entry)
        return call_entry.call_num
       
    def get_ret(self, call_num):
        """ Get call return
        :call_num: unique call number
        :returns: call's return, None if not ready
        """
        if call_num in self.call_rets:
            return self.call_rets[call_num]
        
        return None
    def wait_completion(self, call_num):
        """ Wait till call completed, giving background time to continue
        :call_num: call number
        """
        while True:
            self.root.update()
            call_ret = self.get_ret(call_num)
            if call_ret is not None:
                break

'''                    
    def call(self, *args, **kwargs):
        """ TBD catch unexpected call
        """
        SlTrace.lg(f"Unexpected call {args}, {kwargs}")
'''
        
if __name__ == '__main__':
    def test_fn(root, *args, **kwargs):
        """ Test function
        :root: window
        """
        btn = tk.Button(root, text = f'Click me !\n {args}', 
                command = root.destroy) 

        # Set the position of button on the top of window 
        btn.pack(side = 'top')     
        print(f"test_fn({args}, kwargs={kwargs})")
        return f"returns " f"test_fn({args}, kwargs={kwargs})"

    root = tk.Tk()
            
    bg = TkBgCall(root)
    
    call_num = bg.set_call(test_fn, root,  "a1_val", kwa="kwa_val")
    print(f"call_num={call_num}")
    bg.wait_completion(call_num)
    ret = bg.get_ret(call_num)
    print(f"call_ret: {ret}\n")

    call_num = bg.set_call(test_fn, root, "a1_second_call")
    print(f"call_num={call_num}")
    bg.wait_completion(call_num)
    ret = bg.get_ret(call_num)
    print(f"call_ret: {ret}\n")
