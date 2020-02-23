# select_kbd_cmd.py
"""
Support for keyboard commands / input
Mostly for debugging / analysis while over the game canvas
"""
import os
import sys
from tkinter import *

from select_trace import SlTrace
from select_error import SelectError
from _ast import Num


class SelectKbdCmd:
    
    def __init__(self, game_control):
        """ Setup linking keyboard input
        """
        self.game_control = game_control
        self.mw = game_control.mw           # Shorten access to mw
        self.mw.bind("<KeyPress>", self.key_press)
        self.mw.bind("<KeyRelease>", self.key_release)
        self.kbd_input_flag = False           # In kbd_input gathering
        self.gr_input_top_win = None       # Set if input
        self.keycmd_edge_mark = None        # Current marker edge
        """ Keyboard command control
        """
        self.keycmd_edge = False
        self.keycmd_args = []
        self.multi_key_cmd_str = None       # Current multi key cmd str
        canvas = self.get_canvas()
        if hasattr(canvas, "set_game_control"):
            canvas.set_game_control(game_control)  # hook to info


    def beep(self):
        self.game_control.beep
        

    def get_start_track(self):
        return self.get_canvas().get_start_track()

    
    def set_start_track(self, num=None):
        self.get_canvas().set_start_track(num=num)
        
        
    def get_canvas(self):
        return self.game_control.get_canvas()


    def get_keycmd_edge(self):
        """ Get current marker direction, (row, col)
        """
        ####edge = self.keycmd_edge_mark
        edge = self.game_control.get_selected_part()
        if edge is None:
            edge = self.get_part(type="edge", sub_type="h", row=1, col=1)
        return edge


    def get_keycmd_marker(self):
        """ Get current marker direction, (row, col)
        """
        edge = self.get_keycmd_edge()
        dir = edge.sub_type()
        row = edge.row 
        col = edge.col
        return dir, [row,col]


    def get_part(self, id=None, type=None, sub_type=None, row=None, col=None):
        """ Get basic part
        :id: unique part id
        :returns: part, None if not found
        """
        return self.game_control.get_part(id=id, type=type, sub_type=sub_type, row=row, col=col)

    def get_part_from_tags(self, tags):
        for tag in tags:
            if tag.startswith("part:"):
                match = re.search(r'id:(\d+)', tag)
                if match:
                    part_id = int(match.group(1))
                    return self.get_part(part_id)
        return None
    
    
    def update_keycmd_edge_mark(self, prev_edge_mark, new_edge_mark):
        """ Update edge mark
        :prev_edge_mark:  previous edge mark None if none
        :new_edge_mark:   new edge mark, None if none
        """
        if prev_edge_mark is not None:
            prev_edge_mark.highlight_clear()
        if new_edge_mark is not None:
            new_edge_mark.highlight_set()
        self.keycmd_edge_mark = new_edge_mark


    def key_press(self, event):
        if self.kbd_input_flag:
            self.kbd_input_add_char(event.char)
            return
        
        self.key_press_event(event)
            

    def key_release(self, event):
        """ Keyboard key release processor
        """
        SlTrace.lg("key_release %s" % event.char, "keybd")


    def key_press_event(self, event):
        """ Keyboard key press processor
        """
        if False and not SlTrace.trace("keycmd"):
            return
        
        ec = event.char
        ec_code = event.keycode
        ec_keysym = event.keysym
        self.key_press_cmd(ec, ec_code, ec_keysym)

        
    def key_press_cmd(self, ec=None,
                      ec_code=None,
                      ec_keysym=None):
        """ Keyboard key press / command processor
        """
        if ec is None:
            ec = -1
        if ec_code is None:
            ec_code = -1
        if ec_keysym is None:
            ec_keysym = "NA"
        SlTrace.lg("key press: '%s' %s(x%02X)" % (ec, ec_keysym, ec_code))
        if self.multi_key_cmd is None:
            if ec_keysym == "m":
                self.multi_key_cmd_str = ec_keysym
        if self.multi_key_cmd_str is not None:
            if ec_keysym == ";" or ec_keysym == " " or ec_keysym == "Return":
                self.multi_key_cmd()
                return
            
            self.multi_key_cmd_str += ec_keysym
            return
            
        if SlTrace.trace("selected"):
            self.list_selected("key_press_cmd:" + ec_keysym)
        if ec == "j":       # Info (e.g. "i" for current edge position
            edge = self.get_keycmd_edge()
            if edge is None:
                self.beep()
                return
                
            SlTrace.lg("    %s\n%s" % (edge, edge.str_edges()))
            return

        if ec_keysym == "Return":
            edge = self.get_keycmd_edge()
            if edge is None:
                self.beep()
                return
            
            if edge.is_turned_on():
                self.beep()
                return
            
            edge.display_clear()
            self.game_control.make_new_edge(edge=edge, display=True)
            self.game_control.display_update()       # Ensure screen update
            return        
        
        if (ec_keysym == "Up"
                or ec_keysym == "Down"
                or ec_keysym == "Left"
                or ec_keysym == "Right"
                or ec_keysym == "plus"
                or ec_keysym == "minus"):
            res = self.keycmd_move_edge(ec_keysym)
            return res
        

        if self.keycmd_edge:
            try:
                arg = int(ec)
            except:
                self.keycmd_edge = False
                return
            
            self.keycmd_args.append(arg)
            if len(self.keycmd_args) >= 2:
                self.make_new_edge(dir=self.keycmd_edge_dir, rowcols=self.keycmd_args)
                self.keycmd_edge = False
            return

        if ec_keysym == "h":        # Help
            SlTrace.lg("""
            space - Add multiline blank delimiter
            a - add delimiter with one line of text
            b - list blinking parts
            c - clear current part display
            d - (re)display current part
            f - rurn current part off
            h - Output this help listing
            i - list part, edges of current location
            j - List edge at current edge position
            k - cmds at top of cmd stack
            g - List on square(s) touching current edge
            l - List highlighted parts
            n - turn on current part
            
            r - redo undone command
            s - list selected parts
            t - list parts that are turned on
            v - set current edge
            Selection movement directions:
                UP
                Down
                Left
                Right
                "plus" - rotate selection clockwise
                "minus" - rotate selection counter clockwise
            ; - multi character command
             c[anvas] pattern - list canvas objects with tag "ALL" - all canvas objects
             e[dge] (h/v) row col - display edge (horizontal,vertical) at row, col
                 e.g.  ; e h 1 2  - horizontal edge at row==1, col==2
             g(region) row col - display region at row, col
             p[part] pattern - List parts with tag, default all parts (one entry per part)
             r[ecord] pattern - Trace canvas rectangles with any tag matching pattern
             s[tart] number[current] - start(restart) looking at tracking number
             d[elete] pattern(default .*) delete canvas objects
             
             <cmd>[s]t=[<stack_length>][:<stack_bottom>]] Add stack listing
                 <stack_length> - number of levels listed default: 2
                 <stack_bottom> - bottom of stack listed (0-most recent) default: 2 above
                 Examples:  pt=5 - to parts add stack list of 5 levels
                             pt= - add default stack list to parts
                             pt=6:3 - add stack 6 levels, omitting 3 lowest levels
            """)
            return

        if ec_keysym == "space":
            SlTrace.lg("_" * 50 + "\n\n\n")
            return
        
        if ec_keysym == "a":
            SlTrace.lg("_" * 50 + "\n\n\n")
            annotation = self.kbd_input("Enter annotation:")
            SlTrace.lg(annotation)
            return
       
                
        if ec_keysym == "b":    # List "Blinking" parts
            self.list_blinking("blinking")

        if ec_keysym == "k":    # cmds at top of stack
            self.game_control.command_manager.list_stack()
            
        if ec_keysym == "l":
            part_ids = list(self.game_control.board.area.highlights)
            SlTrace.lg("Highlighted parts(%d):" % len(part_ids))
            for part_id in part_ids:
                part = self.get_part(id=part_id)
                SlTrace.lg("    %s" % part)
            return

        if ec_keysym == "s":        # List those selected
            self.list_selected()
            return

        if ec_keysym == "t":        # List those turned on
            part_ids = list(self.game_control.board.area.parts_by_id)
            n_on = 0
            for part_id in part_ids:
                part = self.get_part(id=part_id)
                if part.is_turned_on():
                    n_on += 1
            SlTrace.lg("parts turned on(%d of %d):" % (n_on, len(part_ids)))
            for part_id in part_ids:
                part = self.get_part(id=part_id)
                if part.is_turned_on():
                    SlTrace.lg("    %s" % part)
            return

            
        if ec == "v":
            self.keycmd_edge = True
            self.keycmd_edge_dir = ec
            self.keycmd_args = []
            return
        
        if ec == "r":
            self.game_control.redo()
            return
        
        if ec_keysym == "g":       # Do info on squares(regions) touching current edge
            edge = self.get_keycmd_edge()
            SlTrace.lg("%s" % edge.str_adjacents())
            return
        
        if ec_keysym == "u":
            self.game_control.undo()
            return
        
        if ec_keysym == "semicolon":
            import re
            kbd_cmd_str = self.kbd_input("Enter cmd:").strip()
            SlTrace.lg("kbd_cmd: %s" % kbd_cmd_str)
            kbd_args = re.split(r'\s+|(?:\s*,\s*)|(?:\s*\(\s*)|(?:\s*\)\s*)', kbd_cmd_str)
            kbd_cmd = kbd_args.pop(0)
            stack_trace = False     # Default stack trace
            stack_len = 2           # number of stack entries listed
            stack_bottom = 0       #  lowest (most recent) listed -0 -> to most recent, 1 next most recent
            stack_match = re.search(r'(?:s?)t=(\d+)?(?::(\d+))?', kbd_cmd.lower())
            if stack_match:
                stack_trace = True
                len_str = stack_match.group(1)
                if len_str:
                    stack_len = int(len_str)
                end_str = stack_match.group(2)
                if end_str:
                    stack_bottom = -int(end_str)
            stack_end = -stack_bottom-1
            stack_begin = stack_end-stack_len
            if kbd_cmd.lower().startswith("c"):
                canvas = self.get_canvas()
                if len(kbd_args) > 0:
                    pat = kbd_args[0]
                else:
                    pat = ".*"
                items = canvas.get_tracked()
                matching_ids = []
                for item in items:
                    (rec_id, track_no, call_stack) = item
                    tags = canvas.gettags(rec_id)
                    for tag in tags:
                        if re.match(pat, tag):
                            matching_ids.append(rec_id)
                            break
                SlTrace.lg("canvas %s: %s" % (pat, matching_ids))
            elif kbd_cmd.lower().startswith("d"):   # delete items
                canvas = self.get_canvas()
                if len(kbd_args) > 0:
                    pat = kbd_args[0]
                else:
                    pat = ".*"
                items = canvas.get_tracked()
                for item in items:
                    (rec_id, track_no, call_stack) = item
                    tags = canvas.gettags(rec_id)
                    for tag in tags:
                        SlTrace.lg("tag:%s" % tag)
                        if re.match(pat, tag):
                            SlTrace.lg("deleting: %s: %s" % (tags, rec_id))
                            canvas.delete(rec_id)
                            break
            elif kbd_cmd.lower().startswith("e"):
                try:
                    edge_dir = kbd_args[0]
                    row = int(kbd_args[1])
                    col = int(kbd_args[2])
                    part = self.get_part(type="edge", sub_type=edge_dir, row=row, col=col)
                    if part is None:
                        raise SelectError(f"Unrecognized command {kbd_cmd_str}")
                    else:
                        SlTrace.lg(f"part: {part}")
                except:
                    SlTrace.lg("Command format: e, [hv], row, col")
            elif kbd_cmd.lower().startswith("g"):
                try:
                    row = int(kbd_args[0])
                    col = int(kbd_args[1])
                    part = self.get_part(type="region", row=row, col=col)
                    if part is None:
                        raise SelectError(f"Unrecognized command {kbd_cmd_str}")
                    else:
                        SlTrace.lg(f"part: {part}")
                except:
                    SlTrace.lg("Command format: e, [hv], row, col")
            elif kbd_cmd.lower().startswith("p"):
                canvas = self.get_canvas()
                if len(kbd_args) > 0:
                    pat = kbd_args[0]
                else:
                    pat = ".*"
                items = canvas.get_tracked()
                matching_parts_by_id = {}
                for item in items:
                    (rec_id, stack_no, stack) = item
                    tags = canvas.gettags(rec_id)
                    part = self.get_part_from_tags(tags)
                    if part is None:
                        continue
                    part_str = str(part)
                    found = re.search(pat, part_str)
                    if found:
                        part_item = (part, item)
                        if part.part_id not in matching_parts_by_id:
                            matching_parts_by_id[part.part_id] = []     # Create list of tags
                        matching_parts_by_id[part.part_id].append(part_item)
                SlTrace.lg("parts pat:%s" % (pat))
                for part_id, part_item_list in matching_parts_by_id.items():
                    part = self.get_part(part_id)
                    SlTrace.lg("    %d (%d parts)" % (part.part_id, len(part_item_list)))
                    for part_item in part_item_list:
                        part, item = part_item
                        rec_id, track_no, stack = item
                        tags = canvas.gettags(rec_id)
                        pt = self.get_part_from_tags(tags)
                        SlTrace.lg("        %d %s %s" % (rec_id, track_no, pt))
                        if stack_trace:
                            rec_id, stack_no, stack = item
                            canvas.trace_item(prefix="        ", rec_id=rec_id,
                                              begin=stack_begin,
                                              end=stack_end)
                       
            elif kbd_cmd.lower().startswith("r"):   # trace rectangles
                canvas = self.get_canvas()
                if len(kbd_args) > 0:
                    pat = kbd_args[0]
                else:
                    pat = ".*"
                items = canvas.get_tracked()
                for item in items:
                    (rec_id, track_no, call_stack) = item
                    tags = canvas.gettags(rec_id)
                    for tag in tags:
                        if re.match(pat, tag):
                            canvas.trace_item(rec_id=rec_id)    
                            break
            
            elif kbd_cmd.lower().startswith("s"):   # start looking
                canvas = self.get_canvas()
                if len(kbd_args) > 0:
                    num = int(kbd_args[0])
                else:
                    num = self.get_start_track()
                    
                SlTrace.lg("Track no set to: %d" % num)
                self.set_start_track(num)
                            
            return
        
        
        x,y = self.game_control.get_xy()
        parts = self.game_control.get_parts_at(x,y)
        if parts:
            SlTrace.lg("x=%d y=%d" % (x,y))
            for part in parts:
                if ec == "i":
                    SlTrace.lg("    %s\n%s" % (part, part.str_edges()))
                elif ec == "d":
                    part.display()
                elif ec == "c":
                    part.display_clear()        # clear display
                elif ec == "n":                 # turn on
                    part.turn_on(player=self.game_control.get_player())
                elif ec == "f":                 # turn off
                    part.turn_off()


    def kbd_input(self, prompt=None):
        """ Get line from graphics window
        """
        inp = self.gr_input(prompt)
        '''
        if prompt is not None:
            print(prompt, file=sys.stderr)
        self.kbd_input_str = ""
        self.kbd_input_flag = True
        while self.kbd_input_flag:
            self.mw.update_idletasks()
            self.mw.update()
            
        return self.kbd_input_str
        '''
        return inp
    
            
    def kbd_input_add_char(self, c):
        if c == "\r" or c == "\n":
            self.kbd_input_flag = False
            print("\n", sep="", end="", file=sys.stderr)
            return
        print(c, sep="", end="", file=sys.stderr)
        self.kbd_input_str += c
        
        
    def list_blinking(self, prefix=None):
        self.game_control.board.area.list_blinking(prefix=prefix)

    
    def list_selected(self, prefix=None):
        self.game_control.board.area.list_selected(prefix=prefix)


    def keycmd_move_edge(self, keysym):
        """ Adjust marker based on current marker state and latest keyboard input symbol
            User remains the same.
            Movement rules:
            1. If keysym is (up,down,left,right) new edge will retain the same orientation and
            move one row/colum in the direction specified by the keysym,
            keep the same direction and move one in the keysym direction.
            2. The new edge, wraps around to the opposite side, if the new loction is our of bounds.
            3. If the keysym is (plus,minus) the new edge will be +/- 90 degrees clockwize
            from the left corner of the original edge
            4. If the (plus,minus) rotation would place an edge outside the latice, the rotation is reversed. 
             
        :keysym:  keyboard key symbol(up,down,left,right,plus,minus) specifying the location of the new edge
        """
        if SlTrace.trace("selected"):
            self.list_selected("keycmd_move_edge before:" + keysym)
        edge = self.get_keycmd_edge()
        edge_dir = edge.sub_type()
        next_dir = edge_dir
        next_row = edge.row 
        next_col = edge.col 

        if keysym == "plus":
            if edge_dir == "h":
                next_dir = "v"
            else:
                next_dir = "h"
                next_col -= 1
        elif keysym == "minus":
            if edge_dir == "h":
                next_dir = "v"
                next_row -= 1
            else:
                next_dir = "h"
        elif keysym == "Up":
            next_row -= 1
        elif keysym == "Down":
            next_row += 1
        elif keysym == "Left":
            next_col -= 1
        elif keysym == "Right":
            next_col += 1

        if next_row < 1:
            next_row = self.game_control.board.nrows
        if (next_row > self.game_control.board.nrows+1
             or (next_row > self.game_control.board.nrows
                  and next_dir == "v")):
            next_row = 1
        if next_col < 1:
            next_col = self.game_control.board.ncols
        if (next_col > self.game_control.board.ncols+1
             or (next_col > self.game_control.board.ncols
                  and next_dir == "h")):
            next_col = 1

        next_edge = self.get_part(type="edge", sub_type=next_dir, row=next_row, col=next_col)
        SlTrace.lg("keycmd_move_edge edge(%s) row=%d, col=%d"
                   % (next_dir, next_row, next_col))
        if next_edge is None:
            raise SelectError("keycmd_move_edge no edge(%s) row=%d, col=%d"
                              % (next_dir, next_row, next_col))
        self.move_edge_cmd(edge, next_edge)


    def move_edge_cmd(self, edge, next_edge):
        """ Move between edges cmd
         - change selection
        :edge: current edge
        :next_edge: new edge
        """
        if SlTrace.trace("track_move_edge"):
            SlTrace.lg("before move_edge_cmd:\nedge:%s\nnext_edge:%s"
                       % (edge, next_edge), "track_move_edge")
        self.game_control.cmd_select(next_edge, display=True)
        if SlTrace.trace("track_move_edge"):
            SlTrace.lg("after move_edge_cmd:\nedge:%s\nnext_edge:%s"
                       % (edge, next_edge), "track_move_edge")


    def multi_key_cmd(self):
        """ Execute multi-key command
        """
        if self.multi_key_cmd_str == "md":  """ Display all parts """


    def gr_input(self, prompt="Enter"):
        """ Get input (line) from canvas, via entry window
        """
            
        def ok_cmd():
            """ Function called  upon "OK" button
            <return> simulates "OK"
            """
            self.gr_input_entry_text = self.gr_input_entry_var.get()    # Retrieve
            self.gr_input_reading = False
            
            
        def on_return_cmd(event=None):
            ok_cmd()
           
            
        if self.gr_input_top_win is None:
            self.gr_input_entry_var = StringVar() # Holds the entry text
            self.gr_input_top_win = Toplevel(self.mw)
            mw = self.gr_input_top_win
            label = Label(mw, text=prompt)    # Create Label with prompt
            label.pack(side=LEFT)
        
            entry = Entry(mw, textvariable=self.gr_input_entry_var, bd=3)        # Create Entry space on right
            entry.pack(side=LEFT, expand=True, fill=BOTH)
            entry.bind('<Return>', on_return_cmd)
            button = Button(mw, text="OK", command=ok_cmd, fg="blue", bg="light gray")
            button.pack(side=RIGHT)
            self.entry = entry
        self.gr_input_entry_var.set("")
        self.entry.focus_set()
        self.gr_input_reading = True    
        while self.gr_input_reading:
            ###self.mw.update_idletasks()
            self.mw.update()
        self.gr_input_top_win.destroy()                    # Close window
        self.gr_input_top_win = None                # Clear it
        return self.gr_input_entry_text
        