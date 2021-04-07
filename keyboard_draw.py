#keyboard_draw.py    12Dec2020  crs
"""
Drawing on turtle window, using keyboard
"""
import os
import sys
import re
import math
import tkinter as tk
import argparse

from select_trace import SlTrace
from select_list import SelectList
from select_window import SelectWindow
from kbd_cmd_proc import KbdCmdProc
from dm_pointer import DmPointer

""" Using ScreenKbd
from screen_kbd import ScreenKbd
"""
from screen_kbd_flex import ScreenKbdFlex

from image_hash import ImageHash
from data_files import DataFiles

undomax = 2000      # Maximum turtle undo count
            
class KeyboardDraw(SelectWindow):

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
        :master: master
        :kbd_master: screen keyboard master, if present
                    must be grid managed
                    default: create Toplevel
        :draw_width: drawing window width default: 1500 pixels
        :draw_height: drawing window height default: 1000
        :kbd_win_x: screen keyboard initial x
        :kbd_win_y: screen keyboard initial y
        :kbd_win_width: screen keyboard width
        :kbd_win_height: screen keyboard height
        :canvas: base canvas
                default: create 500x500
        :side: starting line side length
            default: 100
        :width: starting line width
                default: 20
        :hello_drawing_str: Beginning display command string
                default: HI...
        :with_screen_kbd: Has screen keyboard control
                    default: True
        :show_help: Show help text at beginning
                    default: True
        """
        control_prefix = "KbdDraw"
        self.x_cor = 0 
        self.y_cor = 0 
        self.heading = 0
        self.color_current = "red"
        self.color_changing = True
        self.color_index = 0
        super().__init__(master,title=title,
                         control_prefix=control_prefix,
                         **kwargs)

        self.cmd_pointer = None     # marker pointer
        
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


        self.canv.bind ("<ButtonPress>", self.mouse_down)
        self.cmd_proc = KbdCmdProc(self)
        
        """ Setup our own, outside turtle, key processing """
        self.bound_keys = {}     # functions, bound to keys

        self.master = master
        self.side = side
        self.current_width = width
        self.do_trace = False    # Set True to do debugging trace
        self.do_trace = True
        self.set_key_mapping()
        canvas_width = self.canv.winfo_width()
        canvas_height = self.canv.winfo_height()
        x_start = int(-canvas_width/2 + side)
        y_start = int(canvas_height/2 - side)
        side = self.side
        width = self.current_width
        ostuff_x = x_start + side
        ostuff_y = y_start - 6*side
        hi_stuff_x = ostuff_x+5*side
        hi_stuff_y = ostuff_y +1*side
        hi_side = side/5
            
        if hello_drawing_str == "BUILTIN":
            hello_drawing_str = f"""
            # Beginning screen pattern
            # Add in Family
            minus
            line({side},{width})        # Set side, width
            moveto({x_start},{y_start})
            plus
            setnewline();F;a;m;i;l;y;END
            newline();a;l;e;x;END;image_file(family,alex);q
            newline();d;e;c;l;a;n;END;image_file(family,declan);q
            newline();a;v;e;r;y;END;image_file(family,avery);q
            newline();c;h;a;r;l;i;e;END;image_file(family,charlie);q
            
        ###    # Add in animals
        ###    k
        ###    plus
        ###    k;Right;a;a
        ###    k;Right;a:a
        ###    k;Right;a;a
        ###    k;Right;a;a
        ###    k;Right;a;a
            
            # A bit of other stuff
        check
        shorten();shorten();shorten()
        newline();END;image_file(princesses,princess);q
        image_file(other_stuff,batman) 
        image_file(other_stuff,baseball) 

            """
            hello_drawing_str += f"""
            minus
            # HI in middle of screen
            shape(line)
            marker(line)
            shape(line)
            line({hi_side},{width})        # Set side, width
            moveto({hi_stuff_x},{hi_stuff_y})
            w
            plus
            check
            Down;Down;Down;Down;Down;Down;Down;Down
            Up;Up;Up;Up; Right;Right; Up;Up;Up;Up
            Down;Down;Down;Down;Down;Down;Down;Down
            minus;Right;Right
            
            plus
            Up;Up;Up;Up;Up;Up;Up;Up
            minus
            
            line({side},{width})        # Set side, width
            Down;Down;Right;plus
            """
            
            """
            # Line under
            minus
            line({side},{4})
            moveto({int(self.canvas_width/2-side)},{int(-self.canvas_height/2+side)})
            plus
            Left
            t;=#ff0000;shape(rotate)
            t;=#0ff000;shape()
            t;=#00ff00;shape()
            t;=#000ff0;shape()
            t;=#0000ff;shape()
            t;=#f0f0f0;shape()
            t;=#af0f0f;shape(line)
            t;=#0ff000;shape()
            t;=#00ff00;shape()
            t;=#000ff0;shape()
            t;=#0000ff;shape()
            line({side},{width})        # Set side,width to starting
            w
            check
            """
        self.hello_drawing_str = hello_drawing_str
        SlTrace.lg(f"hello_drawing_str evaluated:"
                   f"\n{hello_drawing_str}")
        
        # Rotating pattern of custom colors
        self.custom_colors = []

        self.setup_image_access()
        self.moves_canvas_tags = []  # Init for canvas part of draw_undo
        self.clear_all()            # Setup initial settings
        
        
        
        self.enlarge_fraction = .2   # Enlargement fraction
        if with_screen_kbd:
            if kbd_master is None:
                kbd_master = tk.Toplevel()
            self.kbd_master = kbd_master
            self.screen_keyboard = ScreenKbdFlex(kbd_master,
                                            on_kbd=self.do_key,
                                            win_x=kbd_win_x,
                                            win_y=kbd_win_y,
                                            win_width=kbd_win_width,
                                            win_height=kbd_win_height,
                                              title="Let's Make a Drawing!")
            self.screen_keyboard.to_top()   # Just earlier to see problems
            self.do_keys(self.hello_drawing_str)
            self.screen_keyboard.to_top()
        if show_help:
            self.help()
        
    def clear_all(self):
        """ Clear screen
        """
        self.cmd_proc.clear_all()
        
        self.is_pendown_orig = True
        self.is_pendown = self.is_pendown_orig       # Drawing pen state
        self.heading_orig = 0
        self.heading = self.heading_orig             # Current heading
        self.side_orig = 100
        self.side = self.side_orig              # Default distance
        self.current_width_orig = 2
        self.current_width = self.current_width_orig  # Current line width
        self.photo_images = {}      # Keeping references
        """ Reset image group access to first file """
        for name in self.image_group_names:
            ifg = self.get_image_file_group(name)
            ifg.set_file_index(-1)
        self.x_cor = 0
        self.y_cor = 0

    def last_command(self):
        if hasattr(self, "cmd_proc"):
            return self.cmd_proc.last_command()
        
        return None
    
    def enable_image_update(self, enable=True):
        """ Enable/Disable kbd image update
        :enable: enable update default: True
        """
        self.screen_keyboard.enable_image_update(enable)

    def help(self):
        """ Help message
        """
        if hasattr(self, "cmd_proc"):
            self.cmd_proc.help()
        else:
            SlTrace.lg("help is on the way")
    
    def trace(self, tstring):
        """ trace info (debugging) when we can't use select_trace
        Place info on next line as a comment line
        :tstring: trace string
        """
        if self.do_trace:
            SlTrace.lg(f"\n#{tstring}", "tracing")

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
        
        self.image_type = KeyboardDraw.IT_FILE
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
            
    def ignore_key(self):
        """ ignore key
        """
        self.trace("ignore key")

        
    def add_canvas_tag(self, tag):
        """ Add tag to this move
        :tag: tag to add
        """
        move = self.get_move()
        if move is None:
            SlTrace.lg(f"add_canvas_tag: No move for tag")
            return
        
        move.canvas_tags.append(tag)
                        
    def xset_color(self, colr=None, changing=None):
        """ set color, with no move
        :colr: new color
             default: use current color(w,2, or color string
            based on:
            self.color_current:
                w : rotate through colors[], using self.color_index
                2 : rotate though self.custom_colors[], using self.color_index
                other : use self.color_current
            self.color_index: index within
                w : colors[]
                2 : self.custom_colors
        :colr: color
                w : set current color to w standard
                2 : set current color to 2 custom
                other : set self.color_current to colr
        :changing: True - color change
                    False - color remains constant
                    default: use self.color_changing
        """
        if changing is None:
            changing = self.color_changing
            
        if colr is None:
            if self.color_current is None:
                return
            else:
                colr = self.color_current 
        self.trace(f"xset_color:{colr}")
        if colr == "w":
            self.color_current = "w"
            self.color_changing = True
        elif colr == "2" or colr == "=":
            self.color_current = "2"
            self.color_changing = True
        else:
            self.color_current = colr
            self.color_changing = changing
        new_color = self.next_color()
        if not self.use_command:    
            self.tu.color(new_color)

    def next_color(self, colr=None, changing=None):
        """ Get next color based on color_current, color_changing
        :colr: color
                default: use self.color_current
        :changing: is color changing
                default: use self.color_changing
        """
        if colr is None:
            colr = self.color_current
        self.color_current = colr
        if changing is None:
            changing = self.color_changing
        self.color_changing = changing
        if self.color_current == 'w':
            if self.color_changing:
                self.color_index += 1
            if self.color_index >= len(self.colors):
                self.color_index = 0        # wrap around
            new_color = self.colors[self.color_index]
        elif self.color_current == '2':
            if changing:
                self.color_index += 1
            if self.color_index >= len(self.custom_colors):
                self.color_index = 0
            new_color = self.custom_colors[self.color_index]
        else:
            new_color = self.color_current
            if type(new_color) != str:
                SlTrace.report(f"new_color:{new_color} not str")
                return
        SlTrace.lg(f"new_color:{new_color}"
                   f" color_current:{self.color_current}"
                   f" color_index:{self.color_index}"
                   f" color_changing:{self.color_changing}", "color")
        return new_color
                
    def set_visible_color(self, colr):
        """ Set visible color based on colr
        :colr: color to be
                - set invisible (white)
                + set visible current color
        """
        if colr == "-":
            self.move_minus()
        elif colr == "+":
            self.move_plus()
        else:
            self.xset_color(colr)

    def marker_set(self, marker=None, changing=None, choose=None):
        """ Event marker setting
        :marker: marker to set
        :changing: auto changing markers
        :choose: True: prompt user for marker
        """
        if choose:
            """ Prompt user for marker
            """
            x0 = 300
            y0 = 400
            width = 200
            height = 400
            SlTrace.lg(f"x0={x0}, y0={y0}, width={width}, height={height}", "choose")
            select_image_files = self.get_image_files()
            select_image_hash = self.get_select_image_hash()
            app = SelectList(items=select_image_files, image_hash=select_image_hash,
                             default_to_files=True,
                             title="Marker Images",
                             position=(x0, y0),
                             size=(width, height))
            selected_field = app.get_selected(return_text=True)
            SlTrace.lg(f"image_image: selected_field:{selected_field}", "choose")
            if selected_field is None:
                return
            
            self.image_chosen = self.image_file_to_info(selected_field)
            if self.image_chosen is None:
                SlTrace.report(f"Sorry, can't load image {selected_field}")
                return

            self.marker_chosen = selected_field
            SlTrace.lg(f"self.image_chosen={self.image_chosen}")
            self.set_marker(marker="image", changing=False)
            self.do_marker()
        else:
            self.set_marker(marker=marker, changing=changing)
            


    def pick_next_image(self):
        """ Get next from current image group
        :returns: imageinfo (key, image)
        """
        display_file = self.get_image_file()
        return self.image_file_to_info(display_file)

    def image_file_to_image(self, file):
        """ Get base image from file
        """
        image = self.marker_image_hash.get_image(
                            key=file,
                            photoimage=False)
        return image
    
    def image_file_to_info(self, display_file):
        """ Convert file name(key) to image_info(key, image)
        :display_file: display file name/key
        :returns: image_info (key, image)
                    None if can't get it
        """
        image = self.image_file_to_image(display_file)
        if image is None:
            SlTrace.report(f"Can't load image:{display_file}")
            return None
        
        return (display_file, image)
    
    def line_setting(self):
        self.line_set(choose=True)
    
    def moveto_setting(self):
        self.moveto_set(choose=True)
    
    def set_pen_state(self, pendwn=None):
        """ Set pen to or back to drawing state
                self.is_pendown
        :pendown: target pen state
                default: current  drawing state
        """
        if self.use_command:
            self.set_pen_state(pendwn=pendwn)
            return 
        
        pen_target = self.is_pendown
        if pendwn is not None:
            pen_target = pendwn
            if pen_target:
                if not self.tu.isdown():
                    self.tu.pendown()
            else:
                if self.tu.isdown():
                    self.tu.penup()
        self.is_pendown = pen_target
                
    def jump_to(self, heading=None, distance=0,
                pendwn=False):
        """ Move pen from current (immediate) location
            :heading: move direction default: current heading
            :distance: distance in direction of heading
            :pendwn: True lower pen, False Raise pen
                    Leave pen in original state after
                    default: raise pen
        """
        if self.use_command:
            self.cmd_jump_to(heading=heading, distance=distance,
                             pendwn=pendwn)
            return 
        
        if pendwn:
            if not self.tu.isdown():
                self.tu.pendown()
        else:
            if self.tu.isdown():
                self.tu.penup()
        if heading is None:
            heading = self.heading
        self.xset_heading(heading, change=False)
        self.tu.forward(distance)
        self.xset_heading(self.heading)        # Restore heading       
        self.set_pen_state()            # Restore pen state
                
    def jump_to_next(self):
        """ Move to next position, invisibly
        """
        if self.use_command:
            self.cmd_jump_to_next()
            return
        
        if self.tu.isdown():
            self.tu.penup()
        self.xset_heading(self.heading)
        theta = math.radians(self.heading)
        x_chg = self.side*math.cos(theta)
        y_chg = self.side*math.sin(theta)
        new_x = self.x_cor + x_chg
        new_y = self.y_cor + y_chg
        self.move_to(new_x, new_y) 
        self.set_pen_state()
                
    def jump_to_next_line(self):
        """ Move to beginning of next line, invisibly
        """
        if not self.use_command:
            if self.tu.isdown():
                self.tu.penup()
        self.xset_heading(self.heading)
        down_heading = self.heading - 90    # Down to next line
        theta = math.radians(down_heading)
        x_chg = self.side*math.cos(theta)
        y_chg = self.side*math.sin(theta)
        new_x = self.text_line_begin_x + x_chg
        new_y = self.text_line_begin_y + y_chg
        self.move_to(new_x, new_y, pen_down=False)      # Beginning of next line 
        self.set_new_line()
        self.set_pen_state()

    def pick_next_shape(self):
        """ Get next from shape list
        :returns: return next shape
        """
        if self.nth_shape > 0:
            self.shape_index += 1
        self.nth_shape  += 1
        nshape = len(self.shape_order)
        if self.shape_index >= nshape:
            self.shape_index = 0
        display_shape = self.shape_order[self.shape_index]
        return display_shape

    def set_shape(self, shape=None, choose=None, changing=None):
        """ Set shape - not much - initially to be in line with
            set_marker
        """
        self.shape_next(shape=shape, choose=choose)

    """ Select special marker images
    """
    
    def marker_animals(self):
        """ Setup to rotate through animal images
        """
        self.set_image_type(KeyboardDraw.IT_FILE)
        self.set_image_group("animals")
        self.image_next('rotateinplace')
    
    def marker_text(self):
        """ Setup to add text character images
        """
        self.set_image_type(KeyboardDraw.IT_FILE)
        self.image_next('rotateinplace')
        
        
                        
    def do_shift(self, shift_on=True):
        """ Shift letters
        :shift_on: Put shift on, adjust letters
                    default: True
        """
        self.screen_keyboard.do_shift(shift_on=shift_on)

    def letter_next(self):
        """ Set letter "shape"
        """
        if self.marker_current == "letter":
            return
        
        self.marker_before_letter = self.marker_current
        self.set_marker("letter")
        self.set_new_line()
        if self.marker_before_letter != "letter":
            self.jump_to(distance=self.side/2)
        self.do_shift()     # Default to uppercase
        self.do_pendown()   # Default to visible
        self.set_key_images(show=False)
        exit_infos = self.get_btn_infos(key="END")
        self.set_btn_image(exit_infos, image="drawing_abc_end.png")
        self.track_keys_text()
        self.master.focus()             # So keyboard is active


        
    def on_text_end(self):
        ###self.text_entry_funcid = self.master.unbind('<KeyPress>', self.text_entry_funcid)
        self.track_keys()   # Reset keys to drawing cmds        
        self.do_shift(False)
        exit_infos = self.get_btn_infos(key="BKSP")
        self.set_btn_image(exit_infos, image=None)
        self.set_key_images(show=True)
        self.set_marker(self.marker_before_letter)

    def get_move(self):
        """ Get most recent move (MoveInfo)
        :returns: move, None if none
        """
        if len(self.move_stack) > 0:
            return self.move_stack[-1]
        
        return None 
    
    def check(self, key):
        print(f"\n#{key}")  # Force even if self.trace is False
        print("check")
    
    def checking(self):
        """ Debugging catch
        """
        self.check("check")
    
    def dotrace(self, key=None):
        """ Flip tracing setting
        """
        
        self.do_trace = not self.do_trace
        
    def tracing(self):
        """ Debugging catch
        """
        self.dotrace("trace")
     
    def get_image_files(self):
        """ get current image group's files
        """
        ifg = self.get_image_file_group()
        return ifg.image_files
     
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

    def get_image_hash(self):
        """ get current image group's files
        """
        ifg = self.get_image_file_group()
        return ifg.image_hash

    def get_select_image_hash(self):
        """ get current image group's SelectList hash
        Note that these may be images whose sizes are
        for the SelectList and not for marker images
        """
        ifg = self.get_image_file_group()
        return ifg.select_image_hash


    def get_image_file_group(self, name=None):
        """ Get current marker image file group (DataFileGroup)
        :name: group name
                default: return current self.image_group
        """
        if name is None:
            ifg = self.image_group
        else:
            ifg = self.ifh.get_group(name)
        return ifg
                
    def get_canvas(self):
        """ Get our working canvas
        """
        return self.canv
    
    def select_print(self, tag, trace=None):
        """ Print select select state
        """
        """TBD"""

    def expand_key(self, key):
        """ Expand key to functional form: name(arg,arg,...)
        """
        if re.match(r'^\w+\(.*\)', key):
            return key      # Already in function form
        
        for short_name in self.key_fun_name:
            if key.startswith(short_name):
                fun_name = self.key_fun_name[short_name]
                arg_str = key[len(short_name):]
                name = f"{fun_name}({arg_str})"
                return name
            
        return key      # Unchanged
        
    nk = 0          # length key spaces so far
    def print_key(self, key):
        """ Print key
        :key: key string
        """
        if self.nk > 0:
            if self.nk > 40:
                print()
                self.nk = 0
            else:
                print(";", end="")
        exp_key = self.expand_key(key)
        self.nk += len(exp_key)
        print(exp_key, end="")
        
    def do_key(self, key, **kwargs):
        """ Process key by
        calling keyfun, echoing key
        :key: key (descriptive string) pressed
                or special "key" e.g. funname(args)
        :kwargs: function specific parameters
                often to "redo" adjusted undone operations
        """
        return self.cmd_proc.do_key(key, **kwargs)
    
    def do_keys(self, keystr):
        """ Do action based on keystr
            semicolon or newline used as separators
            Empty areas between separators are ignored
            lines starting with # are printed but removed
            text starting with "\s+.*" are removed
        :keystr: string of key(values) must match track_key
                interpretations e.g. Up for up-arrow,
                minus for "-"
        """
        rawkeylines = keystr.split('\n')
        code_keylines = []
        for rawkeyline in rawkeylines:
            if re.match(r'^\s*#', rawkeyline):
                code_keylines.append(rawkeyline)    # Pass comment line
                continue
            eol_com_match = re.match(r'^(.*\S)(\s+#.+)$', rawkeyline)
            if eol_com_match:
                code_keylines.append(eol_com_match.group(1))
                code_keylines.append(eol_com_match.group(2)) # remove trailing comment
                continue 
            code_keylines.append(rawkeyline)
        for code_keyline in code_keylines:
            if re.match(r'\s*#', code_keyline):
                print(f"\n{code_keyline}")
                continue
            keys = re.split(r'\s*;\s*|\s+', code_keyline)
            for key in keys:
                if key != "":
                    self.do_key(key)

    def set_key_mapping(self):
        """ Setup key to function mapping
        TBD
        """
        # key, function [, *parameters], 
        key_mapping = [
            ['h', self.help],
            ]

    def on_text_entry(self, event):
        """ Text entry from keyboard
        :event" key press event
        """
        inchar = event.char
        keysym = event.keysym
        keycode = event.keycode
        SlTrace.lg(f"on_text_entry: keysym: {keysym} keycode: {keycode}")

        if keysym == 'End':
            key = "END"
            self.text_enter_key(key)
        if keysym == "Return":
            self.text_enter_key("ENTER")
        elif keysym == 'BackSpace':
            self.draw_undo()
        elif keysym == 'Shift_L' or keysym == 'Shift_R':
            pass            # Just adjust physical keyboard
        elif keysym == 'Caps_Lock':
            pass            # Just adjust physical keyboard
        elif keysym == 'Up' or keysym == 'Down' or keysym == 'Left' or keysym == 'Right':
            self.move(direct=keysym, just_move=True)
        else:
            key = event.char
            self.text_enter_key(key)

    def on_text_entry_screen(self, key):
        """ Text entry from screen keyboard
        :key" key click
        """
        SlTrace.lg(f"on_text_entry_screen: key: {key}")

        if key == "END":
            self.on_text_end()
            return
        
        if key == "BKSP":
            self.draw_undo()
            return 
        
        self.text_enter_key(key=key)
        
    def track_keys_text(self):
        """ Setup keys for text input """
        """ bind screen keyboard keys """
        

    def set_key_images(self, show=False):
        self.screen_keyboard.set_images(show=show)

    def get_btn_infos(self, key=None, row=None, col=None):
        """ Get buttons
        :key: if not None, must match
        :row: if not None, must match
        :col: if not None, must match
        """
        return self.screen_keyboard.get_btn_infos(key=key, row=row, col=col)

    def set_btn_image(self, btn_infos=None, image=None):
        """ Set button (btn_infos) image displayed
        :btn_infos: ButtonInfo, or list of ButtonInfos
        :image" text - image file
                Image - image
        """
        self.screen_keyboard.set_btn_image(btn_infos=btn_infos, image=image)

        

    def draw_undo(self):
        """ Undo most recent operation
        As the only handle we have on turtle objects
        is undobufferentries(), we save a stack of this
        count at the beginning of each opperation.
        Undo consists of calling undo while undobufferentries()
        returns a number greater than the stack entry
        count
        """
        self.trace_move_stack("draw_undo", flag="draw_undo")

        """ Undo move (limits undo)
            Might consider combining with canvas undo
        """
        """ Undo canvas (e.g. image) actions if any
            Have to do check before move because we keep
            the stacks diferently because move_stack[0] remains
        """
        move = self.get_move()
        if move is None:
            SlTrace.lg("draw_undo: Empty Stack - can't undo")
            return 
        
        if len(move.canvas_tags) > 0:
            canvas_tags = move.canvas_tags
            for canvas_tag in canvas_tags:
                self.canv.delete(canvas_tag)
        
        if len(self.move_stack) > 0:        # current is on top of stack
            self.move_undo = self.move_stack.pop()
        else:    
            self.trace_move_stack("draw_undo AFTER - no more undos", flag="draw_undo")
            return
       
        
        """ Undo turtle actions, if any.  """
        if len(self.draw_undo_counts) > 0:        
            while (tu_undo_count:=self.tu.undobufferentries()) > move.undo_count_base:
                SlTrace.lg(f"tu_undo_count: {tu_undo_count}")
                self.tu.undo()
            SlTrace.lg(f"undo_count: {tu_undo_count}")

        self.master.update_idletasks()
        self.trace_move_stack("draw_undo AFTER")
            
    def mouse_down (self, event):
        x_coord = event.x
        y_coord = event.y
        SlTrace.lg(f"canvas_x,y: {x_coord, y_coord}", "mouse_down")

    def canv_coords(self, tu_coords=None):
        """ Canvas x coordinate
        :tu_coords: turtle coordinate pair
                default: use current
        :returns: canvas x_coordinates pair
        """
        if tu_coords is None:
            tu_coords = (self.x_cor, self.y_cor)
        x_cor, y_cor = tu_coords    
        canvas_width = self.canv.winfo_width()
        canvas_height = self.canv.winfo_height()
        x_coor = int(canvas_width/2 + x_cor)
        y_coor = int(canvas_height/2 - y_cor)        # canvas increases downward
        return (x_coor, y_coor)

    def cmd_clear_all(self):
        """ Clear screen
        """
        self.cmd_proc.clear_all()
        

    def display_print(self, tag, trace):
        """ display current display status
        :tag: text prefix
        :trace: trace flags
        """
                        
    
    
    """ End of legacy support
    """
            
def main():
    """ Main Program """
    data_dir = "../data"
    trace = ""
    use_command = True     # True use CommandManager, DrawCommand
    hello_str = None
    hello_file = "keyboard_draw_hello.txt"
    hello_file = "hello_family.txt"
    parser = argparse.ArgumentParser()
    parser.add_argument('--trace', dest='trace', default=trace)
    parser.add_argument('--data_dir', dest='data_dir', default=data_dir)
    parser.add_argument('--hs','--hello_str', dest='hello_str', default=hello_str)
    parser.add_argument('--hf','--hello_file', dest='hello_file', default=hello_file)
    parser.add_argument('-c','--command', dest='use_command', action='store_true', default=use_command)
    
    args = parser.parse_args()             # or die "Illegal options"
    SlTrace.lg("args: %s\n" % args)
    hello_file = args.hello_file
    hello_str = args.hello_str
    data_dir = args.data_dir
    trace = args.trace
    use_command = args.use_command
    
    
    app = tk.Tk()   # initialize the tkinter app
    app.title("Keyboard Drawing")     # title
    app.config(bg='powder blue')    # background
    """ Using ScreenKbd
    app.resizable(0, 0)     # disable resizeable property
    """
    if hello_str is not None:
        pass
    else:
        try:
            with open(hello_file, 'r') as fin:
               hello_str = fin.read()
        except IOError as e:
            SlTrace.report(f"Problem with hello_file:{hello_file}"
                           f"\n in {os.path.abspath(hello_file)}"
                           f"\n error: {e}")
            sys.exit() 
    kb_draw = KeyboardDraw(app,  title="Keyboard Drawing",
                hello_drawing_str=hello_str,
                draw_x=100, draw_y=50,
                draw_width=1500, draw_height=1000,
                kbd_win_x=50, kbd_win_y=25,
                kbd_win_width=600, kbd_win_height=300)

    kb_draw.enable_image_update()      # Enable key image update
    
    tk.mainloop()

if __name__ == "__main__":
    main()