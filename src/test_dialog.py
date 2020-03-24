# test_dialog.py
def histDialog(self):
    "histogramDialog(self) - dialog to setup histogram plot"
    import Tkinter
    if self.histFrame != None: self.histDone()
    top=Toplevel()
    self.histFrame=top
    fm = Frame(top,borderwidth=0)
    top.title('Histogram Dialog...')
    self.histVar = [StringVar(),IntVar(),IntVar()]
    Label(fm,text='Curve # [1-'+str(self.nc)+']:').grid(row=1,column=1,sticky=W)
    asply = tuple(range(1,self.nc+1))
    self.histVar[0] = Pmw.ComboBox(fm,label_text='Pick:',
        labelpos=W, listbox_width=5,dropdown=1,
        scrolledlist_items=asply)
    self.histVar[0].grid(row=1,column=2,sticky=W)
    self.histVar[0].selectitem(0)

    Label(fm,text='Number of bins:').grid(row=2,column=1,sticky=W)
    Entry(fm,width=10,textvariable=self.histVar[1]).grid(row=2,column=2,sticky=W)
    Label(fm,text='Horizontal:').grid(row=3,column=1,sticky=W)
    Checkbutton(fm,variable=self.histVar[2],state=NORMAL).grid(row=3,column=2,sticky=W)
    self.histVar[1].set(20)
    Tkinter.Button(fm,text='Accept',command=self.histRun).grid(row=4,column=1,stick=W)    
    Tkinter.Button(fm,text='Close',command=self.histDone).grid(row=4,column=2,stick=W)    
    fm.pack(fill=BOTH) 
