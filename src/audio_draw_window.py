#audio_draw_window.py    12Dec2022  crs, from audio_window.py
#                        08Nov2022  crs, Author
"""
Provide simple drawing graphical window with audio feedback
to facilitate use and examination by the visually impaired.
Uses turtle to facilitate cursor movement within screen
Adapted from audio_window to concentrate on figure drawing
as well as presentation.
"""
import os
import tkinter as tk

from select_trace import SlTrace
from speaker_control import SpeakerControlLocal
from wx_grid_path import GridPath
from braille_cell import BrailleCell
from magnify_info import MagnifyInfo, MagnifyDisplayRegion
from adw_front_end import AdwFrontEnd

class AudioDrawWindow:



    
    def __init__(self,
        title=None, speaker_control=None,
        win_width=800, win_height=800,
        grid_width=40, grid_height=25,
        x_min=None, y_min=None,
        line_width=1, color="black",
        pos_check_interval= .1,
        pos_rep_interval = .1,
        pos_rep_queue_max = 1,
        visible = True,
        enable_mouse = False,
        pgmExit=None,
        blank_char=",",
        drawing=False,
        show_marked=False,
        shift_to_edge=True,
        silent=False,
        look_dist=2,
        menu_str="",
        key_str="",
        mag_info=None,
        iy0_is_top=True,        # OBSOLETE
                 ):
        """ Setup audio window
        :speaker_control: (SpeakerControlLocal) local access to centralized speech making
        :win_width: display window width in pixels
            default: 800
        :win_height: display window height in pixels
            default: 800
        :x_min: minimum coordinate
                default: 0
        :y_min: minimum coordinate
                default: 0
        :grid_width: braille width in cells
            default: 40
        :grid_height: braille width in cells
            default: 25
        :title: window title
        :pos_check_interval: time between checks/reporting on
                cursor position  default: .1 seconds
        :pos_rep_interval: minimum time between reports
                default: .5 seconds
        :pos_rep_force_output: force output
                default: Force
        :pos_rep_queue_max: maximum position report queue maximum
                default: 4
        :visible: cells are visible
                default: True - visible
        :blank_char: replacement for non-trailing blanks
                    default "," to provide a "mostly blank",
                    non-compressed blank character for the
                    braille graphics
                    default: "," dot 2.
        :shift_to_edge: shift picture to edge/top
                    to aid in finding
                    default: True - shift
        :drawing: We're in drawing mode
                 default: False - no drawing
        :show_marked: Make marked cells
                shown even when invisible
                default: True
        :silent: Suppress talking / audio
                default: False
        :menu_str:  Initial menu commands
                    default=None
                    Note that interpretation is case insensitive
                    Format: <Menu Letter><option letters>; as separator
                            e.g. n:sh;d:d  for Navigator silent, help
        :enable_mouse: mouse cursor operation enabled
                    default: False                                        Drawing: start drawing
        :key_str:  Initial key symbol command string
                    Each command separated by ";" to facilitate
                    recognition of multi charater symbols
                    such as "up", "down" Note that
                    interpretation is case insensitive
        :look_dist: Max number of cells to look ahead and report
                    default: 1
        :iy0_is_top: OBSOLETE
        """
        
        # direction for digit pad
        if title is None:
            title = "AudioDrawWindow"
        self.title = title
        control_prefix = "AudioDraw"
        self.win_width = win_width
        self.win_height = win_height
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_height = win_height/self.grid_height
        self.pgmExit = pgmExit
        if x_min is None:
            x_min = 0
        if y_min is None:
            y_min = 0
        # create the feedback window
        mw = tk.Tk()
        self.title = title
        mw.title(title)
        self.mw = mw
        if speaker_control is None:
            SlTrace.lg("Creating own SpeakerControl")
            speaker_control = SpeakerControlLocal(win=mw)
        self.speaker_control = speaker_control
        #mw.withdraw()


        
        win_print_frame = tk.Frame(mw)
        win_print_frame.pack(side=tk.TOP)
        win_print_entry = tk.Entry(
                                win_print_frame, width=50)
        win_print_entry.pack(side=tk.TOP)
        self.win_print_entry = win_print_entry
        
        canvas = tk.Canvas(mw, width=self.win_width, height=self.win_height)
        canvas.pack()
        self.canvas = canvas
        self.update()        # Force display
        SlTrace.lg(f"canvas width: {canvas.winfo_width()}")
        SlTrace.lg(f"canvas height: {canvas.winfo_height()}")
        self._visible = visible
        self.fte = AdwFrontEnd(self, title=title, silent=silent, color=color)
        self.set_x_min(x_min)
        self.set_y_min(y_min)
        self.set_x_max(x_min + win_width)
        self.set_y_max(y_min + win_height)
        self.set_drawing(drawing)
        self.speak_text(title)

        self.escape_pressed = False # True -> interrupt/flush
        self.cells = {}         # Dictionary of cells by (ix,iy)
        self.set_cell_lims()
        self.do_talking = True      # Enable talking
        self.logging_speech = True  # Output speech to log/screen
        if mag_info is None:
            top_region = MagnifyDisplayRegion(
                x_min=self.get_x_min(), y_min=self.get_y_min(),
                x_max=self.get_x_max(),
                y_max=self.get_y_max(),
                nrows=self.grid_height,
                ncols=self.grid_width,
                
                )
            mag_info = MagnifyInfo(top_region=top_region)
        else:
            if mag_info.description:
                title = mag_info.description
                mw.title(title)
                self.title = title
                self.speak_text(f"Magnification of {title}")
        mag_info.display_window = self    # Magnification setup
        self.mag_info = mag_info
        SlTrace.lg(f"\nAudioDrawWindow() mag_info:\n{mag_info}\n")
        self.mag_selection_tag = None       # mag selection canvas tag, if one
        self.is_selected = False            # Flag as not yet selected
        self.pos_history = []       # position history (ix,iy)
        self.pos_rep_force_output = False
        self.goto_travel_list = []    # Memory of where we have gone
        self.goto_travel_list_index = None
        self.cell_history = []          # History of all movement
        self.set_grid_path()
        self.running = True         # Set False to stop
        self.mw.focus_force()
        self.blank_char = blank_char
        self.shift_to_edge = shift_to_edge
        self.set_look_dist(look_dist)
        self.fte.do_complete(menu_str=menu_str, key_str=key_str)
        #self.pos_check()            # Startup possition check loop
        self.update()     # Make visible


    def exit(self, rc=None):
        """ Main exit if creating magnifications
        """
        if rc is None:
            rc = 0
        if self.pgmExit is not None:
            self.pgmExit()      # Use supplied pgmExit
            
        SlTrace.lg("AudoDrawWindow.exit")
        SlTrace.onexit()    # Force logging quit
        os._exit(0)

    def set_look_dist(self, look_dist):
        self.look_dist = look_dist

    def get_look_dist(self):
        return self.look_dist

    def silence(self):
        """ Check if silent mode
        """
        return self.fte.silence()

    def speak_text(self, msg, dup_stdout=True,
                   msg_type=None,
                   rate=None, volume=None):
        """ Speak text, if possible else write to stdout
        :msg: text message, iff speech
        :dup_stdout: duplicate to stdout default: True
        :msg_type: type of speech default: 'REPORT'
            REPORT - standard reporting
            CMD    - command
            ECHO - echo user input
        :rate: speech rate words per minute
                default: 240
        :volume: volume default: .9            
        """
        self.win_print(msg)
        if self.is_silent():
            if dup_stdout:
                SlTrace.lg(msg)
            return
        
        self.speaker_control.speak_text(msg=msg, msg_type=msg_type,
                             dup_stdout=dup_stdout,
                             rate=rate, volume=volume)

    def speak_text_stop(self):
        """ Stop ongoing speach, flushing queue
        """
        self.speaker_control.speak_text_stop()
        
    def trav_len(self, ix, iy, dir_x, dir_y, require_cell=True):
        """ Find the travel length
        This is the number of steps from cell(ix,iy) in 
        direction (dir_x,dir_y) while still in self.cells[]
        traversal is stopped at traversed cells - in
        self.goto_cell_list
        :ix: cell x-index
        :iy: cell y_index
        :dir_x: x change each step
        :dir_y: y change each step
        :require_cell: Require cell in traversal default: True - required
        :returns: steps_forward, steps_backward, -1,-1
                 if cell, itself is not in figure(self.cells)
        """
        if require_cell and (ix,iy) not in self.cells:
            return -1,-1       # Not in figure
        
        if dir_x == 0 and dir_y == 0:
            return 0,0
        
        tlen_forward = 0
        ix_f = ix
        iy_f = iy
        while True:
            ix_f += dir_x
            iy_f += dir_y
            if (ix_f,iy_f) not in self.cells:
                break
            if (ix_f,iy_f) in self.get_goto_cell_list():
                break
            tlen_forward += 1   # traversal extended

        # Get backend of line
        tlen_backward = 0
        ix_b = ix
        iy_b = iy
        
        while True:
            ix_b -= dir_x
            iy_b -= dir_y
            if (ix_b,iy_b) not in self.cells:
                break
            if (ix_b,iy_b) in self.get_goto_cell_list():
                break
            tlen_backward += 1   # traversal extended
        return tlen_forward,tlen_backward
             
    def draw_cells(self, cells=None, show_points=False):
        """ Display braille cells on canvas
        :cells: list or dictionary cells to draw
        :show_points: instead of braille, show sample points
        """
        SlTrace.lg("draw_cells")
        SlTrace.lg(f"x_min:{self.get_x_min()} y_min: {self.get_y_min()}")
        if cells is None:
            cells = self.get_cells()
        else:
            if not isinstance(cells, dict):
                cs = {}
                for cell in cells:
                    cs[(cell.ix,cell.iy)] = cell
                cells = cs
            self.cells = cells      # Copy
        min_x, max_y, max_x,min_y = self.bounding_box()
        if min_x is not None:            
            SlTrace.lg(f"Lower left: min_x:{min_x} min_y:{min_y}")
            SlTrace.lg(f"Upper Right: max_x:{max_x} max_y:{max_y}")
        SlTrace.lg(f"{len(cells)} cells")
        for cell in cells.values():
            self.display_cell(cell)
            cell.mtype = cell.MARK_UNMARKED
        self.update()
        if min_x is not None:
            self.set_xy((min_x,min_y))
            x,y = self.get_xy()
            #self.pos_check(x=x,  y=y)
        self.set_grid_path()
        self.pos_history = []       # Clear history
        self.set_scanning()         # Setup positioning info
        self.update()
                    
    def print_braille(self, title=None, shift_to_edge=None):
        """ Output braille display
        :title: title default: self.title
        :shift_to_edge: shift figure towards edge to ease finding figure
                        default: self.shift_to_edge
        """
        if title is None:
            title = self.title
        if title is not None:
            print(title)
        if shift_to_edge is None:
            shift_to_edge = self.shift_to_edge
        if shift_to_edge:
            self.find_edges()
            left_edge = self.left_edge
            right_edge = self.right_edge
            top_edge = self.top_edge
            bottom_edge = self.bottom_edge
        else:
            left_edge = 0
            top_edge = self.grid_height-1

        braille_text = ""
        for iy in range(top_edge, bottom_edge):
            line = ""
            for ix in range(left_edge, right_edge):
                cell_ixy = (ix,iy)
                if cell_ixy in self.cells:
                    cell = self.cells[cell_ixy]
                    color = cell.color_string()
                    line += color[0]
                else:
                    line += " "
            line = line.rstrip()
            if self.blank_char != " ":
                line = line.replace(" ", self.blank_char)
            ###print(f"{iy:2}", end=":")
            braille_text += line + "\n"
        SlTrace.lg(braille_text)
        self.mw.clipboard_clear()
        if title is not None:
            self.mw.clipboard_append(f"\n{title}\n")
        self.mw.clipboard_append(braille_text)

    def print_cells(self, title=None):
        """ Display current braille in a window
        """
        if title is not None:
            print(title)
        for ix in range(self.grid_width):
            for iy in range(self.grid_height):
                cell_ixy = (ix,iy)
                if cell_ixy in self.cells:
                    cell = self.cells[cell_ixy]
                    SlTrace.lg(f"ix:{ix} iy:{iy} {cell_ixy}"
                               f" {cell._color}"
                          f" rect: {self.get_cell_rect_tur(ix,iy)}"
                          f"  win rect: {self.get_cell_rect_win(ix,iy)}")
        SlTrace.lg("")

    def find_edges(self):
        """Find  top, left, bottom, right non-blank edges
        so we can shift picture to left,top for easier
        recognition
        :returns: left_edge, top_edge, right_edge, bottom_edge
                    Also sets self.left_edge,...
        """
        left_edge,top_edge, right_edge,bottom_edge = self.bounding_box_ci()
        if bottom_edge is None:
            bottom_edge = self.grid_height-1
                    
        if left_edge > 0:           # Give some space
            left_edge -= 1
        if left_edge > 0:
            left_edge -= 1
        self.left_edge = left_edge
        
        if top_edge > 0:           # Give some space
            top_edge -= 1
        if bottom_edge  < self.grid_height-1:
            bottom_edge += 1        
        self.top_edge = top_edge
        self.bottom_edge = bottom_edge
        
        self.left_edge = left_edge
        self.right_edge = right_edge
         
        return left_edge, top_edge, right_edge, bottom_edge

        
    def set_cursor_pos_win(self, x=0, y=0, quiet=False):
        """ Set mouse cursor position in win(canvas) coordinates
        :x: x-coordinate (win(canvas))
        :y: y-coordinate (win(canvas)) 
        :quiet: Don't announce legal moves
                default:False
        """
        """ Set mouse cursor position in canvas coordinates
        :x: x-coordinate (canvas win)
        :y: y-coordinate (canvas win)
        :quiet: Don't announce legal moves
                default: False
        """
        if not self.running:
            return
        
        self.set_xy((x,y))      # All we do is set coordinate memory
        loc_ixiy = self.get_ixy_at()
        self.pos_history.append(loc_ixiy)   # location history
        SlTrace.lg(f"pos_history:{loc_ixiy}", "pos_tracking")
        cell_ixiy = self.get_cell_at()
        if cell_ixiy is not None:
            self.cell_history.append(cell_ixiy)
            if not self.is_drawing():   # If we're not drawing
                self.mark_cell(cell_ixiy)   # Mark cell if one
        self.cursor_update()

        if not self.mw.winfo_exists():
            return 
        
        self.update()
        if not quiet:
            self.pos_check(force_output=True)

    def move_to_ixy(self, ix=None, iy=None):
        """ Move to grid (cell) ix,iy
        :ix: ix index default: current ix
        :iy: iy index default: current iy
        """
        ix_cur,iy_cur = self.get_ixy_at()
        if ix is None:
            ix = ix_cur 
        if iy is None:
            iy = iy_cur
        win_xc,win_yc = self.get_cell_center_win(ix,iy)
        self.move_to(win_xc,win_yc)



    def move_to(self, x,y, quiet=False):
        """ Move to window loc
        Stop at edges, with message
        :x:  win x-coordinate
        :y: win y-coordinate
        :quiet: Don't announce legal move
                default:False
        """
        self.set_cursor_pos_win(x=x, y=y, quiet=quiet)

    def is_inbounds_ixy(self, *ixy):
        """ Check if ixy pair is in bounds
        :ixy: if tuple ix,iy pair default: current location
              else ix,iy indexes
            ix: cell x index default current location
            iy: cell y index default current location
        :returns: True iff in bounds else False
        """
        ix_cur,iy_cur = self.get_ixy_at()
        if len(ixy) ==  0:
            ix,iy = ix_cur,iy_cur
        elif len(ixy) == 1 and isinstance(ixy[0], tuple):
            ix,iy = ixy[0]
        elif len(ixy) == 2:
            ix,iy = ixy
        else:
            raise Exception(f"bad is_inbounds_ixy args: {ixy}")
        if ix is None:
            ix = ix_cur
        if iy is None:
            iy = iy_cur
        if ix < 0 or ix >= len(self.cell_xs):
            return False
         
        if iy < 0 or iy >= len(self.cell_ys):
            return False
        
        return True 
                       
    def set_cell_lims(self):
        """ create cell boundary values bottom through top
         so:
             cell_xs[0] == left edge
             cell_xs[grid_width] == right edge
             cell_ys[0] == top edge
             cell_ys[grid_height] == bottom edge
        """
         
        self.cell_xs = []
        self.cell_ys = []

        for i in range(self.grid_width+1):
            x = int(self.get_x_min() + i*self.win_width/self.grid_width)
            self.cell_xs.append(x)
        for i in reversed(range(self.grid_height+1)):
            y = int(self.get_y_min() + i*self.win_height/self.grid_height)
            self.cell_ys.append(y)
            
    def get_ix_min(self):
        """ get minimum ix on grid
        :returns: min ix
        """
        return 0

    def get_ix_max(self):
        """ get maximum ix on grid
        :returns: min ix
        """
        return self.grid_width-1

    def get_iy_min(self):
        """ get minimum iy on grid
        :returns: min iy
        """
        return 0

    def get_iy_max(self):
        """ get maximum ix on grid
        :returns: min ix
        """
        return self.grid_height-1

    def get_mag_info(self):
        """ Get magnification info storage
        """
        return self.mag_info

    def get_speaker_control(self):
        """ Get speech control
        """
        return self.speaker_control

        

    def bounding_box(self):
        """ canvas coordinates which bound displayed figure
        :returns: min_x, max_y, max_x, min_y  (upper left) (lower right)
                    None,None,None,None if no figure
        """
        min_ix, max_iy, max_ix, min_iy = self.bounding_box_ci()
        if min_ix is None:
            return None,None,None,None      # No figure
        
        min_x, max_y, _, _ = self.get_cell_rect_tur(min_ix,max_iy)
        _, _, max_x, min_y = self.get_cell_rect_tur(max_ix,min_iy)
        return min_x,max_y, max_x, min_y
    
    def bounding_box_ci(self, cells=None, add_edge=None):
        """ cell indexes which bound the list of cells
        :cells: list of cells, (with cell.ix,cell.iy) or (ix,iy) tuples
                default: list of all cells in figure
        :add_edge: number of cells to add/subtract (if possible)
                     to enlarge/shrink box
                    default: no change
        :returns: 
                    None,None,None,None if no figure
                    upper left ix,iy  lower right ix,iy
        """
        if cells is None:
            if not hasattr(self, "cells"):
                return None,None,None,None         # Not yet setup
            cells = list(self.cells.keys())
        
        ix_min, iy_max, ix_max,iy_min = None,None,None,None
        for cell in cells:
            cell_ixy = cell if isinstance(cell, tuple) else (cell.ix,cell.iy)
            cell_ix, cell_iy = cell_ixy
            if ix_min is None or cell_ix < ix_min:
                ix_min = cell_ix
            if ix_max is None or cell_ix > ix_max:
                ix_max = cell_ix
            if iy_min is None or cell_iy < iy_min:
                iy_min = cell_iy
            if iy_max is None or cell_iy > iy_max:
                iy_max = cell_iy

        if ix_min is None:
            ix_min = 0
        if ix_max is None:
            ix_max = self.grid_width-1
        if iy_min is None:
            iy_min = 0
        if iy_max is None:
            iy_max = self.grid_height-1
        
        if add_edge is not None:    # Extend/Shrink box
            ext_ix_min = ix_min - add_edge
            bd_ix_max = self.get_ix_max() # protect against too large of negative add_edge
            if ext_ix_min > bd_ix_max: ext_ix_min = bd_ix_max
            ix_min = max(ext_ix_min, self.get_ix_min()) # limit to bounds

            ext_iy_min = iy_min - add_edge
            bd_iy_max = self.get_iy_max()
            if ext_iy_min > bd_iy_max: ext_iy_min = bd_iy_max
            iy_min = max(ext_iy_min, self.get_iy_min())
            
            ext_ix_max = ix_max + add_edge
            bd_ix_min = self.get_ix_min()
            if ext_ix_max < bd_ix_min: ext_ix_max = bd_ix_min
            ix_max = min(ext_ix_max, self.get_ix_max())
            
            ext_iy_max = iy_max + add_edge
            bd_iy_min = self.get_iy_min()
            if ext_iy_max < bd_iy_min: ext_ix_max = bd_iy_min
            iy_max = min(ext_iy_max, self.get_iy_max())
            
        return ix_min,iy_min, ix_max,iy_max
            


    def erase_cell(self, cell):
        """ Erase cell
        :cell: BrailleCell
        """
        if cell is None:
            return
        
        # Remove current items, if any
        if cell.canv_items:
            for item_id in cell.canv_items:
                self.canvas.delete(item_id)
            self.update()       # Make change visible
        cell.canv_items = []

    def erase_pos_history(self):
        """ Remove history, undo history marking
        """
        canvas = self.canvas
        for cell_ixy in self.pos_history:
            if not cell_ixy in self.cells:
                continue
            cell = self.cells[cell_ixy]
            self.display_cell(cell)
            '''
            for item_id in cell.canv_items:
                item_type = canvas.type(item_id)
                if item_type == "rectangle":
                    canvas.itemconfigure(item_id, fill='')
                    canvas.tag_lower(item_id)
            '''
        self.pos_history = []
        canvas = self.canvas
        if self.mag_selection_tag is not None:
            canvas.itemconfig(self.mag_selection_tag, outline="red")
        self.is_selected = False         # Flag as unselected
            
        self.update()
                
    def display_reposition_hack(self, cx1,cx2,cy1,cy2, force=False):
        """ ###TFD HACK to reposition cell dispaly
            move x1,x2,y1,y2
        """
        return cx1,cx2,cy1,cy2

    def annotate_cell(self, cell_ixy=None, color=None,
                      outline="blue", outline_width=2,
                      text=None):
        """ Annotate cell to highlight it
        Possibly for perimeter viewing
        :cell_xy: ix,iy tuple default: current location
        :color: rectangle color default: no fill
        :outline: add outline color
                    default: no special outline
        :outline_width: outline width
                    default: 2
        :text: added text default: no text added
        """
        if cell_ixy is None:
            cell_ixy = self.get_ixy_at()
        cell = self.get_cell_at_ixy(cell_ixy=cell_ixy)
        if cell is None:
            return     # Just ignore if missing
        
        self.deannotate_cell(cell_ixy=cell_ixy) #???
        self.display_cell(cell=cell)
        canvas = self.canvas
        cx1,cy1,cx2,cy2 = self.get_win_ullr_at_ixy_canvas(cell_ixy)
        if outline is not None:
            canv_item = canvas.create_rectangle(cx1,cy1,cx2,cy2,
                                fill=color,
                                 outline=outline,
                                 width=outline_width)
            cell.canv_items.append(canv_item)
            
        self.update()    # So we can see it now 
            
        return 

    def deannotate_cell(self, cell_ixy=None, color=None,
                      outline=None, text=None):
        """ deAnnotate cell, restoring cell to normal
        :cell_xy: ix,iy tuple default: current location
        """
        if cell_ixy is None:
            cell_ixy = self.get_ixy_at()
        cell = self.get_cell_at_ixy(cell_ixy=cell_ixy)
        if cell is not None:
            self.display_cell(cell=cell)
            
        return      # Just ignore if missing
    
    def display_cell(self, cell, show_points=False):
        """ Display cell
        :cell: BrailleCell
        :show_points: show points instead of braille
                default: False --> show braille dots
        """
        self.erase_cell(cell)
        if not cell.is_visible():
            return              # Nothing to show
        
        canvas = self.canvas
        ix = cell.ix
        iy = cell.iy
        
        cx1,cy1,cx2,cy2 = self.get_win_ullr_at_ixy_canvas((ix,iy))
        SlTrace.lg(f"{ix},{iy}: {cell} :{cx1},{cy1}, {cx2},{cy2} ", "display_cell")
        if cell.mtype==BrailleCell.MARK_UNMARKED:
            canv_item = canvas.create_rectangle(cx1,cy1,cx2,cy2,
                                    outline="light gray")
        else:
            canv_item = canvas.create_rectangle(cx1,cy1,cx2,cy2,
                                    fill="dark gray",
                                    outline="dark gray")
        cell.canv_items.append(canv_item)
        self.update()
        color = self.color_str(cell._color)
        if len(color) < 1 or color[0] not in BrailleCell.color_for_character:
            color = "black"
        if show_points:
            dot_size = 1            # Display cell points
            dot_radius = dot_size//2
            if dot_radius < 1:
                dot_radius = 1
                dot_size = 2
            for pt in cell.points:
                dx,dy = self.get_point_win(pt)
                x0 = dx-dot_radius
                y0 = dy+dot_size 
                x1 = dx+dot_radius 
                y1 = dy
                canv_item = canvas.create_oval(x0,y0,x1,y1,
                                                fill=color)
                cell.canv_items.append(canv_item)
                SlTrace.lg(f"canvas.create_oval({x0},{y0},{x1},{y1}, fill={color})", "aud_create")
            self.update()    # So we can see it now 
            return
            
        dots = cell.dots
        cell_width = cx2-cx1
        cell_height = cy2-cy1       # y increases down
        # Fractional offsets from lower left corner
        # of cell rectangle
        ll_x = cx1      # Lower left corner
        ll_y = cy1
        ox1 = ox2 = ox3 = .3 
        ox4 = ox5 = ox6 = .7
        oy1 = oy4 = .15
        oy2 = oy5 = .45
        oy3 = oy6 = .73
        dot_size = .25*cell_width   # dot size fraction
        dot_radius = dot_size//2
        dot_offset = {1: (ox1,oy1), 4: (ox4,oy4),
                      2: (ox2,oy2), 5: (ox5,oy5),
                      3: (ox3,oy3), 6: (ox6,oy6),
                      }
        for dot in dots:
            offsets = dot_offset[dot]
            off_x_f, off_y_f = offsets
            dx = ll_x + off_x_f*cell_width
            dy = ll_y + off_y_f*cell_height
            x0 = dx-dot_radius
            y0 = dy+dot_size 
            x1 = dx+dot_radius 
            y1 = dy
            canv_item = canvas.create_oval(x0,y0,x1,y1,
                                            fill=color)
            cell.canv_items.append(canv_item) 
            SlTrace.lg(f"canvas.create_oval({x0},{y0},{x1},{y1}, fill={color})", "aud_create")
        self.update()
        pass
                
    def get_cell_center_win(self, ix, iy):
        """ Get cell's window rectangle x, y  upper left, x,  y lower right
        :ix: cell x index
        :iy: cell's  y index
        :returns: window(0-max): (xc,yc) where
            xc,yc are x,y coordinates of cell's center
        """
        x1,y1, x2,y2 = self.get_cell_rect_win(ix,iy)
        return (x1+x2)/2, (y1+y2)/2 
                
    def get_cell_rect_win(self, ix, iy):
        """ Get cell's window rectangle x, y  upper left, x,  y lower right
        :ix: cell x index
        :iy: cell's  y index
        :returns: window(0-max): (x1,y1,x2,y2) where
            x1,y1 are lower left coordinates
            x2,y2 are upper right coordinates
        """
        win_x1,win_y1,win_x2,win_y2 = self.get_win_ullr_at_ixy((ix,iy))
        return (win_x1,win_y1,win_x2,win_y2)
        
                    
        
    def get_cell_rect_tur(self, ix, iy):
        """ Get cell's turtle rectangle x, y  upper left, x,  y lower right
        :ix: cell x index
        :iy: cell's  y index
        :returns: (min_x,max_y, max_x,min_y)
        """
        if ix is None or ix < 0:
            SlTrace.lg(f"ix:{ix} < 0")
            ix = 0
        max_ix = len(self.cell_xs)-1
        if ix+1 > max_ix:
            SlTrace.lg(f"ix:{ix+1} >= {len(self.cell_xs)}")
            ix = max_ix-1
        if iy is None or iy < 0:
            SlTrace.lg(f"iy:{iy} < 0", "aud_move")
            iy = 0
        max_iy = len(self.cell_ys)-1
        if iy+1 > max_iy:
            SlTrace.lg(f"iy:{iy+1} >= {len(self.cell_ys)}")
            iy = max_iy-1
        x1 = self.cell_xs[ix]
        x2 = self.cell_xs[ix+1]
        y1 = self.cell_ys[iy+1]
        y2 = self.cell_ys[iy]
        return (x1,y1,x2,y2)
        
        
    def get_ixy_at(self, pt=None):
        """ Get cell(indexes) in which point resides
        If on an edge returns lower cell
        If on a corner returns lowest cell
        :pt: x,y pair location
                        in win coordinates
                default: current location
        :returns: ix,iy cell pair
                if out of bounds limit to min/max of ix,iy
        """
        if pt is None:
            pt = self.get_xy()
        x,y = pt
        x_min = self.get_x_min()
        y_min = self.get_y_min()
        ix = int((x-x_min)/self.win_width*self.grid_width)
        iy = int((y-y_min)/self.win_height*self.grid_height)
        #ix = int((x)/self.win_width*self.grid_width)        # TFD
        #iy = int((y)/self.win_height*self.grid_height)      # TFD
        return (ix,iy)

    def get_cells(self):
        """ Get cell dictionary (by (ix,iy)
        """
        return self.cells
    
    def get_cell_at(self, pt=None):
        """ Get cell at location, if one
        :pt: x,y pair location in turtle coordinates
                default: current location
        :returns: cell if at, else None
        """
        cell_ixy = self.get_ixy_at(pt)
        if cell_ixy is None:
            return None 
        
        if cell_ixy in self.cells:
            return self.cells[cell_ixy]
        
        return None

    def set_grid_path(self):
        self.grid_path = GridPath(self)
        
    def get_grid_path(self):
        return self.grid_path
    
    def get_win_ullr_at_ixy(self, ixy):
        """ Get window rectangle for cell at ixy
        :ixy: cell index tupple (ix,iy)
        :returns: (x_left,y_top, x_right,y_bottom)
        """
        ix,iy = ixy
        x_min = self.get_x_min()
        y_min = self.get_y_min()
        x_left = int(ix*(self.win_width/self.grid_width) + x_min)
        x_right = int((ix+1)*(self.win_width/self.grid_width) + x_min)
        y_top = int((iy*(self.win_height/self.grid_height) + y_min))
        y_bottom = int((iy+1)*(self.win_height/self.grid_height) + y_min)
        return (x_left,y_top, x_right,y_bottom)

    def get_win_ullr_at_ixy_canvas(self, ixy):
        """ Get window rectangle for cell at ixy
        :ixy: cell index tupple (ix,iy)
        :returns: (x_left,y_top, x_right,y_bottom) canvas coords
        """
        x_l,y_t, x_r,y_b = self.get_win_ullr_at_ixy(ixy)
        x_left,y_top = self.win_to_canvas((x_l,y_t))
        x_right,y_bottom = self.win_to_canvas((x_r,y_b))
        return (x_left,y_top, x_right,y_bottom)
        
    def win_to_canvas(self, xy):
        """ Convert window coordinates to canvas (min to max) to (0,max)
        :xy: x,y tuple
        :returns: x,y canvas tuple
        """
        x,y = xy
        canvas_x, canvas_y = (x-self.get_x_min(), y-self.get_y_min())
        return (canvas_x,canvas_y)
            
    def get_cell_at_ixy(self,cell_ixy, cells=None, ):
        """ Get cell at (ix,iy), if one
        :cell_ixy: (ix,iy)
        :cells: dictionary of cells by (ix,iy)
                default: self.get_cells()
        :returns: BrailleCell if one, else None
        """
        if cells is None:
            cells = self.get_cells()
        if cell_ixy in cells:
            return cells[cell_ixy]
        
        return None
        

    def is_at_cell(self, pt=None):
        """ Check if at cell
        :pt: x,y pair location in turtle coordinates
                default: current location
        :returns: True if at cell, else False
        """
        if self.get_cell_at(pt) is None:
            return False 
        
        return True

    def is_space(self, ixy, cells=None):
        """ Are we at a space
        :ixy: cell ix,iy indexes
        :cells: cells to check
                default: our cells - get_cells()
        :returns: True if a space (not a cell) 
        """
        if cells is None:
            cells = self.get_cells()
        cell = self.get_cell_at_ixy(cell_ixy=ixy, cells=cells)
        return True if cell is None else False
        
    def set_cell(self, pt=None, color=None):
        """ Set cell at pt, else current cell
        If no cell at current location create cell
        :pt: at point
            default: current location
        :color: color default: current color
        """
        if not self.is_at_cell(pt):
            self.create_cell(color=color)
        self.change_cell(pt=pt, color=color)

    def change_cell(self, pt=None, color=None):
        """ Change cell at pt if None current pt
        :pt: location default: current
        :color: color default: current color
        :returns: updated cell
        """
        if color is None:
            color = self.get_color()
        cell = self.get_cell_at(pt=pt)
        if cell is None:
            cell = self.create_cell(pt=pt, color=color)
        if cell is not None:
            cell.color_cell(color=color)
            self.display_cell(cell)
        self.update()
        return cell
                
    def color_str(self, color=None):
        """ Return color string
        :color: color specification str or tuple
        """
        color_str = color
        if (color_str is None
             or (isinstance(color_str, tuple)
                  and len(color_str) == 0)
             ):
            color_str = self.get_color()
        if isinstance(color_str,tuple):
            if len(color_str) == 1:
                color_str = color_str[0]
            else:
                color_str = "pink"  # TBD - color tuple work
        return color_str

    def is_visible(self):
        """ Check on visible mode
        """
        return self._visible
    
    def set_visible(self, val=True):
        """ Set cells visible/invisible
        Useful to give sighted a vision
        :val: set visible Default: True
        """
        SlTrace.lg(f"set_visible:{val}")
        self._visible = val
        if not val:
            self.set_show_marked(False)     # Make marked also invisible
        for cell in self.cells.values():
            self.set_visible_cell(cell, val)
                
    def set_visible_cell(self, cell, val=True):
        """ Set cells visible/invisible
        Useful to give sighted a vision
        :cell: figure cell
        :val: set visible Default: True
        """
        self.fte.set_visible_cell(cell, val=val)

    def announce_can_not_do(self, msg=None, val=None):
        """ Announce we can't do something
        """
        audio_beep = self.get_audio_beep()
        if audio_beep:
            audio_beep.announce_can_not_do(msg=msg, val=val)
        else:
            self.say_text(msg)
    
    def braille_for_color(self, color):
        """ Return dot list for color
        :color: color string or tuple
        :returns: list of dots 1,2,..6 for first
                letter of color
        """
        
        if color is None:
            color = self.get_color()
        if color is None:
            color = ("black")
        color = BrailleCell.color_str(color)
        c = color[0]
        dots = BrailleCell.braille_for_letter(c)
        return dots
    
    def braille_for_letter(self, c):
        """ convert letter to dot number seq
        :c: character
        :returns: dots tupple (1,2,3,4,5,6)
        """
        return BrailleCell.braille_for_letter(c)

    def clear_cells(self):
        """ remove all cells - clearing board
        Initialize empty board
        """
        cells = self.get_cells()
        for cell in list(cells.values()):
            self.erase_cell(cell)
        del self.cells
        self.cells = {}
        self.draw_cells(cells=self.cells)

        
        
        
    def create_cell(self, cell_ixy=None, color=None,
                    show=True):
        """ Create new cell ad cell_xy
        :cell_xy: ix,iy tuple default: current location
        :color: color default: curren color
        :show: show cell default:True
        :returns: cell
        """
        if cell_ixy is None:
            cell_ixy = self.get_ixy_at()
        if color is None:
            color = self.get_color()
        dots = self.braille_for_color(color)
        bc = BrailleCell(ix=cell_ixy[0], iy=cell_ixy[1],
                         dots=dots, color=color)
        if cell_ixy in self.cells:
            del self.cells[cell_ixy]
        self.cells[cell_ixy] = bc
        if show:
            self.update()
        return bc
            
    def complete_cell(self, cell, color=None):
        """ create/Fill braille cell
            Currently just fill with color letter (ROYGBIV)
        :cell: (ix,iy) cell index or BrailleCell
        :color: cell color default: current color
        :returns: created/modified cell
        """
        if color is None:
            color = self.get_color()
        dots = self.braille_for_color(color)
        bc = BrailleCell(ix=cell[0],iy=cell[1], dots=dots, color=color)
        self.cells[cell] = bc
        return bc

    def update(self):
        """ Update display
        """
        self.mw.update()

    def mainloop(self):
        self.mw.mainloop()
        
    def update_idle(self):
        """ Update pending
        """
        self.mw.update_idletasks()

    """
         Links to front end functions
    """

    def is_inbounds(self,ix=None, iy=None):
        """ Test if inbounds
        :ix: x index - default: don't test
        :iy: y index - default: don't test
        :returns: True iff in bounds
        """
        return self.fte.is_inbounds(ix=ix, iy=iy)

    def set_show_marked(self,val=True):
        """ Show marked "invisible" cells
        """
        self.fte.set_show_marked(val=val)

    def wait_on_output(self):
        """ Wait till queued output speech/tones completed
        """
        self.fte.wait_on_output()
        
    def win_print(self,*args, dup_stdout=False, **kwargs):
        """ print to listing area
        :*args: print-like args
        :**kwargs: print-flags
        :dup_stdout:  send duplicate to stdout
        """
        self.fte.win_print(args=args, dup_stdout=dup_stdout, kwargs=kwargs)

    def get_audio_beep(self):
        """ Get access to audio beep
        """
        return self.fte.get_audio_beep()

    def cursor_update(self):
        """ Update cursor (current position) display
        """
        self.fte.cursor_update()
        
    def mark_cell(self, cell,
                  mtype=BrailleCell.MARK_SELECTED):
        """ Mark cell for viewing of history
        :cell: Cell(BrailleCell) or (ix,iy) of cell
        :mtype: Mark type default: MARK_SELECTED
        """
        self.fte.mark_cell(cell=cell, mtype=mtype)

    def set_color(self, color):
        """ Set current color
        """
        self.fte.set_color(color=color)
        
    def get_color(self):
        """ Get current color
        """
        return self.fte.get_color()
        
    def set_drawing(self, val=True):        
        self.fte.set_drawing(val=val)
        return val
    
    def is_drawing(self):
        return self.fte.is_drawing()

        
    def key_goto(self):
        """ Go to closest figure
            go to figure not in one already
            else go one step within current figure, toward
            longest inside path
        """
        self.fte.key_goto()

    def set_scanning(self, cells=None):
        self.fte.set_scanning(cells=cells)
        
    def get_vol(self, ix, iy, eye_ixy_l=None, eye_ixy_r=None):
        """ Get tone volume for cell at ix,iy
        volume(left,right)
        Volume(in decibel): k1*(k2-distance from eye), k1=1, k2=0
        :ix: cell ix
        :iy: cell iy
        :eye_xy_l: left eye/ear at x,y default: self.eye_xy_l
        :eye_xy_r: right eye/ear at x,y  default: self.eye_xy_r
        return: volume(left,right) in decibel
        """
        return self.fte.get_vol(ix=ix, iy=iy, eye_ixy_l=eye_ixy_l, eye_ixy_r=eye_ixy_r)

    def set_xy(self, xy):
        """ Set our internal win x,y
        :xy: x,y tuple as new win coordinates
        :returs: (x,y) tuple
        """
        return self.fte.set_xy(xy)

    def get_xy(self):
        """ Get current xy pair
        :returns: (x,y) tuple
        """
        return self.fte.get_xy() 

    def get_xy_canvas(self, xy=None):
        """ Get current xy pair on canvas (0-max)
        :xy: xy tuple default: current xy
        :returns: (x,y) tuple
        """
        return self.fte.get_xy_canvas(xy=xy)
    
    def set_x_min(self, val):
        """ Set min
        :val: new x_min
        :returns: new x_min
        """
        return self.fte.set_x_min(val)

    def get_x_min(self):
        return self.fte.get_x_min()

    def set_x_max(self, val):
        """ Set max
        :val: new x_max
        :returns: new x_min
        """
        return self.fte.set_x_max(val)

    def get_x_max(self):
        return self.fte.get_x_max()
        
 
    def set_y_min(self, val):
        """ Set min
        :val: new x_min
        :returns: new x_min
        """
        return self.fte.set_y_min(val)

    def get_y_min(self):
        return self.fte.get_y_min()

    def set_y_max(self, val):
        """ Set max
        :val: new y_max
        :returns: new x_min
        """
        return self.fte.set_y_max(val)

    def get_y_max(self):
        return self.fte.get_x_max()

                
    def pos_check(self, x=None, y=None, force_output=False, with_voice=False):
        """ Do position checking followed by report queue processing
        :x: x postion default: current
        :y: y position default: current
        :force_output: force output, flushing current queue
        :with_voice: say if, even if beep enable
        """
        self.fte.pos_check(x=x, y=y, force_output=force_output,
                             with_voice=with_voice)

    def is_silent(self):
        return self.fte.is_silent()
if __name__ == "__main__":
    SlTrace.clearFlags()
    menu_str = "n:sh;d:d"
    key_str = (
                "d"
                ";c;g;9;9;9;9"
                ";c;r;7;7;7;7"
                ";c;v;2;2;2;c;r;2;2;c;o;2;2;2"
                  ";u;8;8;8;8;8;8;8;8;d"
                ";c;o;1;1;1;1"
                ";c;b;3;3;3;3"
                ";c;g;6;6;c;i;6;6;6;c;v;6;6;6"
                ";w"
            )
    aw = AudioDrawWindow(title="AudioDrawWindow Self-Test",
                         menu_str=menu_str,
                         key_str=key_str)

    aw.fte.do_menu_str("n:nu;d:s")
    aw.fte.do_key_str("u")
    
    
    
    
    aw.mw.mainloop()
    
