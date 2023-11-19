# panel_item_expand.py 
import wx

class MyFrame(wx.Frame):
    def __init__(self, parent, mytitle, mysize):
        wx.Frame.__init__(self, parent, wx.ID_ANY, mytitle, size=mysize)
        panel1 = wx.Panel(self)
        panel2 = wx.Panel(self)
        panel3 = wx.Panel(self)

        panel1.SetBackgroundColour("green")
        panel2.SetBackgroundColour("yellow")
        panel3.SetBackgroundColour("red")

        sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        sizer_v = wx.BoxSizer(wx.VERTICAL)

        st1 = wx.StaticText(panel1, -1, "TEST")
        sizer_h.Add(panel1, 1, wx.EXPAND)
        sizer_v.Add(sizer_h, proportion=1, flag=wx.EXPAND)
        sizer_v.Add(panel2, proportion=2, flag=wx.EXPAND)
        sizer_v.Add(panel3, proportion=1, flag=wx.EXPAND)
        # only set the main sizer if you have more than one
        self.SetSizer(sizer_v)

app = wx.App()
mytitle = "wx.Frame & wx.Panels"
width = 300
height = 320
MyFrame(None, mytitle, (width, height)).Show()
app.MainLoop()