#dm_drawer.py
"""
Hopefully simple drawing control for the DmMarker
family of classes to develop, test and demonsrate
In the interest of simplifying the non-image classes
the image support will be placed in the derived 
class DmDrawerImage

DmDrawer class is a toy class to facilitate
development and self testing DmMarker and
classes based on DmMarker
"""
import os 

from tkinter import *
import copy
import math
import tkinter as tk

from select_trace import SlTrace
from select_error import SelectError
from select_window import SelectWindow

from attr_change import AttrChange, Attribute

class DmDrawer(SelectWindow):

    IT_FILE = "it_file"     # image from file
    IT_TEXT = "it_text"     # image generated 
    
    def __init__(self, master, title=None,
                 kbd_master=None, canvas=None,
                 draw_x=20, draw_y=20,
                 draw_width=1500, draw_height=1000,
                 kbd_win_x=0, kbd_win_y=0,
                 kbd_win_width=350, kbd_win_height=200,
                 side=100,
                 width=20,
                 hello_drawing_str=None,
                 with_screen_kbd=True,
                 show_help=True,
                 **kwargs
                 ):
        """ Keyboard Drawing tool
        with simple functional interface
        """
        if canvas is None:
            canvas = tk.Canvas(master=master,
                               width=draw_width, height=draw_height,
                               bd=2, bg="white", relief="ridge")
            canvas.pack(expand=True, fill=tk.BOTH)
        self.draw_width = draw_width
        self.draw_height = draw_height
        self.canv = canvas
        self.canvas_width = draw_width    # Fudge
        self.canvas_height = draw_height   # Fudge
        self.x_cor = 0
        self.y_cor = 0
        self.side = side
        self.line_width = width
        self.heading = 0
        self.attr_chg = AttrChange()    # Setup attributes
        attr = Attribute("color", 
            ["red", "orange", "yellow", "green",
                "blue", "indigo", "violet"])
        self.attr_chg.add_attr(attr) 
        attr = Attribute("shape", 
            ["line", "square", "triangle", "circle"])
        self.attr_chg.add_attr(attr)
        self.setup_image_access() 
        ###self.canv.bind ("<ButtonPress>", self.mouse_down)
        
        
    def get_canvas(self):
        """ Get our working canvas
        """
        return self.canv
    
    def get_heading(self):
        return self.heading

    def get_x_cor(self):
        return self.x_cor

    def get_y_cor(self):
        return self.y_cor

    def get_next(self, name):
        """ Get next attribute value
        :name: attribute name
        :return: attribute value
        """
        return self.attr_chg.get_next(name)

    def get_copy_move(self):
        return self.copy_move
    
    def set_copy_move(self, copy_move):
        self.copy_move = copy_move
        
    def get_loc(self):
        return (self.get_x_cor(), self.get_y_cor())
        
    def get_side(self):
        return self.side

    def get_width(self):
        return self.line_width
     
    def get_image_file(self, group=None, file=None, next=True):
        """ get current image group's file
        :group: group name default: current group
        :file: file name default: current or next
        :next: if true get next
        """
        ifg = self.get_image_file_group(name=group)
        if file is not None:
            im_file = ifg.get_file(file=file)
            return im_file
            
        if next:
            inc = 1
        else:
            inc = 0
        im_file = ifg.get_file(inc=inc)
        SlTrace.lg(f"get_image_file: {im_file}", "image_display")
        return im_file

    def get_image_file_group(self, name=None):
        """ Get current marker image file group (DataFileGroup)
        :name: group name
                default: return current self.image_group
        """
        if name is None:
            name = "animals"
        ifg = self.ifh.get_group(name)
        return ifg

    def get_next_image(self):
        """ Get next from current image group
        :returns: imageinfo (key, image)
        """
        display_file = self.get_image_file()
        return self.image_file_to_image(display_file)
    
    def set_heading(self, heading):
        self.heading = heading
                


    def set_side(self, side):
        self.side = side

    def set_width(self, line_width):
        self.line_width = line_width


    def set_size(self, side=None, line_width=None):
        if side is not None:
            self.set_side(side)
        if line_width is not None:
            self.set_width(line_width)

    def setup_image_access(self, image_dir=None):
        """ Setup image access for markers
        :image_dir: image file directory
        """
        if image_dir is None:
            image_dir="./images"    # Distribution choice
            SlTrace.lg(f"Trying distibution image dir: {image_dir}")
            if not os.path.exists(image_dir):
                image_dir="../../resource_lib/images"
                SlTrace.lg(f"Using development image dir: {image_dir}")
        
        self.image_type = "it_file"
        self.image_group_names = ["animals", "family", "princesses",
                             "other_stuff"]
        self.image_group_index = len(self.image_group_names)
        if self.image_group_index >= len(self.image_group_names):
            self.image_group_index = 0
        group_name = self.image_group_names[self.image_group_index]
        
        self.ifh = DataFiles(data_dir=image_dir)
        for name in self.image_group_names:
            group_dir = os.path.join(image_dir, name)
            self.ifh.add_group(name, group_dir=group_dir)
                
        SlTrace.lg("Image Files")
        data_files_dir="../../resource_lib/images/animals"
        image_files_dir = os.path.abspath(data_files_dir)
        if not os.path.exists(image_files_dir):
            SlTrace.lg(f'__file__:{__file__}')
            src_dir = os.path.dirname(os.path.abspath(__file__))
            SlTrace.lg(f"Assuming images are in src_dir")
            SlTrace.lg(f'src_dir:{src_dir}')
            prj_dir = os.path.dirname(src_dir)
            SlTrace.lg(f'prj_dir:{prj_dir}')
            image_dir = prj_dir
        self.image_dir = os.path.abspath(image_dir)
        SlTrace.lg(f"image_dir:{image_dir}")
        self.select_image_hash = ImageHash(image_dir=self.image_dir)
        self.select_image_files = self.select_image_hash.get_image_files()
        """ Marker images
            stored at twice size to facilitate rotation without
            loss of picture
            NOTE: needs work to support side size changes
        """
        self.marker_image_hash = ImageHash(image_dir=self.image_dir)
        self.marker_image_files = self.select_image_hash.get_image_files()
        self.image_index = len(self.marker_image_files)    # will wrap to 0
        self.photo_images = {}      # Keeping references
        self.marker_image_tags = []
        self.image_chosen = None 

    def image_file_to_image(self, file):
        """ Get base image from file
        """
        image = self.marker_image_hash.get_image(
                            key=file,
                            photoimage=False)
        return image
