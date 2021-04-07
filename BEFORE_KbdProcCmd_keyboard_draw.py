#keyboard_draw.py    12Dec2020  crs
"""
Drawing on turtle window, using keyboard
"""
import os
import sys
import re
import math
import tkinter as tk
from tkinter import colorchooser
from PIL import ImageTk, Image
from PIL import ImageDraw, ImageFont
import turtle
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

""" Marker/Shape info
    for undo / rotate operations
"""
class MoveInfo:
    MT_GENERAL = "mt_general"
    MT_MARKER = "mt_marker"
    MT_POSITION = "mt_position"
    MT_ADJUSTMENT = "mt_adjustment"
    
    def __init__(self, drawer, move_type=None, marker=None,
                 shape=None, image_info=None,
                 scale=None, line_width=None,
                 key=None):
        """  Marker/Shape info for undo / rotate operations
        :move_type: General move type
                MT_ADJUSTMENT - current move is to be adjusted
                MT_MARKER - new marker
                MT_POSITION - position move
                MT_GENERAL - general move (unknown)
                default: MT_GENERAL 
        :marker: marker type
                default: drawer.marker_current
        :shape: shape type
                default: drawer.shape_current
        :image_info: image information (key, image)
                default: drawer.image_chosen
        :scale: scale multiplier
                default: 1.0
        :line_width: line width
                default: drawer.side
        :key: move's text key, if one
        """
        self.drawer = drawer
        self.undo_count_base = drawer.tu.undobufferentries()
        self.canvas_tags = []       # Filled with this move's tags
        if move_type is None:
            move_type = MoveInfo.MT_GENERAL
        self.move_type = move_type
        if marker is None:
            marker = drawer.marker_current
        self.marker = marker
        if shape is None:
            shape = drawer.shape_current
        self.shape = shape
        if image_info is None:
            image_info = drawer.image_chosen
        self.image_info = image_info
        if scale is None:
            scale = 1.0
        self.scale = scale
        if line_width is None:
            line_width = drawer.current_width
        self.line_width = line_width
        self.key = key
        
        def add_canvas_tag(self, tag):
            """ Add tag to this move
            :tag: tag to add
            """
            self.canvas_tags.append(tag)
            
            
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
                 use_command=True,      # Wave of the future
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
        :use_command:  True - do commands via command_manager
                                        draw_command,...
                        False - do commands via legacy code
                    default: True
        """
        self.use_command = use_command
        control_prefix = "KbdDraw"
        self.x_cor = None 
        self.y_cor = None 
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
                               width=draw_width, height=draw_height)
            canvas.pack()
        self.draw_width = draw_width
        self.draw_height = draw_height
        self.tu_canvas = canvas
        self.canvas_width = draw_width    # Fudge
        self.canvas_height = draw_height   # Fudge


        self.tu_canvas.bind ("<ButtonPress>", self.mouse_down)
        self.tu_screen = turtle.TurtleScreen(self.tu_canvas)
        if self.use_command:
            """ Only for command based stuff
            """
            self.cmd_proc = KbdCmdProc(self)
        else:
            """ Only for legacy - turtle based stuff
            """
            from command_manager import CommandManager
            
            self.command_manager = CommandManager(self)
            self.tu = turtle.RawTurtle(self.tu_canvas)
            self.tu.setundobuffer(undomax)
            self.draw_undo_counts = [self.tu.undobufferentries()] # undo counts
            self.master.bind("<KeyPress>", self.on_key_press)
        
        """ Setup our own, outside turtle, key processing """
        self.bound_keys = {}     # functions, bound to keys

        self.master = master
        self.side = side
        self.current_width = width
        self.do_trace = False    # Set True to do debugging trace
        self.do_trace = True
        self.set_key_mapping()
        x_start = int(-self.canvas_width/2 + side)
        y_start = int(self.canvas_height/2 - side)
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
            e;F;a;m;i;l;y;END
            newline();a;l;e;x;END;image_file(family,alex);q
            newline();d;e;c;l;a;n;END;image_file(family,declan);q
            newline();a;v;e;r;y;END;image_file(family,avery);q
            newline();c;h;a;r;l;i;e;END;image_file(family,charlie);q
            newline();;END
            minus
            
        ###    # Add in animals
        ###    k
        ###    plus
        ###    k;Right;a;a
        ###    k;Right;a:a
        ###    k;Right;a;a
        ###    k;Right;a;a
        ###    k;Right;a;a
            
            # A bit of other stuff
            minus;moveto({ostuff_x},{ostuff_y});plus
            image_file(princesses,princess);q
            minus; moveto({ostuff_x+2*side},{ostuff_y-1*side});plus
            image_file(other_stuff,batman);q 
            minus; moveto({ostuff_x+4*side},{ostuff_y-2*side});plus
            image_file(other_stuff,baseball);q 

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
        self.marker_order = [
            "line",
            "shape",
            "image",
             ]
    
        self.shapes = {
            "line" : self.shape_line,
            "square" : self.shape_square,
            "circle" : self.shape_circle,
            "triangle" : self.shape_triangle,
            }
        self.shape_order = [
            "square",
            "triangle",
            "circle",
            ]
        # a rotating color pattern
        self.colors = ["red", "orange", "green",
                  "blue", "indigo", "violet"]
        
        # Rotating pattern of custom colors
        self.custom_colors = []
        self.key_fun_name = {
            '=' : "color",
            ':' : "line",
            'moveto:' : 'moveto',
            }
    
        self.fun_by_name = {
            'color' : self.color_set,
            'image' : self.image_next,
            'image_file' : self.image_file,
            'line' : self.line_set,
            'marker' : self.set_marker,
            'moveto' : self.moveto_set,
            'newline' : self.newline,
            'shape' : self.shape_next,
            }

        self.setup_image_access()
        self.moves_canvas_tags = []  # Init for canvas part of draw_undo
        self.clear_all()            # Setup initial settings
        
        
        
        self.enlarge_fraction = .2   # Enlargement fraction
        self.track_keys()
        if with_screen_kbd:
            if kbd_master is None:
                kbd_master = tk.Toplevel()
            self.kbd_master = kbd_master
            """ Using ScreenKbd
            self.screen_keyboard = ScreenKbd(kbd_master, on_kbd=self.do_key,
                                              title="Let's Make a Drawing!")
            """
            self.screen_keyboard = ScreenKbdFlex(kbd_master, on_kbd=self.do_key,
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

        self.set_image_group(group_name=group_name)
                
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
    
    def add_custom_color(self, colr):
        """ Add new custom color
        :colr: new custom color
        """
        self.color_current = "2"
        self.custom_colors.append(colr)
        self.color_index = len(self.custom_colors)-1
        self.xset_color()

    def set_command_manager(self, mgr):
        """ Set drawing command manager
        :mgr: command manager for do, undo...
        """
        self.cmd_mgr = mgr
                        
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
            
                        
    def set_marker(self, marker=None, changing=None):
        """ set set curent marker
        marker type , e.g. letter, line, shape, image
        is done via do_marker()
        Sets current move_type to MoveInfo.MT_MARKER
        
        :marker: new marker
             default: use current marker
            based on:
            self.marker_current and self.marker_changing
        """
        if changing is None:
            changing = self.marker_changing
        if marker is None:
            marker = self.next_marker(marker=marker, changing = changing)
        self.marker_current = marker
        move = self.get_move()
        if move:
            move.move_type = MoveInfo.MT_MARKER
        self.trace(f"set_marker:{marker}")
        

    def next_marker(self, marker=None, changing=None):
        """ Get next marker
        :marker: desired marker, if one
                default:
                
        :changing: are the markers changing
                default: use self.marker_changing
                
        """
        if changing is None:
            changing = self.marker_changing
        self.marker_changing = changing
        if marker is None:
            marker = self.marker_current
        self.marker_current = marker
        if changing:
            if marker in self.marker_order:
                self.marker_index = self.marker_order.find(marker)
                self.marker_index += 1
                if self.marker_index >= len(self.marker_order):
                    self.marker_index = 0
                self.marker_current = self.marker_order[self.marker_index]
        return self.marker_current
    
    def draw_postaction(self):
        """ drawing action that
        changes location
        """
        self.trace_move_stack("draw_postaction")

        self.new_pendown = False
        if not self.use_command:
            self.cur_x, self.cur_y = self.tu.position()
            self.start_animation()
        self.trace_move_stack("draw_postaction AFTER")
            
    def draw_preaction(self, move_type=MoveInfo.MT_GENERAL,
                       key=None, **kwargs):
        """ Setup before drawing action
            facilitates storage of move attributes
                move_stack
                turtle actions
                canvas objects (tags)
            to be completed by move specific functions
            Storage completed/recorded by draw_postaction
            Backing out move is via draw_undo
            Moves that are an adjustment of the previous move
            have move_type MT_ADJUSTMENT
            
        :move_type: comming move's type
                    MT_GENERAL - general purpose
                    MT_POSITION - positioning move no new markers
                    MT_MARKER - creating marker
                    MT_ADJUSTMENT - current move is to be adjusted
                                    No new move is added to the stack
                                    
        :key: comming move's key, if one
        :kwargs: supplimental keyword args for moves
                augmentation, especially in adjustments
                for undone redo situations
        """
        self.trace_move_stack("draw_preaction", move_type=move_type)
        if not self.use_command:
            self.stop_animation()
            tu_undo_count = self.tu.undobufferentries()
            self.move_stack.append(MoveInfo(self, move_type=move_type, key=key))
        
        move = self.get_move()
        if not self.use_command:    
            self.x_cor = self.tu.xcor()
            self.y_cor = self.tu.ycor()
        SlTrace.lg(f"draw_preacion: x_cor={self.x_cor} y_cor={self.y_cor}", "draw_action")
        self.xset_color()
        self.set_marker()
        if 'width' in kwargs:
            self.xset_width(kwargs['width'])
        if 'heading' in kwargs:
            self.xset_heading(kwargs['heading'])                
        self.trace_move_stack("draw_preaction AFTER", move_type=move_type)

    def trace_move_stack(self, prefix, move_type=None,
                         key=None,
                         flag=None):
        """ Trace move stack including turtle, canvas, and move_stack
        :prefix: text identifier
        :move_type: if applicable
        :key: key associated with move, if any
        :flag: SelectTrace flag setting default: display
        """
        if flag and not SlTrace.trace(flag):
            return
        
        move = self.get_move()
        if move is None:
            SlTrace.lg(f"{prefix} {key} {move_type}"
                       f"   move_stack EMPTY")
            return 
        
        if key is None:
            
            key = ""
            if move:
                key = move.key
        move_id_str = ""
        if move_type is not None:
            move_id_str = f"({move_type})"
        if SlTrace.trace(flag):
            if not self.use_command:
                tu_undo_count = self.tu.undobufferentries()
            
            SlTrace.lg(f"{prefix} {key} {move_id_str}"
                       f"   tags: {move.canvas_tags}"
                       f"   undo_entries: {move.undo_count_base}"
                       f"   move_stack len: {len(self.move_stack)}")
        
    def set_move(self, move_type=None, key=None):
        """ Set/Adjust current move attributes
        :move_type: move type
        :key: associated key
        """
        move = self.get_move()
        if move is None:
            return
        
        if move_type is not None:
            move.move_type = move_type
        if key is not None:
            move.key = key
        
    def stop_animation(self):
        """ Stop animation (speed up)
        """
        self.tu_screen_delay = self.tu_screen.delay()
        self.tu_screen.delay(0)                # stop animation delay

    def start_animation(self):
        """ Start animation (slow to previous)
        """
        self.tu_screen.update()
        self.tu_screen.delay(self.tu_screen_delay)        # Restore animation delay
        
    def do_marker(self, marker=None):
        """ display, if pendown, current marker
        :marker: symbol/shape/image to use
                default:self.marker_current
        """
        if marker is None:
            marker = self.marker_current
        if self.marker_current == "line":
            self.do_line()
        elif self.marker_current == "shape":
            self.do_shape()
        elif self.marker_current == "image":
            self.do_image()
        else:
            SlTrace.lg(f"do_marker: unrecognized marker:{marker} - ignored")

    def do_line(self, **kwargs):
        """ do line marker
        """
        self.shape_line(**kwargs)
        
    def do_shape(self):
        """ Do shape marker
        """
        self.shape_next()
        
    def do_image(self, image_info=None, move_to_next=True, key=None):
        """ Do image marker
        """
        if self.use_command:
            self.cmd_do_command(image_info=image_info, key=key)
            return
        
        self.set_move(move_type=MoveInfo.MT_MARKER, key=key)
        if self.tu.isdown():
            self.do_image_display(image_info=image_info)
        if move_to_next:
            self.jump_to_next()
    
    def do_image_display(self, image_info=None):
        """ Do image marker display
        """
        self.image_heading_default = 0
        if image_info is None:
            image_info = self.get_marker_image()
        if image_info is None:
            return
        
        image_key, image = image_info
        rotation = (self.heading + self.image_heading_default)%360
        if self.marker_current != "letter":
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
        image = image.resize((int(self.marker_image_width), int(self.marker_image_height)),
                             Image.ANTIALIAS)
        if self.marker_current != "letter":
            image = image.rotate(rotation)
        self.photo_image = ImageTk.PhotoImage(image)
        if image_key not in self.photo_images:
            self.photo_images[image_key] = []
        self.photo_images[image_key].append(self.photo_image)
        canvas_x, canvas_y = self.tu_canvas_coords((self.tu.position()))
        #canvas_x, canvas_y = self.x_cor, self.y_cor
        #canvas_x, canvas_y = 0,0
        #test_tag = self.tu_canvas.create_line(0,0,300,300)
        #test_tag2 = self.tu_canvas.create_line(0,0,100,200)
        #test_tag3 = self.tu_canvas.create_line(0,0,-100,-200)
        canvas_width = self.tu_canvas.winfo_width()
        canvas_height = self.tu_canvas.winfo_height()
        adj_x = -canvas_width/2
        adj_y = -canvas_height/2
        canvas_x += adj_x
        canvas_y += adj_y
        self.marker_image_tag = self.tu_canvas.create_image(
            canvas_x, canvas_y,
            ###anchor="nw",
            image=self.photo_image)
        """ Save for undo, but also for image reference """
        ###if len(self.moves_canvas_tags) == 0:
        ###    self.moves_canvas_tags.append([])   # empty - add list
        self.add_canvas_tag(self.marker_image_tag)

        self.tu_canvas.update()

    def image_file(self, group, name):
        """ create marker at curren location, heading
        from group of name
        :group: group name (e.g. animals, family)
        :name: first file in group which contains the name string
        """
        if group not in self.image_group_names:
            SlTrace.report(f"No image file group {group}"
                           f" groups: {self.image_group_names}")
            return 
        
        ifg = self.get_image_file_group(group)
        image_files = ifg.get_image_files()
        found = None
        for im_name in image_files:
            if im_name.find(name) >= 0:
                found = im_name
                break
        if found is None:
            SlTrace.report(f"{name} not found in image group {group}")
            return 
        
        self.image_chosen = self.image_file_to_info(found)
        if self.image_chosen is None:
            SlTrace.report(f"Sorry, can't load image {found} from group {group}")
            return

        self.marker_chosen = found
        SlTrace.lg(f"self.image_chosen={self.image_chosen}", "image_display")
        self.set_marker(marker="image", changing=False)
        self.do_marker()
            
    def image_next(self, image=None, choose=None):
        """ Go to next image and change per image parameter
            Sets self.image_chosen
        :image:
            'nextone' - select next image as the one
            'rotate' change image and make new image
            'rotateinplace' - change image of current marker
            'same" keep current image
            default: 'rotateinplace' 
        """
        if image is None:
            image = 'rotateinplace'
        elif image == 'same':
            self.set_marker(marker="image", changing=False)
        elif image is not None and image != "" and image in self.marker_image_files:
                self.image_chosen = self.pick_next_image()
        elif choose:
            SlTrace.lg("Don't know how to choose images yet")
            return
        elif image is None or image == "":
            if self.image_current == "rotate":
                self.image_chosen = self.pick_next_image()
            elif self.image_current in self.images:
                self.image_chosen = self.image_current     
        elif image == "nextone":
            self.set_marker(marker="image")
            self.image_chosen = self.pick_next_image()
            self.image_current = self.image_chosen
            self.erase_if_marker()
        elif image == "rotate":
            self.set_marker(marker="image")
            self.image_current = "rotate"
            self.image_chosen = self.pick_next_image()
        elif image == "rotateinplace":
            self.set_marker(marker="image")
            self.image_current = "rotate"
            self.erase_if_marker()
            self.image_chosen = self.pick_next_image()
            move_type = MoveInfo.MT_ADJUSTMENT
            move = self.get_move()
            if move is None or move.move_type == MoveInfo.MT_ADJUSTMENT:
                move_type = MoveInfo.MT_MARKER
            self.draw_preaction(move_type=move_type)
            self.set_pen_state()
            self.do_image()
            self.set_pen_state()
            self.draw_postaction()
            return
        else:
            self.image_chosen = self.pick_next_image()
        self.draw_preaction()
        self.set_pen_state()
        self.do_image()
        self.set_pen_state()
        self.draw_postaction()


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
        
    def get_marker_image(self, image_name=None):
        """ get image based on image type/name
            For now just give latest chosen image
            :returns: image_info (key, image)
        """
        image_info = self.image_chosen
        return image_info
    
    def do_pendown(self):
        """ Do pendown and remember
        """
        self.new_pendown = True
        self.is_pendown = True
        self.tu.pendown()
    
    def do_backward(self, side=None, move_type=MoveInfo.MT_POSITION):
        """ Do backward operation
        :side: distance
        """
        if self.use_command:
            self.cmd_do_backward(side=side, move_type=move_type)
            return
        
        if side is None:
            side = self.side
        self.set_move(move_type=move_type)
        self.tu.backward(side)
        
    def do_forward(self, side=None, move_type=MoveInfo.MT_POSITION):
        if self.use_command:
            self.cmd_do_forward(side=side, move_type=move_type)
            return
        
        if side is None:
            side = self.side
        self.set_move(move_type=move_type)
        self.xset_width(self.current_width)
        self.tu.forward(side)
        
    def clear_all(self):
        """ Clear screen
        """
        if self.use_command:
            self.cmd_proc.clear_all()
            return 
        
        self.move_undo = None   # Most recently undone
        self.move_stack = []    # Stack moves in draw_preaction()
        self.set_image_type(KeyboardDraw.IT_FILE)
        self.tu.speed("fastest")
        self.stop_animation()       # Record speed
        self.start_animation()      # Restart animation
        self.nk = 0

        self.new_pendown = True      # Set to indicate pen just down
        self.is_pendown_orig = True
        self.is_pendown = self.is_pendown_orig       # Drawing pen state
        self.heading_orig = 0
        self.heading = self.heading_orig             # Current heading
        self.side_orig = 100
        self.side = self.side_orig              # Default distance
        self.current_width_orig = 2
        self.current_width = self.current_width_orig  # Current line width
        self.color_changing = True
        self.color_current_orig = "w"     # Default to changing std colors
        self.color_index_orig = 0         # index of current color
        self.color_index = self.color_index_orig
        self.color_current = self.color_current_orig
        self.nth_shape = 0          # Number of previous shapes
        self.shape_index_orig = 0
        self.shape_index = self.shape_index_orig
        self.shape_current_orig = "line"
        self.shape_current = self.shape_current_orig
        
        self.marker_changing = False     # Unchanging
        self.marker_index_orig = 0
        self.marker_index = self.marker_index_orig
        self.marker_current = self.marker_order[self.marker_index]
        self.marker_before_letter = self.marker_current

        """ Undo canvas (e.g. image) actions if any """
        while len(self.moves_canvas_tags) > 0:
            canvas_tags = self.moves_canvas_tags.pop()
            for canvas_tag in canvas_tags:
                self.tu_canvas.delete(canvas_tag)
        self.image_index = len(self.marker_image_files)    # will wrap to 0
        self.image_current = "rotate"
        self.marker_image_tags = []
        self.photo_images = {}      # Keeping references
        """ Reset image group access to first file """
        for name in self.image_group_names:
            ifg = self.get_image_file_group(name)
            ifg.set_file_index(-1)

        self.draw_preaction()
        self.tu.clear()
        self.tu.penup()
        self.tu.home()
        self.x_cor = self.tu.xcor()
        self.y_cor = self.tu.ycor()
        self.do_pendown()
        self.draw_postaction()
        
    def col(self, colr):
        """ Change color/line attributes as a move
        :colr: color string, e.g. "red", "orange"
                =[color spec]
        """
        if colr is None:
            colr = self.color_current
        if colr == "w":
            self.color_current = "w"
            self.color_changing = True
        elif colr == "2":
            self.color_current = "2"
            self.color_changing = True 
        elif colr == "-":
            self.set_pen_state(False)
        elif colr == "+":
            self.set_pen_state(True)
        elif colr.startswith("="):
            color_spec = colr[1:]       # Remainder, if any is spec
            if color_spec == "":
                color_choice = colorchooser.askcolor()
                self.trace(f"color_choice: {color_choice}")            
                if color_choice[1] is None:
                    return
                self.add_custom_color(color_choice[1])
                return
            
            else:
                colr = color_spec
            self.color_current = colr            
            self.color_changing = False       # Force using current color
        else:        
            self.color_current = colr
            if colr in self.colors:
                self.color_index = self.colors.index(colr)
            else:
                self.color_changing = False  # Not in list set as fixed
        ###self.set_visible_color(colr)
        
    def col_r(self):
        self.col("red")
    
    def col_o(self):
        self.col("orange")
    
    def col_y(self):
        self.col("yellow")
    
    def col_g(self):
        self.col("green")
    
    def col_b(self):
        self.col("blue")
    
    def col_i(self):
        self.col("indigo")
    
    def col_v(self):
        self.col("violet")
    
    def col_w(self):
        self.col("w")    # Changing color
    def col_minus(self):
        """ - => invisible(white)
        """
        self.col("-")
        
    def col_plus(self):
        """ + => visible (previous color)
        """
        self.col("+")
        
    def col_equals(self):
        """ = => color chooser for current color
        """
        self.color_set(choose=True)
    
    def color_set(self, colr=None, choose=None):
        """ Set color specification
        :colr: color string
        :choose: prompt user for color default: no choice
        """
        if choose:
            self.col("=")
        else:
            self.col(colr)
            
    def line_set(self, leng=None, wid=None, choose=None):
        """Set line specification (size)
        :leng: line length default: current length
        :wid: line width default: current width
        :choose: Prompt user to choose default: use current
        """
        if choose:
            while True:
                try:
                    inp = input(f"Enter line length[{self.side}]")
                    if inp is None or inp == "":                    
                        inp = str(self.side)
                    self.side = int(inp)
                    break
                except:
                    print(f"{inp} not a legal number - please try again")
                
            while True:
                try:
                    inp = input(f"Enter line width[{self.current_width}]")
                    if inp is None or inp == "":                    
                        inp = str(self.current_width)
                    self.current_width = int(inp)
    
                    break
                except:
                    print(f"{inp} not a legal number - please try again")
            self.trace(f"line length:{self.side} width: {self.current_width}")
            self.tu.listen()        # textinput does its own keybd capture
        else:
            if leng is None or (type(leng) == str and leng == ""):
                leng_new = self.side
            else:
                leng_new = int(float(leng))
            self.side = leng_new
            if wid is None or (type(wid) == str and wid == ""):
                wid_new = self.current_width
            else:
                self.current_width = int(wid)
        self.xset_width(self.current_width)
        self.trace(f"End of line_set width:{self.current_width}, leng:{self.side}")
            
    def moveto_set(self, x=None, y=None, choose=None):
        """ move pen to location
        :x: move to x coordinate default: leave x unchanged
            int or str -> converted to int
        :y: move to y coordinate default: leave  y unchanged
            int or str -> converted to int
        :choose: prompt user for location default: don't ask
        """
        x_cor = self.x_cor
        y_cor = self.y_cor
        if choose:
            while True:
                try:
                    inp = input(f"Enter x position[{x_cor:.0f}]")
                    if inp is None or inp == "":                    
                        inp = str(int(x_cor))
                    x_new = int(inp)
                    break
                except:
                    print(f"{inp} not a legal number - please try again")
                
            while True:
                try:
                    inp = input(f"Enter y position[{y_cor:.0f}]")
                    if inp is None or inp == "":                    
                         inp = str(int(y_cor))
                    y_new = int(inp)
    
                    break
                except:
                    print(f"{inp} not a legal number - please try again")
            self.trace(f"Position x:{x_new} y: {y_new}")
            if not self.use_command():
                self.tu.listen()        # textinput does its own keybd capture
        else:
            if x is None or (type(x) == str and x == ""):
                x_new = x_cor
            else:
                x_new = int(float(x))
            if y is None or (type(y) == str and y == ""):
                y_new = y_cor
            else:
                y_new = int(y)
        self.move_to(x_new, y_new, is_move=True)
        self.trace(f"Position x:{x_new} y: {y_new}")
        self.trace(f"End of move_set key")

    def move_to(self, x,  y, is_move=False, pen_down=None):
        """ Move to position
        :x: new x position
        :y: new y position
        :is_move: True - this is a move and undoable
        :pen_down: True = pen down, False = pen up
                default: use current pen orientation
        """
        if self.use_command:
            self.cmd_move_to(x,y, is_move=is_move, pen_down=pen_down)
            return
        
        if is_move:
            self.no_move_backup = True
            self.set_move(move_type=MoveInfo.MT_POSITION)       # Buffer against loosing move
        self.x_cor = x
        self.y_cor = y
        self.tu.setposition(x, y)
    
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

    def set_new_line(self):
        """ Set current location as beginning of line
        to be used by jump_to_next_line
        """
        self.text_line_begin_x = self.x_cor
        self.text_line_begin_y = self.y_cor
        if self.marker_current != "letter":
            self.letter_next()
        

    def newline(self, nline=1):
        """ Position drawing to next line (after previous text)
        :nline: number of lines to advance
        """
        self.jump_to_next_line()
        
    def shape_circle(self):
        """ Display circle
            Circle of current side diameter, in direction of current heading,
            color,...
        """
        #self.erase_if_marker()
        cir_heading = self.heading + 90
        self.xset_heading(cir_heading, change=False)
        self.tu.circle(-self.side/2)
        self.xset_heading(self.heading)
        self.jump_to_next()

    def shape_image(self, name=None):
        """ Display image/animal
        D                C
                  
              image
                  
                  
        A                B
            image's right side in direction of current heading,
            color,...
        """
        #self.erase_if_marker()
        #self.tu.begin_fill()
        self.jump_to(heading=self.heading, distance=self.side/2)
        self.jump_to_next()

    def shape_square(self):
        """ Display square
        D                C
                  
                  
                  
                  
        A                B
            square in direction of current heading,
            color,...
        """
        #self.erase_if_marker()
        #self.tu.begin_fill()
        self.jump_to(heading=self.heading-90, distance=self.side/2)
        self.tu.forward(self.side)
        our_heading = self.heading
        for _ in range(3):
            our_heading += 90     # 90,90,90
            self.xset_heading(our_heading, change=False)
            self.tu.forward(self.side)
        self.tu.end_fill()
        self.xset_heading(self.heading)    # Insure going right direction
        ###self.jump_to(heading=self.heading+90, distance=self.side/2)
        self.jump_to_next()

    def shape_line(self, **kwargs):
        SlTrace.lg("shape_line", "shape_display")
        """ Display line
            line, in direction of current heading,
            color,...
        """
        #self.erase_if_marker()
        self.set_marker()
        SlTrace.lg(f"shape_line from: x_cor,y_cor:{self.tu.xcor():.0f}, {self.tu.ycor():.0f}", "shape_display")
        if 'width' in kwargs:
            self.xset_width(kwargs['width'])
        else:
            self.xset_width(self.current_width)
        if 'heading' in kwargs:
            self.xset_heading(kwargs['heading'])
        else:
            self.xset_heading(self.heading)
        self.do_forward(self.side, move_type= MoveInfo.MT_MARKER)
        SlTrace.lg(f"shape_line  to: x_cor,y_cor:{self.tu.xcor():.0f}, {self.tu.ycor():.0f}", "shape_display")
        
                
    def shape_triangle(self):
        """ Display triangle
        B


        A            C

                  
        D
            Triangle in direction of current heading,
            color,...
        """
        #self.erase_if_marker()
        our_heading = self.heading+90
        self.jump_to(heading=our_heading,
                      distance=self.side/2)
        #self.tu.begin_fill()
        for _ in range(3):
            our_heading -= 120     # 60,60,60
            self.xset_heading(our_heading, change=False)
            self.tu.forward(self.side)
        self.tu.end_fill()
        ###self.jump_to(heading=self.heading-90,
        ###              distance=self.side/2)
        self.xset_heading(self.heading)    # Insure going right direction
        ###self.jump_to(heading=self.heading-90, distance=self.side/2)
        self.jump_to_next()

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
    
    def marker_family(self):
        """ Setup to rotate through animal images
        """
        self.image_type = KeyboardDraw.IT_FILE
        self.set_image_group("family")
        self.image_next('rotateinplace')
    
    def marker_princesses(self):
        """ Setup to rotate through princesses images
        """
        self.image_type = KeyboardDraw.IT_FILE
        self.set_image_group("princesses")
        self.image_next('rotateinplace')
    
    def marker_other_stuff(self):
        """ Setup to rotate through other images
        """
        self.image_type = KeyboardDraw.IT_FILE
        self.set_image_group("other_stuff")
        self.image_next('rotateinplace')
        
        
        
    def marker_next(self, **kwargs):
        """ Go to next marker if that is changing,
            else to the next shape if that is changing
            else to the next line
            and do the appropriate marker/shape/line
            :kwargs:  suplimental settings
        """
        self.set_move(move_type=MoveInfo.MT_MARKER)
        if self.marker_changing:
            self.set_marker(changing=self.marker_changing)
        if self.marker_current == "image":
            self.do_marker()
        elif self.marker_current == "shape":
            self.color_set()
            self.shape_next()
        elif self.marker_current == "line":
            self.color_set()
            self.do_line(**kwargs)
        elif self.marker_current == "letter":
            self.jump_to_next()                    # Move one space
        else:
            SlTrace.lg(f"Unrecognized marker: {self.marker_current} - ignored")
                        
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
        self.set_images(show=False)
        exit_infos = self.get_btn_infos(key="END")
        self.set_btn_image(exit_infos, image="drawing_abc_end.png")
        self.track_keys_text()
        self.master.focus()             # So keyboard is active
        
    def on_key_press(self, event):
        """ Process all canvas keying
        Avoids confusion with turtle onkey and separate binding
        function is one of single argument keysym
        :event:
        """
        keysym = event.keysym
        if keysym in self.bound_keys:
            fun = self.bound_keys[keysym]
            if fun is not None:
                fun()
                
        
    
    def bind_key(self, keyfun, key):
        """ bind/unbind key to function
        Binds key to function, if present
        else unbind key
        Use self.master.bind('<KeyPress>'...) instead of turtle.onkey
        :keyfun: "No arg" function bound to key
        :key: key pressed
        """
        #key = key.lower()
        str_to_key = {"DEL" : chr(127),
                      "BKSP" : chr(8),
                    }
        
        if keyfun is None:
            del self.bound_keys[key]        
        else:
            self.bound_keys[key] = keyfun  # First or New binding


        
    def on_text_end(self):
        self.text_entry_funcid = self.master.unbind('<KeyPress>', self.text_entry_funcid)
        self.track_keys()   # Reset keys to drawing cmds        
        self.do_shift(False)
        exit_infos = self.get_btn_infos(key="BKSP")
        self.set_btn_image(exit_infos, image=None)
        self.set_images(show=True)
        self.set_marker(self.marker_before_letter)


    def text_enter_key(self, key):
        """ Process next entered letter marker
        :key: letter to be placed
        """
        if len(key) == 1:
            SlTrace.lg(f"text_enter_key: '{key}' ord:{ord(key)}")
        else:
            SlTrace.lg(f"text_enter_key: '{key}'")

                            # Do special characters
        if key == "END":
            self.on_text_end()
            return
        
        
        if key == "BKSP":
            self.draw_undo()
            return
        
        self.draw_preaction(key=key)
        if key == "ENTER":
            self.jump_to_next_line()
            self.draw_postaction()        
        elif key == "Left" or key == "Right" or key == "Up" or key == "Down":
            self.move(key, just_move=True)
            self.set_new_line()     # Set as beginning of line
            self.draw_postaction()
            return
        
        if key == "space".lower():
            key = " "
        
        text_size = int(self.side)
        x0 = 0
        y0 = 0
        font_size = 80
        text_font = ImageFont.truetype("arial.ttf", size=font_size)
        #text_font = ImageFont.truetype("courbd.ttf", size=text_size)
        #text_font = ImageFont.truetype("tahoma.ttf", size=text_size)
        text_color = self.next_color()
        text_bg = "#ffffff"    

        xy = (x0,y0)
        image = Image.new("RGB", (text_size, text_size), (255,255,255))
        draw = ImageDraw.Draw(image)      # Setup ImageDraw access
        draw.text(xy, key, anchor="mt", font=text_font, fill=text_color,
                  bg=text_bg)
        ii = (None, image)
        self.do_image(image_info=ii, key=key)
        self.draw_postaction()
        
    def line_next(self, shape=None, choose=None):
        """ Set line "shape"
        """
        self.set_marker("line")
        
    def shape_next(self, shape=None, choose=None):
        """ Go to next shape and change current side to
        that shape
        :shape:
            'nextone' - select next shape as the one
            'rotate' change shape and make new shape
            'rotateinplace' - change shape of current image 
        """
        if shape is not None and shape != "" and shape in self.shapes:
                display_shape = shape
                self.shape_current = display_shape
        elif choose:
            SlTrace.lg("Don't know how to choose shapes yet")
            return
        elif shape is None or shape == "":
            if self.shape_current == "rotate":
                display_shape = self.pick_next_shape()
            elif self.shape_current in self.shapes:
                display_shape = self.shape_current     
        elif shape == "nextone":
            self.set_marker(marker="shape")
            display_shape = self.pick_next_shape()
            self.shape_current = display_shape
            self.erase_if_marker()
        elif shape == "rotate":
            self.set_marker(marker="shape")
            self.shape_current = "rotate"
            display_shape = self.pick_next_shape()
        elif shape == "rotateinplace":
            self.set_marker(marker="shape")
            self.shape_current = "rotate"
            self.erase_if_marker()
            display_shape = self.pick_next_shape()
        else:
            display_shape = self.shape_current
        shape_fun = self.shapes[display_shape]
        self.set_pen_state()
        shape_fun()
        self.set_pen_state()
        self.set_move(move_type=MoveInfo.MT_MARKER)
        
    def shape_change(self, shape_str=None, choose=None):
        """Set shape
        :shape_str: shape string (name)
            'next' - go to next
            'rotate' - rotate through shapes as movement
            'line'  - line
            'circle' -  circle
            'triangle' - triangle pointing in direction
            'square' - square
            
        :choose: Prompt user to choose
        """
        if choose:
            print("SORRY - choose shapes not yet operational - see  you soon!")
            return
            
            while True:
                try:
                    inp = self.tu.textinput("shape",
                                    f"Enter shape[{self.shape_current}]")
                    if inp is None or inp == "":                    
                        inp = self.shape_current
                    self.shape_current = inp
                    break
                except:
                    print(f"{inp} not a legal number - please try again")
                
            while True:
                try:
                    inp = self.tu.textinput("Line Size",
                                     f"Enter line width[{self.current_width}]")
                    if inp is None or inp == "":                    
                        inp = str(self.current_width)
                    self.current_width = int(inp)
    
                    break
                except:
                    print(f"{inp} not a legal number - please try again")
            self.trace(f"line length:{self.side} width: {self.current_width}")
            self.tu.listen()        # textinput does its own keybd capture
        else:
            if shape_str == 'next':
                self.shape_next()
            elif shape_str == 'rotate':
                self.shape_rotate()
            elif shape_str == 'line':
                self.shape_line()
            elif shape_str == 'circle':
                self.shape_circle()
            elif shape_str == 'triangle':
                self.shape_triangle()
            elif shape_str == 'square':
                self.shape_square()
        self.trace(f"End of shape set shape: {self.shape_current}")
    
    def erase_move(self):
        """ Erase last move
            Currently just a simple turtle undo but soon to be more robust 
        """
        self.trace("erase_move")
        self.draw_undo()

    def erase_if_marker(self):
        """ Remove last move if it is a marker
        This allows modify-in-place
        """
        move = self.get_move()
        if move and move.move_type == MoveInfo.MT_MARKER:
            self.erase_move()

    def cmd_get_loc(self):
        """ Get current location
        :returns: (x_cor, y_cor)
        """
        return (self.x_cor, self.y_cor)

    def set_color(self, color):
        """ Set current color
        """
        self.color_current = color
        
    def set_loc(self, locxy, locy=None):
        """ Set current location
        :locxy: (x,y) if tuple, else x
        :locy: y if necessary
        """
        if isinstance(locxy, tuple):    
            x,y = locxy
        else:
            x,y = locxy, locy
        self.x_cor, self.y_cor = x,y 
    
    def set_heading(self, heading):
        self.heading = heading
                


    def set_side(self, side):
        self.side = side

    def set_width(self, line_width):
        self.current_width = line_width


    def set_size(self, side=None, line_width=None):
        if side is not None:
            self.set_side(side)
        if line_width is not None:
            self.set_width(line_width)

    def get_move(self):
        """ Get most recent move (MoveInfo)
        :returns: move, None if none
        """
        if len(self.move_stack) > 0:
            return self.move_stack[-1]
        
        return None 
    
    def erase_side(self):
        """ Erase side, for possible overwriting
        width, length, and heading remain unchanged
        Position is at beginning of original line
        """
        self.trace("erase_side")
        self.tu.undo()
    
    def move(self, direct, just_move=False, **kwargs):
        """ move a general direction
        using current shape
        Adjusted to text input (self.marker_current)
        :direct: direction Up, Left, Right, Down
        :just_move: True - just move (no shape)
                    default: False
        :kwargs: suplimental parameters for adjustments
        """
        self.trace(f"move: '{direct}'")
        self.set_move(move_type=MoveInfo.MT_MARKER)     # Most likely
        uplr = {'Up' : 90, 'Left' : 180, 'Right' : 0, 'Down' : 270}
        if direct in uplr:
            self.heading = uplr[direct]
            if self.marker_current == "letter":
                self.set_new_line()
            if just_move or self.marker_current != "line":
                self.set_move(move_type=MoveInfo.MT_POSITION)
                self.jump_to_next()
            else:
                self.do_forward(move_type=MoveInfo.MT_MARKER)
        elif direct in "12346789": # Digit moves
            dig2head = {'6':0, '9':45, '8':90,
                        '7':135, '4':180, '1':225,
                        '2':270, '3':315, '6':0,
                        }
            self.set_move(move_type=MoveInfo.MT_MARKER)
            self.heading = dig2head[direct]
        elif direct == '5':     # rotate 45 deg left
            self.heading += 45
        elif direct == '0':     # rotate 45 deg right
            self.heading -= 45
        elif direct == 'space':
            self.erase_side()
            self.heading += 180
        elif direct == 'c':
            self.tu.penup()
            self.tu.home()
            self.do_pendown()
            return
        
        else:
            print(f"Sorry, I don't know what '{direct}' means")
            return      # Do nothing
    
        if self.heading < 0 or self.heading >= 360:
            self.heading = self.heading % 360    # Keep in 0 < 360
        '''
        if self.color_current == "w":    # Changing color
            ###self.trace(f"check for 'w': self.color_current:{self.color_current}")
            self.color_index += 1
            self.color_index = self.color_index % len(self.colors)
        if self.color_index == -1:
            self.set_visible_color(self.color_current)
        else:    
            self.set_visible_color(self.colors[self.color_index])
        '''
        self.xset_heading(self.heading)
        ###self.do_forward(self.side)
        if just_move:
            self.jump_to_next()
        else:
            self.marker_next(**kwargs)
        ###self.draw_postaction()
        
    def move_up(self):
            self.move('Up')
        
    def move_left(self):
        self.move('Left')
        
    def move_right(self):
        self.move('Right')
        
    def move_down(self):
        self.move('Down')
    
    def move_minus(self):
        self.trace("move_minus")
        self.set_pen_state(False)
    
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
        
    def move_plus(self):
        self.trace("move_plus")
        self.set_pen_state(True)
        
    def move_0(self, **kwargs):
        self.move('0', **kwargs)
    
    def move_1(self, **kwargs):
        self.move('1', **kwargs)
    
    def move_2(self, **kwargs):
        self.move('2', **kwargs)
    
    def move_3(self, **kwargs):
        self.move('3', **kwargs)
    
    def move_4(self, **kwargs):
        self.move('4', **kwargs)
    
    def move_5(self, **kwargs):
        self.move('5', **kwargs)
    
    def move_6(self, **kwargs):
        self.move('6', **kwargs)
    
    def move_7(self, **kwargs):
        self.move('7', **kwargs)
    
    def move_8(self, **kwargs):
        self.move('8', **kwargs)
    
    def move_9(self, **kwargs):
        self.move('9', **kwargs)
    
    def move_space(self):
        self.move('space')
    
    def move_c(self):
        self.move('c')

    def line_narrow(self):
        if self.current_width > 2:
            if not self.new_pendown:
                self.erase_if_marker()      # Erase current leg
            current_width = self.current_width - 2
            if self.move_undo and self.move_undo.key:
                self.do_key(self.move_undo.key, width=current_width)

    def line_widen(self):
        if not self.new_pendown:
            self.erase_if_marker()      # Erase current leg
        current_width = self.current_width + 2
        if self.move_undo and self.move_undo.key:
            self.do_key(self.move_undo.key, width=current_width)

    def marker_scale(self, factor):
        """ Scale current marker by factor
        :factor: factor to scale side
        """
        if not self.new_pendown:
            self.erase_if_marker()      # Erase current leg
            if self.move_undo and self.move_undo.key:
                self.side *= factor
                self.do_key(self.move_undo.key)
        '''if image needs special case
        elif move.marker == "image":
            self.side *= 1.1
            if self.move_undo and self.move_undo.key:
                self.do_key(self.move_undo.key)
            ###self.image_next('same')
        '''
                    
    def marker_enlarge(self):       # 't'
        self.marker_scale(1+self.enlarge_fraction)
        
    def marker_shrink(self):
        """ Change current and subsequent lines to a thinner line
        """
        self.marker_scale(1/(1+self.enlarge_fraction))
            
    def marker_rotate(self):       # '/'
        if self.use_command:
            return self.cmd_marker_rotate()
        if not self.new_pendown:
            self.erase_if_marker()      # Erase current leg
            heading = self.heading + 45
            if self.move_undo:
                move = self.move_undo
                if move.shape == "line":
                    self.draw_preaction(key=move.key)
                    self.xset_heading(heading)
                    self.do_forward(move_type=MoveInfo.MT_MARKER)
                    self.draw_postaction()
                elif move.key:
                    self.do_key(move.key, heading=self.heading) 
        
        ''' pre-do_key approach
        move = self.get_move()
        if move:
            self.erase_if_marker()      # Erase current leg
            self.heading += 45
            if move.marker == "line":
                self.shape_next()
            elif move.marker == "shape":
                self.shape_next()
            elif move.marker == "image":
                self.image_next('same')
            elif move.marker == "letter":
                self.letter_next()
                self.text_enter_key(move.key)
                self.on_text_end()
        '''
     
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
        return self.tu_canvas

    def get_heading(self):
        if hasattr(self, "heading"):
            return self.heading
        else:
            return 0

    def get_side(self):
        if hasattr(self, "side"):
            return self.side
        else:
            return 100

    def get_width(self):
        if hasattr(self, "current_width"):
            return self.current_width
        else:
            return 4


    def get_x_cor(self):
        if not hasattr(self, "x_cor") or self.x_cor is None:
            return 0
        
        return self.x_cor


    def get_y_cor(self):
        if not hasattr(self, "y_cor") or self.y_cor is None:
            return 0
        
        return self.y_cor

        
    def xset_heading(self, heading, change=True):
        """ Set heading, changing only if not already there
        :heading: heading to to
        :change: change self.heading, default: True - update self.heading
        """
        if change:
            self.heading = heading
        tu_heading = self.tu.heading()
        if heading != tu_heading:
            self.tu.setheading(heading)
            
    def xset_width(self, width, change=True):
        """ Set line width, if necessary
        :width: line width in pixelx
        :change: Change current width
                default: True
        """
        tu_width = self.tu.width()
        if change:
            self.current_width = width
        if width != tu_width:
            self.tu.width(width)
            
    def set_image_group(self, group_name):
        """ Set current image group name and access
        """
        self.image_group = self.ifh.get_group(group_name)

    def set_image_type(self, type_name):
        """ Set current image group name and access
        """
        self.image_type = type_name

                  
    def make_side(self, sz):
        """ Make side (move) dimension
        :sz: new side size
        """
        self.side = sz
    
    def enlarge_side(self):
        """ Enlarge size a bit
        """
        if not self.new_pendown:
            self.tu.undo()      # Remove previous side
        self.make_side(self.side*(1+self.enlarge_fraction))
        self.do_forward(self.side)
    
    def select_print(self, tag, trace=None):
        """ Print select select state
        """
        """TBD"""
                        
    def reduce_side(self):
        """ Reduce size back to before enlarge_size
        """
        if not self.new_pendown:
            self.tu.undo()
        self.make_side(self.side/(1+self.enlarge_fraction))
        self.do_forward(self.side)
        
    def move_shift(self):
        pass

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
                or special "key" e.g. =<color spec>
        :kwargs: function specific parameters
                often to "redo" adjusted undone operations
        """
        if self.use_command:
            return self.cmd_proc.do_key(key, **kwargs)
        
        SlTrace.lg(f"do_key({key})")
        if key == 'check':
            self.print_key(key)
            self.check(key)
            return
        
        if self.marker_current == "letter":            
            self.text_enter_key(key=key)
            return
        
        if key == "u":
            self.draw_undo()
            return
        
        fun_mat = re.match(r'^(\w+)\((.*)\)$', key)
        if fun_mat:
            self.print_key(key)
            args_str = fun_mat.group(2)
            fun_name = fun_mat.group(1)
            if fun_name in self.fun_by_name:
                fun_fun = self.fun_by_name[fun_name]
            else:
                msg = f"We don't recognize function {fun_name} in {key}"
                SlTrace.report(msg)
                return 
            
            fun_args = re.split(r'\s*,\s*', args_str)
            self.draw_preaction(key=key)
            fun_fun(*fun_args)
            self.draw_postaction()
            return
        
        if re.match(r'^moveto:?.*', key):
            self.print_key(key)
            self.moveto_set(key)        # move with/without specification
            return
        
        if re.match(r'^=.+', key):
            self.print_key(key)
            self.col(key)        # color with specification
            return
        
        if re.match(r'^:.+', key):
            self.print_key(key)
            self.line_set(key)        # color with specification
            return
         
        elif key in self.bound_keys:
            keyfun = self.bound_keys[key]
        elif key in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" and key.lower() in self.bound_keys:
            keyfun = self.bound_keys[key.lower()]
        else:
            print(f"key '{key}' is not yet bound - ignored")
            return
        
        self.print_key(key)
        adj_keys = ["a",    # marker_shrink
                    "k",    # marker_animals
                    "q",    # marker_enlarge
                    "t",    # line_widen
                    "x",    # line_narrow
                    "/",    # markerk_rotate
                    ]
        if key in adj_keys:
            self.trace_move_stack("adjusting move", key=key)
            keyfun()            # stack arrangement
                                # unchanged, just new entries
            self.trace_move_stack("adjusting move AFTER", key=key)
        else:
            move_type = MoveInfo.MT_MARKER
            self.draw_preaction(key=key, move_type=move_type, **kwargs)
            keyfun(**kwargs)
            self.draw_postaction()
    
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
                    
    def track_key(self, keyfun, key):
        """ connect key with function
        key is echoed whenever pressed
        :keyfun: "No argument" function to be executed when key pressed
        :key: key text
        """
        self.bind_key(keyfun, key)

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
        """ Setup keys for text input
        OLD:
        self.text_chars = "abcdefghijklmnopqrstuvwxyz"
        self.text_chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.text_chars += "01234567890"
        self.text_chars += "!@#$%^&*()_+-="
        self.text_chars += "[]\\{}| "
        self.text_chars += ";':"
        self.text_chars += ",./<>?"
        self.text_chars += "\b"     # Special text processing
        self.text_escape_chars = ["BKSP"]
        for key in self.text_chars:
            def ttkey(key=key):
                self.text_enter_key(key=key)
            self.track_key(ttkey, key)

        for key in self.text_escape_chars:
            self.track_key((lambda : self.text_enter_escape_key(key=key)), key)
        
        """
        """ bind keyboard keys """
        self.text_entry_funcid = self.master.bind('<KeyPress>', self.on_text_entry)
        self.set_images(show=False)         # Display only keys (no shape images)
        """ bind screen keyboard keys """
        

    def set_images(self, show=False):
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

                            
    def track_keys(self):
        """ Setup key tracking
        """    
        self.track_key(self.marker_shrink, 'a')
        self.track_key(self.col_b, 'b')
        self.track_key(self.move_c, 'c')
        self.track_key((lambda : self.shape_next('nextone')), 'd')
        self.track_key(self.letter_next, 'e')
        self.track_key(self.line_next, 'f')
        self.track_key(self.col_g, 'g')
        self.track_key(self.help, 'h')        
        self.track_key(self.col_i, 'i')
        self.track_key((lambda : self.marker_set(choose=True)), 'j')
        self.track_key((lambda : self.marker_animals()), 'k')
        self.track_key(self.marker_family, 'l')
        self.track_key(self.moveto_setting, 'm')
        self.track_key(self.col_o, 'o')
        self.track_key(self.marker_enlarge, 'q')
        self.track_key(self.col_r, 'r')
        self.track_key((lambda : self.shape_next('rotateinplace')), 's')
        self.track_key(self.line_widen, 't')
        self.track_key(self.draw_undo, 'u')
        self.track_key(self.col_v, 'v')
        self.track_key(self.col_w, 'w')   # Changing colors
        self.track_key(self.line_narrow, 'x')
        self.track_key(self.col_y, 'y')
        self.track_key(self.clear_all, 'z')
        self.track_key(self.move_up, 'Up')
        self.track_key(self.move_left, 'Left')
        self.track_key(self.move_right, 'Right')
        self.track_key(self.move_down, 'Down')
        self.track_key(self.move_minus, 'minus')
        self.track_key(self.move_plus, 'plus')
        self.track_key(self.marker_princesses, '[')
        self.track_key(self.marker_other_stuff, ']')
        self.track_key(self.col_equals, '=')
        self.track_key(self.line_setting, ':')
        self.track_key(self.line_setting, ';')    # lower case :
        self.track_key(self.checking, '.')        # Converted to >
        self.track_key(self.marker_rotate, '/')
        self.track_key(self.tracing, '!')
        self.track_key(self.move_shift, '')
        self.track_key(self.move_space, 'space')
        self.track_key(self.move_0, '0')
        self.track_key(self.move_1, '1')
        self.track_key(self.move_2, '2')
        self.track_key(self.move_3, '3')
        self.track_key(self.move_4, '4')
        self.track_key(self.move_5, '5')
        self.track_key(self.move_6, '6')
        self.track_key(self.move_7, '7')
        self.track_key(self.move_8, '8')
        self.track_key(self.move_9, '9')
        
        

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
                self.tu_canvas.delete(canvas_tag)
        
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

    def tu_canvas_coords(self, tu_coords=None):
        """ Canvas x coordinate
        :tu_coords: turtle coordinate pair
                default: use current
        :returns: canvas x_coordinates pair
        """
        if tu_coords is None:
            tu_coords = (self.x_cor, self.y_cor)
        x_cor, y_cor = tu_coords    
        canvas_width = self.tu_canvas.winfo_width()
        canvas_height = self.tu_canvas.winfo_height()
        x_coor = int(canvas_width/2 + x_cor)
        y_coor = int(canvas_height/2 - y_cor)        # canvas increases downward
        return (x_coor, y_coor)

    """ command based action methods
    """
    def cmd_marker_rotate(self):
        prev_cmd = self.cmd_get_prev_command()
        if prev_cmd is None:
            return False 
        new_command = self.cmd_start_command()
        rotate = 45
        prev_markers = prev_cmd.get_new_markers()
        new_markers = []
        for prev_marker in prev_markers:
            new_command.add_prev_marker(prev_marker)
            new_marker = prev_marker.rotate(rotate)
            new_command.add_marker(new_marker)
        self.complete_command(new_command)

    def cmd_clear_all(self):
        """ Clear screen
        """
        self.cmd_proc.clear_all()
        
    def cmd_get_last_command(self):
        """ Get last command executed
        Adjusted by undo
        """
        return self.command_manager.get_current_command()
            
    def cmd_get_prev_command(self):
        """ Get previous command, if one
        :returns copy of previous command
        """
        cmd = self.command_manager.get_prev_command()
        return cmd

    """ For legacy support of drawing_command.py main:
    """

    def insert_markers(self, markers):
        """ Insert markers to display
        Update location to final marker's next location 
        :markers: list of markers(DrawMarker) to be removed
        """
        for marker in markers:
            marker.draw()

    def remove_markers(self, markers):
        """ Remove markers from display 
        :markers: list of markers(DrawMarker) to be removed
        """
        for marker in markers:
            marker.undraw()

    def display_print(self, tag, trace):
        """ display current display status
        :tag: text prefix
        :trace: trace flags
        """
        
    def display_update(self, cmd=None):
        """ Update current display
        """
        if cmd is None:
            cmd = self.cmd_get_last_command()
        if cmd is None:
            return          # Nothing to do
        SlTrace.lg(f"display_update:{cmd}", "display_update")
        self.remove_markers(cmd.prev_markers)
        self.insert_markers(cmd.new_markers)
        new_loc = cmd.new_loc
        if new_loc is None:
            cmd.set_new_loc()       # Default command new location
        if cmd.new_loc is not None:
            self.set_loc(cmd.new_loc)
        if self.cmd_pointer is not None:
            self.cmd_pointer.undraw()
        heading = cmd.get_heading()
        self.cmd_pointer = DmPointer(self, x_cor=cmd.new_loc[0],
                                     y_cor=cmd.new_loc[1],
                                     heading=heading)
        self.set_heading(heading)
        self.cmd_pointer.draw()
        self.master.update()
                        
    
    
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
    parser.add_argument('--hello_str', dest='hello_str', default=hello_str)
    parser.add_argument('--hello_file', dest='hello_file', default=hello_file)
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
                kbd_win_width=600, kbd_win_height=300,
                use_command=use_command
                           )

    kb_draw.enable_image_update()      # Enable key image update
    
    kb_draw.tu_screen.listen()
    tk.mainloop()

if __name__ == "__main__":
    main()