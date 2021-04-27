# dm_image.py    28Feb2021  crs  drawing objects
"""
Square marker
"""
import os
from tkinter import *
from PIL import ImageTk, Image
from PIL import ImageDraw, ImageFont

from select_trace import SlTrace

from dm_marker import DmMarker

""" Support for image marker turtle style
"""
class DmImage(DmMarker):    
    def __init__(self, drawer,
                 draw_type=None,
                 file=None, image_base=None,
                 image_heading_default=0,
                 marker_type=None, **kwargs
                  ):
        """ Setup basic marker state
        :drawer: drawing control
        :file: image file, if one
        :image_base: base image, if one
                    May be added later via set_image_base()
        :marker_type: marker type (.e.g "letter")
        :kwargs: basic DmMarker args
        """
        if draw_type is None:
            draw_type = super().DT_IMAGE
        super().__init__(drawer, draw_type=draw_type, **kwargs)
        self.file = file
        self.image_base = image_base
        self.image_heading_default = image_heading_default
        self.marker_type = marker_type

    def __str__(self):
        return super().__str__()

    def draw(self):
        """ Draw square
        """
        super().draw()      # Ground work
        self.add_image()


    def add_image(self):
        """ Do image marker display
        Add image to canvas
        """
        
        image_key = self.file
        image = self.image_base
        rotation = (self.heading + self.image_heading_default)%360
        if self.marker_type != "letter":
            if rotation > 90 and rotation < 270:
                # for image around a vertical axis use Image.FLIP_LEFT_RIGHT
                # for horizontal axis use: Image.FLIP_TOP_BOTTOM
                image = image.transpose(Image.FLIP_TOP_BOTTOM)            
                SlTrace.lg(f"rotation:{rotation} FLIP_TOP_BOTTOM", "image_display")
            elif rotation > 270:
                #image = image.transpose(Image.FLIP_LEFT_RIGHT)            
                #image = image.transpose(Image.FLIP_TOP_BOTTOM)            
                SlTrace.lg(f"rotation:{rotation} FLIP_LEFT_RIGHT", "image_display")
        self.marker_image_width = self.side*2   # allow rotation
        self.marker_image_width = self.side     # Workaround untill...
        self.marker_image_height = self.marker_image_width
        try:
            image = image.resize((int(self.marker_image_width),
                         int(self.marker_image_height)),
                        Image.ANTIALIAS)
        except:
            SlTrace.lg(f"Can't resize Image({image_key}):"
                       f"\n  {self.marker_image_width}x{self.marker_image_height}")
            return 
        SlTrace.lg(f"rotate image: {self.file}", "image")    
        if self.marker_type != "letter":
            image = image.rotate(rotation)

        SlTrace.lg(f"PhotoImage: {self.file}", "image")    
        try:
            photo_image = ImageTk.PhotoImage(image=image)
        except:
            SlTrace.lg(f"Can't make PhotoImage({image_key}):"
                       f"\n  {self.marker_image_width}x{self.marker_image_height}")
            return 
        
        self.add_image_ref(photo_image)     # Save resource or may lose it
        self.create_image(
            self.x_cor, self.y_cor,
            image=photo_image)

    def set_image_base(self, image):
        """ Setup base image
        """
        self.image_base = image
        
if __name__ == "__main__":
    from dm_drawer_image import DmDrawerImage
    
    root = Tk()
    
    drawer = DmDrawerImage(root)
         
    nsquare = 8
    nsquare = 7
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    dms = []
    
    image = drawer.get_next_image()
    dm_base = DmImage(drawer, image_base=image,
                      x_cor=-100, y_cor=100)
    beg=0
    extent = dm_base.side*nsquare
    x_beg = -extent/2
    y_beg = x_beg
    for i in range(beg, beg+nsquare):
        ang =  i*360/nsquare
        icolor = i % len(colors)
        color = colors[icolor]
        dm = dm_base.change(heading=ang, color=color,
                            line_width=(i+1)*2,
                            x_cor=x_beg+i*dm_base.side,
                            y_cor=y_beg+i*dm_base.side,
                            side=(i+5)*20)
        dms.append(dm)
        
    for dm in dms:
        SlTrace.lg(f"\ndm:{dm}")
        dm.draw() 
    
    mainloop()       
