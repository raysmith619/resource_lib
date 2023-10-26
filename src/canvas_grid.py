#canvas_grid.py    14Feb2023  crs  Author
"""
Basis for nestable grid layout within the standard tkinter Canvas Widget.
The plan, which emanates from my TurtleBraille system to aid the viewing,
by the blind of simple turtle graphics.  Our target is a system by which
one is able to segment a canvas based graphic, as a coarse picture (e.g. 40 by 25)
and then easily select a rectangular subsection and then create a similar coarse
picture (e.g. 40 by 25) of that subsection.
The hope is to provide a magnified rendition of a selectable section of a given canvas.

Provide list of canvas items overlapping a region (display cell rectangle).

"""
import tkinter as tk
import sys
import os
import copy

from select_trace import SlTrace
from braille_error import BrailleError
from braille_cell import BrailleCell
from magnify_info import MagnifySelect, MagnifyInfo, MagnifyDisplayRegion
from audio_draw_window import AudioDrawWindow
from speaker_control import SpeakerControlLocal

"""
We now think explicit .base.fn_name is better
for indirect call of tk.Canvas calls:
    find_overlapping, gettags, itemconfigure, type
"""

class CanvasGrid(tk.Canvas):
        
    def __init__(self, master, base=None,
                 pgmExit=None, speaker_control=None,
                 g_xmin=None, g_xmax=None, g_ymin=None, g_ymax=None,
                 g_nrows=25, g_ncols=40,
                 **kwargs):
        """ Set up canvas object with grid
        :base: tk.Canvas, if present, from which we get
                canvas item contents
                default: self
        :pgmExit: program main exit if one default: use local (...os._exit)
        :speaker_control: (SpeakerControlLocal) local access to speech facility
                        REQUIRED
        :g_xmin: Grid minimum canvas coordinate value default: left edge
        :g_xmax: Grid maximum canvas coordinate value default: right edge
        :g_ymin: Grid minimum canvas coordinate value default: top edge
        :g_ymax: Grid maximum canvas coordinate value default: bottom edge
        :g_nrows: Number of rows default: 25
        :g_ncols: Number of columns default: 40
        """
        if base is None:
            base = self 
        self.base = base
        if speaker_control is None:
            SlTrace.lg("Creating local SpeakerControl copy")
            speaker_control = SpeakerControlLocal(win=master)   # local access to speech engine
        self.pgmExit = pgmExit
        self.speaker_control = speaker_control
        self.item_samples = {}      # For incremental presentation  via show_item
        self.audio_wins = []        # window list for access
        self.n_cells_created = 0    # Number of cells in recent window
        super(CanvasGrid,self).__init__(master=master, **kwargs)
        self.pack(expand=True, fill=tk.BOTH)
        self.master.update()
        if g_xmin is None:
            g_xmin = 0
        self.g_xmin = g_xmin
        if g_xmax is None:
            g_xmax = g_xmin + self.winfo_width()
        self.g_xmax = g_xmax
        self.g_width = g_xmax-g_xmin
        if g_ymin is None:
            g_ymin = 0
        self.g_ymin = g_ymin
        if g_ymax is None:
            g_ymax = g_ymin + self.winfo_height()
        self.g_ymax = g_ymax
        self.g_height = abs(g_ymax-g_ymin) # No questions
        self.g_nrows = g_nrows
        self.g_ncols = g_ncols
        self.grid_tag = None        # Most recent grid paint tag
        self.set_grid_lims()
        self.master.withdraw()
        
    def get_grid_lims(self, xmin=None, xmax=None, ymin=None, ymax=None,
                      ncols=None, nrows=None):
        """ create grid boundary values bottom through top, given limits
         so:
             grid_xs[0] == left edge
             grid_xs[grid_width] == right edge
             grid_ys[0] == top edge
             grid_ys[grid_height] == bottom edge
             cell(i,j): grid_xs[i], grid_xs[i+1], grid_ys[j], grid_ys[j+1]
            All coordinates are in canvas values: y==0 at top, increasing down
        :xmin: minimum x default: self.g_xmin
        :xmax: maximim x default: self.g_xmax
        :ymin: minimum y default: self.g_ymin
        :ymax: maximim y defailt: self.g_ymax
        :ncols: grid horizontal columns default: self.g_ncols
        :nrows: grid vertical rows default: self.g_nrows
        :returns: (grid_xs,grid_ys) - list of x limits, list of y limits
        """
        if xmin is None:
            xmin = self.g_xmin 
        if xmax is None:
            xmax = self.g_xmax 
        if ymin is None:
            ymin = self.g_ymin 
        if ymax is None:
            ymax = self.g_ymax 
        if ncols is None:
            ncols = self.g_ncols 
        if nrows is None:
            nrows = self.g_nrows 
            
        g_width = abs(xmax-xmin)
        g_height = abs(ymax-ymin) 
        grid_xs = []
        grid_ys = []

        for i in range(ncols+1):
            x = xmin + i*g_width/ncols
            grid_xs.append(x)
        for i in range(nrows+1):
            y = ymin + i*g_height/nrows
            grid_ys.append(y)
        return grid_xs,grid_ys
        
    def set_grid_lims(self):
        """ create grid boundary values bottom through top
         so:
             grid_xs[0] == left edge
             grid_xs[grid_width] == right edge
             grid_ys[0] == top edge
             grid_ys[grid_height] == bottom edge
             cell(i,j): grid_xs[i], grid_xs[i+1], grid_ys[j], grid_ys[j+1]
        """
        self.grid_xs, self.grid_ys = self.get_grid_lims()

    def create_audio_window(self, title=None,
                 xmin=None, xmax=None, ymin=None, ymax=None,
                 nrows=None, ncols=None, mag_info=None, pgmExit=None,
                 require_cells=False,
                 silent=False):
        """ Create AudioDrawWindow to navigate canvas from the section
        :title: optinal title
                region (xmin,ymin, xmax,ymax) with nrows, ncols
        :speaker_control: (SpeakerControlLocal) local access to centralized speech facility
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
        :returns: AudioDrawWindow instance or None if no cells
                Stores number of cells found in self.n_cells_created
        """
        if pgmExit is None:
            pgmExit = self.exit 

        if mag_info is None:
            mag_info = self.create_magnify_info(x_min=xmin, y_min=ymin,
                                          x_max=xmax, y_max=ymax,
                                          ncols=ncols, nrows=nrows)
            
        if nrows is None:
            nrows = mag_info.mag_nrows
        if ncols is None:
            ncols = mag_info.mag_ncols    
        ixy_items = self.get_canvas_items(xmin=xmin, xmax=xmax,
                                          ymin=ymin,ymax=ymax,
                                          ncols=ncols,nrows=nrows)
        # For debugging / analysis
        xs,ys = self.get_grid_lims(xmin=xmin, xmax=xmax, ymin=ymin,ymax=ymax,
                                   ncols=ncols,nrows=nrows)
        braille_cells = []
        for ixy_item in ixy_items:
            (ix,iy), ids = ixy_item
            if SlTrace.trace("win_items"):
                SlTrace.lg(f"create_audio_window:{ix},{iy}: ids:{ids}")
                for canvas_id in ids:
                    self.show_canvas_item(canvas_id)
            color = self.item_to_color(item_ids=ids)
            if color is not None:
                bcell = BrailleCell(ix=ix, iy=iy, color=color)
                braille_cells.append(bcell)
        self.n_cells_created = len(braille_cells)
        if self.n_cells_created == 0:
            if require_cells:
                return None
                
        adw = AudioDrawWindow(title=title, speaker_control=self.speaker_control,
                              iy0_is_top=True, mag_info=mag_info, pgmExit=pgmExit,
                              x_min=self.g_xmin, y_min=self.g_ymin,
                              silent=silent)
        adw.draw_cells(cells=braille_cells)
        adw.key_goto()      # Might as well go to figure
        self.audio_wins.append(adw)     # Store list for access
        return adw

    def item_to_color(self, item_ids):
        """ Get color string given item id
            Ignore items with fill tuple ending with ''
        :item_ids: list of canvas ids for item
        :returns: color str or None if no item with valid color
        """
        for top_id in reversed(item_ids):
            color_tuple = self.base.itemconfigure(top_id, "fill")
            color = color_tuple[-1]
            if color != '':
                return color       # Take first that has a color  not ''
        return None
        
    def display_cell(self, ixy_item, mark_type=None):
        """ Display grid square based on graphics
        :ixy: (ix,iy) tuple for location
        :mark_type: type one of "braille" - simulated braille
                                "square" - square of cell
                    default: "square"
        """
        (ix,iy), ids = ixy_item
        
        if mark_type is None:
            mark_type = "square"
        color = self.item_to_color(item_ids=ids)
        if color is not None:
            w_left_x,w_upper_y, w_right_x,w_lower_y = self.get_grid_ullr(ix=ix, iy=iy)
            self.create_rectangle(w_left_x, w_upper_y, w_right_x, w_lower_y,
                                  outline=color, width=3)

    def display_cells(self):
        items = self.get_canvas_items()
        for item in items:
            self.display_cell(item)
                    
    def paint_grid(self, color="gray", grid_tag="grid_tag", width=2):
        """ paint grid lines for diagnostic purposes
        :color: grid line color default:gray
        :grid_tag: tag for grid canvas items
        :width: line width default: 2
        """
        self.grid_tag = grid_tag
        width_edge = 7         # So it shows up
        width_now = width
        for i in range(len(self.grid_xs)):          # vertical lines
            x1,x2 = self.grid_xs[i],self.grid_xs[i]
            y1,y2 = self.grid_ys[0],self.grid_ys[len(self.grid_ys)-1]
            width_now = width_edge if i == 0 or i == len(self.grid_xs)-1 else width
            self.create_line(x1,y1,x2,y2, fill=color, tag=grid_tag, width=width_now)
            self.update()
            pass
        for i in range(len(self.grid_ys)):        # horizontal lines
            y1,y2 = self.grid_ys[i],self.grid_ys[i]
            x1,x2 = self.grid_xs[0],self.grid_xs[len(self.grid_xs)-1]
            width_now = width_edge if i == 0 or i == len(self.grid_ys)-1 else width
            self.create_line(x1,y1,x2,y2, fill=color, tag=grid_tag, width=width_now)
            
        self.update()

    def erase_grid_paint(self, grid_tag=None):
        """ Erase painted grid
        :grid_tag: grid_tag used default: self.grid_tag - last grid painted
        """
        if grid_tag is None:
            grid_tag = self.grid_tag
        if grid_tag is not None:
            self.delete(grid_tag)
            self.grid_tag = None
            self.update()

                       
    def get_grid_ullr(self, ix, iy, xs=None, ys=None):
        """ Get cell's canvas rectangle x, y  upper left, x,  y lower right
        
        :ix: cell x index
        :iy: cell's  y index
        :xs: grid x-values default: self.grid_xs
        :ys: grid y-values default: self.grid_ys 
        :returns: grid cell limits: (w_left_x,w_upper_y,
                                  w_right_x,w_lower_y) where
            w_left_x,w_upper_y: are upper left coordinates
            w_right_x,w_lower_y: are lower right coordinates
            Out of bounds - returns min/max in that direction
        """
        if xs is None:
            xs = self.grid_xs
        if ys is None:
            ys = self.grid_ys
        ixmax = len(xs)-2           # last element is upper bound
        iymax = len(ys)-2
        w_left_x = xs[0]            # left edge
        w_upper_y = ys[0]           # top edge
        w_right_x = xs[ixmax-1]
        w_lower_y = ys[iymax-1]
        
        if ix >= 0:
            if ix <= ixmax:
                w_left_x = xs[ix]
                w_right_x = xs[ix+1]
            else:
                w_left_x = xs[ixmax]
                w_right_x = xs[ixmax+1]
        if iy >= 0:
            if iy <= iymax:
                w_upper_y = ys[iy]
                w_lower_y = ys[iy+1]
            else:
                w_upper_y = ys[iymax]
                w_lower_y = ys[iymax+1]
        return (w_left_x,w_upper_y, w_right_x,w_lower_y)


    def get_canvas_items(self,
                        xmin=None, xmax=None, ymin=None, ymax=None,
                        ncols=None, nrows=None,
                        types=None, ex_types=None,
                        tags=None, ex_tags=None, get_color=False):
        """ Get items within grid cells
        :xmin,xmax,ymin,ymax, ncols, nrows: see get_grid_lims()
                        default: CanvasGrid instance values
        :types: list of types, select only items of these types default: All types
        :ex_types: List of types select only items not these types
                Only one of types or ex_types is allowed
        :tags: list of tags, include only items with one of these tags default: allow any tags
        :ex_tags: list of tags, exclude items with any of these tags default: no exclusions
                Only one of tags or ex_tags is allowed
        :get_color: True - returns list of cell colors default: return cell id
        :returns: list of overlapping canvas entries
                list entry format: tuple:
                                (ix,iy) - rectangle x index,  y index
                                    get_color==True: color
                                        list of entry info
                                    get_color==False: canvas item id
                                        color string
        """
                        # Get grid limites - defaulting to self.values
        xs,ys = self.get_grid_lims(xmin=xmin, xmax=xmax, ymin=ymin,ymax=ymax,
                                   ncols=ncols,nrows=nrows)
        ixy_ids_list = []       # Building list of (ix,iy), [overlapping ids]
        if types is not None and ex_types is not None:
            raise BrailleError("Don't support both types and ex_types")
         
        if tags is not None and ex_tags is not None:
            raise BrailleError("Don't support both tags and ex_tags")
         
        if types is not None:       # Support single or list of
            if not isinstance(types, list):
                types = [types]     # Make it a list
        if ex_types is not None:
            if not isinstance(ex_types, list):
                ex_types = [ex_types]     # Make it a list
        if tags is not None:
            if not isinstance(tags, list):
                tags = [tags]
        if ex_tags is not None:
            if not isinstance(ex_tags, list):
                ex_tags = [ex_tags]
        
        SlTrace.lg(f"get_canvas_items"
                   f" xmin={xmin}, xmax={xmax}, ymin={ymin}, ymax={ymax}", "get_items")
        for ix in range(len(xs)-1):
            for iy in range(len(ys)-1):
                cx1,cy1,cx2,cy2 = self.get_grid_ullr(ix=ix, iy=iy, xs=xs, ys=ys)
                item_ids_over_raw = self.base.find_overlapping(cx1,cy1,cx2,cy2)
                if SlTrace.trace("get_items"):
                    if len(item_ids_over_raw) > 0:
                        color = self.item_to_color(item_ids=item_ids_over_raw)
                    else:
                        color = ""
                    SlTrace.lg(f"    {ix},{iy}: cx1,cy1,cx2,cy2 {cx1},{cy1},{cx2},{cy2}"
                               f" item_ids: {item_ids_over_raw} {color}",
                               "get_items")
                if len(item_ids_over_raw) == 0:
                    continue    # Skip if none to check
                
                if (types is None and ex_types is None 
                        and tags is None and ex_tags is None):
                    item_ids_over = item_ids_over_raw     # Everything
                else:
                    item_ids_over = []
                    for item_id in item_ids_over_raw:
                        chosen = True 
                        if types:
                            itype = self.base.type(item_id)
                            if itype in types:
                                chosen = True    # Has required type
                            else:
                                chosen = False 
                        if ex_types:
                            itype = self.base.type(item_id)
                            if itype in ex_types:
                                chosen = False 
                            else:
                                chosen = True     
                        if chosen and tags:
                            chosen = False      # Set True if found
                            tag_list = self.base.gettags(item_id)
                            for tag in tag_list:
                                if tag in tags:
                                    chosen = True   # Has requisite flag 
                                    break
                        if chosen and ex_tags:
                            chosen = True      # Set False if found
                            tag_list = self.base.gettags(item_id)
                            for tag in tag_list:
                                if tag in ex_tags:
                                    chosen = False  # Has an excluded tag 
                                    break
                        if chosen:
                            item_ids_over.append(item_id)
                if len(item_ids_over) > 0:
                    if get_color:
                        color = self.item_to_color(item_ids=item_ids_over)
                        item_infos_over = color         # color string
                    else:
                        item_infos_over = item_ids_over # list of ids
                    ixy_ids_list.append(((ix,iy), item_infos_over))
        return ixy_ids_list

    def show_canvas(self, title=None, types=None, ex_types=None,
                  tags=None, ex_tags=None, get_color=False,
                  always_list=None,
                  xmin=None,ymin=None, xmax=None,ymax=None,
                  ncols=1,nrows=1,
                  prefix=None):
        """ Show whole canvas
            see show_canvas_items for args
        """
        if title is not None:
            SlTrace.lg(title)
        canvas_items = self.base.find_all()
        if len(canvas_items) == 0:
            SlTrace.lg("No canvas items")
            return
        
        for item_id in canvas_items:
            self.show_canvas_item(item_id=item_id, prefix=prefix)
        
    def show_canvas_items(self, title=None, types=None, ex_types=None,
                  tags=None, ex_tags=None, get_color=False,
                  always_list=None,
                  xmin=None,ymin=None, xmax=None,ymax=None,
                  ncols=None,nrows=None,
                  prefix=None):
        """ Show canvas items
        Args are those of get_canvas_items plus
        :title: title default: generated
        :always_list: list of options always listed
                    default: show_canvas_items default
        :prefix: prefix to output, used by show_canvas_item
        :xmin,...: default: self.xmin...
        """
        if title is not None:
            SlTrace.lg(title)
        ixy_ids_list = self.get_canvas_items(types=types,
                                ex_types=ex_types,
                                tags=tags, ex_tags=ex_tags,
                                get_color=get_color,
                                xmin=xmin,ymin=ymin, xmax=xmax,ymax=ymax,
                                ncols=ncols,nrows=nrows,
                                )
        xs,ys = self.get_grid_lims(xmin=xmin,ymin=ymin, xmax=xmax,ymax=ymax,
                                ncols=ncols,nrows=nrows)
        ixy_item_prefix = "" if prefix is None else prefix
        SlTrace.lg(f"{ixy_item_prefix} xs: {xs}")
        SlTrace.lg(f"{ixy_item_prefix} ys: {ys}")
        for ixy_item in ixy_ids_list:
            (ix,iy), ids = ixy_item
            ixy_item_prefix = "" if prefix is None else prefix
            w_left_x,w_upper_y, w_right_x,w_lower_y = self.get_grid_ullr(ix, iy,
                                                                     xs=xs,ys=ys)
            ixy_item_prefix += f" {ix},{iy}:"
            ixy_item_prefix +=  f" [{w_left_x},{w_upper_y}, {w_right_x},{w_lower_y}]"
            if len(ids) > 1:
                SlTrace.lg("")
            for item_id in ids:
                self.show_canvas_item(item_id=item_id, prefix=ixy_item_prefix,
                                      always_list=always_list)

                        
    def show_canvas_item(self, item_id, always_list=None,
                          prefix=None):
        """ display changing values for item
        :always_list: list of options which are always listed
                default: ['fill', 'width']
        """
        if prefix is None:
            prefix = ""
        if prefix != "" and not prefix.endswith(" "):
            prefix += " "       # leave some space
        if always_list is None:
            always_list = ['fill', 'width']  # Check always list
        iopts = self.base.itemconfig(item_id)
        itype = self.base.type(item_id)
        coords = self.base.coords(item_id)
        if itype in self.item_samples:
            item_sample_iopts = self.item_samples[itype]
        else:
            item_sample_iopts = None
     
        SlTrace.lg(f"{prefix} {item_id}: {itype} {coords}")
        ###self.show_coords(coords)
        
        for key in iopts:
            val = iopts[key]
            is_changed = True     # assume entry option changed
            if key not in always_list:  
                if item_sample_iopts is not None:
                    is_equal = True # Check for equal item option
                    sample_val = item_sample_iopts[key]
                    if len(val) == len(sample_val):
                        for i in range(len(val)):
                            if val[i] != sample_val[i]:
                                is_equal = False
                                break
                        if is_equal:
                            is_changed = False
            if is_changed:
                if isinstance(val, float):
                    SlTrace.lg(f"    {key} {val:.2f}")
                else:                     
                    SlTrace.lg(f"    {key} {val}")
            self.item_samples[itype] = iopts

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
            x_min = self.g_xmin
        if y_min is None:
            y_min = self.g_ymin
        if x_max is None:
            x_max = self.g_xmax
        if y_max is None:
            y_max = self.g_ymax
        if ncols is None:
            ncols = self.g_ncols
        if nrows is None:
            nrows = self.g_nrows
        
        top_region = MagnifyDisplayRegion(x_min=x_min, y_min=y_min,
                                          x_max=x_max, y_max=y_max,
                                          ncols=ncols, nrows=nrows)
        mag_info = MagnifyInfo(top_region=top_region,
                               base_canvas=self)
        return mag_info

    def get_mag_info_ullr(self, mag_info):
        """ Get boundaries from mag_info
        :mag_info: (MagnifyDisplayRegion)
        :returns: (left_x,upper_y,
                                    right_x,lower_y)
        """ 
        select = mag_info.select
        disp_region = mag_info.display_region
        if disp_region.ncols is None:
            disp_region.ncols = self.g_ncols
        if disp_region.nrows is None:
            disp_region.nrows = self.g_nrows
        disp_x_cell = (disp_region.x_max-disp_region.x_min)/disp_region.ncols
        disp_y_cell = (disp_region.y_max-disp_region.y_min)/disp_region.nrows
        xmin = select.ix_min*disp_x_cell + disp_region.x_min
        ymin = select.iy_min*disp_y_cell + disp_region.y_min
        xmax = (select.ix_max+1)*disp_x_cell + disp_region.x_min
        ymax = (select.iy_max+1)*disp_y_cell + disp_region.y_min
        return (xmin,ymin, xmax,ymax)   # left, top, right, bottom

    def show_mag_info_items(self, mag_info, ix, iy,
                            title=None, types=None, ex_types=None,
                  tags=None, ex_tags=None, get_color=False,
                  always_list=None,
                  prefix=None):
        """ Display canvas items for display
        :mag_info: (MagnifyDisplayRegion)
        :ix: ix index in mag_info
        :iy: iy index in mag_info
        """
        mag_info_copy = copy.copy(mag_info)     # Don't modify original
        mag_info_copy.select = MagnifySelect(ix_min=ix,ix_max=ix,
                                              iy_min=iy,iy_max=iy)
        xmin,ymin,xmax,ymax = self.get_mag_info_ullr(mag_info=mag_info_copy)
        self.show_canvas_items(title=title, types=types, ex_types=ex_types,
                  tags=tags, ex_tags=ex_tags, get_color=get_color,
                  always_list=always_list,
                  xmin=xmin,ymin=ymin, xmax=xmax,ymax=ymax,
                  ncols=1,nrows=1,
                  prefix=prefix)

                   
    def create_magnification_window(self, mag_info):
        """ Create magnification
        :mag_info: MagnificationInfo containing info
        :returns: instance of AudioDrawWinfow or None if none was created
        """
        select = mag_info.select
        disp_region = mag_info.display_region
        disp_x_cell = (disp_region.x_max-disp_region.x_min)/disp_region.ncols
        disp_y_cell = (disp_region.y_max-disp_region.y_min)/disp_region.nrows
        xmin = select.ix_min*disp_x_cell + disp_region.x_min
        ymin = select.iy_min*disp_y_cell + disp_region.y_min
        xmax = (select.ix_max+1)*disp_x_cell + disp_region.x_min
        ymax = (select.iy_max+1)*disp_y_cell + disp_region.y_min
        SlTrace.lg(f"create_magnification_window:"
                   f" xmin:{xmin} ymin:{ymin} xmax:{xmax} ymax:{ymax}"
                   f" nrows:{disp_region.nrows} ncols:{disp_region.ncols}")
        child_info = mag_info.make_child()
        child_info.display_region = MagnifyDisplayRegion(x_min=xmin, x_max=xmax,
                                        y_min=ymin, y_max=ymax)
        child_info.description = (f"region minimum x: {xmin:.0f}, minimum y: {ymin:.0f},"
                                  + f" maximum x: {xmax:.0f}, maximum y: {ymax:.0f}")
        adw = self.create_audio_window(xmin=xmin, xmax=xmax,
                                       ymin=ymin, ymax=ymax,
                                       nrows=disp_region.nrows,
                                       ncols=disp_region.ncols,
                                       mag_info=child_info,
                                       require_cells=True)            
        return adw 

    def exit(self):
        """ Main exit if creating magnifications
        """
        if self.pgmExit is not None:
            self.pgmExit()      # Use supplied pgmExit
            
        SlTrace.lg("CanvasGrid.exit")
        SlTrace.onexit()    # Force logging quit
        os._exit(0)
        
