#wx_temp_code.py
# code snipits
# 07Nov2024 from wx_tk_bg_call.py
'''       
    def call_check(self):
        """ Call set background calls for pending tk main thread calls
            called back via self.call_bg_call
        """
        while True:
            if self.call_queue.not_empty():
                call_entry = self.call_queue.get()
                self.root.after(0, self.call_bg_call, call_entry)
            else:
                break
        self.root.after(int(self.call_ck_time*1000), self.call_check)

    def call_bg_call(self, call_entry):
        """ calling function, to be called 
        :call_entry: (function, *args, **kwargs)
        """
        function, args, kwargs = call_entry
        try:
            ret = function(*args, **kwargs)
            self.call_rets[self.call_num] = ret
        except:
            SlTrace.lg("exception in {function}, {args}, {kwargs}")
        finally:
            self.root.after(0, self.call_check)
'''
