# grid_resize_image.py
"""
I extended a very nice example I found in stackoverflow.com:
https://stackoverflow.com/questions/7591294/
how-to-create-a-self-resizing-grid-of-buttons-in-tkinter

The additional problem is how to resize the grid of buttons
if they contain images which you also want resized?
The technique I used requires changing the image sizes
proportionally when the window size changes.

The process goes as follows:
    1. Window size changes causing a <Configure> event, which is
    bound to win_size_event.

    2. If win_size_event determines that the button's image size
    has changed sufficiently, resize_grid function
    is called.
    
    3. resize_grid is responsible for altering the buttons
     A. resize_grid checks if the resizing of the buttons will
        exceed the target change in window size. If so, the size
        the changing is stopped to avoid runaway window resising.
     B. resize_grid reconfigures the buttons appropriately 

    The window size to button image size is calculated (roughly)
    by function get_btn_image_size.

"""
import os
import math 
from tkinter import *
from PIL import ImageTk, Image       # Expecting Pillow,
                                    # installed under same name
        
def sign(x):
    """ sign - from stackoverflow suggestion
    :x: value to take sign and return 1 for positive, -1 neg
    """
    return math.copysign(1, x)


class ImageGrid:
    def __init__(self, master=None, image_infos=None,
                 nrow=5, ncol=5,
                 command=None,
                 btn_pad_x=1, btn_pad_y=1, btn_bd=1):
        """ Display a grid of images
        :master: master window/frame default: Tk()
        :image_infos: list of images or (text,image) tuples
                REQUIRED
        :nrow: number of rows
        :ncol: number of columns
        :command: command called when button clicked
                default: internal display called
                command called with image_infos index as arg
        """
        if master is None:
            master = Tk()
        self.master = master
        self.image_infos = image_infos
        self.nrow = nrow
        self.ncol = ncol
        self.command = command
        self.btn_pad_x = btn_pad_x  # Adjustments
        self.btn_pad_y = btn_pad_y
        btn_size_x = btn_size_y = 40    # Initial button size
        self.btn_bd = btn_bd
        self.btn_infos = {}             # Storage [irow,icol}
                                        #    of (btn,base_image)
        self.img_change_target = None   # Target image (width_chg, height_chg)
        self.prev_img_size = None       # (img_width, img_height)
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        
        self.grid_frame=Frame(master)        #Create & Configure frame
        self.grid_frame.grid(row=0, column=0, sticky=N+S+E+W)
        btn_font=('arial', 12, 'bold')
        self.btn_images = {}            # References(by label) to btn photo images
        i_image = -1        # Index through image_infos
        for row_index in range(nrow):
            self.grid_frame.rowconfigure(row_index, weight=1)
            for col_index in range(ncol):
                self.grid_frame.columnconfigure(col_index, weight=1)
                i_image += 1
                if i_image >= len(image_infos):
                    break         # stop at end of images
                image_info = image_infos[i_image]
                if isinstance(image_info, tuple):
                    btn_label = image_info[0]       # (label, image) list
                    base_image = image_info[1]
                else:
                    btn_label = f"({row_index},{col_index})"    # image list
                    base_image = image_info 
                scaled_image = base_image.resize((int(btn_size_x),
                                                  int(btn_size_y)))
                btn_image = ImageTk.PhotoImage(master=self.master, image=scaled_image)
                self.btn_images[btn_label] = btn_image  # save reference
                self.grid_frame.columnconfigure(col_index, weight=1)
                display_text = f"{btn_label}"   # for command display
                btn = Button(self.grid_frame,
                    text = btn_label,
                    font = btn_font,
                    image = btn_image,
                    compound = BOTTOM,      # image below text                    
                    command = lambda txt = display_text : self.cmd(txt))
                btn.grid(row=row_index, column=col_index, sticky=N+S+E+W)
                self.btn_infos[row_index,col_index] = (btn, base_image)
                self.master.update() 
        self.grid_frame.bind('<Configure>', self.win_size_event)

    def cmd(self, text):
        print(f"{text} button clicked")

    def resize_grid(self):
        """ Change image sizes so that new grid size
        approximates the new window size
        Lots of the debugging print calls are left in
        for educational purposes.
        """
        win_width, win_height = self.win_width, self.win_height
        img_width, img_height = self.get_btn_image_size(
                            win_width, win_height)
        print(f"resize_grid: win:{win_width}x{win_height} img:{img_width}x{img_height}")
        if self.prev_img_size is None:
            self.prev_img_size = (img_width, img_height)
        prev_width, prev_height = self.prev_img_size
        width_change = img_width - prev_width
        height_change = img_height - prev_height
        if self.img_change_target is None:
            print(f"   new change_target: {width_change}x{height_change}")
            self.img_change_target = (width_change, height_change)
        width_change_target, height_change_target = self.img_change_target
        print(f"   WxH target:{width_change_target}x{height_change_target}")
        print(f"   WxH change:{width_change}x{height_change}")
        if (sign(width_change) == sign(width_change_target)
                and abs(width_change) > abs(width_change_target)
                and sign(height_change) == sign(height_change_target)
                and abs(height_change) > abs(height_change_target)):
            self.prev_img_size = (img_width, img_height)
            print(f" target made - stop resize")
            print(f" new={img_width}x{img_height} prev={prev_width}x{prev_height}\n")
            
            return      # Met our goal - no more resizing
             
        print(f"     resize to: btn_w={img_width} btn_h={img_height}")
        font_height = int(max(12, min(15, img_height/5)))
        btn_font=('arial', int(-font_height), 'bold')

        for row_index in range(self.nrow):
            for col_index in range(ncol):
                imo_key = (row_index,col_index)
                if not imo_key in self.btn_infos:
                    continue
                btn, base_image = self.btn_infos[imo_key]
                label = btn.cget('text')
                scaled_image = base_image.resize((img_width,
                                              img_height))
                btn_image = ImageTk.PhotoImage(master=self.master, image=scaled_image)
                self.btn_images[label] = btn_image
                btn.config(text=label, font=btn_font, image=btn_image) # store new image
        self.img_change_target = (width_change,height_change)
        print(f"   new change_target: {width_change}x{height_change}")
            
    def win_size_event(self, event):        
        """ Window sizing event
        """
        min_chg = 0    # Minimum change recognizable
        
        self.win_width = win_width = self.master.winfo_width()
        self.win_height = win_height = self.master.winfo_height()
        img_width, img_height = self.get_btn_image_size(
                            win_width, win_height)
        print(f"win_size_event: win:{win_width}x{win_height} img:{img_width}x{img_height}")
        
        if self.prev_img_size is None:
            self.prev_img_size = (img_width, img_height)
        prev_width, prev_height = self.prev_img_size
        width_change = img_width - prev_width
        height_change = img_height - prev_height
        
        if (abs(width_change) >= min_chg
            or abs(height_change) >= min_chg):
            self.resize_grid()
        print("        win_size_event - End")

    def get_btn_image_size(self, win_width=None, win_height=None):
        """ Calculate button's image size based on
        window size and number of button rows, columns
        :win_width: window width (pixels)
                    default: get from window
        :win_height: window height
                    default: get from window
        :returns: (x_size, y_size) in pixels
        """
        text_height = 10
        if win_width is None:
            win_width = self.win_width
        if win_height is None:
            win_height = self.win_height
        btn_size_x_raw = win_width/self.ncol - self.btn_bd
        btn_size_x = btn_size_x_raw - self.btn_pad_x
        btn_image_size_x = btn_size_x 
        
        btn_size_y_raw = win_height/self.nrow - self.btn_bd
        btn_size_y = btn_size_y_raw
        btn_image_size_y = btn_size_y - text_height
        return (int(btn_image_size_x), int(btn_image_size_y)) 

    def mainloop(self):
        self.master.mainloop()

if __name__ == "__main__":
    """ Create some example images without resorting to 
    to other files.  I use text images because they are
    recognizable.
    """
    from PIL import ImageTk, Image
    from PIL import ImageDraw, ImageFont
    
    def pixel2point(px):
        """ Convert pixels to point size
        """
        pt = int(72./96.*px)
        return pt

    
    def make_text_image(text, text_color="blue"):
        """ make image of text
        :text: text string
        :returns: image (Image)
        """
        text_size = 100
        font_size = pixel2point(text_size)
        text_font = ImageFont.truetype("arial.ttf", size=font_size)
        
        image = Image.new("RGB", (text_size, text_size), (255,255,255))
        draw = ImageDraw.Draw(image)      # Setup ImageDraw access
        draw.text((0,0), text,
                  fill=text_color, font=text_font)
        #text_images[text] = image
        return image
    
    nrow = 5
    ncol = 6
    image_infos = []
    for i in range(nrow*ncol):
        ch = chr(ord("A")+i)
        image = make_text_image(ch)
        image_infos.append((ch, image))
    
    ig = ImageGrid(image_infos=image_infos, nrow=nrow, ncol=ncol)
    ig.mainloop()
