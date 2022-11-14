# braille_display  19Apr2022  crs  Author
"""
Display graphics on window
Supports simple graphical point, line specification
Supports display of 6-point cells
on grid_width by grid_height grid
Supports writing out braille stream
"""
from math import sin, cos, pi, atan, sqrt
import turtle as tur
from tkinter import *

from select_trace import SlTrace
from audio_window import AudioWindow

def pl(point_list):
    """ display routine for point list
    Convert points to integer, or .2f
    :point_list: list of points
    :returns s string of (x,y) ...
    """
    if not isinstance(point_list, list):
        point_list = [point_list]
    st = ""
    for point in point_list:
        st += "("
        for i in range(len(point)):
            p = point[i]
            if i > 0:
                st += ","
            if isinstance(p, float):
                st += f"{int(p)}"
            else:
                st += f"{p}"
        st += ")"
    return st 


class BrailleCell:
    """ braille cell info augmented for analysis
    """
    def __str__(self):
        st = f"BCell: [{self.ix},{self.iy}]"
        if self._color is not None:
            st += " " + self._color
        if self._color_bg is not None:
            st += " " + self._color_bg
        return st
        
    def __init__(self, dots=None,
                 color=None, color_bg=None,
                 ix=0, iy=0,
                 points=None):
        """ setup braille cell
        :dots: list of set dots default: none - blank
        :color: color str or tuple
        :ix: cell index(from 0) from left side
        :iy: cell index from bottom
        :points: initial set of points, if any
            default: empty
        """
        self.ix = ix    # Include to make self sufficient
        self.iy = iy
        self.dots = dots
        if color is None:
            color = "black"
        if color_bg is None: 
            color_bg = "white"
        self._color = color
        self._color_bg = color_bg
        if points is None:
            points = set()
        self.points = points
        self.canv_items = []        # canvas items

    def color_str(self, color=None):
        """ Return color string
        :color: color specification str or tuple
        """
        color_str = color
        if (color_str is None
             or (isinstance(color_str, tuple)
                  and len(color_str) == 0)
             ):
            color_str = self._color
        if isinstance(color_str,tuple):
            if len(color_str) == 1:
                color_str = color_str[0]
            else:
                color_str = "pink"  # TBD - color tuple work
        return color_str
        

class P12LineVals:
    """ p1,p2 line function data
    """
    def __init__(self,p1,p2,horz,vert,
                 my,cy,mx,cx):
        self.p1 = p1
        self.p2 = p2
        self.horz = horz
        self.vert = vert
        self.my = my
        self.cy = cy 
        self.mx = mx
        self.cx = cx
        