if __name__ == "__main__":
    import sys
    import time

    
    def test1():
        
        root = tk.Tk()
        cvg = CanvasGrid(root, height=800, width=800)
        for _ in range(2):
            cvg.paint_grid()
            time.sleep(2)
            cvg.erase_grid_paint()
            time.sleep(1)

    def test2():
        root = tk.Tk()
        cvg = CanvasGrid(root, height=450, width=450)
        cvg.create_line(0,0,200,300, width=10, fill="blue", tags="blue_tag")
        cvg.create_line(200,300,400,400, width=10, fill="green", tags=["green1","green2"])
        cvg.create_rectangle(200,200,300,300, fill="red")
        cvg.create_oval(100,200,250,300, fill="orange", tags="orange_tag")

        cvg.show_canvas_items(always_list=[])
        cvg.show_canvas_items(always_list=[],types="rectangle",prefix="rectangle")
        cvg.show_canvas_items(always_list=[],ex_types="rectangle",prefix="ex_types=rectangle ")
        cvg.show_canvas_items(always_list=[],ex_types="rectangle",
                              prefix="blue_tag, ex_types=rectangle ", tags="blue_tag")
        cvg.show_canvas_items(always_list=[],ex_types=["rectangle","line"],
                              prefix='ex_types=["rectangle","line"] ')
        cvg.show_canvas_items(always_list=[],ex_tags="green1",
                              prefix='ex_tags="green1"')

        SlTrace.lg("""Checking: tags="green1" when we have  tags=["green1","green2"] """)
        cvg.show_canvas_items(always_list=[],tags="green1",
                              prefix='tags="green1"')
        cvg.show_canvas_items(always_list=[],tags=["green1","orange_tag"],
                              prefix='tags=["green1","orange_tag"]')
        root.mainloop()
    
    def test3():    
        """ add cell squares to display
        """
        SlTrace.lg("Start test3")
        root = tk.Tk()
        cvg = CanvasGrid(root, height=450, width=450)
        cvg.create_line(0,0,200,300, width=10, fill="blue", tags="blue_tag")
        cvg.create_line(200,300,400,400, width=10, fill="green", tags=["green1","green2"])
        cvg.create_rectangle(200,200,300,300, fill="red")
        cvg.create_oval(100,200,250,300, fill="orange", tags="orange_tag")
        SlTrace.lg("calling display_cells()")
        cvg.display_cells()
        SlTrace.lg("After display_cells()")
        root.mainloop()
    
    def test4():    
        """ Create a AudioDrawWindow from a selection - default whole canvas
        """
        SlTrace.lg("Start test4")
        root = tk.Tk()
        cvg = CanvasGrid(root, height=450, width=450)
        cvg.create_line(0,0,200,300, width=10, fill="blue", tags="blue_tag")
        cvg.create_line(200,300,400,400, width=10, fill="green", tags=["green1","green2"])
        cvg.create_rectangle(200,200,300,300, fill="red")
        cvg.create_oval(150,250,350,350, fill="orange", tags="orange_tag")
        SlTrace.lg("Create a AudioDrawWindow")
        adw1 = cvg.create_audio_window()
        SlTrace.lg("After create_audio_window()")
        
        SlTrace.lg("Create a AudioDrawWindow 2")
        xmin = cvg.g_xmin + cvg.g_width//4
        xmax = cvg.g_xmax - cvg.g_width//4
        ymin = cvg.g_ymin + cvg.g_height//4
        ymax = cvg.g_ymax - cvg.g_height//4
        adw2 = cvg.create_audio_window(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
        SlTrace.lg("After create_audio_window() 2")
        
        SlTrace.lg("Create a AudioDrawWindow 2")
        xmin = xmin+(xmax-xmin)*.3
        xmax = xmin+(xmax-xmin)*.7
        ymin = ymin+(ymax-ymin)*.3
        ymax = ymin+(ymax-ymin)*.7
        adw2 = cvg.create_audio_window(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
        SlTrace.lg("After create_audio_window() 2")
        root.mainloop()
            
    def test4a():    
        """ Create a AudioDrawWindow from a selection - default whole canvas
        """
        SlTrace.lg("Start test4a")
        root = tk.Tk()
        cvg = CanvasGrid(root, height=450, width=450)
        cvg.create_line(0,0,200,300, width=10, fill="blue", tags="blue_tag")
        cvg.create_line(200,300,400,400, width=10, fill="green", tags=["green1","green2"])
        cvg.create_rectangle(200,200,300,300, fill="red")
        cvg.create_oval(150,250,350,350, fill="orange", tags="orange_tag")
        mag_info = MagnifyInfo(base_canvas=cvg)
        SlTrace.lg("Create a AudioDrawWindow")
        adw1 = cvg.create_audio_window()
        SlTrace.lg("After create_audio_window()")

        root.mainloop()
            
    def test4b():    
        """ Create a AudioDrawWindow from a selection - default whole canvas
        """
        SlTrace.lg("Start test4b")
        root = tk.Tk()
        height = 800
        width = height
        cvg = CanvasGrid(root, height=800, width=800)
        cvg.create_line(0,0,200,300, width=10, fill="blue", tags="blue_tag")
        cvg.create_line(200,300,400,400, width=10, fill="green", tags=["green1","green2"])
        cvg.create_rectangle(200,200,300,300, fill="red")
        cvg.create_oval(150,250,350,350, fill="orange", tags="orange_tag")
        #mag_info = MagnifyInfo(base_canvas=cvg)
        SlTrace.lg("Create a AudioDrawWindow")
        cvg.create_audio_window(xmin=0,ymin=0, xmax=width, ymax=height)
        SlTrace.lg("After create_audio_window()")

        root.mainloop()
    
    def test5():    
        """ Create a AudioDrawWindow from a selection - default whole canvas
        """
        SlTrace.lg("Start test5 using canvas scanning")
        root = tk.Tk()
        cv = tk.Canvas(root, height=450, width=450)
        cv.pack()
        cv.create_line(0,0,200,300, width=10, fill="blue", tags="blue_tag")
        cv.create_line(200,300,400,400, width=10, fill="green", tags=["green1","green2"])
        cv.create_rectangle(200,200,300,300, fill="red")
        cv.create_oval(150,250,350,350, fill="orange", tags="orange_tag")
        SlTrace.lg("Tk Canvas create")
        
        mw = tk.Tk()
        cvg = CanvasGrid(mw, base=cv, height=450, width=450)
        
        SlTrace.lg("Create a AudioDrawWindow")
        adw1 = cvg.create_audio_window(title="test5 from tk.canvas scanning")
        SlTrace.lg("After create_audio_window()")
        
        time.sleep(2)
        SlTrace.lg("Create a AudioDrawWindow 2")
        xmin = cvg.g_xmin + cvg.g_width//4
        xmax = cvg.g_xmax - cvg.g_width//4
        ymin = cvg.g_ymin + cvg.g_height//4
        ymax = cvg.g_ymax - cvg.g_height//4
        adw2 = cvg.create_audio_window(title="test5 Magnified window",
                                       xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
        SlTrace.lg("After create_audio_window() 2")
        
        time.sleep(1)
        SlTrace.lg("Create a AudioDrawWindow 3")
        xmin = xmin+(xmax-xmin)*.3
        xmax = xmin+(xmax-xmin)*.7
        ymin = ymin+(ymax-ymin)*.3
        ymax = ymin+(ymax-ymin)*.7
        adw2 = cvg.create_audio_window(title="test5 Magnified more window",
                                       xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
        SlTrace.lg("After create_audio_window() 2")
        root.mainloop()
        
    #test1()
    #test2()
    #test3()
    test5()
    SlTrace.lg("End of Test")
    sys.exit()
        