# draw_marker.py    26Feb2021  crs  drawing objects
"""
Start generalizing as we might have done before_move
"""
from tkinter import *
import copy
import math
import tkinter as tk

from select_trace import SlTrace
from select_error import SelectError
from select_window import SelectWindow

def tp(tps):
    """ Convert tuple to (,,,,) of .0f
    :tps:tuple or list
    """
    tp_str = "("
    for t in tps:
        if tp_str != "(":
            tp_str += ","   # separator
        if t is None:
            tp_str += "None"
        else:
            tp_str += f"{t:.0f}"
    tp_str += ")"
    return tp_str

""" Drawing artifacts
    Only applicable to drawn objects
"""
class DrawnArtifacts:
    def __init__(self):
        self.tags = []
        self.images = []
        
""" Marker info for do / modifications / undo
"""
class DmMarker:
    DT_UNKNOWN = "dt_unknown"
    DT_COLOR = "dt_color"
    DT_HEADING = "dt_heading"
    DT_LINE = "dt_line"
    DT_MOVE = "dt_move"
    DT_MOVE_KEY = "dt_move_key"
    DT_SQUARE = "dt_square"
    DT_TRIANGLE = "dt_triangle"
    DT_CIRCLE = "dt_circle"
    DT_IMAGE = "dt_image"
    DT_SIZE = "dt_size"
    DT_TEXT = "dt_text"     # letter but possibley more
    DT_PEN = "dt_pen"
    DT_POINTER = "dt_pointer"   # turtle pointer
    DT_POSITION = "dt_position"

    def __init__(self, drawer, draw_type=None,
                 copy_move="copy",
                 heading=None, side=None, line_width=None,
                 color=None,
                 x_cor=None,  y_cor=None
                  ):
        """ Setup basic marker state
        :drawer: drawing control
        :draw_type: marker drawing type
                    REQUIRED
        :copy_move: Type operation copy/move/goto operation on destination
                    copy - replicate marker at destination
                    move - move marker(remove from current place) to destination
                    goto - move selector to destination, leaving markers unchanged
                    
                    default: "copy" replicate marker at destination
        :heading: marker direction default: drawer.heading
        :side: marker side size default: drawer.side
        :line_width: marker's line width defalt:drawer.side
        :color: marker's color default: drawer.
        :x_cor: marker's base x_coordinate default: drawer.x_cor
        :y_cor: marker's base y_coordinate default: drawer.y_cor
        """
        self.image_stores = []      # To avoid image loss by reclamation
        self.drawer = drawer
        if draw_type is None:
            raise SelectError("DmMarker: draw_type missing")
        self.draw_type = draw_type
        if copy_move is None:
            copy_move = drawer.get_copy_move()
        self.copy_move = copy_move
        if heading is None:
            heading = drawer.get_heading()
        self.heading = heading
        if side is None:
            side = drawer.get_side()
        self.side = side
        if line_width is None:
            line_width = drawer.get_width()
        self.line_width = line_width
        self.color = color
        if x_cor is None:
            x_cor = drawer.get_x_cor()
        self.x_cor = x_cor
        if y_cor is None:
            y_cor = drawer.get_y_cor()
        self.y_cor = y_cor
        self.update_tur_scale()
        self.drawn = None       # drawn artifacts
    
    def __str__(self):
        str_str = self.__class__.__name__
        str_str += f" {self.copy_move}"
        str_str += f" {self.color}"
        str_str += f" heading={self.heading:.1f}"
        str_str += f" side={self.side:.0f}"
        str_str += f" line_width={self.line_width:.0f}"
        str_str += f" x={self.x_cor:.0f} y={self.y_cor:.0f}"
        return str_str

    def copy(self):
        """ Deep copy for every thing but drawing_controler
        :returns: copied object
        """
        new_obj = copy.copy(self)
        for k, v in self.__dict__.items():
            if k == 'drawer':
                continue        # Just ref
            if k == 'drawn':
                continue        # Don't preserve drawn
            if isinstance(v, Image):
                continue
            if isinstance(v, PhotoImage):
                continue
            try:
                new_obj.__dict__[k] = copy.deepcopy(v)
            except:
                if k in new_obj.__dict__: 
                    new_obj.__dict__[k] = v     # Just pass ref
        return new_obj

    def use_locale(self, marker, cmd=None):
        """ create self copy, then change to locale values
        used by marker  In essence give new marker the locale
        of marker (location, heading...) - shorthand for change()
        :marker: pattern command
        :cmd: later adjustments by command e.g. heading
                default: no adjustments
        """
        new_obj = self.copy()
        new_obj.heading = marker.heading
        new_obj.side = marker.side
        new_obj.line_width = marker.line_width
        new_obj.color = marker.color
        new_obj.x_cor = marker.x_cor
        new_obj.y_cor = marker.y_cor
        if cmd is not None:
            new_obj.heading = cmd.get_heading() # Use latest
        return new_obj
        
    def change(self, 
               move_it=False, move_by=None, heading_by=None,
               heading=None, side=None, line_width=None,
               color=None, x_cor=None,  y_cor=None):
        """ Return a changed version of this object with the 
        non-None parameters changed
        :moveit: if True move object
        :move_by: distance to move
                default: heading
        :heading_by:  move direction
                default: heading
        """
        new_obj = self.copy()
        
        if heading is not None:
            new_obj.heading = heading
        if side is not None:
            new_obj.side = side
        if line_width is not None:
            new_obj.line_width = line_width
        if color is not None:
            new_obj.color = color
        
        if x_cor is not None:
            new_obj.x_cor = x_cor
        if y_cor is not None:
            new_obj.y_cor = y_cor

        if move_it:
            if x_cor or y_cor:
                raise SelectError(f"Can't also include x_cor or y_cor")
            
            if move_by is None:
                move_by = new_obj.side
            if heading_by is None:
                heading_by = new_obj.heading
            new_obj.x_cor, new_obj.y_cor = self.vadd(
                     heading=heading_by, length=move_by)
        return new_obj

    def get_heading(self):
        """ Get marker's heading, else drawer's heading
        """
        if self.heading is not None:
            return self.heading
        
        return self.drawer.get_heading()
    
    def get_next_loc(self):
        """ Get location for next marker, given
        current settings
        :regurns (x_cor,y_cor) of next placed
                marker
        """
        return self.vadd()

    def get_loc(self):
        """ Get our current location
        """
        return (self.x_cor, self.y_cor)

    def get_x_cor(self):
        return self.x_cor
    
    def get_y_cor(self):
        return self.y_cor
        
    def get_side(self):
        if self.side is not None:
            return self.side
        
        return self.drawer.get_side()
    
    def is_visible(self):
        """ Return True if this is a "visible" marker
        suitable for duplicating/repeating
        OVERRIDDEN if not a visible marker
        """
        return True 
        
    def rotate(self, angle=45):
        """ Rotate part
        :angle: angle to rotate
        :returns: new rotated object
        """
        new_heading = self.heading + angle
        new_obj = self.change(heading=new_heading)
        return new_obj
    
    def set_loc(self, loc):
        """ Set current locaion (x_cor, y_cor)
        :loc: location (x_cor,y_cor)
        """
        self.x_cor, self.y_cor = loc
        
    def args_to_kwargs(self, color=None, width=None, dkwargs=None):
        """ Adjust / check  args and kwargs for canvas_create...
        :dkwargs: returnable dictionary of kwargs
                    Adjusted if applicable
        """
                
        if color is not None:
            if 'fill' in dkwargs:
                raise SelectError(f"Can't have color: {color}"
                                  f" fill: {dkwargs['fill']}")
            dkwargs['fill'] = color
        else:
            dkwargs['fill'] = self.color
        if width is not None:
            if 'width' in dkwargs:
                raise SelectError(f"Can't have width: {color}"
                                  f" and dkwargs['width']: {dkwargs['width']}")
            dkwargs['width'] = width
        else:
            dkwargs['width'] = self.line_width
        
    def to_line_args(self, x1=None, y1=None,
                     length=None, heading=None,
                     color=None, width=None,
                     **kwargs):
        """ Calculate create_line args, based on origin, heading, side
        :x1: x origin coordinate default: self.x_cor
        :y1: y origin coordinate default: self.y_cor
        :length: length of line default: self.side
        :color: line color default: from kwargs['fill'], else self.color
        :width: line width default: from kwargs['width'], else self.line_width
        :heading: heading in deg default: self.heading
        :kwargs: dictionary  additional parameters
                defaults: color - self.color, else black
                        width - self.line_width, else 1
        :returs: x1,y1,x2,y2, kwargs as adjusted by defaults
        """
        if x1 is None:
            x1 = self.x_cor
            if x1 is None:
                x1 = 0
        if y1 is None:
            y1 = self.y_cor
            if y1 is None:
                y1 = 0
        if length is None:
            length = self.side
        self.length = length
        if heading is None:
            heading = self.heading
        
        if color is not None:
            if 'fill' in kwargs:
                raise SelectError(f"Can't have color: {color}"
                                  f" fill: {kwargs['fill']}")
            kwargs['fill'] = color
        else:
            kwargs['fill'] = self.color
        if width is not None:
            if 'width' in kwargs:
                raise SelectError(f"Can't have width: {color}"
                                  f" and kwargs['width']: {kwargs['width']}")
            kwargs['width'] = width
        else:
            kwargs['width'] = self.line_width
            
        """ Calculate x2,y2 from x1,y1,heading """
        theta = math.radians(heading)
        try:
            x_chg = self.length*math.cos(theta)
        except:
            SlTrace.lg(f"self.length:{self.length}")
            pass
        y_chg = self.length*math.sin(theta)
        x2 = x1 + x_chg
        y2 = y1 + y_chg
        return x1,y1,x2,y2,kwargs

    def vadd(self, x1=None, y1=None, heading=None, length=None):
        """ Vector add to get x2,y2, uses to_Line_args
        :x1,y1: x,y origin coordinates    default: x_cor, y_cor
        :heading: heading default: self.heading
        :length: distance default: self.side
        :returns: x2,y2
        """
        _,_,x2,y2,_ = self.to_line_args(x1=x1, y1=y1,
                                               heading=heading,
                                               length=length)
        return x2,y2

    def add_line(self, x1=None, y1=None,
                     length=None, heading=None,
                     color=None, width=None,
                     **kwargs):
        """ Add line origin,heading... as in to_line_args
        Line starts from middle of square going in heading direction
        :x1: x origin coordinate default: self.x_cor
        :y1: y origin coordinate default: self.y_cor
        :length: length of line default: self.side
        :color: line color default: from kwargs['fill'], else self.color
        :width: line width default: from kwargs['width'], else self.line_width
        :heading: heading in deg default: self.heading
        :kwargs: additional parameters
                defaults: color - self.color, else black
                        width - self.line_width, else 1
        """
        # Use square as basis, line bysects square
        # from center of left vertical to center of right vertical
        corners = self.get_square(x1=x1, y1=y1,
                     length=length, heading=heading,
                     color=color, width=width)
        x1 = (corners[0][0] + corners[3][0])/2
        y1 = (corners[0][1] + corners[3][1])/2
        x2 = (corners[1][0] + corners[2][0])/2
        y2 = (corners[1][1] + corners[2][1])/2
        
        _,_,_,_,k2args = self.to_line_args(
                        x1=x1, y1=y1,
                        length=length, heading=heading,
                        color=color, width=width, **kwargs)
        self.create_line(x1,y1,x2,y2, **k2args)

    def add_move(self, x1=None, y1=None,
                     length=None, heading=None,
                     color=None, width=None,
                     **kwargs):
        """ Add move origin,heading... as in to_line_args
        drawer loc update happens elsewhere - display_update
        
        :x1: x origin coordinate default: self.x_cor
        :y1: y origin coordinate default: self.y_cor
        :length: length of line default: self.side
        :color: line color default: from kwargs['fill'], else self.color
        :width: line width default: from kwargs['width'], else self.line_width
        :heading: heading in deg default: self.heading
        :kwargs: additional parameters
                defaults: color - self.color, else black
                        width - self.line_width, else 1
        """
        _,_,x2,y2,_ = self.to_line_args(
                        x1=x1, y1=y1,
                        length=length, heading=heading,
                        color=color, width=width, **kwargs)
        self.drawer.set_loc(locxy=(x2,y2))  # Redundant-display_update
        if heading is None:
            heading = self.get_heading()
        self.drawer.set_heading(heading)    # Redundant-display_update
        
    def add_triangle(self, x1=None, y1=None,
                     length=None, heading=None,
                     color=None, width=None,
                     **kwargs):
        """ Add triangle turtle style
        :x1: x origin coordinate default: self.x_cor
        :y1: y origin coordinate default: self.y_cor
        :length: length of line default: self.side (diameter)
        :color: line color default: from kwargs['fill'], else self.color
        :width: line width default: from kwargs['width'], else self.line_width
        :heading: heading in deg default: self.heading (of bounding box)
        :kwargs: additional parameters
                defaults: color - self.color, else black
                        width - self.line_width, else 1
        """
        if x1 is None:
            x1 = self.x_cor
        if y1 is None:
            y1 = self.y_cor
        if length is None:
            length = self.side
        if heading is None:

            heading = self.heading
        # Use square as basis, left verticle is base
        # center of right vertical is peak        
        corners = self.get_square(x1=x1, y1=y1,
                     length=length, heading=heading,
                     color=color, width=width)
        ptxy = []
        x,y = corners[0]
        ptxy.extend([x,y])
        p2 = ((corners[1][0]+corners[2][0])/2,
               (corners[1][1]+corners[2][1])/2)
        ptxy.extend([p2[0],p2[1]])
        x,y = corners[3]
        ptxy.extend([x,y])

        
        self.args_to_kwargs(color=color, width=width, dkwargs=kwargs)
        outline = kwargs['fill']
        kwargs['fill'] = ""
        kwargs['joinstyle'] = MITER
        self.create_polygon(*ptxy, outline=outline, **kwargs) 

    def add_square(self, x1=None, y1=None,
                     length=None, heading=None,
                     color=None, width=None,
                     **kwargs):
        """ Add square turtle style
        Origin is lower left corner of square
        :x1: x origin coordinate default: self.x_cor
        :y1: y origin coordinate default: self.y_cor
        :length: length of line default: self.side (diameter)
        :color: line color default: from kwargs['fill'], else self.color
        :width: line width default: from kwargs['width'], else self.line_width
        :heading: heading in deg default: self.heading (of bounding box)
        :kwargs: additional parameters
                defaults: color - self.color, else black
                        width - self.line_width, else 1
        """
        if x1 is None:
            x1 = self.x_cor
        if y1 is None:
            y1 = self.y_cor
        if length is None:
            length = self.side
        if heading is None:
            heading = self.heading
        
        corners = self.get_square(x1=x1, y1=y1,
                     length=length, heading=heading,
                     color=color, width=width)
        ptxy = []
        for x,y in corners:
            ptxy.extend([x,y])
        self.args_to_kwargs(color=color, width=width, dkwargs=kwargs)
        outline = kwargs['fill']
        kwargs['fill'] = ""
        kwargs['joinstyle'] = MITER
        self.create_polygon(*ptxy, outline=outline, **kwargs) 


    def origin_rotated(self, x1, y1, rotation, side=None):
        """ Get origin changed when square rotated
        :x1: origin x
        :y1: origin y
        :rotation: rotation, in degrees
        :side: length of side default: self.side
        """
        if side is None:
            side = self.side
        theta = math.radians(rotation)
        x2 = -side/2*math.cos(theta) + side/2*math.sin(theta) + side/2 + x1
        y2 = -side/2*math.cos(theta)-side/2*math.sin(theta) + side/2 + y1
        return x2,y2
    
    def get_square(self, x1=None, y1=None,
                     length=None, heading=None,
                     color=None, width=None,
                     **kwargs):
        """ Get square turtle style array of xi,yi: i=0,1,2,3
            i=3    i=2
            
            i=0    i=1
        :x1: x origin coordinate default: self.x_cor
        :y1: y origin coordinate default: self.y_cor
        :length: length of line default: self.side (diameter)
        :color: line color default: from kwargs['fill'], else self.color
        :width: line width default: from kwargs['width'], else self.line_width
        :heading: heading in deg default: self.heading (of bounding box)
        :kwargs: additional parameters
                defaults: color - self.color, else black
                        width - self.line_width, else 1
        :returns: list of corners (xi,yi) for i=1 in range(4)
        """
        if x1 is None:
            x1 = self.x_cor
        if y1 is None:
            y1 = self.y_cor
        if length is None:
            length = self.side
        if heading is None:
            heading = self.heading
        
        x1,y1 = self.origin_rotated(x1, y1, rotation=heading, side=length)
        corners = []    
        for _ in range(4):
            SlTrace.lg(f"add_line(): x1={x1:.0f}, y1={y1:.0f}"
                       f" length={length:.0f}, heading={heading:.0f}",
                       "canvas_display")
            corners.append((x1,y1))
            x1,y1 = self.vadd(x1, y1, heading=heading, length=length)
            heading += 90
        SlTrace.lg(f"x1={x1:.0f}, y1={y1:.0f}"
                   f" length={length:.0f}, heading={heading:.0f} AFTER",
                   "canvas_display")
        return corners

        def create_image(self, x, y, image,
                         to_scale=False,
                         **kwargs):
            """link to tkinter create_image
            :x,y: x,y coordinates
            :image: image to place
            :tu_scale: scale from turtle to canvas 
                        default: False
            :kwargs: additional arguments
            """
            canvas = self.get_canvas()
            x,y = self.tur_scale(to_scale, [x, y])
            image_tag = canvas.create_image(x, y, image=image,
                                            **kwargs)
            self.add_tag(image_tag)

    def tur_scale(self, to_scale, xys):
        """ scale x,y, point pairs if to_scale
        from turtle coordinates to Canvas coordinates
        xc = 0 xt=-win_width/2           xc=win_width xt=win_width/2
        yc = 0 yt=win_height/2           yc=0 yt=win_height/2
        
        
        
        
        
                            xc=win_width/2 xt=0
                            yc=win_height/2 yt=0
                            
                            
                            
                            
                            
        xc=0 xt=-win_width/2            xc=win_height xt=win_height/2
        yc=win_height yt=-win_height/2  yc=win_height yt=-win_height/2
        
        :to_scale: do scaling if True
        :pxy: list of x,y point coordinate pairs
        :returns: return list of scaled x,y coordinate pairs
        """
        if not to_scale:
            return xys      # No scaling - return original values
        
        pair_list = []
        count = 0 
        for coord in xys:
            count += 1
            if count % 2 == 1:
               x = coord 
            else:
               pair_list.append((x, coord))
        xys2 = []
        for xt,yt in pair_list:
            xc = xt + self.canvas_width/2
            yc = -yt + self.canvas_height/2
            xys2.append(xc)
            xys2.append(yc)
        return xys2

    def update_tur_scale(self):
        """ Called to recalibrate scaling between turtle
        coordinates and canvas coordinates
        """
        canvas = self.get_canvas()
        self.canvas_width = canvas.winfo_width()
        resized = False
        if self.canvas_width < 500:
            self.canvas_width = 500
            resized = True
        self.canvas_height = canvas.winfo_height()
        if self.canvas_height < 500:
            self.canvas_height = 500
            resized = True
        if resized:
            canvas.configure(width=self.canvas_width,
                             height=self.canvas_height)
        SlTrace.lg(f"canvas: width:{self.canvas_width}"
                   f"  height:{self.canvas_height}",
                   "resize")
            
    def create_image(self, x, y, image, to_scale=True,
                     **kwargs):
        """ Link to Canvas create_image
        :x,y: turtle coordinates
        :image: photo image
        :to_scale: scale to canvas from turtle
        :kwargs: additional parameters
        """
        canvas = self.get_canvas()
        x, y = self.tur_scale(to_scale, (x,y))
        tag = canvas.create_image(x,y, image=image,
                                  anchor=SW, **kwargs)
        SlTrace.lg(f"create_image: x={x:.0f}, y={y:.0f} tag={tag}",
                   "create_image")
        self.add_tag(tag)
        
    def create_line(self, x1, y1, x2, y2, **kwargs):
        """ link to tkinter create_line
        """
        canvas = self.get_canvas()
        SlTrace.lg(f"create_line: x1={x1:.0f}, y1={y1:.0f}"
                   f", x2={x2:.0f} y2={y2:.0f} tag=?", "canvas_display")
        x1, y1, x2, y2 = self.tur_scale(True, (x1, y1, x2, y2))
        tag = canvas.create_line(x1,y1,x2,y2, **kwargs)
        SlTrace.lg(f"create_line: tag: {tag} {x1, y1, x2, y2}", "canvas_display")
        self.add_tag(tag)
        SlTrace.lg(f"create_line: x1={x1:.0f}, y1={y1:.0f}"
                   f", x2={x2:.0f} y2={y2:.0f} tag={tag}", "canvas_display")
        
    def create_oval(self, x1, y1, x2, y2, **kwargs):
        """ link to tkinter create_oval
        """
        canvas = self.get_canvas()
        x1, y1, x2, y2 = self.tur_scale(True, (x1, y1, x2, y2))
        tag = canvas.create_oval(x1,y1,x2,y2, **kwargs)
        self.add_tag(tag)

    def create_polygon(self, *ptxy, **kwargs):
        """ link to tkinter create_line
        """
        canvas = self.get_canvas()
        ptxy = self.tur_scale(True, ptxy)
        tag = canvas.create_polygon(*ptxy, **kwargs)
        self.add_tag(tag)
        ptxy_str = ""
        for pt in ptxy:
            if ptxy_str != "":
                ptxy_str += ", "
            ptxy_str += f"{pt:.0f}"
        SlTrace.lg(f"create_polygon: ptxy: {ptxy_str} tag={tag}",
                   "display_canvas")
                
    def get_canvas(self):
        """ Get our working canvas
        """
        return self.drawer.get_canvas()

    def get_copy_move(self):
        return self.copy_move
    
    def add_tag(self, tag):
        SlTrace.lg(f"{self.draw_type}.add_tag({tag})", "tags")
        if self.drawn is None:
            self.drawn = DrawnArtifacts()
        self.drawn.tags.append(tag)

    def delete_tag(self,tag):
        SlTrace.lg(f"{self.draw_type}.delete_tag({tag})", "tags")
        canvas = self.get_canvas()
        canvas.delete(tag)

    def add_image_ref(self, image):
        if self.drawn is None:
            self.drawn = DrawnArtifacts()
        self.drawn.images.append(image)

    def delete_image(self,image):
        SlTrace.lg("deleate_image", "delete_image")
        del(image)
        
        
    def draw(self):
        """ Draw/Redraw figure
        Set current marker attributes
        first removing any preexisting artifacts
        """
        #self.undraw()
        self.drawer.set_side(self.side)
        self.drawer.set_width(self.line_width)
        self.drawer.set_heading(self.heading)
        self.drawn = DrawnArtifacts() 
        
    def undraw(self):
        """ Remove drawn artifacts and resources
        """
        if SlTrace.trace("tags"):
            if self.drawn is None:
                tags_str = "None"
            else:
                tags_str = f"{self.drawn.tags}"
            SlTrace.lg(f"{self.draw_type}.undraw: tags: {tags_str}")
        if self.drawn is not None:
            for tag in self.drawn.tags:
                self.delete_tag(tag)
            self.drawn.tags = []
            for image in self.drawn.images:
                self.delete_image(image)
            self.drawn.images = []
            
