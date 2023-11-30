#wxtk.py    29Nov2023  crs, Author
"""
tkinter-like wxPython support
"""
import time
import wx

time_elapsed = False
def no_call(self):
    """ Set flag to indicate time  elapsed
    """
    global time_elapsed
    time_elapsed = True

def after(delay, callback=None):
    """ Call after delay
    :delay: delay in milliseconds
    :callback: function to call
        default: no function, just delay
    """
    global time_elapsed
    if callback is None:
        timer = wx.Timer()
        tr = wx.TimerRunner(timer)
        tr.Start(delay)
    else:
        wx.CallLater(delay, callback)
    return
    
if __name__ == "__main__":
    from select_trace import SlTrace
    import wxtk
 
    def report():
        SlTrace.lg("Reporting")
           
    app = wx.App()
    frame = wx.Frame(None)
    frame.Show()
    delay = 2000
    delay_nf = delay*2
    SlTrace.lg(f"wxtk.after({delay},report)")
    wxtk.after(delay, report)
    
    def testing_after_none():
        SlTrace.lg("Testing after with no function")
        wxtk.after(delay_nf)
        SlTrace.lg(f"After wxtk.after({delay_nf})")
        
    SlTrace.lg(f"wx.CallLater({delay_nf}, testing_after_none)")
    wx.CallLater(delay_nf, testing_after_none)
    SlTrace.lg(f"After setting delayed test: {delay_nf} msec")
    
    app.MainLoop()
    