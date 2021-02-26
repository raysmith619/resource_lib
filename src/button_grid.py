# button_grid.py    08Feb2021  crs
# Adopted from grid_image_resize.py
# https://izziswift.com/how-to-create-a-self-resizing-grid-of-buttons-in-tkinter/

import os
from tkinter import *
from PIL import Image, ImageTk

from select_trace import SlTrace


class ButtonInfo:
    """ Button infos btn, btn base image
    """
    def __init__(self, btn, text=None,
                 row=None, col=None,
                 base_image=None, btn_image=None, file_key=None):
        self.text = text
        self.btn = btn
        self.row = row
        self.col = col
        self.base_image = base_image
        self.btn_image = btn_image      # Scaled/PhotoImaged
        self.file_key = file_key
'''
def key_attr(type=None, text=None, image=None, column=None,
             columnspan=None ):
    return {"type" : type, "text" : text, "image" : image,
            "column" : column, "columnspan" : columnspan}
'''
def key_attr(**kwargs):
    return kwargs

        
class ButtonGrid:
        
    sample_file = "animals.png"

    btn_specs = [
        key_attr(type="ROWCOL", image="SAMPLE"),
        key_attr(type="REPEAT")
        ]
    
    def __init__(self, master,
                 image_dir=None,
                 on_kbd=None,
                 keys=None,
                 key_attrs=None,
                 btn_specs=None,
                 im_fract_x = 1.0, im_fract_y=.8,
                 nrows=4, ncols=8,
                 win_width=1000, win_height=600,
                 chg_fract=.01,
                 btn_padx=2, btn_pady=2, btn_bd=3,
                 btn_font=('arial', 12, 'bold'),
                 ):
        """ Setup Button Grid
        :master: master widget
        :image_dir: image directory
                default: ../images/keys
        :on_kbd: function to call with each key-click
        :keys: list of keys to display on buttons as text
                default: use btn_specs
        :key_attrs: key attributes
                dictionary on key text
                key_text : image_file
                            OR
                          {dictionary:}
                            "text" : button text
                            "image" : image file
                            "column" : button column (starting with 1)
                            "columnspan" : button column span
                            
                default: just display text with no image
        :btn_specs: list of button specifications
            specification:
                {
                    "type" : 
                        "ROWCOL" - use current row_col
                        "REPEAT - repeat list for rest of buttons
                         else - text to be added at top of button

                    "image" :
                        "SAMPLE" - use sample image
                        "BLANK" - no image file
                         else - path to button image, None - No image

                    "column" : starting with 1 default: current
                    "column_span" : default: 1
                }
            default:
                [
                    {"type" : "ROWCOL", "image" : "SAMPLE"}
                    {"type" : "REPEAT"}
                ]
                
        :im_fract_x: x button fraction taken by image default: 1.0
        :im_fract_y: y button fraction taken by image default: .8
        :nrows: Number of rows default: 4
        :ncols: Number of columns default: 8
        :win_x: window x start default: 20
        :win_y: window y start default: 20
        :win_width: grid window width default: 1000
        :win_height: grid window height default: 600
        """
        self.ims = []       # TFD

        small = 2
        small_image = Image.new("RGB", (small, small), (255,255,255))
        small_btn_image = ImageTk.PhotoImage(small_image)
        self.blank_image = small_btn_image

        self.show_images = True         # False disables image showing
        self.enable_image_update(False)   # Set True to enable image size update
        self.btn_infos = []          # button info in order of creation
        self.master = master
        if image_dir is None:
            src_dir = os.path.dirname(os.path.abspath(__file__))
            prj_dir = os.path.dirname(src_dir)
            image_dir = os.path.join(prj_dir, "images", "keys")
            if not os.path.exists(image_dir):
                image_dir = os.path.join(src_dir, "images", "keys")
                SlTrace.lg(f"Looking for images under src dir: {image_dir}")
                
                
        self.image_dir = image_dir
        self.on_kbd = on_kbd
        if keys is not None:
            """ Generate btn_specs from keys and key_files """
            if btn_specs is not None:
                SlTrace.report(f"Can't have both keys and btn_specs")
                exit()
            btn_specs = []
            for key in keys:
                spec = {"type" : "key", "text" : key}
                if key_attrs and key in key_attrs:
                    if isinstance(key_attrs[key],dict):
                        spec.update(key_attrs[key])
                    else:
                        spec["image"] = key_attrs[key]    
                btn_specs.append(spec)
            SlTrace.lg(f"keys: {len(keys)} generated specs {len(btn_specs)}")    
        if btn_specs is None:
            btn_specs = ButtonGrid.btn_specs
        self.btn_specs = btn_specs
        self.im_fract_x = im_fract_x
        self.im_fract_y = im_fract_y
        self.btn_padx = btn_padx
        self.btn_pady = btn_pady
        self.btn_bd = btn_bd
        self.nrows = nrows
        self.ncols = ncols
        self.chg_fract = chg_fract
        self.btn_padx = btn_padx          # Button attributes
        self.btn_pady = btn_pady 
        self.btn_bd = btn_bd
        self.btn_font = btn_font
        
        self.win_x = 0
        self.win_y = 0
        self.win_width_orig = self.win_width = win_width
        self.win_height_orig = self.win_height = win_height
                                # Setup for next sizing test
        btn_size_x, btn_size_y = self.get_btn_image_size()
        self.btn_image_size_x_prev = btn_size_x # Save for new size
        self.btn_image_size_y_prev = btn_size_y
        
        btn_size_x, btn_size_y = self.get_btn_image_size()
        self.btn_image_size_x_prev = btn_size_x
        self.btn_image_size_y_prev = btn_size_y
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        #Create & Configure frame 
        keybd_frame=Frame(self.master)
        keybd_frame.rowconfigure(0, weight=1)
        keybd_frame.columnconfigure(0, weight=1)
        keybd_frame.grid(sticky=N+S+E+W)
        keybd_frame.bind('<Configure>', self.win_size_event)
        specs = self.btn_specs.copy()
        row_start = 0
        row_current = row_start
        col_start = 0
        col_current = col_start
        for _ in range(self.nrows):
            row_current += 1
            col_current = col_start
            keybd_frame.rowconfigure(row_current, weight=1)
            for _ in range(ncols):
                keybd_frame.columnconfigure(col_current, weight=1)
                key_frame = Frame(keybd_frame)
                key_frame.rowconfigure(0, weight=1)
                key_frame.columnconfigure(0, weight=1)
                btn_background = "white"
                btn_foreground = "black"
                btn_compound = BOTTOM
                btn_width = btn_size_x
                base_image = None
                if len(specs) == 0:
                    SlTrace.lg("Unexpected end to specifications"
                               f" row_current:{row_current} col_current: {col_current}"
                               f"\n list:{self.btn_specs}")
                    break
                spec = specs.pop(0)
                spec_type = spec["type"]
                if spec_type == "REPEAT":
                    specs = self.btn_specs.copy()
                    continue
                elif spec_type == "ROWCOL":
                    btn_text = f"{row_current},{col_current}"
                else:
                    btn_text = spec["text"]
                if "image" not in spec or spec["image"] is None:
                    btn_width = 7       # Best guess text chars
                    btn_compound = None
                    btn_image = None
                    spec_image_file = None
                else:
                    btn_width = 7*12       # Best guess text pixels
                    spec_image_file = spec["image"]
                    if spec_image_file == "SAMPLE":
                        spec_image_file = ButtonGrid.sample_file
                    if not os.path.isabs(spec_image_file):
                        spec_image_file = os.path.join(image_dir, spec_image_file)
                        if not os.path.isabs(spec_image_file):
                            SlTrace.lg(f"key path:{spec_image_file}", "trace_keys")       
                        spec_image_file = os.path.abspath(spec_image_file)
                    SlTrace.lg(f"key path:{spec_image_file}", "trace_keys")
                    if not os.path.exists(spec_image_file):
                        SlTrace.lg(f"We Can't find image file for {btn_text}"
                                           f"\n looking in: {spec_image_file}")
                        continue
                    SlTrace.lg(f"spec_image_file: {spec_image_file}", "btn")
                    base_image = Image.open(spec_image_file)
                    scaled_image = base_image.resize((int(btn_size_x),
                                                      int(btn_size_y)))
                    btn_image = ImageTk.PhotoImage(scaled_image)
                                                            # avoid loss
                SlTrace.lg(f"btn: btn_text:{btn_text} btn_image: {btn_image}", "btn")
                if "column" not in spec:
                    col_current += 1
                else:
                    col_current = spec["column"]
                cmd = lambda x = btn_text: self.buttonClick(x)
                
                if "columnspan" in spec and spec["columnspan"] is not None:
                    btn_columnspan = spec["columnspan"]
                else:
                    btn_columnspan = None
                key_frame.grid(row=row_current, column=col_current,
                               columnspan=btn_columnspan,
                                sticky=N+S+E+W)  
                if "columnspan" in spec and spec["columnspan"] is not None:
                    col_current += btn_columnspan-1
                    
                btn = Button(key_frame,
                    text = btn_text,
                    image = btn_image,
                    compound = btn_compound,                    
                    width = btn_width,
                    bg = btn_background,
                    fg = btn_foreground,
                    activebackground = 'white',
                    activeforeground = 'black',
                    relief = 'raised',
                    padx = self.btn_padx,
                    pady = self.btn_pady, 
                    bd = self.btn_bd,
                    font=self.btn_font,
                    command = cmd)
                if btn_image is None:
                    bti_image = btn_image
                else:
                    bti_image = btn_image
                btn_info = ButtonInfo(btn=btn,
                                    text=btn_text,
                                    row=row_current,
                                    col=col_current,
                                    base_image=base_image,
                                    btn_image=bti_image,
                                    file_key=spec_image_file,
                                    )
                self.ims.append(bti_image)       # TFD
                btn.grid(sticky=N+S+E+W)  
                self.btn_infos.append(btn_info)
                btn.rowconfigure(0, weight=1)
                btn.columnconfigure(0, weight=1)


    # function for button click
    def buttonClick(self, input):    
        if self.on_kbd is not None:
            self.on_kbd(input)

    def do_shift(self, shift_on=True):
        """ Shift letters
        :shift_on: Put shift on, adjust letters
                    default: True
        """
        self.shift_on = shift_on
        for btn_info in self.btn_infos:
            if btn_info.text is not None and len(btn_info.text) == 1:
                text = btn_info.text
                text = text.upper() if self.shift_on else text.lower()
                btn_info.btn.configure(text=text)
            
        
        
    def enable_image_update(self, enable=True):
        """ Enable/Disable image size update
        :enable: True - enable default: True
        """
        self.image_update_enabled = enable

    def get_btn_image_size(self):
        """ Calculate button's image size based on
        current window size and number of button rows, columns
        :returns: (x_size, y_size) in pixels
        """
        btn_size_x_raw = self.win_width/self.ncols - self.btn_bd
        btn_size_x = btn_size_x_raw - self.btn_padx
        btn_image_size_x = btn_size_x * self.im_fract_x 
        
        btn_size_y_raw = self.win_height/self.nrows - self.btn_bd
        btn_size_y = btn_size_y_raw - self.btn_padx
        btn_image_size_y = btn_size_y * self.im_fract_y
        return (int(btn_image_size_x), int(btn_image_size_y)) 

    def win_size_event(self, event):
        """ Window sizing event
        """
        win_x = self.master.winfo_x()
        win_y = self.master.winfo_y()
        win_width = self.master.winfo_width()
        win_height = self.master.winfo_height()
        SlTrace.lg(f"win_x:{win_x} win_y:{win_y}"
                   f" win_width: {win_width} win_height: {win_height}",
                   "win_size_event")

        '''
        self.set_prop_val("win_x", win_x)
        self.set_prop_val("win_y", win_x)
        self.set_prop_val("win_width", win_width)
        self.set_prop_val("win_height", win_height)
        '''
        self.win_x = win_x
        self.win_y = win_y
        self.win_width = win_width
        self.win_height = win_height
        
        btn_image_size_x_new, btn_image_size_y_new = self.get_btn_image_size()
        xfchg = self.get_chg_fract(btn_image_size_x_new, self.btn_image_size_x_prev) 
        yfchg = self.get_chg_fract(btn_image_size_y_new, self.btn_image_size_y_prev) 
        if xfchg > self.chg_fract or yfchg > self.chg_fract:
            self.start_update_button_images()
        self.master.update_idletasks()  # Allow size change to restart


    def get_chg_fract(self, new_val, old_val):
        """ maximum chg
        :new_val: new value
        :old_val: old value
        :returns: largest fraction change
        """
        new_ratio = new_val/old_val
        old_ratio = 1/new_ratio
        chg_ratio = min(new_ratio, old_ratio)
        chg_fract = 1-chg_ratio
        return chg_fract


    def set_images(self, show=False):
        self.show_images = show
        for btn_info in self.btn_infos:
            self.reimage(btn_info)            

    def set_btn_image(self, btn_infos=None, image=None):
        """ Set button (btn_infos) image displayed
        :btn_infos: ButtonInfo, or list of ButtonInfos
        :image" text - image file
                Image - image
        """
        btn_size_x, btn_size_y = self.get_btn_image_size()
        if not isinstance(btn_infos, list):
            btn_infos = [btn_infos]
        if isinstance(image, str):
            spec_image_file = image
            if not os.path.isabs(spec_image_file):
                spec_image_file = os.path.join(self.image_dir, spec_image_file)
                if not os.path.isabs(spec_image_file):
                    SlTrace.lg(f"key path:{spec_image_file}", "trace_keys")       
                spec_image_file = os.path.abspath(spec_image_file)
            SlTrace.lg(f"key path:{spec_image_file}", "trace_keys")
            if not os.path.exists(spec_image_file):
                SlTrace.lg(f"We Can't find image file for {btn_infos}"
                                   f"\n looking in: {spec_image_file}")
            
            SlTrace.lg(f"spec_image_file: {spec_image_file}", "btn")
            base_image = Image.open(spec_image_file)
            scaled_image = base_image.resize((int(btn_size_x),
                                              int(btn_size_y)))
            btn_image = ImageTk.PhotoImage(scaled_image)
        elif image is None:
            btn_image = self.blank_image
        else:
            btn_image = image
        for btn_info in btn_infos:
            btn = btn_info.btn
            if btn_image is None:
                btn_image = self.small_image
            btn_info.btn_image = btn_image      # Change so resizing retains view
            btn.config(image=btn_image, compound=BOTTOM)    

    def get_btn_infos(self, key=None, row=None, col=None):
        """ Get buttons
        :key: if not None, must match
        :row: if not None, must match
        :col: if not None, must match
        """
        bis = []
        for btn_info in self.btn_infos:
            if key is not None and btn_info.text != key:
                continue
            if row is not None and btn_info.row != row:
                continue
            if col is not None and btn_info.col != col:
                continue
            bis.append(btn_info)
        return bis            
    
    def start_update_button_images(self):
        """ Start phased button image size updating which updates
        the button sizes one at a time till all images fit the newest size
        """
                                # Setup for next test
        btn_size_x, btn_size_y = self.get_btn_image_size()
        self.btn_image_size_x_prev = btn_size_x # Save for new size
        self.btn_image_size_y_prev = btn_size_y
        SlTrace.lg(f"start update_button_images: x: {btn_size_x} y: {btn_size_y}")
        self.update_image_index = 0
        if self.image_update_enabled and SlTrace.trace("enable_image_update"):
            SlTrace.lg(f"delayed update_button_image")
            self.master.after(0, self.update_button_image)
        
    def update_button_image(self):
        """ Update next button image size
        If more images to go, set next call
        """
        SlTrace.lg(f"update_button_image index: {self.update_image_index}",
                   "image_update")
        if self.update_image_index >= len(self.btn_infos):
            SlTrace.lg(f"update_buton_image complete")
            return              # Update complete - no more
        
        btn_info = self.btn_infos[self.update_image_index]
        self.reimage(btn_info=btn_info)
        self.update_image_index += 1
        self.master.after(0, self.update_button_image)

    def reimage(self, btn_info=None, base_image=None):
        """ Change button image
        :btn_info: ButtonInfo
        :base_image: alternate button image
                default: use btn_info.base_mage
        """
        btn = btn_info.btn
        if base_image is None:
            base_image = btn_info.base_image
        if base_image is None:
            return
    
        btn_size_x, btn_size_y = self.get_btn_image_size()
        if self.show_images:
            btn_size_x, btn_size_y = self.get_btn_image_size()
            btn = btn_info.btn
            base_image = btn_info.base_image
            
            scaled_image = base_image.resize((int(btn_size_x),
                                              int(btn_size_y)))
        else:    
            small = 2
            scaled_image = Image.new("RGB", (small, small), (255,255,255))
        btn_image = ImageTk.PhotoImage(scaled_image)
        self.btn_image_store(btn_image, btn_info=btn_info)  # save ref to 
        btn.config(image=btn_image) # store new image
        SlTrace.lg(f"update_button_image:[{self.update_image_index}]"
                   f" btn_size_x: {btn_size_x}"
                   f" btn_size_y: {btn_size_y}",
                   "image_update")

    def btn_image_store(self, btn_image, btn_info):
        """ Store new button image, deleating old one if present
        Note: storage is required to avoid probable early deletion
        :btn_image: new button image
        :btn_info: current button info
        """
        if btn_info.btn_image is not None:
            del(btn_info.btn_image)
        btn_info.btn_image = btn_image
    
    def update_button_images(self):
        self.btn_image_store = []       # Delete stored images
        btn_size_x, btn_size_y = self.get_btn_image_size()
        self.btn_image_size_x_prev = btn_size_x # Save for new size
        self.btn_image_size_y_prev = btn_size_y
        self.update_button_images_count += 1    # Signal update
        SlTrace.lg(f"update_button_images: count:{self.update_button_images_count}")    
        """ Update displayed images in hopes to appropriately
        scale them to window size change
        """
        ##self.btn_image_store = [] # Free up storage
        for btn_info in self.btn_infos:
            self.master.update_idletasks()    # Allow for changes
            current_count = self.update_button_images_count
            if current_count > self.update_button_images_count:
                SlTrace.lg(f"update_count change: {self.update_button_images_count}")
                return
            
            btn = btn_info.btn
            base_image = btn_info.base_image
            if base_image is None:
                continue
            
            scaled_image = base_image.resize((int(btn_size_x),
                                              int(btn_size_y)))
            btn_image = ImageTk.PhotoImage(scaled_image)
            self.btn_image_store.append(btn_image)  # save ref to 
                                                        # avoid loss
            btn.config(image=btn_image) # store new image
        SlTrace.lg(f"update_button_image: btn_size_x: {btn_size_x} btn_size_y: {btn_size_y}")    

