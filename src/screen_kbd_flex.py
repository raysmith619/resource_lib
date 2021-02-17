# screen_kbd_flex.py    09Feb2021  crs, adapt/extend/steal
# Adapt screen_kbd.py to use button_grid.py(ButtonGrid)
# screen_kbd.py based on GitHub/Saujanya0910/On-Screen-Keyboard
# on-screen-keyboard.py
"""
Provide On-screen keyboard with alternative key display
A goal is to display to the users(mostly aged 3-8years)
pictures that correspond to game actions,
 e.g."upward right arrow" for the number pad "9" key.
We are hoping to develop a package which will facilitate
providing youthful users better keyboard access to computer
games.

"""
# import tkinter library with an alias
import os
from tkinter import *
import tkinter as tk
from PIL import Image, ImageTk
from functools import partial

from select_trace import SlTrace
from button_grid import ButtonGrid, key_attr

class ScreenKbdFlex:

    
    """ Translation of key to on_kbd argument
    If present translate, else pass key
    """
    
    key_tran_default = {
        " Space " : "space",        # Space bar display
        " " : "space",
        "-" : "minus",
        "+" : "plus",
        
        }
    
    def __init__(self, master,
                title="Flexible On-screen Keyboard",
                on_kbd=None, image_dir=None,
                key_tran = None,
                text_rows=3,
                win_x=50,
                win_y=100,
                win_width=300,
                win_height=100,
                **kwargs):
        """ Setup Screen Keyboard
        :master: master element
        :on_kbd: function of one argument, to be called
                when key button is clicked/pressed
                default: no call
        :text_rows: Number of rows in text display
                default = 3
        """
        SlTrace.lg("Setup Screen Keyboard")
        win_setting = "%dx%d+%d+%d" % (win_width, win_height, win_x, win_y)
        master.geometry(win_setting)

        self.shift_on = False

        SlTrace.lg(f"Initial image_dir: {image_dir}")
        self.on_kbd = on_kbd
        if key_tran is None:
            key_tran = self.key_tran_default
        self.key_to_on_kbd = key_tran
        self.text_rows = text_rows

        self.master = master
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)


        self.kbd_frame = Frame(self.master)
        self.kbd_frame.grid(sticky=N+S+E+W)  
        self.kbd_frame.rowconfigure(0, weight=1)
        self.kbd_frame.rowconfigure(1, weight=1)
        self.kbd_frame.rowconfigure(2, weight=8)
        self.kbd_frame.columnconfigure(0, weight=1)
        self.kbd_frame.config(bg='powder blue')    # background
        
        # heading for the app
        label1 = Label(self.kbd_frame, text = title,
                       font=('arial', 20, 'bold'),
                       bg = 'powder blue',
                       fg = '#000000')
                       
        # create the heading
        label1.grid(sticky=N+S+E+W)
        label1.rowconfigure(0, weight=1)
        label1.columnconfigure(0, weight=1)
        
        # text box
        text_box_frame = Frame(self.kbd_frame) 
        text_box_frame.grid(sticky=N+S+E+W)  
        text_box_frame.rowconfigure(0, weight=1)
        text_box_frame.columnconfigure(0, weight=1)
        self.text_box = Text(text_box_frame, 
                        height = self.text_rows, 
                        font = ('arial', 10, 'bold'),
                        wrap = WORD)
        
        # create the textbox and focus
        self.text_box.grid(sticky=N+S+E+W)
        self.text_box.rowconfigure(0, weight=1)
        self.text_box.columnconfigure(0, weight=1)
        self.text_box.focus()
        
        keys_frame = Frame(self.kbd_frame)
        keys_frame.grid(sticky=N+S+E+W)  
        keys_frame.rowconfigure(0, weight=1)
        keys_frame.columnconfigure(0, weight=1)

        """ Setup for QWERTY keyboard
            with key face images for keyboard_draw
        """

        # key buttons list
        buttons = [
            '`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-'  , '=','BKSP', 'HOME', 'END',
            '!', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p','BKSP', '7', '8'  , '9'   , '-',
            'Tab', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', '[', ']', '4', '5', '6', '+',
            'Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', '?', '1', '2', '3', '*',
            'Space',       ' 0 ', 'DEL',  'ENTER' 
            ]
        
        SlTrace.lg(f"Number buttons:{len(buttons)}")
        
        # Alternative key faces - key attributes
        key_attrs = {
            '=' : "color_stripes.png",
            '7' : "arrow_135.png", '8' : "arrow_90.png",        '9' : "arrow_45.png",
            '4' : "arrow_180.png", '5' : "rotate_left.png",     '6' : "arrow_0.png",
            '1' : "arrow_225.png", '2' : "arrow_270.png",       '3' : "arrow_315.png",
            '0' : "rotate_right.png",
            ' 0 ' : key_attr(text="0", image="rotate_right.png", column=14),
            '[' : "princesses.png",
            ']' : "other_stuff.png",
            '/' : "drawing_rotate_2.png",
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
            'z' : "clear_all.png",
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
        
        
        self.button_grid = ButtonGrid(keys_frame,
                            nrows=5, ncols=16,
                            keys=buttons,
                            key_attrs=key_attrs,
                            on_kbd=self.buttonClick,
                            win_width=win_width,
                            win_height=win_height*(5/7),
                             **kwargs)
                        
    def do_shift(self, shift_on=True):
        """ Shift letters
        :shift_on: Put shift on, adjust letters
                    default: True
        """
        self.shift_on = shift_on
        self.button_grid.do_shift(shift_on=shift_on)
        
    def enable_image_update(self, enable=True):
        """ Enable/Disable kbd image update
        :enable: enable update default: True
        """
        self.button_grid.enable_image_update(enable)
        
        
    # check if the button corresponds to a letter
    def is_letter(self, s):
        return len(s) == 1 and 'a' <= s <= 'z'

    # function for button click
    def buttonClick(self, input):
    
        if input == 'Shift':
            # toggle shift status
            self.shift_on = not self.shift_on
            self.do_shift(self.shift_on)
        else:
            if input == ' Space ':
                self.text_box.insert(INSERT,' ')
            elif input == 'Tab':
                self.text_box.insert(INSERT, '    ')
            elif input == 'BKSP':
                self.backspace()
            else:
                # update text of letter buttons
                if self.is_letter(input):
                    input = input.upper() if self.shift_on else input.lower()
                self.text_box.insert(INSERT, input)
        if self.on_kbd is not None:
            if input in self.key_to_on_kbd:
                input = self.key_to_on_kbd[input]
            self.on_kbd(input)
    # function for backspace
    def backspace(self):
        self.text_box.delete('insert-1chars', INSERT)
    
    def input_char(self, input):
        """ Replicate action for input key
        :input: key/char from another source
        """
        self.text_box.insert(INSERT, input)

    def set_images(self, show=False):
        """ Set key images to show or not show
        :show: True - show images on keys
                default: hide
        """
        self.button_grid.set_images(show=show)

    def get_btn_infos(self, key=None, row=None, col=None):
        """ Get buttons
        :key: if not None, must match
        :row: if not None, must match
        :col: if not None, must match
        """
        return self.button_grid.get_btn_infos(key=key, row=row, col=col)

    def set_btn_image(self, btn_infos=None, image=None):
        """ Set button (btn_infos) image displayed
        :btn_infos: ButtonInfo, or list of ButtonInfos
        :image" text - image file
                Image - image
        """
        self.button_grid.set_btn_image(btn_infos=btn_infos, image=image)

    def to_top(self):
        """ Bring screen keyboard to top and focus
        """
        self.master.deiconify()

if __name__ == "__main__":
    keyboardApp = tk.Tk()   # initialise the tkinter app
    keyboardApp.config(bg='powder blue')    # background
    #keyboardApp.resizable(0, 0)     # disable resizeable property
    
    def on_kbd(input):
        """ Test keyboard button click
        :input: key text
        """
        SlTrace.lg(f"key: '{input}'")

    
    
    sk = ScreenKbdFlex(keyboardApp, title="Testing ScreenKbdFlex",
                       on_kbd=on_kbd,
                       win_x=50, win_y=100,
                       win_width=600, win_height=350)                      
    # run the main loop of the app
    keyboardApp.mainloop()
     
