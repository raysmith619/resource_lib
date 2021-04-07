# dm_text.py    28Feb2021  crs  drawing objects
"""
Square marker
"""
from tkinter import *
from PIL import ImageTk, Image
from PIL import ImageDraw, ImageFont

from select_trace import SlTrace

from dm_image import DmImage

""" Support for image marker turtle style
"""
class DmText(DmImage):    
    def __init__(self, drawer, text=None,
                  **kwargs):
        """ Setup text marker state
        :drawer: drawing control
        :text: text to display
        :kwargs: basic DrawMarker args
        """
        super().__init__(drawer, draw_type=super().DT_TEXT,
                         marker_type="letter",
                         **kwargs)
        self.set_text_image(text)
        
        
        
    def set_text_image(self, text):
        """ Setup base image to represent text
        :text:
        """
        self.text = text
        text_size = int(self.side)
        font_size = 80
        text_font = ImageFont.truetype("arial.ttf", size=font_size)
        #text_font = ImageFont.truetype("courbd.ttf", size=text_size)
        #text_font = ImageFont.truetype("tahoma.ttf", size=text_size)
        text_color = self.color
        text_bg = ""    

        ###xy = (x0,y0)
        image = Image.new("RGB", (text_size, text_size), (255,255,255))
        draw = ImageDraw.Draw(image)      # Setup ImageDraw access
        draw.text((0,0), self.text, anchor="mt",
                  fill=text_color, font=text_font,
                  bg=text_bg)
        self.set_image_base(image)
        

    def __str__(self):
        return self.text + ":" + super().__str__()

    def change(self, text=None, **kwargs):
        """ Change object attibutes, returning changed object
            initial object is unchanged
            :text: new text/letter
            :kwargs: reminder of args
        """
        new_obj = super().change(**kwargs)
        if text is not None:
            new_obj.set_text_image(text)
        return new_obj
        
        
if __name__ == "__main__":
    from dm_drawer_image import DmDrawerImage
    
    root = Tk()
    
    drawer = DmDrawerImage(root)
         
    nsquare = 7
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    dms = []
    
    dm_base = DmText(drawer, text="A",
                      x_cor=200, y_cor=300)
    beg=0
    extent = dm_base.side*nsquare
    x_beg = 2*dm_base.side-extent/2
    y_beg = x_beg
    for i in range(beg, beg+nsquare):
        ang =  i*360/nsquare
        icolor = i % len(colors)
        color = colors[icolor]
        text = chr(ord(dm_base.text)+i)   
        dm = dm_base.change(heading=ang, color=color,
                            line_width=(i+1)*2,
                            x_cor=x_beg+.5*i*dm_base.side,
                            y_cor=y_beg+.5*i*dm_base.side,
                            side=(i+5)*20,
                            text=text)
        dms.append(dm)
        
    for dm in dms:
        SlTrace.lg(f"\ndm:{dm}")
        dm.draw()
        root.update() 
    
    mainloop()       
