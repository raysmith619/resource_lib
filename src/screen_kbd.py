# screen_kbd.py    10Jan2021  crs, adapt/extend/steal
# Based on GitHub/Saujanya0910/On-Screen-Keyboard
# on-screen-keyboard.py
"""
Provide On-screen keyboard with alternative key display
A goal is to display to the users(mostly aged 3-8years)
pictures that correspond to game actions,
 e.g."upward right arrow" for the number pad "9" key.
We are hoping to develop a package which will facilitate
providing youthful users better keyboard access to computer
games.

Initially the screen keys will be hard coded.  The plan is to
provide flexibility.
"""
# import tkinter library with an alias
import os
from tkinter import *
import tkinter as tk
from PIL import Image, ImageTk
from functools import partial

from select_trace import SlTrace

class ScreenKbd:

    
    """ Translation of key to on_kbd argumnet
    If present translate, else pass key
    """
    
    key_tran_default = {
        " Space " : "space",        # Space bar display
        " " : "space",
        "-" : "minus",
        "+" : "plus",
        
        }
    
    def __init__(self, master,
                 title="On-screen Keyboard",
                 on_kbd=None, image_dir=None,
                 key_tran = None,
                 text_rows=3):
        """ Setup Screen Keyboard
        :master: master element
        :on_kbd: function of one argument, to be called
                when key button is clicked/pressed
                default: no call
        :text_rows: Number of rows in text display
                default = 3
        """
        self.kbd_frame = Frame(master)
        self.on_kbd = on_kbd
        if key_tran is None:
            key_tran = ScreenKbd.key_tran_default
        self.key_to_on_kbd = key_tran
        self.text_rows = text_rows
        self.kbd_frame.config(bg='powder blue')    # background
        self.kbd_frame.grid()

        # heading for the app
        label1 = Label(self.kbd_frame, text = title,
                       font=('arial', 30, 'bold'),
                       bg = 'powder blue',
                       fg = '#000000')
                       
        # create the heading
        label1.grid(row = 0, columnspan = 40)
        
        # text box 
        self.textBox = Text(self.kbd_frame, 
                        width = 180,
                        height = self.text_rows, 
                        font = ('arial', 10, 'bold'),
                        wrap = WORD)
        
        # create the textbox and focus
        self.textBox.grid(row = 1, columnspan = 40)
        self.textBox.focus()
        
        # buttons list
        self.buttons = [
            '`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-'  , '=','BKSP', 'HOME', 'END',
            '!', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p','BKSP', '7', '8'  , '9'   , '-',
            'Tab', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', '[', ']', '4', '5', '6', '+',
            'Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', '?', '1', '2', '3', '*',
            ' Space ',       '0', 'DEL',  'ENTER' 
            ]

        # initialise row, col for buttons
        nkey_rows = 5       # Number of rows of keys
        nkey_accross = 16   # Number of keys accross
        key_start_row = 3         # Grid row for first row of keys
        space_row = key_start_row + nkey_rows
        space_col_left = 2       # Space bar left
        space_col_right = 12    # Space bar right
        space_col_span = space_col_right - space_col_left +1
        var_row = key_start_row
        var_col = 0
        
        # Alternative key faces
        self.alt_key_files = {
            '=' : "color_stripes.png",
            '7' : "arrow_135.png", '8' : "arrow_90.png",        '9' : "arrow_45.png",
            '4' : "arrow_180.png", '5' : "rotate_left.png",     '6' : "arrow_0.png",
            '1' : "arrow_225.png", '2' : "arrow_270.png",       '3' : "arrow_315.png",
            '0' : "rotate_right.png",

            'a' : "size_decrease.png",
            'd' : "shapes_one.png",
            'f' : "lines_one.png",
            'h' : "drawing_help_me.png",
            'j' : "drawing_lion2.png",
            'k' : "images_next.png",
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
        
        
        if image_dir is None:
            SlTrace.lg(f'__file__:{__file__}')
            src_dir = os.path.dirname(os.path.abspath(__file__))
            SlTrace.lg(f'src_dir:{src_dir}')
            prj_dir = os.path.dirname(src_dir)
            SlTrace.lg(f'prj_dir:{prj_dir}')
            image_dir = os.path.join(prj_dir, "images", "keys")
            if not os.path.exists(image_dir):
                image_dir = src_dir     # assume images with src
                
        image_dir = os.path.abspath(image_dir)
        SlTrace.lg(f"image_dir:{image_dir}")
        self.image_dir = image_dir
        
        self.alt_key_faces = {}
        btn_size_x = 50
        btn_size_y = 40
        for alt_key in self.alt_key_files:
            alt_key_file = self.alt_key_files[alt_key]
            if alt_key_file is not None:
                alt_key_path = os.path.join(self.image_dir,
                                             alt_key_file)
                SlTrace.lg(f"alt_key:{alt_key} path:{alt_key_path}")
                if not os.path.exists(alt_key_path):
                    SlTrace.lg(f"We Can't find image for key {alt_key}"
                               f"\n looking in: {alt_key_path}")
                    continue
                base_image = Image.open(alt_key_path)
                scaled_image = base_image.resize((btn_size_x, btn_size_y))
                image = ImageTk.PhotoImage(scaled_image)
                self.alt_key_faces[alt_key] = image
        
        # toggle shift button press
        self.shift_on = False
        # save references of letter buttons
        self.letter_buttons = []

        for button in self.buttons:
            # command to run on every button click - buttonClick() function 
            cmd = lambda x = button: self.buttonClick(x)
            btn_text = button       # Default - text display
            btn_width = 7
            btn_image = None        # Default - no image
            btn_background = "black"
            btn_foreground = "white"
            btn_compound = None
            if button in self.alt_key_faces:
                alt_key_image = self.alt_key_faces[button]
                if alt_key_image is not None:
                    file = self.alt_key_files[button]
                    SlTrace.lg(f"button:{button} file: {file}")
                    btn_image = alt_key_image
                    btn_width = 70         # Pixels
                    btn_background = "white"
                    btn_foreground = "light gray"
                    btn_compound = tk.BOTTOM
                    #btn_text = None
                    SlTrace.lg(f"btn_image:{btn_image}")
            # for every button except 'space'
            if var_row < space_row and button != ' Space ':
                SlTrace.lg(f"add key button:{button} var_col:{var_col} var_row:{var_row}")
                btn = tk.Button(self.kbd_frame,
                    text = btn_text,
                    image = btn_image,
                    compound = btn_compound,                    
                    width = btn_width,
                    bg = btn_background,
                    fg = btn_foreground,
                    activebackground = 'white',
                    activeforeground = 'black',
                    relief = 'raised',
                    padx = 3,
                    pady = 3, 
                    bd = 5,
                    font=('arial', 12, 'bold'),
                    command = cmd)
                btn.grid(row = var_row, column = var_col)
                # save reference of letter buttons
                if self.is_letter(button):
                    self.letter_buttons.append(btn)
                 # go to next column for every different button
                var_col += 1
        
                # if number of buttons in one line crosses nkeys_accross,
                # go to next row and 0th col
                if var_col >= nkey_accross:
                    var_col = 0
                    var_row += 1 
            else:
                SlTrace.lg(f"SPACE BAR possibility: {button}")
                if button == ' Space ':
                    tk.Button(self.kbd_frame, 
                        text = btn_text,
                        image = btn_image,                    
                        compound = btn_compound,                    
                        width = 50, 
                        bg = btn_background,
                        fg = btn_foreground,
                        activebackground = 'white',
                        activeforeground = 'black',
                        relief = 'raised',
                        padx = 3,
                        pady = 3, 
                        bd = 12,
                        font=('arial', 12, 'bold'),
                        command = cmd).grid(row = space_row-1, column = space_col_left, columnspan = space_col_span)
                    var_col = space_col_left + space_col_span
                else:
                    if button == '0':
                        col_sp = 2
                        btn_wid = 7*2
                        bdr = 12
                    else:
                        col_sp = 1
                        btn_width = 7
                        bdr = 5
                    if button in self.alt_key_faces:
                        alt_key_image = self.alt_key_faces[button]
                        if alt_key_image is not None:
                            file = self.alt_key_files[button]
                            SlTrace.lg(f"button:{button} file: {file}")
                            btn_image = alt_key_image
                            btn_width = 70         # Pixels
                            btn_background = "white"
                            btn_foreground = "black"
                            btn_compound = tk.BOTTOM
                            #btn_text = None
                            SlTrace.lg(f"btn_image:{btn_image}")
                    btn = tk.Button(self.kbd_frame,
                        text = btn_text,
                        image = btn_image,                    
                        compound = btn_compound,                    
                        width = btn_width,
                        bg = btn_background,
                        fg = btn_foreground,
                        activebackground = 'white',
                        activeforeground = 'black',
                        relief = 'raised',
                        padx = 3,
                        pady = 3, 
                        bd = bdr,
                        font=('arial', 12, 'bold'),
                        command = cmd)
                    btn.grid(row = space_row, column = var_col, columnspan=col_sp)
                    var_col += col_sp 
                    # save reference of letter buttons
                        
    
    # check if the button corresponds to a letter
    def is_letter(self, s):
        return len(s) == 1 and 'a' <= s <= 'z'

    # function for button click
    def buttonClick(self, input):
    
        if input == 'Shift':
            # toggle shift status
            self.shift_on = not self.shift_on
            # update text of letter buttons according to status of shift btn
            for btn in self.letter_buttons:
                text = btn['text']
                btn['text'] = text.upper() if self.shift_on else text.lower()
        else:
            if input == ' Space ':
                self.textBox.insert(INSERT,' ')
            elif input == 'Tab':
                self.textBox.insert(INSERT, '    ')
            elif input == 'BKSP':
                self.backspace()
            else:
                # update text of letter buttons
                if self.is_letter(input):
                    input = input.upper() if self.shift_on else input.lower()
                self.textBox.insert(INSERT, input)
        if self.on_kbd is not None:
            if input in self.key_to_on_kbd:
                input = self.key_to_on_kbd[input]
            self.on_kbd(input)
    # function for backspace
    def backspace(self):
        self.textBox.delete('insert-1chars', INSERT)
    
    def input_char(self, input):
        """ Replicate action for input key
        :input: key/char from another source
        """
        self.textBox.insert(INSERT, input)
        

if __name__ == "__main__":
    keyboardApp = tk.Tk()   # initialise the tkinter app
    keyboardApp.config(bg='powder blue')    # background
    #keyboardApp.resizable(0, 0)     # disable resizeable property
    sk = ScreenKbd(keyboardApp, title="Testing ScreenKbd")
    
    # run the main loop of the app
    keyboardApp.mainloop()
     
