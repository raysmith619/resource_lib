# braille_display  19Apr2022  crs  Author
"""
Display graphics on window
Supports simple graphical point, line specification
Supports display of 6-point cells
on grid_width by grid_height grid
Supports writing out braille stream
"""
from math import sin, cos, pi, atan, sqrt

from tkinter import *
from select_trace import SlTrace

class BrailleCell:
    """ braille cell info augmented for analysis
    """
    def __init__(self, dots=None, colors=None,
                 ix=0, iy=0):
        """ setup braille cell
        :dots: list of set dots default: none - blank
        :colors: colors str or tuple
        :ix: cell index(from 0) from left side
        :iy: cell index from bottom
        """
        self.ix = ix    # Include to make self sufficient
        self.iy = iy
        self.dots = dots
        self.colors = colors 
        
class DisplayCmd:
    """ Display command - create part of the display
        Supports rerunning display command list
        Records most recent values, to be used as defaults
    """
    cmd = None 
    p1 = None 
    x = None 
    y = None 
    p2 = None 
    pts = None 
    colos = "black" 
    width = 1
    size = 5
     
    def __init__(self, cmd=None, p1=None, x=None, y=None,
                    p2=None, pts=None,
                    size=None,
                    colors=None, width=None):
        self.cmd = cmd
        if p1 is None:
            if (x is not None or y is not None):
                if x is None:
                    x = DisplayCmd.x
                if y is None:
                    y = DisplayCmd.y
                p1 = (x,y)
            else:
                p1 = DisplayCmd.p2
        if p1 is None:
            p1 = DisplayCmd.p2
        if p2 is None:
            p2 = DisplayCmd.p2
            
        DisplayCmd.p1 = self.p1 = p1
        DisplayCmd.p2 = self.p2 = p2
        
        DisplayCmd.x = self.x = x 
        DisplayCmd.y = self.y = y
        if size is None:
            size = DisplayCmd.size
        DisplayCmd.size = size
        self.pts = pts      # No default
        if colors is None:
            colors = DisplayCmd.colors 
        DisplayCmd.colors = self.colors = colors 
        DisplayCmd.width = self.width = width
        self.p12_line_vals = {}    # generic p1,p2 line function
                            # constants
        
    def __str__(self):
        st = f"DisplayCmd: {self.cmd}"
        if self.p1 is not None:
            st += f" pt1: {self.p1}"
        if self.p2 is not None:
            st += f" pt2: {self.p2}"
        if self.colors is not None:
            st += f" color: {self.colors}"
        if self.width is not None:
            st += f" width: {self.width}"
        return st
        

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
    """ Create and display graphics on a braille screen
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
                 win_width=800, win_height=800,
                 grid_width=40, grid_height=25,
                 use_full_cells= True,
                 x_min=None, y_min=None,
                 line_width=1, color="black",
                 point_resolution=None):
        """ Setup display
        :title: display screen title
        :win_width: display window width in pixels
            default: 800
        :win_height: display window height in pixels
            default: 800
        :grid_width: braille width in cells
            default: 40
        :grid_height: braille width in cells
            default: 25
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
        """
        if title is None:
            title = "Braille Display"
        self.title = title
        self.win_width = win_width
        self.win_height = win_height
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
        self.color = color
        self.cmds = []      # Commands to support redo
        self.cells = {}     # BrailleCell hash by (ix,iy)
        self.set_cell_lims()
        self.lfun_horz = False 
        self.lfun_vert = False 
        self.p2 = self.p2 = (0,0)
        
    def set_cell_lims(self):
        """ create cell bottom values through top
         so:
             cell_xs[grid_width] == right edge
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
        
        
    def add_color(self, colors=None):
        """ Add color string, or color tuple
        :color: tuple - color, fill
                string - color string
        """
        dc = DisplayCmd(cmd="add_color", colors=colors)
        self.add_color_do(dc)

    def add_color_do(self, cmd):
        """ Execute add_colors action
        """
        SlTrace.lg(f"add_colors_do: {cmd}")
        self.colors = cmd.colors
        
        
    def add_dot(self, size=None, colors=None):
        """ Add new point
        :size: diameter of dot
        :colors: point colors
        """
        dc = DisplayCmd(cmd="add_dot", size=size,
                         colors=colors)
        self.cmds.append(dc)
        self.add_dot_do(dc)

    def add_dot_do(self, cmd):
        """ Execute add_dot action
        """
        SlTrace.lg(f"add_dot_do: {cmd}", "braille_cmd")
        pt = cmd.p2
        if pt is None:
            pt = cmd.p1
        if pt is None:
            pt = self.p2
        if pt is None:
            pt = self.p2
            
        cells = self.get_dot_cells(pt=pt, size=cmd.size, colors=cmd.colors)
        self.populate_cells(cells)
        
        
    def add_point(self, p1=None, x=None, y=None, colors=None,
                  width=None):
        """ Add new point
        :p1: (x,y) pair for point
        OR 
        :x: x-position on win_width/win_height screen
            default: previous x
        :y: y-position on win_width/win_height screen
            default: previous y
        :colors: point colors
        :width: width for connecting points
            default: previous width [1]
        """
        dc = DisplayCmd(cmd="add_point", p1=p1, x=x, y=y,
                        colors=colors, width=width)
        DisplayCmd.p2 = p1      # Save as destination
        self.cmds.append(dc)
        self.add_point_do(dc)

    def add_point_do(self, cmd):
        """ Execute add_point action
        """
        SlTrace.lg(f"add_point_do: {cmd}")
        cells = self.get_point_cells(pt=cmd.p1, width=cmd.width)
        self.populate_cells(cells)
        

    def add_line(self, p1=None, p2=None, colors=None, width=None):
        """ Add new line
        :p1: xy pair - beginning point
            default: previous point (add_point or add_line)
        :p2: xy pair - ending point
            default: previous point (add_point or add_line)
        :colors: line colors
            default: previous color ["black"]
        :width: line width 
            default: previous width [1]
        """
        dc = DisplayCmd(cmd="add_line", p1=p1, p2=p2,
                        colors=colors, width=width)
        self.cmds.append(dc)
        self.add_line_do(dc)

    def add_line_do(self, cmd):
        """ Execute command
        """
        self.p1 = cmd.p1
        self.p2 = cmd.p2
        cells = self.get_line_cells(cmd.p1, cmd.p2, cmd.width)
        self.populate_cells(cells)
        
    def add_lines(self, pts, colors=None, width=None):
        """ Add new line
        :pts: list of points (x,y) pairs
        :colors: line color
            default: previous color ["black"]
        :width: line width 
            default: previous width [1]
        """
        dc = DisplayCmd(cmd="add_lines", pts=pts,
                        colors=colors, width=width)
        self.cmds.append(dc)
        self.add_lines_do(dc)

    def add_lines_do(self, cmd):
        """ Execute command
        """
        
        
    def set_color(self, color):
        """ Set color
        :color: point color
        """
        dc = DisplayCmd(cmd="set_color")
        self.cmds.append(dc)
        self.set_color_do(dc)


    def set_color_do(self, cmd):
        """ Execute add_point action
        """
        SlTrace.lg(f"set_color_do: {cmd}")
        self.color = cmd.color
            
            
    def set_p12_line_funs(self, p1, p2):
        """ Set line functions which provide determine
        x from y,  y from x to place (x,y) on line
        functions are self.p12_line_x(y, p1=p1, p2=p2)
        and self.p12_line_y(x, p1=p1, p2=p2)
        Store m, c constants in self.p12fun[(p1,p2)].lfun.XXX
                    p1
                    p2
                    horz
                    vert
                    my
                    cy
                    mx
                    cx
        :p1: beginnin point (x,y)
        :p2: ending point (x,y)
        """
        x1,y1 = p1
        x2,y2 = p2
        x_diff = x2 - x1
        y_diff = y2 - y1
        horz = False 
        vert = False 
        
        if x_diff == 0:
            vert = True 
        else:
            my = y_diff/x_diff
            cy = y1 - self.lfun_my*x1 
        if y_diff == 0:
            horz = True 
        else:
            mx = x_diff/y_diff 
            cx = x1 - self.lfun_mx*y1 
        self.p12_line_vals[(p1,p2)] = P12LineVals(
            p1=p1,p2=p2,horz=horz,vert=vert,
            mx=mx,cx=cx, my=my, cy=cy)
        
        
    def set_line_funs(self, p1, p2):
        """ Set line functions which provide determine
        x from y,  y from x to place (x,y) on line
        functions are self.line_x(y) and self.line_y(x)
        :p1: beginnin point (x,y)
        :p2: ending point (x,y)
        """
        SlTrace.setFlags("point")
        x1,y1 = p1
        x2,y2 = p2
        x_diff = x2 - x1
        y_diff = y2 - y1
        self.lfun_p1 = p1
        self.lfun_p2 = p2
        self.lfun_horz = False 
        self.lfun_vert = False
        self.lfun_rangle = 0 
        self.lfun_sin = 1       # to support x = s*sin(0),...
        self.lfun_cos = 1
        if x_diff == 0:
            self.lfun_vert = True 
        else:
            self.lfun_my = y_diff/x_diff
            self.lfun_cy = y1 - self.lfun_my*x1 
        if y_diff == 0:
            self.lfun_horz = True 
        else:
            self.lfun_mx = x_diff/y_diff 
            self.lfun_cy = y1 - self.lfun_my*x1 
            self.lfun_cx = x1 - self.lfun_mx*y1
        if x_diff == 0:
            rangle = pi/2
        elif y_diff == 0:
            rangle = 0
        else:
            rangle = atan(1/self.lfun_my)
        self.rangle = rangle
        self.lfun_sin = sin(rangle)
        self.lfun_cos = cos(rangle)
            
    def line_y(self, x):
        """ calculate pt y, given pt x
        having line setup from set_line_funs
        :x: pt x value
        :returns:  y value , None if undetermined
        """
        if self.lfun_horz:
            return self.lfun_p1[1]  # constant y
        
        if self.lfun_vert:
            return None 
        
        y = self.lfun_my*x + self.lfun_cy
        return y

    def p12_line_y(self, x, p1=None, p2=None):
        """ calculate pt y, given pt x
        having line setup from set_p12_line_funs
        :x: pt x value
        :p1: first point of line
        :p2: last point of line
        :returns:  y value , None if undetermined
        """
        if p1 is None:
            raise Exception ("p1, required is missing")
        if p2 is None:
            raise Exception ("p2, required is missing")
        
        pvals = self.p12_line_vals[(p1,p2)]
        if pvals.horz:
            return pvals.p1[1]  # constant y
        
        if pvals.vert:
            return None 
        
        y = pvals.my*x + pvals.cy
        return y

    def line_x(self, y):
        """ calculate pt x, given pt y
        having line setup from set_line_funs
        :x: pt x value
        :returns:  x value , None if undetermined
        """
        if self.lfun_horz:
            return None 
        
        if self.lfun_vert:
            return self.lfun_p1[0]  # constant x
        
        x = self.lfun_mx*y + self.lfun_cx
        return x
        

    def p12_line_x(self, y, p1=None, p2=None):
        """ calculate pt x, given pt y
        having line setup from set_p12line_funs
        :x: pt x value
        :p1: first point of line
        :p2: second point of line
        :returns:  x value , None if undetermined
        """
        if p1 is None:
            raise Exception ("p1, required is missing")
        if p2 is None:
            raise Exception ("p2, required is missing")

        pvals = self.p12_line_vals[(p1,p2)]
        if pvals.horz:
            return None 
        
        if pvals.vert:
            return pvals.p1[0]  # constant x
        
        x = pvals.mx*y + pvals.cx
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
        :pt: x,y pair location in window coordinates
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
        
    def get_dot_cells(self, pt, size=None, colors=None):
        """ Get cells included by dot
        :pt: beginning point (x,y)
        :size: dot thickness in pixels
            default: previous line width
        :returns: list of cells included by dot
        """
        if size is None:
            size = self.line_width
        if pt is None:
            pt = self.p2
        if pt is None:
            pt = self.p1    
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
        cell_set_filled = self.fill_cells(point_list)    
        return cell_set_filled 

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
    
            
    def fill_points(self, point_list, point_resolution=None):
        """ Fill surrounding points assuming points are connected
        and enclose an area. - we will, eventualy, do
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
        fill_point_set = set()
        plist = iter(point_list)
        p1 = next(plist)
        while True:
            p2 = next(plist, None)
            if p2 is None:
                break 
            p3 = next(plist, None)
            if p3 is None:
                break 
            points = self.get_points_triangle(p1,p2,p3,
                                              point_resolution=point_resolution)
            fill_point_set.update(points)
        return fill_point_set

    def get_points_triangle(self,p1,p2,p3, point_resolution=None):
        """ Get points in triangle
        Strategy fill from left to right
        with vertical lines separated by point_resolution
        Start at x = min_x stopping at x >= max_x
        :p1,p2,p3: triangle points (x,y) tupple
        :point_resolution:  maximum pint separation to avoid
            gaps default: self.point_resolution
        :returns: set of fill points
        """
        min_x_p = p1
        min_x = p1[0]
        
        # Find min_x, max_x
        # Create pxs a list of the points
        # in ascending x order
        pxs = [min_x_p]    # point to process
                                # starting with min
        for p in [p2,p3]:
            x = p[0]
            if x < min_x:
                min_x = x 
                min_x_p = p
                pxs.insert(0,p)
            elif len(pxs) > 1 and x < pxs[1][0]:
                pxs.insert(1,p)
            else:
                pxs.append(p)
        fill_points = set()    
        # Process traiangle in two steps
        # with increasing x values
        #   pxs[0] to pxs[1]        
        #   psx[1] to pxs[2] 
        
        # pxs[0] to pxs[1]   
        line_01_points = self.get_line_points(pxs[0], pxs[1],
                                point_resolution=point_resolution)
        line_02_points = self.get_line_points(pxs[0],pxs[2],
                                point_resolution=point_resolution)
        for i in range(len(line_01_points)):
            p_line_01 = line_01_points[i]
            p_line_02 = line_02_points[i] 
            vert_points = self.get_line_points(p_line_01,p_line_02)
            fill_points.update(vert_points)

        # pxs[1] to pxs[2]
        end_line_01 = len(line_01_points)
        line_12_points = self.get_line_points(pxs[1], pxs[2],
                                point_resolution=point_resolution)
        end_line_02 = len(line_02_points)
        for i in range(end_line_01, end_line_02):
            p_line_02 = line_02_points[i]
            p_line_12 = line_12_points[i-end_line_02] 
            vert_points = self.get_line_points(p_line_02,p_line_12,
                              point_resolution=point_resolution)
            fill_points.update(vert_points)
        return fill_points

    def get_line_points(self, p1, p2, point_resolution=None):
        """ Get spaced points on line from p1 to p2
        :p1: p(x,y) start
        :p2: p(x,y) end
        :point_resolution: maximum separation
        :returns: list of points from p1 to p2
                separated by point_resolution pixels
        """
        SlTrace.lg(f"\nget_line_points: p1={p1} p2={p2}", "point")
        if point_resolution is None:
            point_resolution = self.point_resolution
        self.set_line_funs(p1=p1, p2=p2)
        x1,y1 = p1
        x2,y2 = p2
        p_dist_between_12 = sqrt((x2-x1)**2+(y2-y1)**2)
        p_chg = point_resolution
        
        pt = p1
        point_list = [p1]       # Always include end points
        while True:
            pt_x,pt_y = pt
            px_chg = p_chg*self.lfun_cos
            py_chg = p_chg*self.lfun_sin
            pt_x = pt_x + px_chg
            pt_y = pt_y + py_chg
            pt = (pt_x,pt_y)
            SlTrace.lg(f"pt={pt}")
            p_dist = sqrt((pt_x-x1)**2+(pt_y-y1)**2)
            if p_dist >= p_dist_between_12:
                # at end point, if not already there
                pt_x,pt_y = int(pt_x),int(pt_y)
                pt = (pt_x,pt_y)
                if pt !=point_list[-1]:
                    point_list.append(pt)
                break
             
            point_list.append(pt)
            
        SlTrace.lg(f"return: {point_list}", "point")
        return point_list
    
    def populate_cells(self, cells, colors=None):
        """ Populate display cells
        :cells: set/list of ix,iy pairs
        :colors: cell colors
                default: self.color
        """
        SlTrace.lg(f"populate_cells: add: {len(cells)} cells before: {len(self.cells)}", "cell")
        if colors is None:
            colors = DisplayCmd.colors
        
        for cell in cells:
            if SlTrace.trace("cell"):
                if cell in self.cells:
                    SlTrace.lg(f"{cell} already in self.cells")
                else:
                    SlTrace.lg(f"{cell} is new")
            self.complete_cell(cell, colors=colors)
        SlTrace.lg(f"populate_cells: cells after: {len(self.cells)}", "cell")

    def braille_for_color(self, colors):
        """ Return dot list for color
        :colors: color string or tuple
        :returns: list of dots 1,2,..6 for first
                letter of color
        """
        if colors is None:
            colors = ("black")
        if isinstance(colors, str):
            colors = (colors)
        if len(colors) < 1:
            colors = ("black")
        c = colors[0]
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
        
    def complete_cell(self, cell, colors=None):
        """ Fill braille cell
            Currently just fill with color letter (ROYGBIV)
        :cell: (ix,iy) cell index
        :color: cell color default:DisplayCmd.color
        """
        if colors is None:
            colors = DisplayCmd.colors
        dots = self.braille_for_color(colors)
        bc = BrailleCell(ix=cell[0],iy=cell[1], dots=dots, colors=colors)
        self.cells[cell] = bc

    def braille_display(self):
        """ Display current braille in a window
        """
        mw = Tk()
        mw.title(self.title)
        self.mw = mw
        canvas = Canvas(mw, width=self.win_width, height=self.win_height)
        canvas.pack()
        self.braille_canvas = canvas
        for ix in range(self.grid_width):
            for iy in range(self.grid_height):
                cell_ixy = (ix,iy)
                if cell_ixy in self.cells:
                    self.display_cell(self.cells[cell_ixy])


    def print_cells(self):
        """ Display current braille in a window
        """
        SlTrace.lg(f"print_cells {len(self.cells)} on")
        for ix in range(self.grid_width):
            for iy in range(self.grid_height):
                cell_ixy = (ix,iy)
                if cell_ixy in self.cells:
                    SlTrace.lg(f"ix:{ix} iy:{iy} {cell_ixy}"
                          f" rect: {self.get_cell_rect_tur(ix,iy)}"
                          f"  win rect: {self.get_cell_rect_win(ix,iy)}")
        SlTrace.lg("")


    def display_cell(self, cell):
        """ Display cell
        :cell: BrailleCell
        """
        ix = cell.ix
        iy = cell.iy 
        canvas = self.braille_canvas
        cx1,cy1,cx2,cy2 = self.get_cell_rect_win(ix=ix, iy=iy)
        canvas.create_rectangle(cx1,cy1,cx2,cy2)
        colors = cell.colors
        dots = cell.dots
        grid_width = cx2-cx1
        grid_height = cy1-cy2       # y increases down
        # Fractional offsets from lower left corner
        # of cell rectangle
        ll_x = cx1      # Lower left corner
        ll_y = cy2
        ox1 = ox2 = ox3 = .3 
        ox4 = ox5 = ox6 = .7
        oy1 = oy4 = .25
        oy2 = oy5 = .55
        oy3 = oy6 = .85
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
            canvas.create_oval(x0,y0,x1,y1, fill=colors) 
    def mainloop(self):
        """ tk.mainloop() link
        """
        self.mw.mainloop()
        
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
                    
    def braille_print(self):
        """ Output braille
        """
        for iy in range(self.grid_height):
            line = ""
            for ix in range(self.grid_width):
                cell_ixy = (ix,iy)
                if cell_ixy in self.cells:
                    cell = self.cells[cell_ixy]
                    line += cell.colors[0]
                else:
                    line += " "
            line.rstrip()
            print(line)
        
if __name__ == "__main__":
    SlTrace.lg("Self Test")
    SlTrace.clearFlags()
    SlTrace.setFlags("point")
    bw = BrailleDisplay()
    
    if SlTrace.trace("cell"):
        SlTrace.lg("cell limits")
        for ix in range(len(bw.cell_xs)):
            SlTrace.lg(f"ix: {ix} {bw.cell_xs[ix]:5}")
        for iy in range(len(bw.cell_ys)):
            SlTrace.lg(f"iy: {iy} {bw.cell_ys[iy]:5}")
        
    sz = 300
    color = "purple"
    wd = 1
    a_dot = True
    a_square = False
    a_diamond = False
    if a_dot:
        bw.add_dot(size = sz, colors=color)
        
    if a_square:
        bw.add_point(p1=(-sz,sz), colors=color, width=wd)
        bw.add_line(p2=(sz,sz))
        bw.add_line(p2=(sz,-sz))
        bw.add_line(p2=(-sz,-sz))
        bw.add_line(p2=(-sz,sz))

    sz *= .7
    if a_diamond:
        color = "red"
        bw.add_point(p1=(0,sz), colors=color, width=wd)
        bw.add_line(p2=(sz,0))
        bw.add_line(p2=(0,-sz))
        bw.add_line(p2=(-sz,0))
        bw.add_line(p2=(0,sz))
    bw.braille_display()
    SlTrace.lg("braille_output")
    bw.braille_print()
    if SlTrace.trace("cells"):
        bw.print_cells()
    bw.mainloop()      
