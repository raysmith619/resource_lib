# select_list_ckbox.py 14Apr2020    crs
"""
TEMPORARY - to replace select_list with ckbox option
Select list choose from a list of strings - returning selected
Adapted from traceControlWindow
"""
from tkinter import *
import atexit

import time

from select_trace import SlTrace
from image_hash import ImageHash

class SelectList(Toplevel):
    def __init__(self, tcbase=None, title=None, items=None,
                 ckbox=False,
                 entry_text=None,
                 position=None,
                 size=None,
                 image_size=None, image_hash=None, default_to_files=False, cancel_value=None):
        """ 
        :tcbase: - parent - call basis must have tc_destroy to be called if we close
        :title: Window title
        :items: list of strings / or file names if (<file:....>
            files are displayed as images
        :ckbox: True - provide check boxes for all entries
                returns: list of checked
        :position: (x,y) in pixels on screen
        :size: (width, hight) in in pixels of window
        :entry_text: If present, include entry at top of list
                    Place text as initial entry contents
        :image_size: (width, height) of image in pixels
        :image_hash: access to image files
        :default_to_files: True = default to file names else assume text entry fields
                        default: false
        """
        self.done = False           # Set True if done (OK, Cancel)
        self.ok = False             # Set if OK
        self.canceled = False
        self.standalone = False      # Set True if standalone operation
        self.ckbox = ckbox
        if ckbox:
            self.ckbox_vars_by_item = {}    # corresponds 1-to-1 self.items
        self.items = items
        if image_size is None:
            image_size = (125, 125)
        self.image_size = image_size
        self.default_to_files = default_to_files
        if tcbase is None:
            SlTrace.lg("Standalone SelectList")
            tcbase = Toplevel()
            frame = Frame(tcbase)
            frame.pack()
            self.standalone = True
            root.withdraw()
        self.tc_mw = self.tcbase = tcbase
        if position is None:
            position = (800, 100)
        if size is None:
            size = (200, 200)
        x0 = position[0]
        y0 = position[1]
        w = size[0]
        h = size[1]
        tc_geo = f"{w}x{h}+{x0}+{y0}"
        self.tc_mw.geometry(tc_geo)
        if title is None:
            title = "Testing"
        self.entry_text = entry_text
        self.entry_text_var = None      # Text Entry
        self.tc_mw.title(title)
        top_frame = Frame(self.tc_mw)
        top_frame.pack(side="top", fill="both", expand=False)
        self.top_frame = top_frame
        if title is not None:
            title_label = Label(master=self.top_frame, text=title, font="bold")
            title_label.pack(side="top", fill="both", expand=False)
        ok_button = Button(master=self.top_frame, text="OK", command=self.on_ok)
        ok_button.pack(side="left", fill="both", expand=False)
        cancel_button = Button(master=self.top_frame, text="CANCEL", command=self.on_cancel)
        cancel_button.pack(side="right", fill="both", expand=False)
        self.tc_mw.protocol("WM_DELETE_WINDOW", self.delete)
        top_frame.pack(side="top", fill="both", expand=False)
        tc_frame = Frame(self.tc_mw)
        tc_frame.pack(side="top", fill="both", expand=True)
        self.tc_frame = tc_frame
        self.tc_text_frame = None           # So we can destroy / resetup in create_items_region
        self.items_text = None
        self.sb = None
        if image_hash is None:
            image_hash = ImageHash()
        self.image_hash = image_hash
        self.selected_text_field = None
        self.cancel_value = cancel_value
            
        self.create_items_region(items=items)
            
    def create_items_region(self, items=None):
        if self.tc_text_frame is not None:
            self.tc_text_frame.pack_forget()
            self.tc_text_frame.destroy()
            self.tc_text_frame = None
            
        if self.sb is not None:
            self.sb.destroy()
        self.update()                           # Show progress
        self.tc_text_frame = Frame(self.tc_frame)
        self.tc_text_frame.pack(side="top", fill="both", expand=True)

        self.start = 0
        self.sb = Scrollbar(master=self.tc_text_frame, orient="vertical")
        max_width = 5
        min_height = 10
        t_height = min_height
        max_height = 20
        nfound = 0
        n_text = 0
        for item in items:
            if self.is_image(item):
                width = 10
            else:
                n_text += 1             # Count text entries
                width = len(item)
            if width > max_width:
                max_width = width
            nfound += 1
        win_width = max_width
        if nfound < min_height:
            t_height = min_height
        if nfound > max_height:
            t_height = max_height
            
        text_region = Text(self.tc_text_frame, width=win_width, height=t_height,
                    yscrollcommand=self.sb.set,
                    state=DISABLED)
        self.sb.config(command=text_region.yview)
        self.sb.pack(side="right",fill="y")
        text_region.pack(side="top", fill="both", expand=True)
        self.update()                           # Show progress
        self.data_by_widget = {}      # Dictionary by widget to  (btn, text_field, image)
        if self.entry_text is not None:
            max_width = max(int(self.image_size[0]/6), max_width)
            self.add_text_entry(text_region, text=self.entry_text, width=max_width)                
        for item in items:
            if self.ckbox:
                if self.is_image(item):
                    image = self.get_image(self.image_name(item), width=max_width)
                    self.add_image_ckbox(text_region, image=image, text_field=item)
                else:
                    self.add_text_ckbox(text_region, item, width=max_width+3)                
            else:
                if self.is_image(item):
                    image = self.get_image(self.image_name(item), width=max_width)
                    self.add_image_button(text_region, image=image, text_field=item)
                else:
                    self.add_text_button(text_region, item, width=max_width+3)                
        self.update()                           # Show progress
        if self.standalone:
            atexit.register(self.on_exit)
            self.update_loop()

    def add_image_button(self, text_region, image=None, text_field=None):
        
        btn = Button(text_region, image=image, command=lambda : self.do_image_button(text_field))
        self.data_by_widget[btn] = (btn, text_field, image)     # field is what we need
        text_region.config(state=NORMAL)
        text_region.window_create("end", window=btn)
        text_region.insert("end", "\n")

    def add_text_button(self, text_region, text=None, width=None):
        if text is None:
            text = ""
        if width is None:
            width = len(text) + 3
        btn = Button(text_region, text=text, command=lambda : self.do_text_button(text))
        self.data_by_widget[btn] = (btn, text)     # field is what we need
        text_region.config(state=NORMAL)
        text_region.window_create("end", window=btn)
        text_region.insert("end", "\n")

    def add_text_ckbox(self, text_region, text=None, width=None):
        """ Add check box entry
        """
        if text is None:
            text = ""
        if width is None:
            width = len(text) + 3
        ckbox_var = BooleanVar()
        ckbox = Checkbutton(text_region, text=text, variable=ckbox_var)
        self.data_by_widget[ckbox] = (ckbox, ckbox_var, text)     # field is what we need
        self.ckbox_vars_by_item[text] = ckbox_var
        text_region.config(state=NORMAL)
        text_region.window_create("end", window=ckbox)
        text_region.insert("end", "\n")
        text_region.config(state=DISABLED)

    def add_image_ckbox(self, text_region, image=None, text_field=None):
        SlTrace.lg("add_image_ckbox - TBD")
        
    def add_text_entry(self, text_region, text=None, width=None):
        """ Add text entry, records last entry added"""
        if text is None:
            text = ""
        entry_text_var = StringVar()
        entry_text_var.set(text)
        ent = Entry(text_region, width=width, textvariable=entry_text_var, bd=5, relief=RIDGE)
        self.data_by_widget[ent] = (ent, entry_text_var, text)
        text_region.config(state=NORMAL)
        text_region.window_create("end", window=ent)
        text_region.insert("end", "\n")
        text_region.config(state=DISABLED)
        ent.bind("<Return>", self.enter_entry)
        self.entry_text_var = entry_text_var       # Save for use on OK

    def on_ok(self):
        """ OK button pressed
        """
        SlTrace.lg("OK button pressed")
        if self.ckbox:
            self.ok = True
            self.done = True
            return
        
        if self.entry_text_var is not None:
            text = self.entry_text_var.get()
            self.ok_text(text)
            self.ok = True
        else:
            self.on_cancel()
        
    def on_cancel(self):
        """ Cancel button pressed
        """
        self.delete()
        
    def delete(self):
        """ Called to delete window, e.g. when x was clicked
        """
        self.canceled = True
        self.done = True
        
        
    def do_image_button(self, text_field):
        self.selected_text_field = text_field
        self.ok = True
        self.done = True
        
    def do_text_button(self, text):
        self.selected_text_field = text
        self.ok = True
        self.done = True
        
    def image_name(self, item_text):
        """ Convert item_text to image name
        :item_text: text
        """
        return self.image_hash.image_name(item_text, default_to_files=self.default_to_files)
        
        
    def is_image(self, item_text):
        return self.image_hash.is_file(item_text, default_to_files=self.default_to_files)
            
    def get_image(self, item_text, width=None):
        image_size = self.image_size
        image = self.image_hash.get_image(item_text, size=image_size)
        return image
        
    def get_selected(self):
        """ Return selected field: <file:....> for selected image file, else text entry
        """
        while not self.done:                
            self.sleep(.1)
        self.delete_tc_window()
        if self.canceled:
            text_field = self.cancel_value
        else:
            text_field = self.selected_text_field
        if self.is_image(text_field):
            text_field = self.image_hash.name2image_string(text_field)
        return text_field
        
    def get_checked(self):
        """ Return list of checked: <file:....> for selected image file, else text entry
        """
        while not self.done:
            self.sleep(.1)
        self.delete_tc_window()
        if self.canceled:
            return []    
                
        if self.ok:
            checked_items = []
            for item in self.items:
                ckbox_var = self.ckbox_vars_by_item[item]
                cked = ckbox_var.get()
                if cked:
                    checked_items.append(item)
            return checked_items
        
        return []
        
    def on_exit(self):
        """ Close down window on program exit
        """
        SlTrace.lg("Closing down Trace Control Window")
        self.delete_tc_window()
        
    def update_loop(self):
        """ continue repeated tk.update() calls
        to enable window operation
        """
        loop_time = 50          # Loop recall time (msec)
        self.update()
        self.tc_mw.after(loop_time, self.update_loop)

    def update(self):
        if self.tc_mw is not None and self.tc_mw.winfo_exists():
            self.tc_mw.update()
        
    def sleep(self, sec):
        """ "sleep" for a number of sec
        without stoping tkinter stuff
        :sec: number of milliseconds to delay before returning
        """
        if self.tc_mw is None:
            return
        
        self.update()             # Insure at least one update
        now = time.time()
        end_time = now + sec
        while time.time() < end_time:
            if self.tc_mw is None:
                return
            
            self.update()
        return
    
    def mainloop(self):
        self.tc_mw.mainloop()
        
    def delete_tc_window(self):
        """ Process Trace Control window close
        """
        if self.tc_mw is not None:
            self.tc_mw.destroy()
            self.tc_mw = None
        
        if self.tcbase is not None and hasattr(self.tcbase, 'tc_destroy'):
            self.tcbase.tc_destroy()
                
    def enter_entry(self, event):
        widget = event.widget
        _, entry_text_var, _ = self.data_by_widget[widget]
        text = entry_text_var.get()
        self.ok_text(text)

    
    
    def ok_text(self, text):
        self.default_to_files = False       # Assuming text (no modification)
        self.selected_text_field = text
        self.ok = True
        self.done = True
        
