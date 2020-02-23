# select_play_cmd.py
""" Process command stream commands
"""
import re

from select_trace import SlTrace
from select_error import SelectError
from select_stream_command import SelectStreamCmd

class SelectPlayCommand:
    
    def __init__(self, play_control, command_stream):
        """ Setup command processing
        :play_conrol: SelectPlay control instance
        :command_stream: (SelectCommandFileControl) command stream access
        """
        self.play_control = play_control
        self.command_stream = command_stream
        self.stack_trace = True     # force values
        self.stack_begin = -8
        self.stack_end = -2

        
    def do_stcmd(self, stcmd):
        """ Execute play command
        :stcmd: command (py)
        :returns: True if succesful
        """

        stcmd_name = stcmd.name    
        if SlTrace.trace("stcmd_list"):
            SlTrace.lg("    %s" % (stcmd))

        if stcmd_name == "execute_file":
            file_name = self.get_arg(stcmd, 1, "")            
            return self.play_control.cmd_stream.procFile(file_name)
        
        if stcmd_name == "lg":
            """ Version of Sl1Trace.lg(text[ flag_string})
            :args[0] text to log
            :args[1]: optional flag to enable logging default: log it
            """
            if len(stcmd.args) == 0:
                raise SelectError("Required text argument is missing")
            
            text = stcmd.args[0].str
            totrace = True              # Default - list
            if len(stcmd.args) >= 2:
                flag = stcmd.args[1].str
                if not SlTrace.trace(flag):
                    totrace = False
            if totrace:    
                SlTrace.lg(text)
            
            return True
        
        if stcmd_name == "doc_string":
            return True
        
        if stcmd_name == "enter":
            return self.do_stcmd_enter(stcmd)
        
        if stcmd_name == "set_level":
            """ pgm version of SlTrace.set_level(flag, level)
            """
            if len(stcmd.args) >= 1:
                flag = stcmd.args[0].str
            else:
                raise SelectError("Missing set_level flag arg")
            
            if len(stcmd.args) >= 2:
                level = int(stcmd.args[1].str)
            else:
                level = 1
                
            SlTrace.setLevel(flag, level)
            return True
        
            
        if (stcmd_name == "up"
                or stcmd_name == "down"
                or stcmd_name == "left"
                or stcmd_name == "right"
                or stcmd_name == "plus"
                or stcmd_name == "minus"):
            res = self.stcmd_move_edge(stcmd)
            return res

        if stcmd_name == "help":        # Help
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
            return True

        if stcmd_name == "space":
            """ List separator
            :args[0]: optional annotation text if present
            """
            SlTrace.lg("_" * 50 + "\n\n\n")
            if len(stcmd.args) >= 1:
                SlTrace.lg(stcmd.args[0].str)
            return True
       
                
        if stcmd_name == "blinking":    # List "Blinking" parts
            self.list_blinking("blinking")
            return True
                
        if stcmd_name == "stack":    # cmds at top of stack
            self.play_control.command_manager.list_stack()
            
        if stcmd_name == "lighted":
            part_ids = list(self.play_control.board.area.highlights)
            SlTrace.lg("Highlighted parts(%d):" % len(part_ids))
            for part_id in part_ids:
                part = self.get_part(id=part_id)
                SlTrace.lg("    %s" % part)
            return True
        
        
        if stcmd_name =="select":
            return self.select(stcmd)

        if stcmd_name == "selected":        # List those selected
            self.list_selected()
            return True

        if stcmd_name == "turnedon":        # List those turned on
            part_ids = list(self.play_control.board.area.parts_by_id)
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

            
        if stcmd_name == "set_edge":
            return self.do_stcmd("enter")

        if stcmd_name == "set_playing":
            return self.set_playing(stcmd)
        
        if stcmd_name == "set_player":
            return self.set_player(stcmd)
        
                
        if stcmd_name == "redo":
            nt = 1
            if stcmd.args:
                nt = int(stcmd.args[0].str)
            for i in range(nt):
                res = self.play_control.redo()
                if not res:
                    break
            return res
        
        if stcmd_name == "info":       # Do info on squares(regions) touching current edge
            edge = self.get_keycmd_edge()
            SlTrace.lg("%s" % edge.str_adjacents())
            return True 
        
        
        if stcmd_name == "undo":
            nt = 1
            if stcmd.args:
                nt = int(stcmd.args[0].str)
            for i in range(nt):
                res = self.play_control.undo()
                if not res:
                    break
            return res
        
        
        if stcmd_name == "canvas":
            canvas = self.get_canvas()
            if len(stcmd.args) >= 1:
                pat = stcmd.args[0].str
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
            return True
        
        if stcmd_name == "delete":
            canvas = self.get_canvas()
            if len(stcmd.args) >= 1:
                pat = stcmd.args[0].str
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
            return True        
                    
        if stcmd_name == "parts":
            canvas = self.get_canvas()
            if len(stcmd.args) >= 1:
                pat = stcmd.args[0].str
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
                    if self.stack_trace:
                        rec_id, stack_no, stack = item
                        canvas.trace_item(prefix="        ", rec_id=rec_id,
                                          begin=self.stack_begin,
                                          end=self.stack_end)
            return True
                   
        if stcmd_name == "parts":
            canvas = self.get_canvas()
            if len(stcmd.args) >= 1:
                pat = stcmd.args[0].str
            else:
                pat = ".*"
            items = canvas.get_tracked()
            return False        # TBD
            
        if stcmd_name == "rectangles":
            canvas = self.get_canvas()
            if len(stcmd.args) >= 1:
                pat = stcmd.args[0].str
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
            return True
        
        if stcmd_name == "set_start":
            canvas = self.get_canvas()
            if len(stcmd.args) >= 1:
                num = int(stcmd.args[0].str)
            else:
                num = self.get_start_track()
                canvas = self.get_canvas()
                    
                SlTrace.lg("Track no set to: %d" % num)
                self.set_start_track(num)
                            
            return True
        
        if stcmd_name == "stack":
            self.play_control.command_manager.list_stack()
            return True
        
        raise SelectError("Unsuported command %s" % stcmd)
        return False
        
        
    def list_blinking(self, prefix=None):
        self.play_control.board.area.list_blinking(prefix=prefix)

    
    def list_selected(self, prefix=None):
        self.play_control.board.area.list_selected(prefix=prefix)


    def stcmd_move_edge(self, stcmd):
        """ Adjust marker based on current marker state and latest keyboard input symbol
            User remains the same.
            Movement rules:
            1. If stc_name is (up,down,left,right) new edge will retain the same orientation and
            move one row/colum in the direction specified by the stc_name,
            keep the same direction and move one in the stc_name direction.
            2. The new edge, wraps around to the opposite side, if the new loction is our of bounds.
            3. If the stc_name is (plus,minus) the new edge will be +/- 90 degrees clockwize
            from the left corner of the original edge
            4. If the (plus,minus) rotation would place an edge outside the latice, the rotation is reversed. 
             
        :stcmd.name:  command (up,down,left,right,plus,minus) specifying the location of the new edge
        :stcmd.args[0] - if present, times command is to be executed
        """
        stc_name = stcmd.name
        ntime = 1               # Default 1 time
        if len(stcmd.args) >= 1:
            ntime = int(stcmd.args[0].str)
            
        edge = self.get_keycmd_edge()
        edge_dir = edge.sub_type()
        next_dir = edge_dir
        next_row = edge.row 
        next_col = edge.col 

        if stc_name == "plus":
            if edge_dir == "h":
                next_dir = "v"
            else:
                next_dir = "h"
                next_col -= 1
        elif stc_name == "minus":
            if edge_dir == "h":
                next_dir = "v"
                next_row -= 1
            else:
                next_dir = "h"
        elif stc_name == "up":
            next_row -= 1
        elif stc_name == "down":
            next_row += 1
        elif stc_name == "left":
            next_col -= 1
        elif stc_name == "right":
            next_col += 1

        if next_row < 1:
            next_row = self.play_control.board.nrows
        if (next_row > self.play_control.board.nrows+1
             or (next_row > self.play_control.board.nrows
                  and next_dir == "v")):
            next_row = 1
        if next_col < 1:
            next_col = self.play_control.board.ncols
        if (next_col > self.play_control.board.ncols+1
             or (next_col > self.play_control.board.ncols
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
        self.play_control.cmd_select(next_edge, display=True)
        if SlTrace.trace("track_move_edge"):
            SlTrace.lg("after move_edge_cmd:\nedge:%s\nnext_edge:%s"
                       % (edge, next_edge), "track_move_edge")
    

    def do_stcmd_enter(self, stcmd=None):
        """ Enter command - add current Edge
        """
        edge = self.get_current_edge()
        if edge is None:
            self.beep()
            return False
        
        if edge.is_turned_on():
            self.beep()
            SlTrace.lg("%s edge already turned on" % stcmd)
            return True
        
        edge.display_clear()
        self.make_new_edge(edge=edge, display=True)
        self.display_update()       # Ensure screen update
        return True        


    def get_current_edge(self):
        """ Get current marker direction, (row, col)
        """
        return self.play_control.get_current_edge()


    def beep(self):
        self.play_control.beep()

        
    def get_canvas(self):
        return self.play_control.get_canvas()


    def get_part(self, id=None, type=None, sub_type=None, row=None, col=None):
        """ Get basic part
        :id: unique part id
        :returns: part, None if not found
        """
        return self.play_control.get_part(id=id, type=type, sub_type=sub_type, row=row, col=col)

    def get_part_from_tags(self, tags):
        for tag in tags:
            if tag.startswith("part:"):
                match = re.search(r'id:(\d+)', tag)
                if match:
                    part_id = int(match.group(1))
                    return self.get_part(part_id)
        return None


    def get_keycmd_edge(self):
        """ Get current marker direction, (row, col)
        """
        ####edge = self.keycmd_edge_mark
        edge = self.play_control.get_selected_part()
        if edge is None:
            edge = self.get_part(type="edge", sub_type="h", row=1, col=1)
        return edge
        
    
    def make_new_edge(self, edge=None, display=True):
        return self.play_control.make_new_edge(edge=edge, display=True)
    
    def display_update(self):
        self.play_control.display_update()
        
    
    def get_players(self, all=False):
        """ Get players
        :all: all players default: just currently playing
        """
        return self.play_control.get_players(all=all)


    def get_arg(self, stcmd, argno=1, default="", req=False):
        """ Get argument
        :argno: argument position, starting at 1 for first
        :default: default value, type is used as required arg type
                default: "", str
        :req: Argument is required Default: optional
        """
        '''
        if not isinstance(stcmd, SelectStreamCmd):
            raise SelectError("get_arg missing stcmd arg")
        '''
        if len(stcmd.args) < argno:
            if req:
                raise SelectError("Missing REQUIRED argno:%d" % argno)
            return default
        
        argtype = type(default)
        argstr = stcmd.args[argno-1].str
        if argtype == int:
            return int(argstr)

        if argtype == float:
            return float(argstr)

        if argtype == bool:
            return bool(argstr)

        return argstr 


    def select(self, ptype, row=None, col=None, keep=False):
        """ Select part
        :ptype: part type: "h" horizontal edge
                            "v" vertical edge
        :row: row in grid
        :col" column in grid
        :keep: keep previously selected default: False
        :returns: True iff successful
        """
        if isinstance(ptype, SelectStreamCmd):
            stcmd = ptype
            ptype = self.get_arg(stcmd, 1)
            row = self.get_arg(stcmd, 2, 1, req=True)
            col = self.get_arg(stcmd, 3, 1, req=True)
            keep = self.get_arg(stcmd, 4, False)
        
        return self.play_control.select(ptype, row=row, col=col, keep=keep)


    def enter(self):
        """ Enter command - add current Edge
        """
        edge = self.get_current_edge()
        if edge is None:
            self.beep()
            SlTrace.lg("enter() no edge selected")
            return True
        
        if edge.is_turned_on():
            self.beep()
            SlTrace.lg("enter() edge alreay turned on")
            return True
        
        edge.display_clear()
        self.make_new_edge(edge=edge, display=True)
        self.display_update()       # Ensure screen update
        return True        



    def set_player(self, name):
        """ Record player  as next player
        :name: player's label or start (first match)
        """
        if isinstance(name, SelectStreamCmd):
            stcmd = name
            name = self.get_arg(stcmd)
            return self.set_player(name)
        
        players = self.get_players(all=True)
        for player in players:
            if player.label.startswith(name):
                self.play_control.player_control.set_player(player)
                break
        return True


    def set_playing(self, playing=None):
        """ Set players playing via
        comma separated string
        :playing: comma separated string of playing player's Labels
        """
        if isinstance(playing, SelectStreamCmd):
            stcmd = playing
            playing = self.get_arg(stcmd, 1)
            return self.set_playing(playing=playing)
        
        if self.play_control.player_control is None:
            raise SelectError("control_player_control not set")
            
        self.play_control.player_control.set_playing(playing)
        return True
    