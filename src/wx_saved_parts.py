        self.adw_panel = self.cell_pan     
        self.window_sizer = wx.BoxSizer()
        # Set sizer for the frame, so we can change frame size to match widgets
        self.window_sizer.Add(self.adw_panel, 1, wx.ALL | wx.EXPAND)

        self.wc_sizer = wx.BoxSizer(wx.VERTICAL)
        self.adw_echo_text = wx.TextCtrl(self.adw_panel, size=(int(win_width*.9),20))
        #self.cell_pan = wx.Panel(self.adw_panel)
        #self.wc_sizer.Add(self.adw_echo_text, 0, wx.ALIGN_CENTER_HORIZONTAL)
        #self.wc_sizer.Add(self.cell_pan, 1, wx.EXPAND|wx.EXPAND)
        #self.adw_panel.SetSizer(self.wc_sizer)



class CanvasFrame(wx.Frame):
    def __init__(self, parent, panel=None, **kwargs):
        """Constructor"""
        super().__init__(parent, **kwargs)
        if panel is None:
            panel = CanvasPanel(self)
        self.panel = panel
        self.SetBackgroundColour("green")
        
        sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        sizer_v = wx.BoxSizer(wx.VERTICAL)
        win_width = kwargs["size"][0]
        self.echo_text = wx.TextCtrl(self.panel, size=(int(win_width*.9),20))
        sizer_v.Add(self.echo_text, 1, wx.ALIGN_CENTER_HORIZONTAL)
        sizer_v.Add(self.panel, 1, wx.EXPAND)
        
        sizer_h.Add(sizer_v, proportion=1, flag=wx.EXPAND)

        # only set the main sizer if you have more than one
        #self.SetSizer(sizer_h)
        self.Show()


    def OnSize(self, e):
        self.Refresh()


    def create_rectangle(self, cx1,cy1,cx2,cy2,
                                **kwargs):
        return self.panel.create_rectangle(cx1,cy1,cx2,cy2,
                                **kwargs)

    
    def create_oval(self, x0,y0,x1,y1,
                        **kwargs):
        """ Implement create_oval
            supporting fill, outline, width
        """
        return self.panel.create_oval(x0,y0,x1,y1, **kwargs)

    def create_line(self, x0,y0,x1,y1, **kwargs):
        """ Implement tkinter's create_line
        :args: x1,y1,...xn,yn
        :kwargs:  width=, fill=, tags=[]
        """
        return self.panel.create_line(x0,y0,x1,y1, **kwargs)


    def delete(self, id_tag):
        """ Delete object in panel
        :id_tag: if str: "all" - all items, else tag
                else id
        """
        return self.panel.delete(id_tag)


threaded mainloop version
    def mainloop(self):
        title = self.title
        if title is None:
            title = "Braille Display -"
        canvas_items = False
        if SlTrace.trace("show_canvas_items"):
            canvas_items = True
        wx_proc = th.Thread(target=self.display_proc)
        wx_proc.start()
        #tur.done()
        tk.mainloop()
        SlTrace.lg("End of tk.mainloop()")

    def display_proc(self):
        SlTrace.lg("display_proc()")
        app = wx.App()
        self.app = app
        #wx.CallLater(0, self.display, app=app)
        #wx.CallLater(2000, SlTrace.lg, "After 2nd CallLater")
        self.display(app=self.app)
        SlTrace.lg("self.display call()")
        self.app.MainLoop()
                
    def done(self):
        self.mainloop()

    # Special functions
    def set_blank(self, blank_char):
        """ Set blank replacement
        :blank_char: blank replacement char
        :returns: previous blank char
        """
        ret = self.blank_char
        self.blank_char = blank_char
        return ret