if __name__ == '__main__':
    def report_change(item, val, cklist=None):
        SlTrace.lg("changed: %s = %d" % (item, val))
        new_val = SlTrace.getLevel(item)
        SlTrace.lg("New val: %s = %d" % (item, new_val))
        if cklist is not None:
            cklist.list_ckbuttons()
    
    root = Tk()
    SlTrace.set_mw(root)
    ###frame = Frame(root)
    ###frame.pack()
    SlTrace.setProps()
    image_hash = ImageHash(image_dir="../images/animals")
    image_files = image_hash.get_image_files()
    text_items = ["ONE","TWO", "3", "FOUR"]
    x0 = 300
    y0 = 400
    width = 200
    height = 400
    SlTrace.lg(f"x0={x0}, y0={y0}, width={width}, height={height}", "select_list")
    
    SlTrace.lg("Text ckbox")                    
    app = SelectList(ckbox=True,
                     items=text_items, position=(x0, y0), size=(width, height),
                     title="Text Ckbox")
    selected_field = app.get_checked()
    SlTrace.lg(f"text_items: selected_field:{selected_field}")    
    
    SlTrace.lg("Text Buttons")                    
    app = SelectList(items=text_items, position=(x0, y0), size=(width, height),
                     title="Text Buttons")
    selected_field = app.get_selected()
    SlTrace.lg(f"text_items: selected_field:{selected_field}")    

    SlTrace.lg("Text Buttons + entry")
    app = SelectList(items=text_items, position=(x0, y0), size=(width, height),
                     entry_text="Add your own",
                     title="Text Buttons - with entry")
    selected_field = app.get_selected()
    SlTrace.lg(f"text_items + entry: selected_field:{selected_field}")    

    SlTrace.lg("Image Buttons")
    app = SelectList(items=image_files, image_hash=image_hash, default_to_files=True,
                     title="Image Buttons",
                     position=(x0, y0), size=(width, height))
    selected_field = app.get_selected()
    SlTrace.lg(f"image_image: selected_field:{selected_field}")

    SlTrace.lg("Image Buttons + entry")
    app = SelectList(items=image_files, image_hash=image_hash, default_to_files=True,
                     title="Image Buttons",
                     entry_text="Add your own",
                     position=(x0, y0), size=(width, height))
    selected_field = app.get_selected()
    SlTrace.lg(f"image_image: selected_field:{selected_field}")
        
    SlTrace.lg("End of test")