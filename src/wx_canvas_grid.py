#wx_canvas_grid.py  24Oct2023  crs, from canvas_grid.py
#                   14Feb2023  crs  Author
"""
Basis for nestable grid layout displayed using wxPython
The base graphic is a populated tkinter Canvas Widget
The plan, which emanates from my TurtleBraille system to aid the viewing,
by the blind of simple turtle graphics.  Our target is a system by which
one is able to segment a canvas based graphic, as a coarse picture (e.g. 40 by 25)
and then easily select a rectangular subsection and then create a similar coarse
picture (e.g. 40 by 25) of that subsection.
The hope is to provide a magnified rendition of a selectable section of a given canvas.

Provide list of canvas items overlapping a region (display cell rectangle).

"""
import sys
import os
import copy
import tkinter as tk

from select_trace import SlTrace
from braille_error import BrailleError
from braille_cell import BrailleCell
from magnify_info import MagnifySelect, MagnifyInfo, MagnifyDisplayRegion
from wx_speaker_control import SpeakerControlLocal

"""
We now think explicit .base.fn_name is better
for indirect call of tk.Canvas calls:
    find_overlapping, gettags, itemconfigure, type
"""

class CanvasGrid(tk.Canvas):
        
    def __init__(self,
                 master=None,
                 base=None, title="Base Grid",
                 pgmExit=None,
                 g_xmin=None, g_xmax=None, g_ymin=None, g_ymax=None,
                 g_nrows=25, g_ncols=40,
                 x_offset=None, y_offset=None,
                 **kwargs):
        """ Set up canvas object with grid
        :master: widget master
                default: no canvas setup, just use base for data
        :base: tk.Canvas, if present, from which we get
                canvas item contents
                default: self
        :title: window title
        :pgmExit: program main exit if one default: use local (...os._exit)
        :g_xmin: Grid minimum canvas coordinate value default: left edge
        :g_xmax: Grid maximum canvas coordinate value default: right edge
        :g_ymin: Grid minimum canvas coordinate value default: top edge
        :g_ymax: Grid maximum canvas coordinate value default: bottom edge
        :g_nrows: Number of rows default: 25
        :g_ncols: Number of columns default: 40
        :x_offset: offset external to internal
                default: 1/2 (x_max-x_min)        
        :y_offset: offset external to internal
                default: 1/2 (y_max-y_min)
        """
        self.ncall_get_cell_specs = 0       # Facilitate tracking          
        self.master = master
        if base is None:
            base = tk.Canvas(master) 
        self.base = base
        self.title = title
        self.pgmExit = pgmExit
        self.item_samples = {}      # For incremental presentation  via show_item
        self.audio_wins = []        # window list for access
        self.n_cells_created = 0    # Number of cells in recent window
        if master is not None:
            super(CanvasGrid,self).__init__(master=master, **kwargs)
            #self.pack(expand=True, fill=tk.BOTH)
            self.master.update()

        if g_xmin is None:
            g_xmin = -self.base.winfo_width()/2
        self.g_xmin = g_xmin
        if g_xmax is None:
            g_xmax = self.base.winfo_width()/2 
        self.g_xmax = g_xmax
        self.g_width = self.base.winfo_width()
        if g_ymin is None:
            g_ymin = -self.base.winfo_height()/2
        self.g_ymin = g_ymin
        if g_ymax is None:
            g_ymax = self.base.winfo_height()/2
        self.g_ymax = g_ymax
        self.g_height = self.base.winfo_height()
        self.g_nrows = g_nrows
        self.g_ncols = g_ncols
        self.grid_tag = None        # Most recent grid paint tag
        self.set_cell_lims()

    def get_canvas_lims(self, win_fract=True):
        """ Get canvas limits - internal values, to which
        self.base.find_overlapping(cx1,cy1,cx2,cy2) obeys.
        NOTE: These values, despite some vague documentation, may be negative
              to adhere to turtle coordinate settings.
        :win_fract: True - fraction of window -x_min = 0. x_max = 1....
        :returns: internal (xmin, xmax, ymin, ymax)
        """
        if win_fract:
            return (0.,1., 0.,1.)
        
        return (self.g_xmin, self.g_xmax, self.g_ymin, self.g_ymax)
            
    def get_grid_lims(self, win_fract=True,
                      xmin=None, xmax=None, ymin=None, ymax=None,
                      ncols=None, nrows=None):
        """ create grid boundary values bottom through top, given limits
         so:
             grid_xs[0] == left edge
             grid_xs[grid_width] == right edge
             grid_ys[0] == top edge
             grid_ys[grid_height] == bottom edge
             cell(i,j): grid_xs[i], grid_xs[i+1], grid_ys[j], grid_ys[j+1]
            All coordinates are in canvas values: y==0 at top, increasing down
        :win_fract: True(default) - xmin,... are fractions (0. to 1.) of display
        :xmin: minimum x default: 0. or self.g_xmin
        :xmax: maximim x default: 1. or self.g_xmax
        :ymin: minimum y default: 0. or self.g_ymin
        :ymax: maximim y defailt: 1 or self.g_ymax
        :ncols: grid horizontal columns default: self.g_ncols
        :nrows: grid vertical rows default: self.g_nrows
        :returns: (grid_xs,grid_ys) - list of x limits (coordinates),
                                      list of y limits (coordinates)
        """
        
        if xmin is None:
            xmin = 0. if win_fract else self.g_xmin 
        if xmax is None:
            xmax = 1. if win_fract else self.g_xmax 
        if ymin is None:
            ymin = 0. if win_fract else self.g_ymin 
        if ymax is None:
            ymax = 1. if win_fract else self.g_ymax 
        if ncols is None:
            ncols = self.g_ncols 
        if nrows is None:
            nrows = self.g_nrows 
            
        g_width = self.g_width
        g_height = self.g_height 
        grid_xs = []
        grid_ys = []

        fg_xmin = self.g_xmin + xmin*g_width
        fg_xmax = self.g_xmin + xmax*g_width
        fg_width = fg_xmax - fg_xmin
        for i in range(ncols+1):
            if win_fract:
                x = fg_xmin + i*fg_width/ncols
            else:
                xmin + i*g_width/ncols                 
            grid_xs.append(x)
            
        fg_ymin = self.g_ymin + ymin*g_height
        fg_ymax = self.g_ymin + ymax*g_height
        fg_height = fg_ymax - fg_ymin
        for i in range(nrows+1):
            if win_fract:
                x = fg_ymin + i*fg_height/nrows
            else:
                xmin + i*g_height/nrows                 
            grid_ys.append(x)

        return grid_xs,grid_ys

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
                       
    def set_cell_lims(self, cell_y_increase=False):
        """ create cell boundary values bottom through top
        Assumes values increases with cell index
        To adjust for the reverse replace index i with (N-i)
        Sets up self.cell_y_min
                self.cell_y_max
         so:
             cell_xs[0] == left edge
             cell_xs[grid_width] == right edge
                            y-increasing             y-decreasing
             top edge :     cell_ys[0]               cell_ys[grid_height]   
             bottom edge :  cell_ys[grid_height]     cell_ys[0]
        :cell_y_increase: y value increases with index
                    default: False to follow turtle coordinate system
        """
         
        self.cell_xs = []
        self.cell_ys = []
        self.cell_y_increase = cell_y_increase

        x_min = self.get_x_min()
        x_max = self.get_x_max()
        grid_width = self.g_xmax-self.g_xmin
        x_cell = (x_max-x_min)/grid_width
        for i in range(self.g_ncols+1):
            x = int(x_min + i*x_cell)
            self.cell_xs.append(x)
            
        y_min = self.get_y_min()
        y_max = self.get_y_max()
        y_cell = (y_max-y_min)/self.g_nrows
        for i in range(self.g_nrows+1):
            y = int(y_min + i*y_cell)   # Stored in y increasing order
            self.cell_ys.append(y)

        if self.cell_y_increase:
            self.cell_y_min = self.cell_ys[0]
            self.cell_y_max = self.cell_ys[len(self.cell_ys)-1]
        else:   # decrease
            self.cell_y_min = self.cell_ys[len(self.cell_ys)-1]
            self.cell_y_max = self.cell_ys[0]



    def get_cell_iy12(self, y):
        """ Get cell index based on previous set_cell_lims setting of
        self.cell_ys and self.cell_y_increase
        :y: y value
        """
        if y < self.cell_y_min:
            SlTrace.lg(f" y({y} too small set to {self.cell_y_min})")
            y = self.cell_y_min
        if y > self.cell_y_max:
            SlTrace.lg(f" y({y} too large set to {self.cell_y_max})")
            y = self.cell_y_min
        for i in range(len(self.cell_ys)):
            if self.cell_ys_increases:
                i_top = i
                i_bot = i_bot + 1   #  y index and value increase downward
                yc_topv = self.cell_ys[i_top]
                yc_botv = self.cell_ys[i_bot]
                if y <= yc_topv and y >= yc_botv:
                    break    
            else:   # decrease
                i_top = len(self.cell_ys)-1
                i_bot = i_bot - 1
                yc_topv = self.cell_ys[i_top]
                yc_botv = self.cell_ys[i_bot]
                if y <= yc_topv and y >= yc_botv:
                    break    
        return i_top,i_bot

    def get_cell_y12(self, iy, cell_y_increase=None, cell_ys=None):
        """ Get cell ytop,ybot range given iy index
        :iy:
        :cell_y_increase: value icreases with index iff Trie
                default: False - index increases down value increases up == turtle coord
        :ys: y limit array (increasing with index)
        """
        if cell_y_increase is None:
            cell_y_increase = self.cell_y_increase
        if cell_ys is None:
            cell_ys = self.cell_ys
        if cell_y_increase:
            cell_iy_top = iy
            cell_iy_bot = cell_iy_top+1
        else:       # decrease
            if iy == 0:
                cell_iy_top = 0
            else:
                cell_iy_top = iy-1
            cell_iy_bot = cell_iy_top+1
                        
        if cell_iy_top < 0:
            SlTrace.lg(f"cell iy({cell_iy_top} too small set to {0})")
            cell_iy_top = 0
            cell_iy_bot = cell_iy_top+1
        if cell_iy_bot >= len(cell_ys):
            SlTrace.lg(f" iy({cell_iy_bot} too large set to {len(cell_ys)-1})")
            cell_iy_bot = len(cell_ys)-1
            cell_iy_top = cell_iy_bot-1
        cell_y_top = cell_ys[cell_iy_top]
        cell_y_bot = cell_ys[cell_iy_bot]
        return cell_y_top,cell_y_bot            

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
        x1 = self.cell_xs[ix]
        x2 = self.cell_xs[ix+1]
        y1,y2 = self.get_cell_y12(iy)
        return (x1,y1,x2,y2)

                       
    def get_grid_ullr(self, ix, iy, cell_y_increase=None, xs=None, ys=None):
        """ Get cell's canvas rectangle x, y  upper left, x,  y lower right
        
        :ix: cell x index
        :iy: cell's  y index
        :y_increase: y increases with iy iff True
                    default: use current self.cell_y_increase
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
        if cell_y_increase is None:
            cell_y_increase = self.cell_y_increase
        ixmax = len(xs)-2           # last element is upper bound
        w_left_x = xs[0]            # left edge
        w_right_x = xs[ixmax-1]
        
        if ix >= 0:
            if ix <= ixmax:
                w_left_x = xs[ix]
                w_right_x = xs[ix+1]
            else:
                w_left_x = xs[ixmax]
                w_right_x = xs[ixmax+1]
        w_upper_y, w_lower_y = self.get_cell_y12(iy, cell_y_increase=cell_y_increase,
                                                 cell_ys=ys)
        return (w_left_x,w_upper_y, w_right_x,w_lower_y)


    def get_canvas_items(self,
                        win_fract=None,
                        xmin=None, xmax=None, ymin=None, ymax=None,
                        ncols=None, nrows=None,
                        types=None, ex_types=None,
                        tags=None, ex_tags=None, get_color=False):
        """ Get items within grid cells
        :win_fract: True(default) - xmin,... are fractions of display
                    False - xmin,... are coodinates
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
        xs,ys = self.get_grid_lims(win_fract = win_fract,
                                   xmin=xmin, xmax=xmax, ymin=ymin,ymax=ymax,
                                   ncols=ncols,nrows=nrows)
        SlTrace.lg(f"\nget_canvas_items")
        SlTrace.lg(f"xmin={xmin}, xmax={xmax}"
                   f", ymin={ymin},ymax={ymax}"
                   f", ncols={ncols},nrows={nrows}")
        SlTrace.lg(f"xs:{xs}\nys:{ys}")
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
        for ix in range(len(xs)):
            for iy in range(len(ys)):
                cx1,cy1,cx2,cy2 = self.get_grid_ullr(ix=ix, iy=iy, xs=xs, ys=ys)
                item_ids_over_raw = self.base.find_overlapping(cx1,cy1,cx2,cy2)
                if self.ncall_get_cell_specs > 0 or SlTrace.trace("get_items"):
                    if len(item_ids_over_raw) > 0:
                        color = self.item_to_color(item_ids=item_ids_over_raw)
                    else:
                        color = ""
                    SlTrace.lg(f"    {ix},{iy}: cx1,cy1,cx2,cy2 {cx1},{cy1},{cx2},{cy2}"
                               f" item_ids: {item_ids_over_raw} {color}", "canvas_items")
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


    def get_cell_specs(self,
                        win_fract=True,
                        x_min=None, x_max=None,
                        y_min=None, y_max=None,
                        n_cols=None, n_rows=None):
        """ Get cell specifications (ix,iy,color) from grid
        :win_fract: True - x_min,... are fractions of region
                    False x_min are coordinates
        :xmin,xmax,ymin,ymax, ncols, nrows: see get_grid_lims()
                        default: CanvasGrid instance values
        """
        self.ncall_get_cell_specs += 1
        ixy_items = self.get_canvas_items(win_fract=win_fract,
                                          xmin=x_min, xmax=x_max,
                                          ymin=y_min,ymax=y_max,
                                          ncols=n_cols,nrows=n_rows)
        cell_specs = []
        for ixy_item in ixy_items:
            (ix,iy), ids = ixy_item
            color = self.item_to_color(item_ids=ids)
            if color is not None:
                cell_spec = (ix, iy, color)
                cell_specs.append(cell_spec)
        return cell_specs

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

    def get_x_max(self):
        return self.g_xmax

    def get_x_min(self):
        return self.g_xmin

    def get_y_max(self):
        return self.g_ymax

    def get_y_min(self):
        return self.g_ymin

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
    import tkinter as tk
    import wx
    from wx_audio_draw_window import AudioDrawWindow
    app = wx.App()
    
    def test1():
        
        root = tk.Tk()
        cvg = CanvasGrid(root, height=800, width=800)
        for _ in range(2):
            cvg.paint_grid()
            time.sleep(2)
            cvg.erase_grid_paint()
            time.sleep(1)
            cvg.paint_grid()
            time.sleep(5)
            
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
        adw1 = AudioDrawWindow(canvas_grid=cvg)
        SlTrace.lg("After create_audio_window()")
        
        SlTrace.lg("Create a AudioDrawWindow 2")
        xmin = cvg.g_xmin + cvg.g_width//4
        xmax = cvg.g_xmax - cvg.g_width//4
        ymin = cvg.g_ymin + cvg.g_height//4
        ymax = cvg.g_ymax - cvg.g_height//4
        adw2 = AudioDrawWindow(canvas_grid=cvg,xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
        SlTrace.lg("After create_audio_window() 2")
        
        SlTrace.lg("Create a AudioDrawWindow 2")
        xmin = xmin+(xmax-xmin)*.3
        xmax = xmin+(xmax-xmin)*.7
        ymin = ymin+(ymax-ymin)*.3
        ymax = ymin+(ymax-ymin)*.7
        adw2 = AudioDrawWindow(canvas_grid=cvg,xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
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
        adw1 = AudioDrawWindow(canvas_grid=cvg,)
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
        AudioDrawWindow(canvas_grid=cvg,xmin=0,ymin=0, xmax=width, ymax=height)
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
        adw1 = AudioDrawWindow(canvas_grid=cvg, title="test5 from tk.canvas scanning")
        SlTrace.lg("After create_audio_window()")
        
        time.sleep(2)
        SlTrace.lg("Create a AudioDrawWindow 2")
        xmin = cvg.g_xmin + cvg.g_width//4
        xmax = cvg.g_xmax - cvg.g_width//4
        ymin = cvg.g_ymin + cvg.g_height//4
        ymax = cvg.g_ymax - cvg.g_height//4
        
        adw2 = AudioDrawWindow(title="test5 Magnified window",
                                    x_min=xmin, y_min=ymin,
                                    grid_width=cvg.g_width//4,
                                    grid_height=cvg.g_height//4)
        SlTrace.lg("After create_audio_window() 2")
        
        time.sleep(1)
        SlTrace.lg("Create a AudioDrawWindow 3")
        xmin = xmin+(xmax-xmin)*.3
        xmax = xmin+(xmax-xmin)*.7
        grid_width = xmax-xmin
        ymin = ymin+(ymax-ymin)*.3
        ymax = ymin+(ymax-ymin)*.7
        grid_height = abs(ymax-ymin)
        adw2 = AudioDrawWindow(title="test5 Magnified more window",
                                       x_min=xmin, grid_width=grid_width,
                                       y_min=ymin, grid_height=grid_height)
        SlTrace.lg("After create_audio_window() 2")
        root.mainloop()
        
    test1()
    #test2()
    #test3()
    #test5()
    SlTrace.lg("End of Test")
    sys.exit()
        