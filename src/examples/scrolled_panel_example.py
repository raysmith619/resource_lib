#wx_scrolled_panel_example.py   26apr2024  crs, from wxPython
text = '''
ScrolledPanel extends wx.ScrolledWindow, adding all
the necessary bits to set up scroll handling for you.

Here are three fixed size examples of its use. The
demo panel for this sample is also using it -- the
wx.StaticLine below is intentionally made too long so a scrollbar will be
activated.'''

import wx
import wx.lib.scrolledpanel as scrolled

class TestPanel(scrolled.ScrolledPanel):

    def __init__(self, parent):

        scrolled.ScrolledPanel.__init__(self, parent, -1)

        vbox = wx.BoxSizer(wx.VERTICAL)

        desc = wx.StaticText(self, -1, text)

        desc.SetForegroundColour("Blue")
        vbox.Add(desc, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        vbox.Add(wx.StaticLine(self, -1, size=(1024, -1)), 0, wx.ALL, 5)
        vbox.Add((20, 20))

        self.SetSizer(vbox)
        self.SetupScrolling()


app = wx.App(0)
frame = wx.Frame(None, wx.ID_ANY)
fa = TestPanel(frame)
frame.Show()
app.MainLoop()