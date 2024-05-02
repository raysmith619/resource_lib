#sizer_auto.py   19Apr2024  crs from stackoverflow
# arranging-the-panels-automatically-in-wxpython

import wx

########################################################################
class SubPanel(wx.Panel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent, number):
        """Constructor"""
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour("red")

        label = "Sub panel-%s" % number
        lbl = wx.StaticText(self, label=label)

        sizer = wx.BoxSizer()
        sizer.Add(lbl, 0, wx.ALL|wx.CENTER, 5)
        self.SetSizer(sizer)

########################################################################
class ColorPanel(wx.Panel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent, number, color, sub_panels):
        """Constructor"""
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(color)

        label = "Panel-%s" % number
        lbl = wx.StaticText(self, label=label)

        v_sizer = wx.BoxSizer(wx.VERTICAL)
        for i in range(sub_panels):
            p = SubPanel(self, i+1)
            v_sizer.Add(p, 0, wx.ALL|wx.EXPAND|wx.CENTER, 10)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(v_sizer, 0, wx.ALL, 5)
        sizer.Add(lbl, 0, wx.ALL|wx.CENTER, 5)
        self.SetSizer(sizer)

########################################################################
class MainPanel(wx.Panel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        v_sizer = wx.BoxSizer(wx.VERTICAL)

        colors = [("green", 3),
                  ("yellow", 2),
                  ("light blue", 2),
                  ("purple", 2)]
        count = 1
        for color, subpanel in colors:
            panel = ColorPanel(self, count, color, subpanel)
            hsizer.Add(panel, 1, wx.EXPAND)
            count += 1

        orange_panel = ColorPanel(self, count, "orange", 0)
        v_sizer.Add(hsizer, 1, wx.EXPAND)
        v_sizer.Add(orange_panel, 1, wx.EXPAND)

        self.SetSizer(v_sizer)

########################################################################
class MainFrame(wx.Frame):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title="Panels!", size=(600,400))
        panel = MainPanel(self)
        self.Show()

#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()