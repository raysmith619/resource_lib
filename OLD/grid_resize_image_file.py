# grid_resize_image_file.py
"""
I extended a very nice example I found in stackoverflow.com:
https://stackoverflow.com/questions/7591294/
how-to-create-a-self-resizing-grid-of-buttons-in-tkinter

The additional problem is how to resize the grid of buttons
if they contain images which you also want resized?
The technique I used required binding the window resizing event
to a function to resize the image proportionly with the window
resizing
"""
import os
import math 
import glob
from tkinter import *
from PIL import Image, ImageTk      # Expecting Pillow,
                                    # installed under same name
        
def sign(x):
    """ sign - from stackoverflow suggestion
    :x: value to take sign and return 1 for positive, -1 neg
    """
    return math.copysign(1, x)





#Create a nrow x ncol (rows x columns) grid of buttons inside the frame
nrow = 5
ncol = 10
i_image = -1        # Index to current image file
btn_size_x = 100
btn_size_y = 100

class ImageGrid:
    def __init__(self, master=None, images=None, nrow=5, ncol=5,
                 btn_pad_x=1, btn_pad_y=1, btn_bd=1):
        """ Display a grid of images
        :master: master window/frame default: Tk()
        :images: list of image files (strs) or (image, file) (tuple)
                REQUIRED
        :nrow: number of rows
        :ncol: number of columns
        """
        if master is None:
            master = Tk()
        self.master = master
        self.images = images
        self.nrow = nrow
        self.ncol = ncol
        self.btn_pad_x = btn_pad_x  # Adjustments
        self.btn_pad_y = btn_pad_y
        self.btn_bd = btn_bd
        self.btn_images = {}            # refs to photoimages
        self.btn_infos = {}             # Storage [irow,icol}
                                        #    of (btn,base_image)
        self.img_change_target = None   # Target image (width_chg, height_chg)
        self.prev_img_size = None       # (img_width, img_height)
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        
        self.grid_frame=Frame(master)        #Create & Configure frame
        self.grid_frame.grid(row=0, column=0, sticky=N+S+E+W)
        btn_font=('arial', int(-btn_size_y/5), 'bold')
        i_image = 0
        for row_index in range(nrow):
            self.grid_frame.rowconfigure(row_index, weight=1)
            for col_index in range(ncol):
                self.grid_frame.columnconfigure(col_index, weight=1)
                i_image += 1
                if i_image >= len(image_infos):
                    i_image = 0         # If necessary, cycle
                image_info = images[i_image]
                if type(image_info) == str:
                    image_file = image_info
                    base_image = Image.open(image_file)
                else:
                    image_file, base_image = image_info 
                btn_text = f"{row_index},{col_index}"
                scaled_image = base_image.resize((int(btn_size_x),
                                                  int(btn_size_y)))
                btn_image = ImageTk.PhotoImage(master=self.master, image=scaled_image)
                self.btn_images[col_index,row_index] = btn_image # keep ref
                    
                self.grid_frame.columnconfigure(col_index, weight=1)
                display_text = f"{btn_text} {os.path.basename(image_file)}"
                btn = Button(self.grid_frame,
                    text = btn_text,
                    font = btn_font,
                    image = btn_image,
                    compound = BOTTOM,                    
                    command = lambda txt = display_text : self.cmd(txt))
                btn.grid(row=row_index, column=col_index, sticky=N+S+E+W)
                self.btn_infos[row_index,col_index] = (btn, base_image) 
        self.grid_frame.bind('<Configure>', self.win_size_event)

    def cmd(self, text):
        print(f"{text} button clicked")
        
    def resize_grid(self):
        """ Change image sizes so that new grid size
        approximates the new window size
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
                
                btn, base_image = self.btn_infos[row_index,col_index]
                scaled_image = base_image.resize((img_width,
                                              img_height))
                btn_image = ImageTk.PhotoImage(master=self.master, image=scaled_image)
                self.btn_images[row_index, col_index] = btn_image
                btn_text = f"{row_index},{col_index}"
                btn.config(text=btn_text, font=btn_font, image=btn_image) # store new image
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

# Get some images
# I use some I created for keyboard_draw
src_dir = os.path.dirname(__file__)
prj_dir = os.path.dirname(src_dir)
image_dir = os.path.join(prj_dir, "images", "keys")
image_path = os.path.join(image_dir, "*.png")
print(f"If you choose, replace image_dir: {image_dir}")

image_infos = []        # file,base_image pairs
for file in glob.glob(image_path):
    if not os.path.exists(file):
        print(f"We Can't find image file {file}")
        continue
    try:
        base_image = Image.open(file)
    except:
        print(f"Can't open image file: {file} - skipping")
        continue
    image_infos.append((file, base_image))
    
if len(image_infos) == 0:
    print(f"No image files found in {image_dir}")
    sys.exit()

nrow = 5
ncol = 16
gd = ImageGrid(images=image_infos, nrow=nrow, ncol=ncol)
gd.mainloop()
