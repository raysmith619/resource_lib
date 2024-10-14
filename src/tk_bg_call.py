#tk_bg_call.py 2024Sep2024  crs
""" 
Background caller to facilitate calling functions from within tkinter's main thread
Tkinter requires that some functions be executed in the main thread
"""

import tkinter as tk

class TkBgCall:
    
    def __init__(self, master, function=None):
        """ Setup for background call which
                1. Executes in master.mainloop()
                2. Returns when done, with the return value
        :master: master (root) object
        :function: function to be called
        """
        self.master = master
        self.function = function
    
    def bg_caller(self, function, args, kwargs):
        """ Calls function.  Signals when call is complete 
        """
        self.call_done = False
        ret = function(*args, **kwargs)
        self.call_ret = ret     # Save function return for delayed return
        self.call_done = True   # Signal call is done
        
    def call(self, function=None, *args, **kwargs):
        """ Call function in bacground, returning return value
        :function: function to call default: self.function
        :args: positional args
        :kwargs: keyword args
        :returns: function return value
        """
        if function is None:
            function = self.function
        self.master.after(0, self.bg_caller, function, args, kwargs)    
        while True:     # wait till function call is complete
            self.master.update_idletasks()
            self.master.update()
            if self.call_done:
                break
        return self.call_ret            
        
        
if __name__ == '__main__':
    def test_fn(a1, kwa="kwa_val"):
        """ Test function
        """
        print(f"test_fn({a1}, kwa_val={kwa})")
        return f"returns " f"test_fn({a1}, kwa_val={kwa})"

    root = tk.Tk()
            
    bc = TkBgCall(root)
    
    ret = bc.call(test_fn, "a1_val", kwa="kwa_val")
    print(f"ret={ret}")
    
    ret = bc.call(test_fn, "a1_second_call")
    print(f"ret={ret}")        