if __name__ == "__main__":
    #Create & Configure root 
    root = Tk()
    prj_dir = ".."
    image_dir = os.path.join(prj_dir, "images", "keys")
    SlTrace.lg(f"Try src dir: {image_dir}")
    alt_key_file = "animals.png"
    images = [alt_key_file]
    
    def on_kbd(input):
        """ Test keyboard button click
        :input: key text
        """
        SlTrace.lg(f"key: '{input}'")
    
    # buttons list
    buttons = [
        '`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-'  , '=','BKSP', 'HOME', 'END',
        '!', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p','BKSP', '7', '8'  , '9'   , '-',
        'Tab', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', '[', ']', '4', '5', '6', '+',
        'Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', '?', '1', '2', '3', '*',
        'Space',       ' 0 ', 'DEL',  'ENTER' 
        ]
    
    SlTrace.lg(f"Number buttons:{len(buttons)}")
    
    # Alternative key faces
    alt_key_files = {
        '=' : "color_stripes.png",
        '7' : "arrow_135.png", '8' : "arrow_90.png",        '9' : "arrow_45.png",
        '4' : "arrow_180.png", '5' : "rotate_left.png",     '6' : "arrow_0.png",
        '1' : "arrow_225.png", '2' : "arrow_270.png",       '3' : "arrow_315.png",
        '0' : "rotate_right.png",
        ' 0 ' : key_attr(text="0", image="rotate_right.png", column=14),
        '[' : "princesses.png",
        ']' : "other_stuff.png",
        'Space' : key_attr(text="Space", column=5, columnspan=6),
        'a' : "size_decrease.png",
        'd' : "shapes_one.png",
        'e' : "drawing_abc.png",
        'f' : "lines_one.png",
        'h' : "drawing_help_me.png",
        'j' : "drawing_lion2.png",
        'k' : "images_next.png",
        'l' : "family.png",
        'q' : "size_increase.png",
        's' : "shapes_next3.png",
        't' : "width_increase.png",
        'x' : "width_decrease.png",
        'u' : "undo_drawing.png",
        'z' : "clear_all_2.png",
        '-' : "drawing_clear.png",
        '+' : "drawing_show.png",
        'r' : "drawing_red.png",
        'o' : "drawing_orange.png",
        'y' : "drawing_yellow.png",
        'g' : "drawing_green.png",
        'b' : "drawing_blue.png",
        'i' : "drawing_indigo.png",
        'v' : "drawing_violet.png",
        'w' : "drawing_rainbow.png",
        }


    
    from trace_control_window import TraceControlWindow
    
    bg = ButtonGrid(root, image_dir=image_dir,
                    on_kbd=on_kbd,
                    keys=buttons,
                    key_attrs=alt_key_files,
                    btn_specs=None,
                    win_width=600, win_height=400,
                    im_fract_x=.9, im_fract_y=.7,
                    btn_padx=2, btn_pady=2, btn_bd=3,
                    btn_font=('arial', 12, 'bold'),
                    nrows=5, ncols=16)
    tc = TraceControlWindow(bg)
    bg.enable_image_update()
    end_btn_infos = bg.get_btn_infos(key="END")
    bg.set_btn_image(end_btn_infos, "drawing_abc_end.png")
            
    root.mainloop()
    