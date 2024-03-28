import wx

DATA = [
    (1, 'nudge nudge'),
    (2, 'wink wink'),
    (1, 'I bet she does'),
    (3, 'say no more!'),
]

class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None)
        panel = wx.Panel(self)
        self.text = wx.StaticText(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer(1)
        sizer.Add(self.text, 0, wx.ALIGN_CENTER)
        sizer.AddStretchSpacer(1)
        panel.SetSizer(sizer)
        self.index = 0
        self.update()
    def update(self):
        duration, label = DATA[self.index]
        self.text.SetLabel(label)
        self.index = (self.index + 1) % len(DATA)
        wx.CallLater(int(duration * 1000), self.update)

if __name__ == '__main__':
    app = wx.App(None)
    frame = Frame()
    frame.SetTitle('Example')
    frame.SetSize((400, 300))
    frame.Center()
    frame.Show()
    app.MainLoop()