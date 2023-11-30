#wx_timer_ex.py
# Cross-Platform, Python, wxPython / By Mike / August 25, 2009

import wx
import time
 
class MyForm(wx.Frame):
 
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Timer Tutorial 1", 
                                   size=(500,500))
 
        # Add a panel so it looks the correct on all platforms
        panel = wx.Panel(self, wx.ID_ANY)
        
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)

        self.toggleBtn = wx.Button(panel, wx.ID_ANY, "Start")
        self.toggleBtn.Bind(wx.EVT_BUTTON, self.onToggle)

    def onToggle(self, event):
        btnLabel = self.toggleBtn.GetLabel()
        if btnLabel == "Start":
            print("starting timer...")
            self.timer.Start(1000)
            self.toggleBtn.SetLabel("Stop")
        else:
            print("timer stopped!")
            self.timer.Stop()
            self.toggleBtn.SetLabel("Start")
            
    def update(self, event):
        print("\nupdated: ", time.ctime())
 
# Run the program
if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = MyForm().Show()
    app.MainLoop()