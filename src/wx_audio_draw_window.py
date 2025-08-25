#wx_audio_draw_window.py 24May2023  crs, from audio_draw_window.py
#                        12Dec2022  crs, from audio_window.py
#                        08Nov2022  crs, Author
"""
Remodeled from tkinter base to use wxPython to facilitate
better support with screen readers such as NVDA and JAWS

Provide simple drawing graphical window with audio feedback
to facilitate use and examination by the visually impaired.
TBD: Using wxPython to facilitate cursor movement within screen
Adapted from audio_window to concentrate on figure drawing
as well as presentation.
"""
import sys
import os
import datetime
import re

import wx
import traceback

from select_trace import SlTrace
from wx_speaker_control import SpeakerControlLocal
from wx_grid_path import GridPath
from braille_cell import BrailleCell
from magnify_info import MagnifyInfo, MagnifyDisplayRegion
from wx_stuff import *
from wx_adw_front_end import AdwFrontEnd
from wx_adw_menus import AdwMenus
from wx_canvas_panel import CanvasPanel
from wx_braille_cell_list import BrailleCellList
from wx_tk_rpc_user import TkRPCUser
from wx_canvas_panel_item import CanvasPanelItem

class AudioDrawWindow(wx.Frame):
    def __init__(self,
        tkr=None,
        snapshot_num=None,
        display_list=None,
        app=None,
        id_title = "unknown",
        title=None, speaker_control=None,
        win_width=800, win_height=800,
        grid_width=40, grid_height=25,
        win_fract=True,
        x_min=None, y_min=None,
        x_max=None, y_max=None,
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
        shift_to_edge=None,
        silent=False,
        look_dist=2,
        menu_str="",
        key_str="",
        mag_info=None,
        setup_wx_win = True,
        iy0_is_top=True,        # OBSOLETE
                 ):
        self.id_title = id_title
        SlTrace.lg(f"""\nAudioDrawWindow:
        tkr={tkr},
        snapshot_num={snapshot_num},
        display_list={display_list},
        app={app},
        id_title={id_title},
        title={title},
        speaker_control={speaker_control},
        win_width={win_width}, win_height={win_height},
        grid_width={grid_width}, grid_height={grid_height},
        win_fract={win_fract},
        x_min={x_min}, y_min={y_min},
        x_max={x_max}, y_max={y_max},
        line_width={line_width}, color={color},
        pos_check_interval= {pos_check_interval},
        pos_rep_interval = {pos_rep_interval},
        pos_rep_queue_max = {pos_rep_queue_max},
        visible = {visible},
        enable_mouse = {enable_mouse},
        pgmExit={pgmExit},
        blank_char={blank_char},
        drawing={drawing},
        show_marked={show_marked},
        shift_to_edge={shift_to_edge},
        silent={silent},
        look_dist={look_dist},
        menu_str={menu_str},
        key_str={key_str},
        mag_info={mag_info},
        setup_wx_win = {setup_wx_win},
        iy0_is_top={iy0_is_top},        # OBSOLETE           
                   """, "adw")
        SlTrace.lg(f"AudioDrawWindow: {id_title = }")
        #frame = CanvasFrame(title=mytitle, size=wx.Size(width,height))
        """ Setup audio window
        :tkr: Access to remote tk information default: simulated access
        :make_snapshot: make a snapshot of current canvas
                        default: False - use current window state 
        :app: wx application object
            default: create object
        :speaker_control: (SpeakerControlLocal) local access to centralized speech making
        :win_width: display window width in pixels
            default: 800
        :win_height: display window height in pixels
            default: 800
        :win_fract: True - x_min,x_max are fraction of self.draw_width()
                            y_min,y_max are fractions of self.draw_height()
                    False - values
                    default: True
        :x_min: minimum coordinate
                default: win_fract: True: 0
                                False: 0
        :y_min: minimum coordinate
                default: win_fract: True:  0
                                    False: 0

        :x_max: maximum coordinate
                default: win_fract: True: 1
                                    False: self.draw_width()
        :y_max: maximum coordinate
                default: win_fract: True: 1
                                    False: self.draw_height()
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
                    default: False - no shift
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
        if app is None:
            app = wx.App()
        self.app = app
        if win_width is None:
            win_width = 800
        if win_height is None:
            win_height = 800
        super().__init__(None, title=title,
                         size=wx.Size(win_width, win_height))
        self.cells = {}         # Dictionary of cells by (ix,iy)
        self.cells_comps = {}   # Dictionary of cell composite items by (ix,iy)
        self._cursor_xy = None  # Cursor, if one, position
                                #   xy pair on canvas (0-max)
        self._cursor_rect = None    # Refresh rectangle, if one
        self._cursor_item = None    # position cursor tag
        self.snapshot_num = snapshot_num
        if tkr is None:
            tkr = TkRPCUser(simulated=True)
        self.tkr = tkr
        SlTrace.lg("USER: Linking AudioDrawWindow to tkr", "adw")
        tkr.set_adw(self)   # Support access, only first

        self.display_list = display_list
        if title is None:
            title = "AudioDrawWindow"
        self.title = title
        control_prefix = "AudioDraw"
        self.win_width = win_width
        self.win_height = win_height
        self.pgmExit = pgmExit
        if x_min is None:
            x_min = 0. if win_fract else 0.
        if y_min is None:
            y_min = 0. if win_fract else 0.
        if x_max is None:
            x_max = 1. if win_fract else self.draw_width()
        if y_max is None:
            y_max = 1. if win_fract else self.draw_height()
        # create the audio feedback window
        self.title = title
        
        self.Show()
        #self.adw_panel = wx.Panel(self)
        if speaker_control is None and setup_wx_win:
            SlTrace.lg("Creating own SpeakerControl")
            speaker_control = SpeakerControlLocal()
        self.speaker_control = speaker_control
        #mw.withdraw()
        
        ###wxport### For print entry support
        self.win_print_entry = None


        self._visible = visible
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.canv_pan = CanvasPanel(self)
        if shift_to_edge is None:
            shift_to_edge = True
        self.shift_to_edge = shift_to_edge
        self.fte = AdwFrontEnd(self, title=title, silent=silent, color=color)
        self.canv_pan.set_key_press_proc(self.fte.key_press)
        self.menus = AdwMenus(self.fte, frame=self)
            
        self.cell_height = self.draw_height()/self.grid_height
        self.set_win_fract(win_fract)
        self.set_x_min(x_min)
        self.set_y_min(y_min)
        self.set_x_max(x_max)
        self.set_y_max(y_max)
        self.set_drawing(drawing)
        ###self.speak_text(title)

        self.escape_pressed = False # True -> interrupt/flush
        #self.set_cell_lims()
        self.do_talking = True      # Enable talking
        self.logging_speech = True  # Output speech to log/screen
        self.from_initial_canvas = False    # True iff from initial drawing
        nrows = grid_height
        ncols = grid_width
        if mag_info is None:
            self.from_initial_canvas = True     # Setup from original canvas
            top_region = MagnifyDisplayRegion(
                win_fract=win_fract,
                x_min=x_min,
                x_max=x_max,
                y_min=y_min,
                y_max=y_max,
                nrows=nrows,
                ncols=ncols)
            if not win_fract:
                x_min, x_max, y_min, y_max = tkr.get_canvas_lims()  # get actual limits
            display_region = MagnifyDisplayRegion(
                win_fract=win_fract,
                x_min=x_min,
                y_min=y_min,
                x_max=x_max,
                y_max=y_max,
                nrows=nrows,
                ncols=ncols)
            mag_info = MagnifyInfo(top_region=top_region,
                                   display_region=display_region)
            self.cell_specs = self.get_cell_specs(
                                        snapshot_num=self.snapshot_num,
                                        win_fract=win_fract,
                                        x_min=x_min,x_max=x_max,
                                        y_min=y_min,y_max=y_max)
        else:
            if mag_info.description:
                title = mag_info.description
                ###wxport###mw.title(title)
                self.title = title
                ###self.speak_text(f"Magnification of {title}")
        mag_info.display_window = self    # Magnification setup
        if mag_info.parent_info is not None:
            mag_info.parent_info.child_infos.append(mag_info)
        self.mag_info = mag_info
        SlTrace.lg(f"\nAudioDrawWindow() mag_info:\n{mag_info}\n",
                   "audio_draw_window")
        self.mag_selection_id = None       # mag selection canvas tag, if one
        self.is_selected = False            # Flag as not yet selected
        self.pos_history = []       # position history (ix,iy)
        self.pos_rep_force_output = False
        self.goto_travel_list = []    # Memory of where we have gone
        self.goto_travel_list_index = None
        self.cell_history = []          # History of all movement
        self.set_grid_path()
        self.running = True         # Set False to stop
        ###wxport###self.mw.focus_force()
        self.blank_char = blank_char
        self.set_look_dist(look_dist)
        #self.pos_check()            # Startup possition check loop
        self.fte.do_complete(menu_str=menu_str, key_str=key_str)
        self.setup_cells()
        self.update(full=True)     # Make visible
        self.Raise()                # put on top

    def setup_cells(self):
        """ Setup/display cells if any
        """
        if self.display_list is not None:
            display_list = self.display_list
            if type(display_list) == str:
                display_list = BrailleCellList().get_from_string(display_list)
            display_cells = {}
            for dc in display_list :
                ix,iy,color = dc.ix,dc.iy,dc._color
                dcell = BrailleCell(ix=ix, iy=iy,
                                    color=color)
                display_cells[(ix,iy)] = dcell
            if SlTrace.trace("cell_spec"):
                SlTrace.lg("from display_list - draw_cells")
        if self.from_initial_canvas:
            SlTrace.lg("from_initial_canvas - draw_cells", "adw")
            self.draw_cells(self.cell_specs)
        self.key_goto()      # Might as well go to figure
        self.find_edges()
        if True:
            self.get_cell_bounds("setup_cells")  # Show figure bounds

    def exit(self, rc=None):
        """ Main exit if creating magnifications
        """
        if rc is None:
            rc = 0
        if self.pgmExit is not None:
            self.pgmExit()      # Use supplied pgmExit
            
        SlTrace.lg("AudoDrawWindow.exit", "adw")
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

    def stop_speak_text(self):
        """ Stop ongoing speach, flushing queue
        """
        self.speaker_control.stop_speak_text()
        
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
        :cells: list of BrailleCell or (ix,iy,color)tuple
                or dictionary of BrailleCell  cells
                to draw
        :show_points: instead of braille, show sample points
        """
        SlTrace.lg("draw_cells", "draw_cells")
        if type(cells) == str:
            tbstk = traceback.extract_stack()
            tbstk_lst = traceback.format_list(tbstk)
            tbstr = "\n".join(tbstk_lst)
            SlTrace.lg(f"draw_cells: {cells} - error?\n{tbstr}\n")
            return
        
        SlTrace.lg(f"x_min:{self.get_x_min()} y_min: {self.get_y_min()}", "draw_cells")
        if cells is None:
            cells = self.get_cells()
        else:
            if not isinstance(cells, dict):
                cs = {}
                for cell in cells:
                    bcell = BrailleCell.tuple_to_braille_cell(cell)
                    cs[(bcell.ix,bcell.iy)] = bcell
                cells = cs
            self.cells = cells      # Copy
        min_x, max_y, max_x,min_y = self.bounding_box(cells=cells)
        if min_x is not None:
            SlTrace.lg(f"Drawn cells bounding box", "draw_cells")            
            SlTrace.lg(f"Upper left: min_x:{min_x} max_y:{max_y}", "draw_cells")
            SlTrace.lg(f"Lower Right: max_x:{max_x} min_y:{min_y}", "draw_cells")
            self.get_cell_bounds("draw_cells", cells=cells)
        SlTrace.lg(f"{len(cells)} cells", "draw_cells")
        for cell in cells.values():
            self.display_cell(cell)
            cell.mtype = cell.MARK_UNMARKED
        if min_x is not None:
            self.set_xy((min_x,min_y))
            x,y = self.get_xy()
            #self.pos_check(x=x,  y=y)
        self.set_grid_path()
        self.pos_history = []       # Clear history
        self.set_scanning()         # Setup positioning info
                    
    def print_braille(self, title=None, shift_to_edge=None):
        """ Output braille display
            with an "identificatin title" created
            from source file name, date, login name
            to start each print for identification
        :title: title default: self.title
        :shift_to_edge: shift figure towards edge to ease finding figure
                        default: self.shift_to_edge
        """
        if self.id_title is not None:
            id_title = self.id_title
        SlTrace.lg(f"print_braille: {id_title = }")
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
            top_edge = 0
            right_edge = self.grid_width-1
            bottom_edge = self.grid_height-1

        braille_text = ""
        for iy in range(top_edge, bottom_edge):
            line = ""
            for ix in range(left_edge, right_edge+1):
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
        data = f"\n{id_title}"
        data += f"\n{title}\n"
        data += braille_text
        SlTrace.lg(f"clipboard data:\n{data}")
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(data))
            wx.TheClipboard.Close()
        else:
            SlTrace.lg("Can't paste to clipboard")

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
        self.add_to_pos_history(loc_ixiy)
        cell_ixiy = self.get_cell_at()
        if cell_ixiy is not None:
            self.cell_history.append(cell_ixiy)
            if not self.is_drawing():   # If we're not drawing
                self.mark_cell(cell_ixiy)   # Mark cell if one
        
        self.cursor_update()

        ###wxport###if not self.mw.winfo_exists():
        ###wxport###    return 
        
        #self.update()
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
                
    def get_ix_min(self):
        """ get minimum ix on grid
        :returns: min ix
        """
        return 0

    def get_ix_max(self):
        """ get maximum ix on grid
        :returns: max ix
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

        

    def bounding_box(self, cells=None, add_edge=None):
        """ canvas coordinates which bound displayed figure
        :cells: list of cells, (with cell.ix,cell.iy) or (ix,iy) tuples
                default: list of all cells in figure
        :add_edge: number of cells to add/subtract (if possible)
                     to enlarge/shrink box
                    default: no change
        :returns: min_x, max_y, max_x, min_y  (upper left) (lower right)
                    None,None,None,None if no figure
        """
        min_ix, min_iy, max_ix, max_iy = self.bounding_box_ci(
                                    cells=cells, add_edge=add_edge)
        if min_ix is None:
            return None,None,None,None      # No figure
        
        min_x, max_y, _, _ = self.get_cell_rect_tur(min_ix,min_iy)
        _, _, max_x, min_y = self.get_cell_rect_tur(max_ix,max_iy)
        SlTrace.lg(f"bounding_box: min_x,max_y, max_x, min_y {min_x,max_y, max_x, min_y}",
                   "bounding_box")
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
        SlTrace.lg(f"bounding_box_ci: ix_min,iy_min, ix_max,iy_max: {ix_min,iy_min, ix_max,iy_max}",
                   "adw")    
        return ix_min,iy_min, ix_max,iy_max
            


    def erase_cell(self, cell, force_refresh=True):
        """ Erase cell
        :cell: BrailleCell
        """
        if cell is None:
            return
        
        # Remove current items, if any
        if cell.canv_items:
            for item_id in cell.canv_items:
                self.canv_pan.delete(item_id)
        cell.canv_items = []
        if force_refresh:
            self.refresh_cell(cell)      # Mark as dirty

    def erase_pos_history(self):
        """ Remove history, undo history marking
        """
        for cell_ixy in self.pos_history:
            if cell_ixy in self.cells:
                cell = self.cells[cell_ixy]
                self.mark_cell(cell, BrailleCell.MARK_UNMARKED)
                self.display_cell(cell)
        self.pos_history = []
        self.remove_mag_selection()    
        ###self.update()
                
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

    def update_cell(self, cell, **kwargs):
        """ Update cell, with "inplace" attribute changes 
        :**kwargs: attributes to be changed
        """
        items = self.get_cell_items(cell)   # Get rectangle item(s)
        if len(items) > 0:
            self.canv_pan.update_item(items[0], **kwargs)
            self.canv_pan.refresh_item(items[0])
        
        
    def display_cell(self, cell, show_points=False):
        """ Display cell
        :cell: BrailleCell
        :show_points: show points instead of braille
                default: False --> show braille dots
        """
        if not cell.is_visible():
            self.erase_cell(cell)
            return              # Nothing to show
        
        ix = cell.ix
        iy = cell.iy
        comp_id = self.canv_pan.create_composite(disp_type=CanvasPanelItem.DT_CELL,
                                                 desc=str(cell))
        cell.canv_items.append(comp_id)
        comp_item = self.canv_pan.id_to_item(comp_id)
        cell.comp_item = comp_item
        self.canv_pan.add_cell(comp_item)   
        cx1,cy1,cx2,cy2 = self.get_win_ullr_at_ixy_canvas((ix,iy))
        SlTrace.lg(f"{ix},{iy}: {cell} :{cx1},{cy1}, {cx2},{cy2} ", "display_cell")
        
        if cell.mtype==BrailleCell.MARK_UNMARKED:
            canv_id = self.canv_pan.create_rectangle(cx1,cy1,cx2,cy2,
                                    fill="#d3d3d3",
                                    outline="dark gray")
        else:
            canv_id = self.canv_pan.create_rectangle(cx1,cy1,cx2,cy2,
                                    fill="#b0b0b0",
                                    outline="dark gray")
        comp_item.add(canv_id)
        
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
                canv_id = self.canv_pan.create_oval(x0,y0,x1,y1,
                                                fill=color)
                cell.canv_items.append(canv_id)
                SlTrace.lg(f"canv_pan.create_oval({x0},{y0},{x1},{y1}, fill={color})", "aud_create")
        else:            
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
                canv_id = self.canv_pan.create_oval(x0,y0,x1,y1,
                                                fill=color)
                comp_item.add(canv_id) 
                SlTrace.lg(f"canv_pan.create_oval({x0},{y0},{x1},{y1}, fill={color})", "aud_create")
        self.refresh_cell(cell) 
        self.cursor_update()
        
    def display_cell_end(self, cell):
        """ Complete cell display
        :cell: BrailleCell to display
        """
        self.refresh_cell(cell) 


    def cell_mtype_to_fill(self, mtype=BrailleCell.MARK_SELECTED):
        """ Convert cell mtype to fill color
        :mtype: cell mark type default: selected
        :returns: fill string
        """
        MARK_UNSELECTED = 1
        MARK_SELECTED = 2
        MARK_TRAVERSED = 3

        fill = "#b0b0b0"    # 
        if mtype == BrailleCell.MARK_SELECTED:
            fill = "#d3d3d3"
        elif mtype == BrailleCell.BrailleCell.MARK_UNSELECTED:
            fill = "#b0b0b0"
        return fill

    def mark_cell(self, cell,
                  mtype=BrailleCell.MARK_SELECTED):
        """ Mark cell for viewing of history
        :cell: Cell(BrailleCell) or (ix,iy) of cell
        :mtype: Mark type default: MARK_SELECTED
        """
        if isinstance(cell, BrailleCell):
            ixy = (cell.ix,cell.iy)
        else:
            ixy = cell
        cells = self.get_cells()
        if ixy in cells:
            cell = cells[ixy]
            cell.mtype = mtype
            #fill = self.cell_mtype_to_fill(mtype)
            #self.update_cell(cell, fill=fill)
            self.display_cell(cell)
            self.refresh_cell(cell)

    def draw_height(self):
        """ drawing area height reduced from window height
        """
        return self.win_height*(21/25)  # Hack for now

    def draw_width(self):
        """ drawing area width reduced from window width
        """
        return self.win_width*(38/40)  # Hack for now
    
    def partial_update_add(self, item):
        """ Add item to partial update
        :item: item to add
        """
        self.canv_pan.partial_update_add(item=item)
        
    def partial_update_complete(self):
        """ Complete partial_update
        """
        self.canv_pan.partial_update_complete()
            
    def partial_update_is_in(self):
        """ Check if in partial update
        """
        return self.canv_pan.partial_update_is_in()
    
    def partial_update_start(self, rect=None):
        """ Setup a partial window update
        :rect: rectangle if present
        """
        self.canv_pan.partial_update_start(rect=rect)
        

                
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
        ix = int((x-x_min)/self.draw_width()*self.grid_width)
        iy = int((y-y_min)/self.draw_height()*self.grid_height)
        #ix = int((x)/self.self.draw_height()*self.grid_width)        # TFD
        #iy = int((y)/self.self.draw_height()*self.grid_height)      # TFD
        return (ix,iy)

    def get_cells(self):
        """ Get cell dictionary (by (ix,iy)
        """
        return self.cells
    
    def iterate_cells(self):
        """ Get an iteratable to traverse cells (BrailleCell)
        :returns: iteratable through cells (BrailleCell)
        """
        return self.get_cells().values()

    def get_cell_rect(self, cell):
        """ Get cell's wx.Rect bounds
        :returns: bounding rectangle wx:Rect
        """
        ix = cell.ix
        iy = cell.iy    
        cx1,cy1,cx2,cy2 = self.get_win_ullr_at_ixy_canvas((ix,iy))
        rect = wx.Rect(wx_Point(cx1,cy1), wx_Point(cx2,cy2))
        return rect
        
    def get_cell_items(self, cell, canv_type="create_rectangle"):
        """ Get cell's item (rectangle)
        :cell: BrailleCell
        :returns: item (in canvas_panel), None if no item
        """
        ix = cell.ix
        iy = cell.iy    
        cx1,cy1,cx2,cy2 = self.get_win_ullr_at_ixy_canvas((ix,iy))
        loc = wx.Point(int((cx1+cx2)/2),
                       int((cy1+cy2)/2))
        items = self.canv_pan.get_panel_items(loc, canv_type=canv_type)
        return items

    def get_overlapping_items(self, item):
        """ Get display items overlapping item
        :item: item(CanvasPanelItem)/id
        :returns: list of overlapping items (CanvasPanelItem)
        """
        item_d = {}     # dictionary by (id)
        if type(item) == int and item in self.canv_pan.items_by_id:
            item = self.canv_pan.items_by_id[item]
        displayed_items = self.get_displayed_items()
        
        for displayed_item in displayed_items:
            if self.is_overlapping(item, displayed_item):
                did = displayed_item.get_id()
                item_d[did] = displayed_item
        item_cells = list(item_d.values())
        return item_cells
            
                   
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
    
    def get_braille_cells(self, 
                        x_min=None, y_min=None,
                        x_max=None, y_max=None,
                        ncols=None, nrows=None):
        """ Get braille cells from remote tk canvas
        :returns: list of BrailleCell
        """        
        
        specs = self.get_cell_specs(
                        win_fract=self.win_fract,
                        x_min=x_min, y_min=y_min,
                        x_max=x_max, y_max=y_max,
                        n_cols=ncols, n_rows=nrows)

        braille_cells = []
        for spec in specs:
            ix,iy,color = spec
            bcell = BrailleCell(ix=ix, iy=iy, color=color)
            braille_cells.append(bcell)
        return braille_cells
    
    def get_cell_specs(self,
                       snapshot_num=None,
                       win_fract=True, 
                        x_min=None, y_min=None,
                        x_max=None, y_max=None,
                        n_cols=None, n_rows=None):
        """ Get cell specs from remote tk canvas
        :returns: list of cell specs (ix,iy,color)
        """
        if snapshot_num is None:
            snapshot_num = self.snapshot_num        
        cell_specs = self.tkr.get_cell_specs(
                        snapshot_num=snapshot_num,
                        win_fract=win_fract,
                        x_min=x_min, y_min=y_min,
                        x_max=x_max, y_max=y_max,
                        n_cols=n_cols, n_rows=n_rows)
        #SlTrace.lg(f"AudioDrawWindow.get_cell_specs: {cell_specs}")
        return cell_specs

    def get_canvas_lims(self, win_fract=True):
        """ Get canvas limits - internal values, to which
        self.base.find_overlapping(cx1,cy1,cx2,cy2) obeys.
        NOTE: These values, despite some vague documentation, may be negative
              to adhere to turtle coordinate settings.
        
        :returns: internal (xmin, xmax, ymin, ymax)
        """
        return self.tkr.get_canvas_lims(win_fract=win_fract)



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
        x_left = int(ix*(self.draw_width()/self.grid_width) + x_min)
        x_right = int((ix+1)*(self.draw_width()/self.grid_width) + x_min)
        y_top = int((iy*(self.draw_height()/self.grid_height) + y_min))
        y_bottom = int((iy+1)*(self.draw_height()/self.grid_height) + y_min)
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
        :returns: x,y canvas tuple (canv_panel)
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

    def refresh_cell(self, cell):
        """ Mark cell dirty, in need of repainting
        :cell: BrailleCell
        """
        brect = self.get_cell_rect(cell)
        SlTrace.lg(f"refresh_cell:{(cell.ix,cell.iy)} {brect}", "refresh")
        self.canv_pan.refresh_rectangle(brect)
                
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
    
    def add_to_pos_history(self, loc_ixiy):
        """ Accumulate position history
        :loc_ixiy: (ix,iy) of current location
        """
        self.pos_history.append(loc_ixiy)   # location history
        SlTrace.lg(f"pos_history:{loc_ixiy}", "pos_tracking")

    
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
        SlTrace.lg("\nclear_cells")
        cells = self.get_cells()
        for cell in list(cells.values()):
            self.erase_cell(cell)
        self.draw_cells(cells=self.cells)
        del self.cells
        self.cells = {}
        self.clear()
        self.key_pendown(False) # Raise pen off paper
        
        
        
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
            self.display_cell(bc)
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

    def update(self, x1=None, y1=None, x2=None, y2=None, full=False):
        """ Update display
            If x1,...y2 are present - limit update to rectangle
        """
        self.canv_pan.update(x1=x1, y1=y1, x2=x2, y2=y2, full=full)

    def MainLoop(self):
        self.app.MainLoop()
        
    def update_idle(self):
        """ Update pending
        """
        #self.Refresh()

    """ Creation/Modification Code
    """

    def create_audio_window(self, title=None,
                 snapshot_num=None,
                 win_width=None,
                 win_height=None,
                 win_fract=True,
                 xmin=None, xmax=None, ymin=None, ymax=None,
                 nrows=None, ncols=None, mag_info=None, pgmExit=None,
                 require_cells=False,
                 silent=False,
                 cell_specs=None):
        """ Create new AudioDrawWindow to navigate canvas from the section
        :title: optional title
                region (xmin,ymin, xmax,ymax) with nrows, ncols
        :snapshot_num: create a snapshot of current window
                default: track main window
        :win_width: window width default: self.win_width
        :win_height: window height default: self.draw_height()
        :speaker_control: (SpeakerControlLocal) local access to centralized speech facility
        :win_fract: True - xmin,xmax... are fractions 0. to 1. of window region
        :xmin,xmax,ymin,ymax,: see get_grid_lims()
                        default: CanvasGrid instance values
        :nrows,ncols: grid size for scanning
                default: if mag_info present: mag_info.mag_nrows, .mag_ncols
        :mag_info: magnification info (MagnifyInfo)
                    default: None
        :pgm_exit: function to call upon exit request
        :require_cells: Require at least some display cells to 
                    create window
                    default: False - allow empty picture
        :silent: quiet mode default: False
        :cell_specs: cells to display default: check for cells
        :returns: AudioDrawWindow instance or None if no cells
                Stores number of cells found in self.n_cells_created
        """
        if title is None:
            title = self.title
        self.title = title
        if pgmExit is None:
            pgmExit = self.exit 

        if mag_info is not None:
            title = f"Magnification {mag_info.description}"
        else:
            mag_info = self.create_magnify_info(
                                          x_min=xmin, y_min=ymin,
                                          x_max=xmax, y_max=ymax,
                                          ncols=ncols, nrows=nrows)
        if snapshot_num is None:
            snapshot_num = self.snapshot_num
                
        if nrows is None:
            nrows = mag_info.mag_nrows
        if ncols is None:
            ncols = mag_info.mag_ncols
        if cell_specs is None:        
            cell_specs = self.get_cell_specs(win_fract=win_fract,
                                            x_min=xmin, y_min=ymin,
                                            x_max=xmax, y_max=ymax,
                                            n_cols=ncols, n_rows=nrows)    
        self.n_cells_created = len(cell_specs)
        SlTrace.lg(f"create_audio_window:"
                   f" {self.n_cells_created} cells")
        SlTrace.lg(f"cell_specs: {cell_specs}", "cell_specs")
        if self.n_cells_created == 0:
            if require_cells:
                return None
                
        adw = AudioDrawWindow(tkr=self.tkr,
                              snapshot_num=snapshot_num,
                              app=self.app,
                              id_title=self.id_title,
                              title=title,
                              speaker_control=self.speaker_control,
                              iy0_is_top=True, mag_info=mag_info,
                              pgmExit=pgmExit,
                              win_width=win_width,
                              win_height=win_height,
                              x_min=xmin,
                              y_min=ymin,
                              x_max=xmax,
                              y_max=ymax,
                              silent=silent)
        adw.draw_cells(cells=cell_specs)
        adw.key_goto()      # Might as well go to figure
        return adw


    def create_magnify_info(self, x_min=None,y_min=None,
                    x_max=None,y_max=None,
                    ncols=None, nrows=None):
        """ Create a MagnifyInfo, using our values as defaults
        :x_min: minimum x value - left side 
        :y_min: minimum y value - top side
        :x_max: maximum x value - right side
        :y_max: maximum  y value - bottom side
        :ncols: number of grid columns
        :nrows: number of grid rows
        """
        if x_min is None:
            x_min = self.get_x_min()
        if y_min is None:
            y_min = self.get_y_min()
        if x_max is None:
            x_max = self.get_x_max()
        if y_max is None:
            y_max = self.get_y_max()
        if ncols is None:
            ncols = self.grid_width
        if nrows is None:
            nrows = self.grid_width
        
        top_region = MagnifyDisplayRegion(x_min=x_min, y_min=y_min,
                                          x_max=x_max, y_max=y_max,
                                          ncols=ncols, nrows=nrows)
        mag_info = MagnifyInfo(top_region=top_region,
                               base_canvas=self)
        return mag_info
                   
    def get_cell_bounds(self, title=None, cells=None, add_edge=0, display_region=None,
                        special=False):
        """ Get cell list bounds
        :title: optional title display default: no title
        :cells: list of cells, (with cell.ix,cell.iy) or (ix,iy) tuples
                default: list of all cells in figure
        :add_edge: number of cells to add/subtract (if possible)
                     to enlarge/shrink box
                    default: no change
        :display_region: (MagnifyDisplayRegion) display region
        :special: True - suppress extra display e.g. non-None cells processing
        :returns: xmin,ymin (upper left), xmax,ymax (lower right) display
        """
        if title is not None:
            SlTrace.lg(f"\n{title}", "cell_bounds")
        if not special and cells is not None:
            SlTrace.lg("Full display bounds", "cell_bounds")
            self.get_cell_bounds(cells=[(0,0), (self.grid_width-1,self.grid_height-1)],
                                 special=True)
            SlTrace.lg("\nFull figure bounds", "adw")
            self.get_cell_bounds(cells=None)
        ix_min, iy_min, ix_max, iy_max = self.bounding_box_ci(cells, add_edge)
        if display_region is None:
            di = self.get_mag_info()
            if di is None:
                SlTrace.lg("No Magnification Info")
                return None,None,None,None
            display_region = di.display_region
        dr = display_region
        disp_x_cell = (dr.x_max-dr.x_min)/dr.ncols
        disp_y_cell = (dr.y_max-dr.y_min)/dr.nrows
        xmin = ix_min*disp_x_cell + dr.x_min
        ymin = iy_min*disp_y_cell + dr.y_min
        xmax = (ix_max+1)*disp_x_cell + dr.x_min
        ymax = (iy_max+1)*disp_y_cell + dr.y_min
        SlTrace.lg(f"bounding indexes: ix_min:{ix_min}, iy_min:{iy_min}"
                   f", ix_max:{ix_max}, iy_max:{iy_max}", "cell_bounds")
        SlTrace.lg(f"cell bounds:"
                   f" xmin:{xmin} ymin:{ymin} xmax:{xmax} ymax:{ymax}"
                   f" nrows:{dr.nrows} ncols:{dr.ncols}", "cell_bounds")
                   
    def create_magnification_window(self, mag_info, adj_cell=.1):
        """ Create magnification
        :mag_info: MagnificationInfo containing info
        :adj_cell: Expansion adjustment fraction of cell
                default: 0
        :returns: instance of AudioDrawWinfow or None if none was created
        """
        select = mag_info.select
        disp_region = mag_info.display_region
        disp_x_cell = (disp_region.x_max-disp_region.x_min)/disp_region.ncols
        disp_y_cell = (disp_region.y_max-disp_region.y_min)/disp_region.nrows
        xmin = select.ix_min*disp_x_cell + disp_region.x_min - adj_cell*disp_x_cell
        ymin = select.iy_min*disp_y_cell + disp_region.y_min - adj_cell*disp_y_cell
        xmax = (select.ix_max+1)*disp_x_cell + disp_region.x_min + adj_cell*disp_x_cell
        ymax = (select.iy_max+1)*disp_y_cell + disp_region.y_min + adj_cell*disp_y_cell
        SlTrace.lg(f"create_magnification_window:"
                   f" xmin:{xmin} ymin:{ymin} xmax:{xmax} ymax:{ymax}"
                   f" nrows:{disp_region.nrows} ncols:{disp_region.ncols}", "adw")
        child_info = mag_info.make_child()
        child_info.display_region = MagnifyDisplayRegion(x_min=xmin, x_max=xmax,
                                        y_min=ymin, y_max=ymax)
        child_info.description = (f"{child_info.info_number}"
                                  + f" region min x: {xmin:.2f}, min y: {ymin:.2f},"
                                  + f" max x: {xmax:.2f}, max y: {ymax:.2f}")
        SlTrace.lg(f"create_audio_window: snapshot_num={self.snapshot_num}")
        adw = self.create_audio_window(snapshot_num=self.snapshot_num,
                                       xmin=xmin, xmax=xmax,
                                       ymin=ymin, ymax=ymax,
                                       nrows=disp_region.nrows,
                                       ncols=disp_region.ncols,
                                       mag_info=child_info,
                                       require_cells=True)            
        return adw 


    def cursor_update(self):
        """ Update cursor (current position) display
        Cursor is displayed at end of OnPaint
        
        """
        self._cursor_xy = self.get_xy_canvas()
        self.canv_pan.refresh_cursor()   # Remove old cursor, if any

        if self.mag_selection_id is not None:
            self.canv_pan.add_item(self.mag_selection_id)

    # REPLACED to set cursor
    # which is diplayed at end of OnPaint()
    def cursor_update_OLD(self):
        """ Update cursor (current position) display
        """
        self.remove_cursor()
        self.add_cursor()
        self.refresh_cursor()
        if self.mag_selection_id is not None:
            self.canv_pan.add_item(self.mag_selection_id)


    def refresh_cursor(self):
        """ Refresh cursor update
        """
        if self._cursor_item is not None:
            self.refresh_item(self._cursor_item)
                
    def remove_cursor(self):
        """ Remove old cursor if one"""
        if self._cursor_item is not None:
            overlapping_items = self.get_overlapping_items(self._cursor_item)
            self.canv_pan.delete(self._cursor_item)
            self._cursor_item = None
            for item in overlapping_items:
                self.canv_pan.add_item(item)
    
    def add_cursor(self):
        """ Add new cursor display
        """            
        rd = 5
        pos_x,pos_y = self.get_xy_canvas()

        x0 = pos_x-rd
        x1 = pos_x+rd
        y0 = pos_y-rd
        y1 = pos_y+rd
        self._cursor_item = self.canv_pan.create_cursor(x0,y0,x1,y1,
                                                    disp_type=CanvasPanelItem.DT_CURSOR,
                                                    fill="red")
        self.canv_pan.add_cursor(self._cursor_item)
        overlapping_items = self.get_overlapping_items(self._cursor_item)
        for item in overlapping_items:
                self.canv_pan.add_item(item)

    """
    Links to canvas_grid
    """
        
    def get_cell_rect_tur(self, ix, iy):
        """ Get cell's turtle rectangle x, y  upper left, x,  y lower right
        :ix: cell x index
        :iy: cell's  y index
        :returns: (min_x,max_y, max_x,min_y)
        """
        return self.tkr.get_cell_rect_tur(ix=ix, iy=iy)

    """
    Links to canvas panel - most are direct
    """
    
    def clear(self):
        """ Clear panel
        """
        self.canv_pan.clear()
        self.set_cursor_pos_win()
        
    def redraw(self):
        """ Redraw screen
        """
        self.canv_pan.redraw()

    def refresh_item(self, item):
        self.canv_pan.refresh_item(item)

    def get_displayed_items(self):
        """ Get list of displayed items
        :returns: list of permanently displayed values (AdwDisplayPendingItem)
        """
        return self.canv_pan.get_displayed_items()

    def is_overlapping(self, item1, item2):
        """ Check if two display items are overlapping
        :returns: True iff overlapping
        """
        return self.canv_pan.is_overlapping(item1, item2)

    """
         Links to front end functions
    """
    def is_pendown(self):
        """ Test if pen is down (marking)
        """
        return self.fte.is_pendown()
    
    
    def key_pendown(self, val=True):
        """ Lower/raise pen (starting,stopping) drawing
        :val: lower pen, if True else raise pen
        """
        self.fte.key_pendown(val)


    def set_initial_location(self):
        """ Set/Reset initial location of cursor
        """
        self.fte.set_initial_location()


    def is_inbounds(self,ix=None, iy=None):
        """ Test if inbounds
        :ix: x index - default: don't test
        :iy: y index - default: don't test
        :returns: True iff in bounds
        """
        return self.fte.is_inbounds(ix=ix, iy=iy)

    def remove_mag_selection(self):
        """ Remove magnify selection and marker
        """
        self.fte.remove_mag_selection()

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
    
    def set_win_fract(self, val):
        """ Set fraction indicator
        :val: new win_fract
        :returns: new win_fract
        """
        return self.fte.set_win_fract(val)

    def get_win_fract(self):
        return self.fte.get_win_fract()
    
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
    SlTrace.setupLogging(logToScreen=True)
    def test_window_ops():
        SlTrace.clearFlags()
        app = wx.App()
        
        
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

        key_str = (
                    "d"
                    ";c;g;9;9;9;9"
                    ";c;r;7;7;7;7"
    
                    ";w"
                )
        
        key_str = ""
        
        tkr = TkRPCUser(simulated=True)
        aw = AudioDrawWindow(tkr=tkr,
                            id_title = "Selftest-no turtle",
                            title="AudioDrawWindow Self-Test",
                            app=app,
                            menu_str=menu_str,
                            key_str=key_str,
                            silent=False)
        '''
        aw.fte.do_menu_str("n:nu;d:s")
        aw.fte.do_key_str("u")
        '''
        
        aw.MainLoop()

    def test_tk_track(figure=1):
        SlTrace.clearFlags()
        app = wx.App()
        SlTrace.lg("After clearFlags")
        SlTrace.lg("Checking talk_cmd", "talk_cmd")
        tkr = TkRPCUser(simulated=True, figure=figure)
        aw = AudioDrawWindow(tkr=tkr,
                            title="AudioDrawWindow Self-Test",
                            app=app,
                            silent=False)
        
        #SlTrace.setFlags("refresh,draw_rect,draw_oval,mouse_cell")
        aw.MainLoop()
    
    test_window_ops()
    #test_tk_track(figure=1)
    #test_tk_track(figure=2)
