#kbd_cmd_proc.py    18Mar2021  crs
""" keyboard_draw command processor
Provides link between KeyboardDraw and command structure 
Encapsulates keyboard key commands, Command, Command Manager
"""
import math
import re
import random 
from tkinter import colorchooser

from select_trace import SlTrace
from select_error import SelectError
from attr_change import AttrChange, Attribute

from command_manager import CommandManager
from drawing_command import DrawingCommand
from dm_attributes import DmAttributes
from dm_color import DmColor
from dm_heading import DmHeading
from dm_image import DmImage
from dm_line import DmLine
from dm_marker import DmMarker
from dm_move import DmMove
from dm_move_key import DmMoveKey
from dm_pen import DmPen
from dm_pointer import DmPointer
from dm_position import DmPosition
from dm_square import DmSquare
from dm_triangle import DmTriangle

from dm_text import DmText
from dm_size import DmSize
from dm_circle import DmCircle
from _operator import index

class KbdCmdProc:
    
    def __init__(self, drawer):
        self.drawer = drawer
        self.command_manager = CommandManager(self)
        self.set_drawing() # In figure drawing mode
        self.cmd_pointer = None
        self.drawer.master.bind("<KeyPress>", self.on_key_press)
        self.is_drawing = True      # Start in drawing mode 
        
        """ Translation (partial) from key to keysym
        """
        self.key2sym = {
            ' ' :"space",
            '=' : "equal",
            '/' : "slash",
            '[' : "leftbracket",
            ']' : "rightbracket",
            'Space':"space",    # ScreenKbdFlex - special
            }
        
        self.keys_to_funs = [
            (self.cmd_color_adjust, ('w', 'equal')),
            (self.cmd_visibility_adjust, ('minus','plus')),
            (self.cmd_size_adjust, (':',';','a','q','r','t')),
            (self.cmd_position_adjust, ('c','m','Left','Right','Up', 'Down')),
            (self.cmd_add_new_direction, ('0','1','2','3','4','5','6','7','8','9')),
            (self.cmd_help, 'h'),
            (self.cmd_images, ('j','k','l',
                               'bracketleft','bracketright')),
            (self.cmd_shapes, ('s','f')),
            (self.cmd_rotate, 'slash'),
            (self.cmd_redo, 'y'),
            (self.cmd_repeat, 'space'),
            (self.cmd_undo, 'u'),
            (self.cmd_restore_all, 'x'),
            (self.cmd_clear_all, 'z'),
            (self.cmd_do_trace, '!'),
            (self.set_text_mode, ('e','END'))
            ]
        self.setup()

        
        """
        function definitions
        """
    
        self.fun_by_name = {
            'color' : self.cmd_set_color,
            'drawing' : self.set_drawing_mode,
            'image_file' : self.cmd_image_file,
            'lengthen' : self.lengthen,
            'line' : self.cmd_set_line,
            'marker' : self.cmd_set_marker_type,
            'moveto' : self.cmd_moveto,
            'narrow' : self.narrow,
            'newline' : self.cmd_newline,
            'setnewline' : self.set_newline,
            'shorten' : self.shorten,
            'text' : self.set_text_mode,
            'shape' : self.cmd_set_shape_type,
            'widen' : self.widen,
            }
        self.setup()
        
    def help(self):
        print("""
    h - print this help message
    color keys:
        r : red, o-range, y-yellow, g-green, b-blue,
        i : indigo, v-violet
        w : changing colors
        - : make lines invisible(white)
        + : make lines visible(previous color)
        = : Set line color from color chooser
            Colors can be changed via arrow keys
            Press <space> to select color, <ENTER> to
            choose the color The Mouse can also be used.
    side size keys:
        : or ; : Interactively Set line length and width in pixels
            from script (:width[:length])
                         e.g. :100:5 for len 100 width 5 
        q : increase marker size (10%)
        a : decrease-marker size (undo a previous 10% increase)
        t : increase current line thickness by two
        x : decrease current line thickness by two
    move keys:
        m : move to location script: moveto[:][x][:y]
            Move to x,y location (-512..512)
                default: no movement in direction if direction is empty
                    example: moveto::500 just moves to y=500, x unchanged
            m, moveto alone prompts user for values
                    
        arrows : in direction of arrow(Up,Down,Right,Left)
        Digits : 1-9 for directions of keypad
                7 8 9
                4   6
                1 2 3  for example 9-diagonal up to right
            5 : rotate 45 deg to left, then draw line
            0 : rotate 45 deg to right, then draw line 
            space : rotate 180 deg (reverse direction)
        u : "undo" - take back last graphic action
                    Note: Most drawing actions use
                          several graphics actions
        c : move to center
        e : do letters / text, until DEL key pressed
        s : "shape" - set shape to next
        d : "determine" choose shape - via dialog
        f : "fan" - set shape to rotate as we move
        z : clear screen of drawing, reset to original values
        
    Image Keys
        w : set colors to change each move
        s : Set shapes to change each move
        d : Change to a particular shape
        j : Select an animal picture for each move
        k : Change animal picture each press
        l : Change family picture each press
        [ : Change princess picture each press
        ] : Change other_stuff picture each press

    Text Keys
        e : Set to text (letter) entering mode
            Keys pressed now will create letters on the screen
            Screen keyboard now shows letters in most key positions
        END : quit text (letter) mode and go back to shapes/animals...
            Screen keyboard now changes back to shapes/animals...
        
    Special keys /commands
        ., check - used for debugging
        """)
        ###SlTrace.lg(f"turtle: width:{self.turtle_cv.canvwidth} height:{self.turtle_cv.canvheight}")
    
        
    def on_key_press(self, event):
        """ Process all canvas keying
        :event:
        """
        keysym = event.keysym
        self.do_keysym(keysym)
        
    def do_keysym(self, keysym):
        SlTrace.lg(f"do_keysym: {keysym}", "input")
        if keysym == "check":
            SlTrace.lg("Just checking")
            return

        """ Functions work in all modes """
        if self.ck_function(keysym):
            return 
        
        if self.is_drawing:
            self.drawing_cmd(keysym)
        else:
            self.text_cmd(keysym)

    def text_cmd(self, keysym):
        """ Do command in text mode
            Enter text unless special command
            END - go back to figure drawing mode
            Right, Left, Up, Down - do motions
            Return - go to next line
        """
        SlTrace.lg(f"text_cmd({keysym})")
        if keysym.lower() == "space":   # Support symbolic
            keysym = " "
            
        if keysym == "BackSpace":
            return self.command_manager.undo()
        
        if keysym.lower() == 'end':
            self.set_drawing_mode()
            return True
        
        if keysym == "Return" or keysym == "ENTER":
            self.cmd_newline()
            return True 
        
        if keysym in ['Right','Left', 'Up', 'Down']:
            self.drawing_cmd(keysym)
            return

        cmd = DrawingCommand(f"cmd_{keysym}")
        marker = DmText(self, text=keysym)
        cmd.add_marker(marker)
        return cmd.do_cmd()
                
        SlTrace.report(f"Don't recognize text {keysym}"
                       f" as a text_cmd")
        return False

    def key_to_sym(self, key):
        """ Convert key to symbol text
        if no translation - return key unchanged
        :key: standard key
        """
        if key in self.key2sym:
            key = self.key2sym[key]
        return key
        
    def do_key(self, key, **kwargs):
        """ Process key by
        calling keyfun, echoing key
        :key: key (descriptive string) pressed
                or special "key" e.g. =<color spec>
        :kwargs: function specific parameters
                often to "redo" adjusted undone operations
        """
        keysym = self.key_to_sym(key)
        self.do_keysym(keysym)
        
    def set_drawing(self, drawing=True):
        """ Set drawing mode
        :drawing: True - set figure drawing mode
                  False - set text drawing mode
                default: True
        """
        self.is_drawing = drawing

     
    def get_image_file(self, group=None, file=None, next=True):
        """ get current image group's file
        :group: group name default: current group
        :file: file name default: current or next
        :next: if true get next
        """
        return self.drawer.get_image_file(group=group, file=file,
                                          next=next)

    def cmd_image_file(self, group=None, file=None):
        """ create marker at current location, heading
        from group of name
        :group: group name (e.g. animals, family)
        :name: first file in group which contains the name string
        """
        image_file = self.get_image_file(group=group, file=file,
                                         next=True)
        if image_file is None:
            SlTrace.report(f"No image file group {group}"
                           f" groups: {self.image_group_names}")
            return False
        
        image_base = self.drawer.image_file_to_image(image_file)
        if image_base is None:
            raise SelectError(f"Can't get image from {image_file}")
        
        return self.cmd_do_image(file=image_file,
                                 image_base=image_base)
        
        
    def cmd_help(self, keysym):
        """ Generate help message
        """
        self.drawer.help()
        
        
    def drawing_cmd(self, keysym):
        """ Do figure drawing command
        :keysym: key symbol
                recognizes \w+\([^)]*\) as a function call
        """
        if keysym == 'e' or keysym == "End":
            self.set_text_mode(keysym)
            return
            
        keysym = self.key_to_sym(keysym)    # Translate if necess
        dr_fun = self.get_key_fun(keysym)
        if dr_fun is None:
            SlTrace.report(f"Don't recognize drawing key cmd:"
                           f" {keysym}")
            return
        dr_fun(keysym)

    def get_key_fun(self, keysym):
        """ Get function to implement key command
        May optimize this table processing later by placing the info
        into a dictionary of function by keysym
        :keysym: key symbol
        """
        for keys_to_fun in self.keys_to_funs:
            fun, syms = keys_to_fun
            if not isinstance(syms, tuple):
                syms = (syms)   # tuple of one
            if keysym in syms:
                return fun
        
        return None     # keysym not found

    def ck_function(self, keysym):
        """ Check for function, an process if one
        function patterns:
            1. ^(\w+)\((.*)\)$
            2. =([^)]+) treated as color($1)
        :keysym: function pattern: 
        :retuns: True if function pattern matches
                False if not a function pattern
        """
        spec_mat = re.match(r'^=([\)]+)', keysym)
        if spec_mat is not None:
            keysym = f"color({spec_mat.group(1)})"
        fun_mat = re.match(r'^(\w+)\((.*)\)$', keysym)
        if fun_mat is None:
            return False 
        
        self.print_key(keysym)
        args_str = fun_mat.group(2)
        fun_name = fun_mat.group(1)
        if fun_name in self.fun_by_name:
            fun_fun = self.fun_by_name[fun_name]
            if args_str != "":
                fun_args = re.split(r'\s*,\s*', args_str)
                fun_fun(*fun_args)
            else:
                fun_fun()   # No args necessary
            return True
        
        raise SelectError(f"Unrecognized function: {fun_name}")
        
    def cmd_clear_all(self, keysym):
        """ Clear screen
        """
        while not self.command_manager.command_stack.is_empty():
            self.command_manager.undo()
        self.attr_chg.reset()       # Reset attribute settings
        
    def cmd_restore_all(self, keysym):
        """ Restore (Undo cmd_clear_all)
        """
        while not self.command_manager.undo_stack.is_empty():
            self.command_manager.redo()
    
    def cmd_color_adjust(self, keysym):
        """ Color adjustments
            w - rotating colors
            equal - choose color
        """
        
        if keysym == 'w':
            self.set_next_change("color", "ascending")
            color = self.get_next("color")
        elif keysym == "equal":
            color_choice = colorchooser.askcolor()
            SlTrace.lg(f"color_choice: {color_choice}")            
            if color_choice is None or color_choice[1] is None:
                return
            
            self.set_next_change("color", "constant")
            color = color_choice[1]
            self.add_next_change_value("color", value=color)
        else:
            SlTrace.report(f"Unrecognized color adjust: {keysym}")
            
        marker = DmColor(self, color=color)
        
        cmd_last = self.last_marker_command()
        marker_last = self.last_marker()
        if marker_last is None:
            marker = DmColor(self, color=color)
            cmd = DrawingCommand(f"cmd_{keysym}")
            cmd.add_markers(marker)
        else:
            #self.undo_last_marker_command() # undo to last marker
            ###cmd = cmd_last.reverse_copy()
            cmd = DrawingCommand(f"cmd_{keysym}")
            marker = marker_last
            marker = marker.use_locale(marker_last)
            marker = marker.change(color=color)
            cmd.add_prev_markers(marker_last)
            cmd.add_markers(marker)

        return cmd.do_cmd()

    def cmd_images(self, keysym):
        """ Create image markers
        replacing previous marker, if one
        
            j - choose from current group
            k - rotate through animals
            l - rotate through family
            [ (bracketleft) - rotate through princesses
            ] (bracketright)- rotate other
        :keysym: image type
        """
        char2group = {
                       'k':"animals",
                       'l':"family",
                       'bracketleft':"princesses",
                       'bracketright':"other_stuff",
            }
        if keysym in char2group:
            group = char2group[keysym]
        else:
            SlTrace.report(f"image command {keysym} is not available yet")
            return False
        
        return self.cmd_do_image(group=group)
        
    def clear_all(self):
        """ Clear screen
        """
        while not self.command_manager.command_stack.is_empty():
            self.command_manager.undo()

    def setup(self):
        """ Setup with pointer visible
        """
        self.x_cor = 0
        self.y_cor = 0
        self.heading = 0
        self.side = 100
        self.line_width = 4
        self.copy_move = "copy"
        self.set_newline()
        self.attr_chg = AttrChange()    # Setup attributes
        attr = Attribute("color", 
            ["red", "orange", "yellow", "green",
                "blue", "indigo", "violet"])
        self.attr_chg.add_attr(attr) 
        attr = Attribute("shape", 
            ["line", "square", "triangle", "circle"])
        self.attr_chg.add_attr(attr) 
        self.set_drawing_mode(True)
        self.display_update()

    def do_cmd(self, cmd):
        """ Do command, first checking for 
        "universal" conditions, e.g. will the command
        collide with the edge.
        :cmd: command to execute
        :returns: result of command
                False if command could not be executed
        """
        next_loc = cmd.get_next_loc()
        if self.is_on_canvas(next_loc):
            return cmd.do_cmd()     # No change to cmd
        
        if self.adj_movement(cmd):
            return cmd.do_cmd()     # Executed changed
        
        return False                # Can't execute    

    def is_on_canvas(self, loc):
        """ Check if location is on canvas
        :loc: (x,y) location (0,0) is center
        """
        x,y = loc
        boundary = 10
        canvas = self.get_canvas()
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if (x < -width/2 + boundary
             or x > width/2 - boundary
             or y < -height/2 + boundary
             or y > height/2 - boundary):
            return False 
        
        return True

    def adj_movement(self, cmd):
        """ Adjust cmd movement to keep on screen
        If at an angle( not 90 deg) to edge - "bounce" off
        at -angle
        If at 90 deg to edge "bounce" off at 90 deg but
        displaced by size toward free side.
        """
        boundary = cmd.get_side()/2
        heading = cmd.get_heading()
        theta = math.radians(heading)
        xchg = math.cos(theta)
        ychg = math.sin(theta)
        loc = cmd.get_next_loc()
        x,y = loc
        canvas = self.get_canvas()
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        x_edge = False 
        y_edge = False
        SlTrace.lg(f"adj: heading({heading:.1f} xchg={xchg:.2f} ychg={ychg:.2f}") 
        
        if x < -width/2 + boundary:
            x_edge = True 
            new_xchg = -xchg
        elif x > width/2 - boundary:
            x_edge = True 
            new_xchg = -xchg
        else:
            new_xchg = xchg
        if y < -height/2 + boundary:
            y_edge = True 
            new_ychg = -ychg
        elif y > height/2 - boundary:
            y_edge = True 
            new_ychg = -ychg
        else:
            new_ychg = ychg
            
        if not x_edge and not y_edge:
            return True         # OK - No adjustment required

        if abs(new_ychg) < 1e-9:
            SlTrace.lg(f"new_ychg == 0: y_cor: {cmd.get_y_cor()}")
            new_y_cor = cmd.get_y_cor()+cmd.get_side()
            if new_y_cor < -height/2 + boundary:
                new_y_cor = height/2 - boundary
            elif new_y_cor > height/2 - boundary:
                new_y_cor = -height/2 + boundary
            
            cmd.set_y_cor(new_y_cor)
            new_heading = heading+180    # more TBD
        elif abs(new_xchg) < 1e-9:
            SlTrace.lg(f"new_xchg == 0: x_cor: {cmd.get_x_cor()}")
            new_x_cor = cmd.get_x_cor()+cmd.get_side()
            SlTrace.lg(f"new_ychg == 0: y_cor: {cmd.get_y_cor()}")
            new_x_cor = cmd.get_x_cor()+cmd.get_side()
            if new_x_cor < -height/2 + boundary:
                new_x_cor = height/2 - boundary
            elif new_x_cor > height/2 - boundary:
                new_x_cor = -height/2 + boundary
            cmd.set_x_cor(new_x_cor)
            new_heading = heading+180    # at more TBD
        else:
            new_theta = math.atan2(new_ychg, new_xchg)
            new_heading = math.degrees(new_theta)
        cmd.set_heading(new_heading)
        SlTrace.lg(f"adj: new: heading({new_heading:.2f}"
                   f" xchg={new_xchg:.2f} ychg={new_ychg:.2f}")
        SlTrace.lg(f"    new loc: {cmd.get_x_cor():.1f},"
                   f" {cmd.get_y_cor():.1f}") 
        return True   
                          
    def cmd_do_trace(self, keysym):
        self.drawer.dotrace()
        
    def cmd_redo(self, keysym):
        return self.command_manager.redo()

    def cmd_repeat(self, keysym):
        cmd = self.command_manager.get_repeat()
        if cmd is None:
            return False 
        
        return self.do_cmd(cmd)

    def cmd_undo(self, keysym=None):
        return self.command_manager.undo()
        
    def cmd_visibility_adjust(self, keysym):
        """ Adjust visibility
            minus - penup
            plus = pendown
        """
        sym_to_pen_desc = {'minus':"penup",
                           'plus':"pendown"}
        if keysym not in sym_to_pen_desc:
            SlTrace.report(
                f"Not a recognized pen descripiton keysym: {keysym}")
            return False 
        
        marker = DmPen(self, keysym)
        cmd = DrawingCommand(f"cmd_{keysym}")
        cmd.add_marker(marker)
        return cmd.do_cmd()

    def cmd_size_adjust(self, keysym):
        """ Adjust marker size
            a - reduce length
            q - increase length
            t - widen line
            r - narrow line
        """
        len_mult = 1.2
        min_width = 2
        width_mult = 1.3
        sym_to_size = {'a','q','t','r'}
        if keysym not in sym_to_size:
            SlTrace.report(
                f"Not a recognized size descripiton keysym:{keysym}")
            return False

        side = self.get_side()
        width = self.get_width()            
        new_side = new_width = None     # Set, if changed 
        if keysym == 'a':
            new_side = side / len_mult
        elif keysym == 'q':
            new_side = side * len_mult
        elif keysym == 'r':
            if width <= min_width:
                return False
             
            new_width = width/width_mult
        elif keysym == 't':
            new_width = width*width_mult
        else:
            raise SelectError(f"Unrecognized resize cmd: {keysym}")
        
        cmd_last = self.last_marker_command()
        marker_last = self.last_marker()
        if marker_last is None:
            marker = DmSize(self, side=new_side,
                            line_width=new_width)
            cmd = DrawingCommand(f"cmd_{keysym}")
            cmd.add_markers(marker)
        else:
            #self.undo_last_marker_command() # undo to last marker
            ###cmd = cmd_last.reverse_copy()
            cmd = DrawingCommand(f"cmd_{keysym}")
            marker = marker_last
            marker = marker.use_locale(marker_last)
            marker = marker.change(side=new_side,
                                   line_width=new_width)
            cmd.add_prev_markers(marker_last)
            cmd.add_markers(marker)

        return cmd.do_cmd()

    def shorten(self):
        self.cmd_size_adjust('a')
        
    def lengthen(self):
        self.cmd_size_adjust('q')
        
    def widen(self):
        self.cmd_size_adjust('t')
        
    def narrow(self):
        self.cmd_size_adjust('x') 
           
    def cmd_set_color(self, color=None):
        """ Set color
        :color: color to set
        """
        cmd = DrawingCommand(f"cmd_color")
        marker = DmColor(self, color=color)
        cmd.add_marker(marker)
        return cmd.do_cmd()

    def cmd_set_marker_type(self, marker_type=None):
        """ Set marker type
        :marker_type: marker description:
        """
        cmd = DrawingCommand(f"cmd_marker")
        marker = DmAttributes(self, marker_type=marker_type)
        cmd.add_marker(marker)
        return cmd.do_cmd()

    def cmd_set_shape_type(self, shape_type=None):
        """ Set shape type
        :shape_type: shape description:
        """
        cmd = DrawingCommand(f"cmd_shape")
        marker = DmAttributes(self, shape_type=shape_type)
        cmd.add_marker(marker)
        return cmd.do_cmd()

    def cmd_set_line(self, length_str=None, width_str=None):
        """ Set line(or other shape) length, width
        :side: length of line
                default: no change
        :line_width: width of line
                default: no change
        """
        cmd = DrawingCommand(f"cmd_size")
        marker = DmSize(self, side=float(length_str),
                         line_width=float(width_str))
        cmd.add_marker(marker)
        return cmd.do_cmd()

    def cmd_rotate(self, keysym):
        """ Create current shape
        :keysym: key
            / - Rotate between shapes in place
            TBD - other direction...
         """
        if keysym == 'slash':
            heading_chg = 45
        
            cmd_last = self.last_marker_command()
            marker_last = self.last_marker()
            if marker_last is None:
                new_heading = self.get_heading() + heading_chg
                marker = DmHeading(self, heading=new_heading)
                cmd = DrawingCommand(f"cmd_{keysym}")
                cmd.add_markers(marker)
            else:
                self.undo_last_marker_command() # undo to last marker
                cmd = DrawingCommand(f"cmd_{keysym}")
                marker = marker_last.copy()
                marker = marker.use_locale(marker_last)
                new_heading = marker.get_heading()+heading_chg
                marker = marker.change(heading=new_heading)
                cmd.add_markers(marker)

        return cmd.do_cmd()
        
        SlTrace.report(f"Unrecognized rotate command: {keysym}")

    def cmd_do_image(self, group=None, file=None):
        """ Create a specified image
        :group: image file group, e.g., animals
        :file: image file, if one first match
                default: next
        """
        cmd_last = self.last_command()
        if cmd_last is None:
            cmd = DrawingCommand(f"cmd_image")
            marker = self.make_image(group=group, file=file)
            cmd.add_markers(marker)
        else:
            marker_last = self.last_command_marker()
            cmd = DrawingCommand(f"cmd_image")
            marker = self.make_image(group=group, file=file)
            if marker_last is not None:
                if marker_last.is_visible():
                    self.cmd_undo() # Change in-place
                marker = marker.use_locale(marker_last)
            cmd.add_markers(marker)
        return cmd.do_cmd()

    def cmd_do_shape(self, shape_type):
        """ Create a specified shape
        :shape_type: "line", "square", ...
        """
        cmd_last = self.last_command()
        new_color = self.get_next("color")
        if cmd_last is None:
            cmd = DrawingCommand(f"cmd_{shape_type}")
            marker = self.make_shape(shape=shape_type)
            marker = marker.change(color=new_color)
            cmd.add_markers(marker)
        else:
            marker_last = self.last_command_marker()
            cmd = DrawingCommand(f"cmd_{shape_type}")
            marker = self.make_shape(shape=shape_type)
            if marker_last is not None:
                if marker_last.is_visible():
                    self.cmd_undo() # Change in-place
                marker = marker.use_locale(marker_last)
            marker = marker.change(color=new_color)
            cmd.add_markers(marker)
        return cmd.do_cmd()

    def cmd_shapes(self, keysym):
        """ Create a shape
        :keysym: key
            s - Rotate between shapes in place
            d - OPEN
            f - set to "line" shape
        """
        if keysym == 's':
            new_shape_type = self.get_next("shape")
            return self.cmd_do_shape(shape_type=new_shape_type)
        
        elif keysym == "f":
            return self.cmd_do_shape(shape_type="line")
        
        elif keysym == "d":
            raise SelectError(f"Unused shapes cmd: {keysym}")
        
        raise SelectError(f"Unrecognized shapes cmd: {keysym}")

    def get_next(self, name):
        """ Get next attribute value
        :name: attribute name
        :return: attribute value
        """
        return self.attr_chg.get_next(name)

    def add_next_change_value(self, name, value, index=None):
        """ Add new value to attribute
        :name: attribute name
        :value: value to be added
        :index: index at which to add
                default: beginning of values list
        """
        self.attr_chg.add_value(name=name, value=value, index=index)
                                     
    def get_next_change(self, name):
        """ Get attribute change value, e.g. constant, ascending, ...
        :name: attribute name
        :return: attribute change setting
        """
        return self.attr_chg.get_next_change(name)
        


    def set_next_change(self, name=None, changes=None):
        """ set attribute changes
        :attr: attribute name
        :changes: attribute value
        """
        self.attr_chg.set_next_change(name=name, changes=changes)

    def make_image(self, group=None, file=None):
        """ Create genaric marker of given image
        :group: image group e.g. animals, family, ...
        :file: sub file name e.g. alex, first partial match
                default: next
        :returns: DmImage marker, None if none
        """
        image_file = self.get_image_file(group=group, file=file,
                                         next=True)
        if image_file is None:
            SlTrace.report(f"No image file group {group}"
                           f" groups: {self.image_group_names}")
            return False
        
        image_base = self.drawer.image_file_to_image(image_file)
        if image_base is None:
            raise SelectError(f"Can't get image from {image_file}")
        
        marker = DmImage(self, file=image_file,
                          image_base=image_base)
        return marker
        
        
    
    def make_shape(self, shape=None):
        """ Create generic marker of given type
        :shape: line, square, triangle, ...
        :returns: marker
        """
        if shape == "line":
            return DmLine(self)
       
        if shape == "square":
            return DmSquare(self)    

        if shape == "triangle":
            return DmTriangle(self)
        
        if shape == "circle":
            return DmCircle(self)
        
        raise SelectError(f"Can't create shape {shape}")
        
    def cmd_moveto(self, x_str, y_str):
        """ Move to x,y location
        :x: x coordinate
        :y: y coordinate
        """
        cmd = DrawingCommand(f"cmd_move")
        marker = DmPosition(self,
                             x_cor=float(x_str),
                             y_cor=float(y_str))
        cmd.add_marker(marker)
        return cmd.do_cmd()
        
                
    def cmd_newline(self, lines=None):
        """ Move to beginning of next line, invisibly
        force text mode
        """
        heading = self.get_heading()
        down_heading = heading - 90    # Down to next line
        theta = math.radians(down_heading)
        side = self.get_side()
        x_chg = side*math.cos(theta)
        y_chg = side*math.sin(theta)
        new_x = self.text_line_begin_x + x_chg
        new_y = self.text_line_begin_y + y_chg
        self.text_line_begin_y = new_y      # Update y offset
        cmd = DrawingCommand(f"cmd_newline")
        marker = DmPosition(self, x_cor=new_x, y_cor=new_y)
        cmd.add_marker(marker)
        self.set_text_mode()
        cmd.do_cmd()
        
    def cmd_position_adjust(self, keysym):
        """ Positioning commands
         c - center within screen
         m - move to some place ???
         Left - move to left
         Right - move to right
         Up - move up
         Down - move down
        Movement depends on previous command.
        1. If previous heading unchanged
            then move one side in current direction
        2. Else if previous marker is a line,shape or image
            then set heading and location that the
            next such object will be flush
            with the previous objec but have
            the new heading
         
        :keysym: key event keysym
        """
        if (keysym == "Up" or keysym == "Down"
               or keysym == "Left" or keysym == "Right"):
            prev_heading = self.get_heading()
            marker = DmMoveKey(self, keysym=keysym)
            new_heading = marker.get_heading()
            if new_heading != prev_heading:
                marker = DmHeading(self, heading=new_heading)
            cmd = DrawingCommand(f"cmd_{keysym}")
            cmd.add_marker(marker)
            SlTrace.lg(f"cmd={cmd}", "cmd_trace")
            return cmd.do_cmd() 

        if keysym == 'c':
            marker = DmPosition(self, x_cor=0, y_cor=0)
            cmd = DrawingCommand(f"cmd_{keysym}")
            cmd.add_marker(marker)
            return cmd.do_cmd()
        else:
            raise SelectError(f"Don't understand keysym:{keysym}")    
         
    def cmd_add_new_direction(self, keysym):
        """ Add copy of current marker/figure
         in new direction
            7 8 9 
            4 5 6
            1 2 4
              0
        """
        dig2head = {'6':0, '9':45, '8':90,
            '7':135, '4':180, '1':225,
            '2':270, '3':315, '6':0,
            }
        cur_heading = self.get_heading()
        if keysym == '0':
           new_heading = cur_heading - 45
        elif keysym == '5':
            new_heading = cur_heading + 45 
        elif keysym not in dig2head:
            SlTrace.report(f"{keysym} is not a recogized new direction")
            return False 
        else:
            new_heading = dig2head[keysym]        

        cmd_last = self.last_marker_command()
        marker_last = self.last_marker()
        cmd = DrawingCommand(f"cmd_{keysym}")
        if marker_last is None:
            new_color = self.get_next("color")
            new_shape_type = self.get_next("shape")
            marker = self.make_shape(shape=new_shape_type)
            marker = marker.change(
                               color=new_color,
                               heading=new_heading)
        else:
            color_change = self.get_next_change("color")
            if color_change != "constant":
                new_color = self.get_next("color")
            else:
                new_color = None    # No change - maybe special
                
            marker = marker_last.copy()
            x_cor, y_cor = marker_last.get_next_loc()
            marker = marker.change(x_cor=x_cor, y_cor=y_cor,
                                   color=new_color,
                                   heading=new_heading)
        cmd.add_markers(marker)
            
        return self.do_cmd(cmd)


    def insert_markers(self, markers):
        """ Insert markers to display
        Update location to final marker's next location 
        :markers: list of markers(DrawMarker) to be removed
        """
        for marker in markers:
            marker.draw()


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
        
    ''' OBSOLETE VERSION    
    def display_update(self, cmd=None):
        """ Update current display
        """
        if cmd is None:
            cmd = self.last_command()
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
        self.drawer.master.update()
        '''

    def display_update(self, cmd=None):
        """ Update current display
        """
        if cmd is None:
            cmd = self.last_command()
        if cmd is not None:
            SlTrace.lg(f"display_update:{cmd}", "display_update")
            self.remove_markers(cmd.prev_markers)
            self.insert_markers(cmd.new_markers)
            new_loc = cmd.get_next_loc()
            if new_loc is None:
                cmd.set_next_loc()       # Default command new location
            heading = cmd.get_heading()
            x_cor, y_cor = cmd.get_next_loc()
            side = cmd.get_side()
            self.set_side(side)
            copy_move = cmd.get_copy_move()
            self.set_copy_move(copy_move)
        else:
            x_cor, y_cor = self.get_loc()
            heading = self.get_heading()
        self.set_heading(heading)
        if self.cmd_pointer is not None:
            self.cmd_pointer.undraw()
        self.set_loc(x_cor,y_cor)
        self.cmd_pointer = DmPointer(self, x_cor=x_cor,
                                     y_cor=y_cor,
                                     heading=heading)
        self.cmd_pointer.draw()
        self.drawer.master.update()

    def set_color(self, color):
        self.color = color

    def cmd_get_loc(self):
        """ Get current location
        :returns: (x_cor, y_cor)
        """
        return (self.x_cor, self.y_cor)
        
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
        self.line_width = line_width


    def set_size(self, side=None, line_width=None):
        if side is not None:
            self.set_side(side)
        if line_width is not None:
            self.set_width(line_width)

    def set_pen(self, pen_desc="down"):
        self.pen_desc = pen_desc

    def get_marker_type(self):
        return self.marker_type
    
    def set_marker_type(self, marker_type):
        self.marker_type = marker_type

    def get_shape_type(self):
        return self.shape_type
    
    def set_shape_type(self, shape_type):
        self.shape_type = shape_type

    def set_drawing_mode(self, keysym=None, force=False):
        """ Set figure drawing mode
        :force: force operation
                default: only operate if not already drawing
        """
        if not self.is_drawing or force:
            self.is_drawing = True
            self.set_key_images(show=True) 

    def set_key_images(self, show=False):
        if hasattr(self.drawer, "screen_Keyboard"):
            self.drawer.screen_keyboard.set_images(show=show)

    def set_text_mode(self, keysym=None, force=False):
        """ Set text mode
        :force: if True force operation, not testing
                default: Only operate if not is_drawing
        """
        if self.is_drawing:
            self.is_drawing = False 
            self.set_key_images(show=False)

    def set_newline(self, x_cor=None, y_cor=None):
        """ Set curret location as line beginning
        to be used by jump_to_next_line
        set to text mode if not alreaty there
        :x_cor: x_cor default= current x_cor
        :y_cor: y_cor default= current y_cor
        """
        
        if x_cor is None or x_cor == "":
            x_cor = self.get_x_cor()
        if x_cor is str:
            x_cor = float(x_cor)
        self.text_line_begin_x = x_cor
        if y_cor is None or y_cor == "":
            y_cor = self.get_y_cor()
        if y_cor is str:
            x_cor = float(y_cor)
        self.text_line_begin_y = y_cor
        self.set_text_mode()
        
    def get_canvas(self):
        """ Get our working canvas
        """
        return self.drawer.get_canvas()


    def last_command(self):
        return self.command_manager.last_command()

    def last_command_marker(self):
        """ get last command's last marker, if one
        :returns: marker else None
        """
        cmd = self.last_command()
        if cmd is None:
            return None 
        
        if len(cmd.new_markers) == 0:
            return None 
        
        return cmd.new_markers[-1]

    def last_marker_command(self):
        """ get most recently executed "marker" command
        shape, image, etc. visible which makes sense to 
        repeat on the screen
        :returns: command or None if none
        """
        cmds = self.command_manager.command_stack.get_cmds()
        for cmd in reversed(cmds):
            if len(cmd.new_markers) == 0:
                SlTrace.lg(f"last_marker_command - no markers")
                continue
            for marker in cmd.new_markers:
                if marker.is_visible():
                    if SlTrace.trace("last_marker"):
                        SlTrace.lg(f"last_marker_command: {cmd}")
                    return cmd
                SlTrace.lg(f"last_marker_command not visible {cmd}")
        return None 

    def undo_last_marker_command(self):
        """ remove to last "marker" command, if found
        shape, image, etc. visible which makes sense to 
        repeat on the screen
        :returns: True if found
                    False if not found
        """
        found_marker = False
        back_count = 0
        cmds = self.command_manager.command_stack.get_cmds()
        for cmd in reversed(cmds):
            if len(cmd.new_markers) == 0:
                back_count += 1
                continue
            for marker in cmd.new_markers:
                if marker.is_visible():
                    found_marker = True
                    break
            back_count += 1
            if found_marker:
                break
                
        if found_marker:
            for _ in range(back_count):
                self.command_manager.undo()
            return True 
        
        return False

    def last_marker(self):
        """ Get most recent marker command's marker
        """
        cmd = self.last_marker_command()
        if cmd is None:
            return None
        
        for marker in reversed(cmd.new_markers):
            if marker.is_visible():
                return marker
            
        return None 
        
    def get_heading(self):
        return self.heading

    def get_x_cor(self):
        return self.x_cor

    def get_y_cor(self):
        return self.y_cor

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

    def select_print(self, tag, trace=None):
        """ Print select select state
        """
        return self.drawer.select_print(tag, trace=trace)

    def next_color(self):
        return self.get_next("color")
    
    
if __name__ == "__main__":
    from tkinter import *
    from keyboard_draw import KeyboardDraw
    root = Tk()
    
    kb_draw = KeyboardDraw(root,  title="Testing KbdCmdProc",
                show_help=False,        # No initial help
                with_screen_kbd=False,   # No screen keyboard
                )
    kb_draw.color_current = "w"
    
    kcp = KbdCmdProc(kb_draw)
    kcp.help()
    kcp.set_loc(-300,0)
    
    root.mainloop()   
        