class BrailleDisplay:
    """ Create and display graphics using Braille
    """
    dots_for_character = {
        " ": (),    # blank
        "a": (1),
        "b": (1,2),
        "c": (1,4),
        "d": (1,4,5),
        "e": (1,5),
        "f": (1,2,5),
        "g": (1,2,4,5),
        "h": (1,2,5),
        "i": (2,4),
        "j": (2,4,5),
        "k": (1,3),
        "l": (1,2,3),
        "m": (1,3,4),
        "n": (1,3,4,5),
        "o": (1,3,5),
        "p": (1,2,3,4),
        "q": (1,2,3,4,5),
        "r": (1,2,3,5),
        "s": (2,3,4),
        "t": (2,3,4,5),
        "u": (1,3,6),
        "v": (1,2,3,6),
        "w": (2,4,5,6),
        "x": (1,3,4,6),
        "y": (1,3,4,5,6),
        "z": (1,3,5,6),
        }
    
    
    def __init__(self, title="Braille Display",
                 tu=None,
                 win_width=800, win_height=800,
                 grid_width=40, grid_height=25,
                 use_full_cells= True,
                 x_min=None, y_min=None,
                 line_width=1, color="black",
                 color_bg = None,
                 color_fill = None,
                 point_resolution=None,
                 blank_char=",",
                 shift_to_edge=True):
        """ Setup display
        :title: display screen title
        :tu: turtle instance
            default: create one
        :win_width: display window width in pixels
            default: 800
        :win_height: display window height in pixels
            default: 800
        :grid_width: braille width in cells
            default: 40
        :grid_height: braille width in cells
            default: 25
        :color: drawing color
                default: turtle default
        :color_fill: fill color
                default: drawing color
        :color_bg: background color
                default: turtle default
        :use_full_cells: Use full cells for point/lines
            e.g. place color letter in cell
            default: True - usefull cells
        :x_min: x value for left side default: -win_width/2
        :y_min:  y value for bottom default: -win_height/2
        :line_width: line width
        :point_resolution: Distance between points below
            with, no difference is recognized
            default: computed so as to avoid gaps
                    between connected points
                    conservative to simplify/speed
                    computation
        :blank_char: replacement for non-trailing blanks
                    default "," to provide a "mostly blank",
                    non-compressed blank character for the
                    braille graphics
                    default: "," dot 2.
        :shift_to_edge: shift picture to edge/top
                    to aid in finding
                    default: True - shift
        """
        if title is None:
            title = "Braille Display"
        self.title = title
        self.win_width = win_width
        self.win_height = win_height
        if tu is None:
            tu = tur.Turtle()
            screen = tur.Screen()
            screen.screensize(win_width,win_height)
        else:
            screen = tur.Screen()
        self.tu = tu          # For turtle screen
        self.screen = screen
        
        self.grid_width = grid_width
        self.cell_width = win_width/self.grid_width
        self.grid_height = grid_height
        self.cell_height = win_height/self.grid_height
        if point_resolution is None:
            point_resolution = int(min(self.cell_width,
                                  self.cell_height)-1)
        if point_resolution < 1:
            point_resolution = 1
        self.point_resolution = point_resolution
        self.use_full_cells = use_full_cells
        if x_min is None:
            x_min = -win_width//2
        self.x_min = x_min
        self.x_max = x_min + win_width
        if y_min is None:
            y_min = -win_width//2
        self.y_min = y_min
        self.y_max = y_min + win_height
        self.line_width = line_width
        self._color = color
        if self._color is not None:
            self.tu.color(self._color)
        self._color_fill = color_fill
        if self._color_fill is not None:
            self.tu.fillcolor(self._color_fill)
        self._color_bg = color_bg
        if self._color_fill is not None:
            self.tu.bgcolor(self._color_bg)
        self.cmds = []      # Commands to support redo
        self.cells = {}     # BrailleCell hash by (ix,iy)
        self.set_cell_lims()
        self.lfun_horz = False 
        self.lfun_vert = False 
        self.x = self.y = 0
        self.angle = 0          # degrees (angle)
        self.pt = self.p2 = (self.x, self.y)
        self.blank_char = blank_char
        self.shift_to_edge = shift_to_edge
        self.is_pendown = True 
        self.is_filling = False
        
    def set_cell_lims(self):
        """ create cell boundary values bottom through top
         so:
             cell_xs[0] == left edge
             cell_xs[grid_width] == right edge
             cell_ys[0] == bottom edge
             cell_ys[grid_height] == top edge
        """
         
        self.cell_xs = []
        self.cell_ys = []

        for i in range(self.grid_width+1):
            x = int(self.x_min + i*self.win_width/self.grid_width)
            self.cell_xs.append(x)
        for i in range(self.grid_height+1):
            y = int(self.y_min + i*self.win_height/self.grid_height)
            self.cell_ys.append(y)
        
    def add_dot(self, size=None, *color):
        """ Add new point
        :size: diameter of dot
        :color: point color
        """
        SlTrace.lg(f"add_dot: ", "braille_cmd")
        self.tu.dot(size, *color)
        if size is None:
            size = self.line_width
        pt = (self.x,self.y)
        if len(color)==0:
            color = self._color
            
        points = self.get_dot_points(pt=pt, size=size)
        self.populate_cells_from_points(points, color=color)
        
    def add_line(self, p1=None, p2=None, color=None, width=None):
        """ Add new line
        :p1: xy pair - beginning point
            default: previous point (add_point or add_line)
        :p2: xy pair - ending point
            default: previous point (add_point or add_line)
        :color: line color
            default: previous color ["black"]
        :width: line width 
            default: previous width [1]
        """
        if p1 is None:
            p1 = (self.x,self.y)
        if p2 is None:
            raise Exception("p2 is missing")
        if self.is_filling:
            self.add_to_fill(p1,p2)
        if width is None:
            width = self.line_width
        if color is None:
            color = self._color
        if self.is_pendown:
            points = self.get_drawn_line_points(p1, p2, width)
            self.populate_cells_from_points(points, color=color)
        self.x, self.y = p2
        
        
    def set_line_funs(self, p1, p2):
        """ Set line functions which provide determine
        x from y,  y from x to place (x,y) on line
        functions are self.line_x(y) and self.line_y(x)
        :p1: beginning point (x,y)
        :p2: ending point (x,y)
        """
        x1,y1 = p1
        x2,y2 = p2
        self.lfun_x_diff = x2 - x1
        ###if abs(self.lfun_x_diff) < small:
        ###    self.lfun_x_diff = 0
        self.lfun_y_diff = y2 - y1
        ###if abs(self.lfun_y_diff) < small:
        ###    self.lfun_y_diff = 0
        self.lfun_dist = sqrt(self.lfun_x_diff**2
                              +self.lfun_y_diff**2)
        self.lfun_x_chg_gt = False
        if abs(self.lfun_x_diff) >= abs(self.lfun_y_diff):
            self.lfun_x_chg_gt = True
        if self.lfun_dist != 0: 
            self.lfun_sin = self.lfun_y_diff/self.lfun_dist
            self.lfun_cos = self.lfun_x_diff/self.lfun_dist
        else:
            self.lfun_sin = self.lfun_cos = 0
        
        self.lfun_p1 = p1
        self.lfun_p2 = p2
        self.lfun_horz = False 
        self.lfun_vert = False
        if self.lfun_x_diff == 0:
            self.lfun_vert = True 
        else:
            self.lfun_my = self.lfun_y_diff/self.lfun_x_diff
            self.lfun_cy = y1 - self.lfun_my*x1 
        if self.lfun_y_diff == 0:
            self.lfun_horz = True 
        else:
            self.lfun_mx = self.lfun_x_diff/self.lfun_y_diff 
            self.lfun_cx = x1 - self.lfun_mx*y1
        if self.lfun_x_diff == 0:
            if self.lfun_y_diff >= 0:
                self.lfun_rangle = pi/2
            else:
                self.lfun_rangle = -pi/2
        elif self.lfun_y_diff == 0:
            if self.lfun_x_diff >= 0:
                self.lfun_rangle = 0
            else:
                self.lfun_rangle = pi
        else:
            self.lfun_rangle = atan(self.lfun_my)
        #unit_normal (length 1 orthogonal to line)
        uno_rangle = self.lfun_unorm_rangle = self.lfun_rangle + pi/2
        self.lfun_unorm_sin = sin(uno_rangle)
        self.lfun_unorm_cos = cos(uno_rangle)
        self.lfun_unorm_x = self.lfun_unorm_cos
        self.lfun_unorm_y = self.lfun_unorm_sin
            
    def line_y(self, x):
        """ calculate pt y, given pt x
        having line setup from set_line_funs
        :x: pt x value
        :returns:  y value , None if undetermined
        """
        if self.lfun_horz:
            return self.lfun_p1[1]  # constant y
        
        if self.lfun_vert:
            return self.lfun_p1[1]  # Just pick first 
        
        y = self.lfun_my*x + self.lfun_cy
        return y

    def line_x(self, y):
        """ calculate pt x, given pt y
        having line setup from set_line_funs
        :x: pt x value
        :returns:  x value , None if undetermined
        """
        if self.lfun_horz:
            return self.lfun_p1[0]  # Just pick first 
        
        if self.lfun_vert:
            return self.lfun_p1[0]  # constant x
        
        x = self.lfun_mx*y + self.lfun_cx
        return x
        
        
    def get_line_cells(self, p1, p2, width=None):
        """ Get cells touched by line
        :p1: beginning point (x,y)
        :p2: end point (x,y)
        :width: line thickness in pixels
            default: previous line width
        :returns: list of cells included by line
        """
        SlTrace.lg(f"\nget_line_cells: p1({p1}) p2({p2}", "cell")
        self.set_line_funs(p1=p1, p2=p2)
        x1,y1 = p1
        x2,y2 = p2
        xtrav = x2-x1
        xtrav_abs = abs(xtrav)
        ytrav = y2-y1   # y goes from y1 to y2
        ytrav_abs = abs(ytrav)
        if xtrav_abs > ytrav_abs:
            tstart = x1
            tend = x2
        else:
            tstart = y1
            tend = y2
        tdir = tend - tstart  # just the sign
        trav_step = 1   # cautious
        if tdir < 0:
            trav_step *= -1
        cells = set()
        point_cells = self.get_point_cells(p1)
        cells.update(point_cells)
        tloc = tstart
        pt = p1
        while True:
            pt_x,pt_y = pt
            if tdir > 0:    # going up
                if tloc > tend:
                    break
            else: # going down
                if tloc < tend:
                    break
            if xtrav_abs >  ytrav_abs:
                pt_x += trav_step
                tloc = pt_x
                pt_y = self.line_y(pt_x)
            else:
                pt_y += trav_step
                tloc = pt_y
                pt_x = self.line_x(pt_y)
            pt = (pt_x, pt_y)
            pt_cells = self.get_point_cells(pt)
            cells.update(pt_cells)
        SlTrace.lg(f"line_cells: {cells}\n", "cell")
        return list(cells)
                
        
        
    def get_point_cell(self, pt):
        """ Get cell in which point resides
        If on an edge returns lower cell
        If on a corner returns lowest cell
        :pt: x,y pair location in turtle coordinates
        :returns: ix,iy cell pair
        """
        x,y = pt
        ix = int((x-self.x_min)/self.win_width*self.grid_width)
        iy = int((y-self.y_min)/self.win_height*self.grid_height)
        return (ix,iy)
        
    def get_point_cells(self, pt, width=None):
        """ Get cells touched by point
        For speed we select all cells within x+/-.5 line width
        and y +/- .5 line width
        For now, ignore possibly interveining cells for
        lines wider than a cell
        :p1: beginning point (x,y)
        :width: line thickness in pixels
            default: previous line width
        :returns: list of cells included by point
        """
        if pt is None:
            pt = self.p2
            
        if width is None:
            width = self.line_width
        
        self.line_width = width
        cell_pt = self.get_point_cell(pt) 
        cells_set = set()     # start with point
        cells_set.add(cell_pt)
        x0,y0 = pt
        for p in [(x0-width,y0+width),   # Add 4 corners
                  (x0+width,y0+width),
                  (x0+width,y0-width),
                  (x0-width,y0)]:
            cell = self.get_point_cell(p)
            SlTrace.lg(f"get_point_cells: p({p}): cell:{cell}", "cell")
            cells_set.add(cell)
        #SlTrace.lg(f"get_point_cells: cells_set:{cells_set}", "cell")
        lst = list(cells_set)
        SlTrace.lg(f"get_point_cells: list:{lst}", "cell")
        return list(cells_set) 

    def update_cell(self, ix=None, iy=None, pt=None,
                    color=None):
        """ Add / update cell
            if the cell is already present it is updated:
                pt, if present is added
                color is replaced
        cell grid ix,iy:
        :ix: cell x grid index 
        :iy: cell y grid index
        OR
        :pt: (x,y) point coordinate of point
            added to cell
        
        :color: cell color
        :returns: new/updated BrailleCell
        """
        if color is None:
            color = self._color
        if ix is not None and iy is None:
            raise Exception(f"iy is missing ix={ix}")
        if iy is not None and ix is None:
            raise Exception(f"iy is missing ix={iy}")
        if ix is not None:
            cell_ixiy = (ix,iy)
        else:
            if pt is None:
                raise Exception("pt is missing")
            cell_ixiy = self.get_point_cell(pt)
        if cell_ixiy in self.cells:
            cell = self.cells[cell_ixiy]
        else:
            cell = BrailleCell(ix=cell_ixiy[0],
                        iy=cell_ixiy[1], color=color)
            self.cells[cell_ixiy] = cell
        if pt is not None:
            cell.points.add(pt) 
        if color is not None:
            color = color
            cell._color = color
            dots = self.braille_for_color(color)
            cell.dots = dots

        return cell
                
    def get_dot_points(self, pt, size=None):
        """ Get fill points included by dot
        :pt: beginning point (x,y)
        :size: dot thickness in pixels
            default: previous line width
        :returns: set of fill ponints
        """
        if size is None:
            size = self.line_width
        if pt is None:
            pt = self.p2
        pt_x,pt_y = pt
        pt_sep = self.point_resolution
        radius = size/2
        npt = int(radius*2*pi/pt_sep)
        point_list = []
        for i in range(npt):
            rangle = i*2*pi/npt
            dx = radius*cos(rangle)
            dy = radius*sin(rangle)
            x = pt_x + dx
            y = pt_y + dy
            point = (int(x),int(y))
            point_list.append(point)
        point_set = self.fill_points(point_list)
        return point_set 

    def fill_cells(self, point_list, point_resolution=None):
        """ Convert set of points to cells
        :points_list:
        :point_resolution: 
            default: self.point_resolution
        :returns: set of cells filling enclosed region
        """
        points = self.fill_points(point_list=point_list,
                                   point_resolution=None)
        cells = self.points_to_cells(points)
        return cells 

    def points_to_cells(self, points):
        """ Convert points to cells
        :points: list, set iterable of points (x,y)
        :returns: set of cells
        """
        cells = set()
        for point in points:
            cell = self.get_point_cell(point)
            cells.add(cell)
        return cells

    """ begin_fill, end_fill support
    """
    def add_to_fill(self, *points):
        """ Add points to fill perimiter
        :points: points to add
        """
        for point in points:
            self._fill_perimiter_points.append(point)
            
    def do_fill(self):
        """ Fill, using fill perimiter points
        """
        fill_points = self.fill_points(
                        self._fill_perimiter_points)
        self.populate_cells_from_points(
                        fill_points,
                        color=self._color_fill)
    
            
    def fill_points(self, point_list, point_resolution=None):
        """ Fill surrounding points assuming points are connected
        and enclose an area. - we will, eventually, do
        "what turtle would do".
        Our initial technique assumes a convex region:
            given every sequential group of points (pn,
            pn+1,pn+2), pn+1 is within the fill region.
        We divide up the fill region into triangles:
            ntriangle = len(point_list)-2
            for i in rage(1,ntriangle):
                fill_triangle(pl[0],pl[i],pl[i+1])
            
        :point_list: list (iterable) of surrounding points
        :point_resolution: distance under which cells containing
                each point will cover region with no gaps
                default: self.point_resolution
        :returns: set of points (ix,iy) whose cells
                cover fill region
        """
        if point_resolution is None:
            point_resolution = self.point_resolution
        SlTrace.lg(f"fill_points: {pl(point_list)} res:{point_resolution}", "xpoint")
        fill_point_set = set()
        if len(point_list) < 3:
            return set()
         
        plist = iter(point_list)
        p1 = point_list[0]
        for i in range(2,len(point_list)):
            p2 = point_list[i]
            p3 = point_list[i-1]
            points = self.get_points_triangle(p1,p2,p3,
                                    point_resolution=point_resolution)
            fill_point_set.update(points)
        return fill_point_set

    def get_points_triangle(self,p1,p2,p3, point_resolution=None):
        """ Get points in triangle
        The goal is that, when each returned point is used in generating the
        including cell, the resulting cells completely fill the triangle's
        region with minimum number of gaps and minimum fill outside the
        triangle. Strategy fill from left to right with vertical fill lines
        separated by a pixel distance of point_resolution which will be
        converted to fill points.
        
        Strategy

                                       * pxs[1]
                                    *   *
                                  *      *        
                                *       |*
                              *         | *
                            * |         |  *
                          *   |         |  *
                        *|    |         |   *
                      *  |    |  more   |   *
                    *    |    |   lines |    *
                 *  |    |    |         |    *
        pxs[0] *    |    |    |         |    |*  
                 *  |    |    |         |    |*
                    *    |    |         |    | *
                      *  |    |         |    | *
                         *    |         |    |  *
                             *          |    |  *
                                *       |    |  *
                                   *    |    |   *
                                      * |    |   *
                                         *   |    *
                                           * |    |*
                                             *    |*
                                                *  *
                                                    *  pxs[2]

        Begin by adding points directly included by the
        triangle's three edges.  Then continue with
        the following.
        
        Construct a series of vertical fill lines separated
        by point_resolution such that the fill points from
        these lines will appropriately cover the triangle.
 
        Organize the triangle vertex points by ascending x
        coordinate value into list pxs:
                pxs[0]: pxs[0].x <= pxs[1].x minimum x
                pxs[1]: pxs[1].x <= pxs[2].x
                pxs[2]: pxs[2].x             maximum x
        
        Construct a list of x-coordinate values separated by
        point_resolution: xs
            pxs[0].x < xs[i] < pxs[2].x
        
        Construct a list of point pairs, each point being
        the end point of a vertical fill line with x coordinate
        in xs[i].  The vertical fill line end points will be
        stored in a coordinated pair of lists:
            pv_line_02 - end points on psx[0]-pxs[2]
            pv_line_012 - end points on pxs[0]-pxs[1]-pxs2]
        Each pair of end points is constructed for an
        x-coordinate found in xs[i] as such:
            1. One end point will be on the pxs[0]-pxs[2] line
               with x-coordinate of xs[i], and stored in
               list pv_line_02[i].
            2. The other end point will be, also with
               x-coordinate xs[i] on
                A. pxs[0]-pxs[1] line when xs[i] < pxs[1].x
                B. pxs[1]-pxs[2] line when xs[i] >= pxs[1].x
                    
        Each vertical fill line segment constructed from
        end points pv_line_02[i] and pv_line_012[i] is used
        to generate fill points at a separation of a distance
        point_resolution.
        :p1,p2,p3: triangle points (x,y) tupple
        :point_resolution:  maximum pint separation to avoid
            gaps default: self.point_resolution
        :returns: set of fill points
        """
        SlTrace.lg(f"get_points_triangle:{pl(p1)} {pl(p2)} {pl(p3)}", "xpoint")
        fill_points = set()
        if point_resolution is None:
            point_resolution = self.point_resolution
        por = point_resolution
        # Include the edge lines
        lep = self.get_line_points(p1, p2, point_resolution=por)
        fill_points.update(lep)
        lep = self.get_line_points(p2, p3, point_resolution=por)
        fill_points.update(lep)
        lep = self.get_line_points(p3, p1, point_resolution=por)
        fill_points.update(lep)
        x_min_p = p1
        x_min = p1[0]
        
        # Find x_min, max_x
        # Create pxs a list of the points
        # in ascending x order
        pxs = [x_min_p]    # point to process
                                # starting with min
        for p in [p2,p3]:
            x = p[0]
            if x < x_min:
                x_min = x 
                x_min_p = p
                pxs.insert(0,p)
            elif len(pxs) > 1 and x < pxs[1][0]:
                pxs.insert(1,p)
            else:
                pxs.append(p)
        # Generate list of x values separated by point_resolution
        # starting at x = x_min ending at or after max_x
        #
        xs = []
        x = x_min
        while x <= pxs[2][0]:
            xs.append(x)
            x += point_resolution
            
        SlTrace.lg(f"pxs:{pxs}", "xpoint")
        
        # Start including the three edges as perimiter   
        line_01_points = self.get_line_points(pxs[0], pxs[1],
                                point_resolution=point_resolution)
        line_02_points = self.get_line_points(pxs[0],pxs[2],
                                point_resolution=point_resolution)
        line_12_points = self.get_line_points(pxs[1], pxs[2],
                                point_resolution=point_resolution)
        # Place the edge points in the fill area
        fill_points.update(line_01_points)
        fill_points.update(line_02_points)
        fill_points.update(line_12_points)
        
        # proceed from left (x_min) to right (max_x)
        pv_line_02 = []
        pv_line_012 = []
        # populate vertical fill line line_02 end points
        self.set_line_funs(pxs[0],pxs[2])
        for i in range(len(xs)):
            x = xs[i]
            y = self.line_y(x)
            pv_line_02.append((x,y))
        
        # populate vertical fill line_012 end points
        self.set_line_funs(pxs[0],pxs[1])
        on_line_12 = False   # on or going to be
        last_line_01_x = pxs[1][0]
        for i in range(len(xs)):
            x = xs[i]
            if on_line_12 or x >= last_line_01_x:
                if not on_line_12:
                    self.set_line_funs(pxs[1], pxs[2])
                    on_line_12 = True  
            y = self.line_y(x)
            p = (x,y)
            pv_line_012.append(p)
        
        # Processing vertical fill lines
        for i in range(len(xs)):
            p1 = pv_line_02[i] 
            p2 = pv_line_012[i] 
            vline_points = self.get_line_points(p1,p2,
                                point_resolution=point_resolution)
            fill_points.update(vline_points)
        return fill_points

    def get_drawn_line_points(self, p1, p2, width=None,
                              point_resolution=None):
        """ Get drawn line fill points
        Find perimeter of surrounding points of a rectangle
        For  simplicity we consider vertical width
        :p1: beginning point
        :p2: end point
        :width: width of line
            default: self.line_width
        :point_resolution: fill point spacing
            default: self.point_resolution
        :returns: set of fill points
        """
        ###pts = self.get_line_points(p1,p2)
        ###return set(pts)
        
        if width is None:
            width = self.line_width
        if point_resolution is None:
            point_resolution = self.point_resolution
        pr = point_resolution
        SlTrace.lg(f"get_drawn_Line_points {p1} {p2}"
                   f" width: {width} res: {pr}", "xpoint")
        p1x,p1y = p1
        p2x,p2y = p2
        self.set_line_funs(p1, p2)
        
        dx = self.lfun_unorm_x*width/2 # draw width offsets
        dy = self.lfun_unorm_y*width/2
        pp1 = (p1x+dx,p1y+dy) # upper left corner
        pp2 = (p2x+dx,p2y+dy) # upper right corner
        pp3 = (p2x-dx,p2y-dy) # lower right corner
        pp4 = (p1x-dx,p1y-dy) # lower left corner
        perim_list = [pp1, pp2, pp3, pp4]
        filled_points = self.fill_points(perim_list)
        return filled_points
    
    def get_line_points(self, p1, p2, point_resolution=None):
        """ Get spaced points on line from p1 to p2
        :p1: p(x,y) start
        :p2: p(x,y) end
        :point_resolution: maximum separation
        :returns: list of points from p1 to p2
                separated by point_resolution pixels
        """
        SlTrace.lg(f"\nget_line_points: p1={pl(p1)} p2={pl(p2)}", "xpoint")
        self.set_line_funs(p1=p1, p2=p2)
        if p1 == p2:
            return [p1,p2]
        
        if point_resolution is None:
            point_resolution = self.point_resolution
        x1,y1 = p1
        x2,y2 = p2
        p_chg = point_resolution
        
        pt = p1
        point_list = [p1]       # Always include end points
        p_len = 0.               # Travel length
        while True:
            pt_x,pt_y = pt
            p_len += p_chg
            SlTrace.lg(f"pt={pl(pt)} p_len={p_len:.5}", "xpoint")
            if p_len > self.lfun_dist:
                break
            
            pt_x = int(x1 + p_len*self.lfun_cos)
            pt_y = int(y1 + p_len*self.lfun_sin)
            pt = (pt_x,pt_y)
            point_list.append(pt)
        
        # at end point, if not already there
        if pt != point_list[-1]:
            point_list.append(pt)
            
        SlTrace.lg(f"return: {point_list}", "xpoint")
        return point_list
    
    def populate_cells_from_points(self, points, color=None):
        """ Populate display cells, given points, color
        :points: set/list of points(x,y) tuples
        :color: cell color
                default: self._color
        """
        SlTrace.lg(f"populate_cells_from_points: add: "
                   f" {len(points)} points before:"
                   f" {len(self.cells)}", "point")
        if color is None:
            color = self._color
        
        for point in points:
            SlTrace.lg(f"point:{point}", "point")
            self.update_cell(pt=point, color=color)
        SlTrace.lg(f"populate_cells: cells after: {len(self.cells)}", "xpoint")

    def color_str(self, color):
        """ convert turtle colors arg(s) to color string
        :color: turtle color arg
        """
        color_str = color
        if (color_str is None
             or (isinstance(color_str, tuple)
                  and len(color_str) == 0)
             ):
            color_str = self._color
        if isinstance(color_str,tuple):
            if len(color_str) == 1:
                color_str = color_str[0]
            else:
                color_str = "pink"  # TBD - color tuple work
        return color_str
    
    def braille_for_color(self, color):
        """ Return dot list for color
        :color: color string or tuple
        :returns: list of dots 1,2,..6 for first
                letter of color
        """
        
        if color is None:
            color = self._color
        if color is None:
            color = ("black")
        color = self.color_str(color)
        c = color[0]
        dots = self.braille_for_letter(c)
        return dots
    
    def braille_for_letter(self, c):
        """ convert letter to dot number seq
        :c: character
        :returns: dots tupple (1,2,3,4,5,6)
        """
        if c not in BrailleDisplay.dots_for_character:            c = " " # blank
        dots = BrailleDisplay.dots_for_character[c]
        return dots
        
    def complete_cell(self, cell, color=None):
        """ create/Fill braille cell
            Currently just fill with color letter (ROYGBIV)
        :cell: (ix,iy) cell index or BrailleCell
        :color: cell color default: current color
        """
        if color is None:
            color = self._color
        dots = self.braille_for_color(color)
        bc = BrailleCell(ix=cell[0],iy=cell[1], dots=dots, color=color)
        self.cells[cell] = bc

    def braille_window(self, title, show_points=False):
        """ switch between braile_window_none and
            braille_window_audio
        """
        self.braille_window_audio(title, show_points)
        ###self.braille_window_none(title, show_points)
        
    def braille_window_none(self, title, show_points=False):
        """ Display current braille in a window
        :title: window title
        :show_points: Show included points instead of braille dots
                default: False - show braille dots
        """
        mw = Tk()
        if title is not None and title.endswith("-"):
            title += " Braille Window"
        mw.title(title)
        self.mw = mw
        canvas = Canvas(mw, width=self.win_width, height=self.win_height)
        canvas.pack()
        self.braille_canvas = canvas
        for ix in range(self.grid_width):
            for iy in range(self.grid_height):
                cell_ixy = (ix,iy)
                if cell_ixy in self.cells:
                    self.display_cell(self.cells[cell_ixy],
                                      show_points=show_points)
        mw.update()     # Make visible

    def braille_window_audio(self, title, show_points=False):
        """ Display current braille in a window
            with audio feedback
        :title: window title
        :show_points: Show included points instead of braille dots
                default: False - show braille dots
        """
        if title is not None and title.endswith("-"):
            title += " Braille Window"
        aud_win = AudioWindow(title=title,
                              win_width=self.win_width,
                              win_height=self.win_height,
                              grid_width=self.grid_width,
                              grid_height=self.grid_height,
                              x_min=self.x_min, y_min=self.y_min)
        aud_win.draw_cells(cells=self.cells, show_points=show_points)

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



    def show_item(self, item):
        """ display changing values for item
        """
        canvas = self.screen.getcanvas()
        iopts = canvas.itemconfig(item)
        itype = canvas.type(item)
        coords = canvas.coords(item)
        if itype in self.tk_item_samples:
            item_sample_iopts = self.tk_item_samples[itype]
        else:
            item_sample_iopts = None
        SlTrace.lg(f"{item}: {itype} {coords}")
        for key in iopts:
            val = iopts[key]
            is_changed = True     # assume entry option changed
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
                SlTrace.lg(f"    {key} {val}")
            self.tk_item_samples[itype] = iopts


    def print_tk_items(self, title=None):
        """ Display current braille in a window
        """
        self.tk_item_samples = {}
        if title is not None:
            SlTrace.lg(title)
        canvas = self.screen.getcanvas()
        for item in sorted(canvas.find_all()):
            self.show_item(item)
        SlTrace.lg("")

    def display(self, braille_window=True, braille_print=True,
               print_cells=False, title=None,
               points_window=False,
               tk_items=False):
        """ display grid
        :braille_window: True - make window display of braille
                        default:True
        :braille_print: True - print braille
                        default: True
        :print_cells: True - print out non-empty cells
                        default: False
        :title: text title to display
                    default:None - no title
        :points_window: make window showing display points
                        instead of braille dots
                    default: False - display dots
        :tk_items: True - display tkinter obj in cell
                    default: False
        """
        self.find_edges()
        if braille_window:
            if title is None:
                title = "Audio Feedback -"
            tib = title
            if tib is not None and tib.endswith("-"):
                tib += " Braille Window"
            self.braille_window(title=tib)
        if points_window:
            tib = title
            if tib is not None and tib.endswith("-"):
                tib += " Display Points"
            self.braille_window(title=tib, show_points=points_window)
        if braille_print:
            tib = title
            if tib is not None and tib.endswith("-"):
                tib += " Braille Print Output"
            self.print_braille(title=tib)
        if print_cells:
            tib = title
            if tib is None:
                tib = "Print Cells"
            if tib is not None and tib.endswith("-"):
                tib += " Braille Cells"
            self.print_cells(title=tib)
        if tk_items:
            tib = title
            if tib is not None and tib.endswith("-"):
                tib += " Tk Cells"
            self.print_tk_items(title=tib)

    def find_edges(self):
        """Find  top and left non-blank edges
        so we can shift picture to left,top for easier
        recognition
        """
        left_edge = self.grid_width-1
        for iy in range(self.grid_height):
            for ix in range(left_edge):     # till closest found
                cell_ixy = (ix,iy)
                if cell_ixy in self.cells:
                        left_edge = ix  # Found lines left
                        break
        if left_edge > 0:           # Give some space
            left_edge -= 1
        if left_edge > 0:
            left_edge -= 1
        self.left_edge = left_edge
        
        top_edge = 0
        for ix in range(self.grid_width):
            for iy in reversed(range(top_edge, self.grid_height)):
                cell_ixy = (ix,iy)
                if cell_ixy in self.cells:
                    top_edge = iy  # Found lines top
                    break
        if top_edge < self.grid_height-1:           # Give some space
            top_edge += 1
        if top_edge  < self.grid_height-1:
            top_edge += 1
        self.top_edge = top_edge
        return left_edge, top_edge
    
    def clear_display(self):
        """ Clear display for possible new display
        """
        self.cmds = []      # Commands to support redo
        self.cells = {}     # BrailleCell hash by (ix,iy)
        

    def snapshot(self, title=None, clear_after=False):
        """ Take snapshot of current braille_screen
        :title: title of snapshot
        :clear_after: clear braille screen after snapshot
        """
        
    
    
    def display_cell(self, cell, show_points=False):
        """ Display cell
        :cell: BrailleCell
        :show_points: show points instead of braille
                default: False --> show braille dots
        """
        ix = cell.ix
        iy = cell.iy 
        canvas = self.braille_canvas
        cx1,cy1,cx2,cy2 = self.get_cell_rect_win(ix=ix, iy=iy)
        canvas.create_rectangle(cx1,cy1,cx2,cy2, outline="light gray")
        color = self.color_str(cell._color)
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
                canvas.create_oval(x0,y0,x1,y1, fill=color)
            self.mw.update()    # So we can see it now 
            return
            
        dots = cell.dots
        grid_width = cx2-cx1
        grid_height = cy1-cy2       # y increases down
        # Fractional offsets from lower left corner
        # of cell rectangle
        ll_x = cx1      # Lower left corner
        ll_y = cy2
        ox1 = ox2 = ox3 = .3 
        ox4 = ox5 = ox6 = .7
        oy1 = oy4 = .15
        oy2 = oy5 = .45
        oy3 = oy6 = .73
        dot_size = .25*grid_width   # dot size fraction
        dot_radius = dot_size//2
        dot_offset = {1: (ox1,oy1), 4: (ox4,oy4),
                      2: (ox2,oy2), 5: (ox5,oy5),
                      3: (ox3,oy3), 6: (ox6,oy6),
                      }
        for dot in dots:
            offsets = dot_offset[dot]
            off_x_f, off_y_f = offsets
            dx = ll_x + off_x_f*grid_width
            dy = ll_y + off_y_f*grid_height
            x0 = dx-dot_radius
            y0 = dy+dot_size 
            x1 = dx+dot_radius 
            y1 = dy
            canvas.create_oval(x0,y0,x1,y1, fill=color) 

    def update(self):
        self.mw.update()
                
    def get_cell_rect_win(self, ix, iy):
        """ Get cell's window rectangle x, y  upper left, x,  y lower right
        :ix: cell x index
        :iy: cell's  y index
        :returns: window(0-max): (x1,y1,x2,y2) where
            x1,y1 are lower left coordinates
            x2,y2 are upper right coordinates
        """
        if ix < 0:
            SlTrace.lg(f"ix:{ix} < 0")
            return (0,0,0,0)
        if ix >= len(self.cell_xs):
            SlTrace.lg(f"ix:{ix} >= {len(self.cell_xs)}")
            return (0,0,0,0)
        if iy < 0:
            SlTrace.lg(f"ix:{iy} < 0")
            return (0,0,0,0)
        if iy >= len(self.cell_ys):
            SlTrace.lg(f"iy:{iy} >= {len(self.cell_ys)}")
            return (0,0,0,0)
        tu_x1,tu_y1,tu_x2,tu_y2 = self.get_cell_rect_tur(ix,iy)
        w_x1 = tu_x1 + self.win_width//2
        w_y1 = self.win_height//2 - tu_y1
        w_x2 = tu_x2 + self.win_width//2
        w_y2 = self.win_height//2 - tu_y2
        return (w_x1,w_y1,w_x2,w_y2)
        
    def get_point_win(self, pt):
        """ Get point in window coordinates
        :pt: (x,y) point in turtle coordinates
        :returns: (x,y)
        """
        tu_x,tu_y = pt
        
        w_x = tu_x + self.win_width//2
        w_y = self.win_height//2 - tu_y
        return (w_x,w_y)
                    
        
    def get_cell_rect_tur(self, ix, iy):
        """ Get cell's turtle rectangle x, y  upper left, x,  y lower right
        :ix: cell x index
        :iy: cell's  y index
        """
        if ix < 0:
            SlTrace.lg(f"ix:{ix} < 0")
            return (0,0,0,0)
        if ix >= len(self.cell_xs):
            SlTrace.lg(f"ix:{ix} >= {len(self.cell_xs)}")
            return (0,0,0,0)
        if iy < 0:
            SlTrace.lg(f"ix:{iy} < 0")
            return (0,0,0,0)
        if iy >= len(self.cell_ys):
            SlTrace.lg(f"iy:{iy} >= {len(self.cell_ys)}")
            return (0,0,0,0)
        x1 = self.cell_xs[ix]
        x2 = self.cell_xs[ix+1]
        y1 = self.cell_ys[iy]
        y2 = self.cell_ys[iy+1]
        return (x1,y1,x2,y2)
                    
    def print_braille(self, title=None):
        """ Output braille
        """
        if title is not None:
            print(title)
        if self.shift_to_edge:
            self.find_edges()
            left_edge = self.left_edge
            top_edge = self.top_edge
        else:
            left_edge = 0
            top_edge = self.grid_height-1
            
        for iy in reversed(range(top_edge)):
            line = ""
            for ix in range(left_edge, self.grid_width):
                cell_ixy = (ix,iy)
                if cell_ixy in self.cells:
                    cell = self.cells[cell_ixy]
                    color = cell.color_str()
                    line += color[0]
                else:
                    line += " "
            line = line.rstrip()
            if self.blank_char != " ":
                line = line.replace(" ", self.blank_char)
            ###print(f"{iy:2}", end=":")
            print(line)

    """
    turtle commands
    These commands:
        1. call turtle via self.tu, self.screen
        2. set local drawing state
        3. create BrailleCell self.cells
        4. return turtle call return
    """
    def backward(self, length):
        return self.forward(-length)
    
    def color(self, *args):
        rt = self.tu.color(*args)
        if len(args) == 1:
            self.pencolor(args[0])
        elif len(args) == 2:
            self.pencolor(args[0])
            self.fillcolor(args[1])
        elif len(args) == 3:
            self._color = args
        return rt

    def pencolor(self, *args):
        rt = self.tu.pencolor(*args)
        if len(args) == 1:
            self._color = args[0]
        elif len(args) == 3:
            self._color = args
        else:
            raise Exception(f"pencolor illegal args:{args}")
        
        return rt
        
    def fillcolor(self, *args):
        rt = self.tu.fillcolor(*args)
        if len(args) == 1:
            self._color_fill = args[0]
        elif len(args) == 3:
            self._color_fill = args
        else:
            raise Exception(f"pencolor illegal args:{args}")
        
        return rt
        
    def dot(self, size=None, *color):
        rt = self.tu.dot(size, *color)
        self.add_dot(size, *color)
        return rt
    
    def filling(self):
        return self.tu.filling()
    
    def begin_fill(self):
        rt = self.tu.begin_fill()
        self.is_filling = True
        self._fill_perimiter_points = []
        return rt
        
                
    def end_fill(self):
        rt = self.tu.end_fill()
        self.do_fill()
        self.is_filling = False
        return rt
    
    def forward(self, length):
        """ Make step forward, updating location
        """
        rt = self.tu.forward(length)
        x1 = self.x
        y1 = self.y
        angle = self.angle
        rangle = angle/180*pi
        x2 = x1 + length*cos(rangle)
        y2 = y1 + length*sin(rangle)
        self.goto(x=x2, y=y2)
        return rt
    
    def goto(self, x, y=None):
        rt = self.tu.goto(x,y) 
        x1 = self.x
        y1 = self.y
        x2 = x 
        if y is None:
            y = self.y
        y2 = y 
        self.add_line(p1=(x1,y1), p2=(x2,y2))
        return rt

    def heading(self):
        rt = self.tu.heading()
        return rt 
            
    def setpos(self, x, y=None):
        return self.goto(x, y=y) 
    def setposition(self, x, y=None):
        return self.goto(x, y=y) 
    
    def left(self, angle):
        rt = self.tu.left(angle)
        self.angle += angle
        return rt
    
    def pendown(self):
        rt = self.tu.pendown()
        self.is_pendown = True
        return rt
    
    def penup(self):
        rt = self.tu.penup()
        self.is_pendown = False
        return rt
    
    def right(self, angle):
        rt = self.tu.right(angle)
        self.angle -= angle
        return rt

    def setheading(self, to_angle):
        rt = self.tu.setheading(to_angle)
        self.angle
        return rt
    def seth(self, to_angle):
        return self.setheading(to_angle)
        
    def speed(self, speed):
        rt = self.tu.speed(speed)
        self._speed = speed
        return self.tu.speed(speed)
    
    def mainloop(self):
        return self.screen.mainloop()
    def done(self):
        return self.mainloop()
    
    def pensize(self, width=None):
        rt = self.tu.pensize(width=width)
        if width is not None:
            self.line_width = width
        return rt
    def width(self, width=None):
        return self.pensize(width=width)

    # screen functions
    def screensize(self, canvwidth=None, canvheight=None, bg=None):
        return self.screen.screensize(canvwidth=None,
                                       canvheight=None, bg=None)

    # Special functions
    def set_blank(self, blank_char):
        """ Set blank replacement
        :blank_char: blank replacement char
        :returns: previous blank char
        """
        ret = self.blank_char
        self.blank_char = blank_char
        return ret
        
if __name__ == "__main__":
    import braille_display_test2

