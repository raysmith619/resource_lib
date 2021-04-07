# text_image.py    07Mar2021  crs
"""
Display Text image
"""
from tkinter import *
from PIL import ImageTk, Image
from PIL import ImageDraw, ImageFont

from select_trace import SlTrace

def pixel2point(px):
    """ Convert pixels to point size
    """
    pt = int(72./96.*px)
    return pt

if __name__ == "__main__":
    root = Tk()
    win_width = 300
    win_height = 300
    root.geometry(f"{win_width}x{win_height}")
    canvas_width = .9*win_width
    canvas_height = .9*win_width
    canvas = Canvas(root, width=canvas_width,
                    height=canvas_height, bg="light green")
    canvas.pack()
    
    text = "A"
    text_size = int(.9*canvas_width)
    font_size = int(1.5*pixel2point(text_size))
    SlTrace.lg(f"text_size:{text_size} font_size:{font_size}")
    text_font = ImageFont.truetype("arial.ttf", size=font_size)
    text_color = "blue"
    text_bg = "red"    
    text_images = {}
    photo_images = {}
    
    image = Image.new("RGB", (text_size, text_size),
                      (255,255,255))
    draw = ImageDraw.Draw(image)      # Setup ImageDraw access
    dt_anchor = None
    tx = int(1.*text_size/2)
    ty = int(.7*text_size/2)
    tx = int(text_size/2)
    ty = int(.7*text_size/2)
    tx = ty = int(text_size/2); dt_anchor = "mm"
    tx = ty = int(0); dt_anchor = "la"
    draw.rectangle([0,0,text_size,text_size], fill="pink",
                   outline="black")
    draw.text((tx,ty), text, anchor=dt_anchor,
              fill=text_color, font=text_font,
              bg=text_bg)
    text_images[text] = image
    image = image.resize((text_size,text_size))
    photo_image = ImageTk.PhotoImage(image)
    photo_images[text] = photo_image     # Save resource or may lose it
    
    ci_anchor = "center"
    x = y = int(text_size/2); ci_anchor = "center"
    tag = canvas.create_image(x,y, image=photo_image,
                              anchor=ci_anchor)
    SlTrace.lg(f"create_image: x={x:.0f}, y={y:.0f} tag={tag}")

    root.mainloop()
