import tkinter as tk

class MyEntry(tk.Entry):
    """Entry widget with Return bound to provide tabbing functionality"""
    def __init__(self, master, **kw):
        tk.Entry.__init__(self, master, **kw)
        self.next_widget = None
        self.bind("<Return>", self.on_ret)
    def on_ret(self, ev):
        if self.next_widget:
            self.event_generate('<<TraverseOut>>')
            self.next_widget.focus()
            self.next_widget.event_generate('<<TraverseIn>>')
        else:
            self.event_generate('')
        return "break"
    def set_next(self, widget):
        """Override the default next widget for this instance"""
        self.next_widget = widget

def add_entry(parent, row, **kwargs):
    widget = MyEntry(parent, **kwargs)
    widget.grid(row=row, column=0, sticky=tk.NSEW)
    return widget

def main(args=None):
    root = tk.Tk()

    frame = tk.LabelFrame(root, text="Entries", width=200, height=200)

    entries = []
    for row in range(4):
        e = add_entry(frame, row)
        entries.append(e)
    e.set_next(entries[0])

    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=0)

    button = tk.Button(root, text="Exit", command=root.destroy)

    frame.grid(row=0, column=0, sticky=tk.NSEW)
    button.grid(row=1, column=0, sticky=tk.SE)
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    entries[0].focus_set()
    root.mainloop()

if __name__ == '__main__':
    main()