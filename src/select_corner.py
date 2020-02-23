# select_corner.py        

from math import sqrt

from select_trace import SlTrace
from select_error import SelectError
from select_loc import SelectLoc
from select_part import SelectPart

class SelectCorner(SelectPart):
    corner_width_display = 8    # Default display size of corner in pixels
    corner_width_select = 8    # Default select size of corner in pixels
    corner_width_standoff = 10    # Default standoff size of corner in pixels
    corner_fill = "red" # Default corner color
    corner_fill_highlight = "pink"      # Default corner highlight color


    '''Use default copy.deepcopy()
    def __deepcopy__(self, memo=None):
        """ provide deep copy as a custimized "constructor",
        reducing recusion
        """
        res = self.copy()        
        return res
    '''

    
    def __init__(self, sel_area, **kwargs):
        super().__init__(sel_area, "corner", **kwargs)
                    
            
    def display(self):
        """ Display corner on inside upper left corner
        """
        SlTrace.lg("%s: %s at %s" % (self.part_type, self, str(self.loc)), "display")
        
        if not self.sel_area.display_game:
            return

        self.display_clear()
        if self.is_highlighted():
            """ Highlight given corner
            :hand: Corner handle
            :Returns: object tag for deletion
            """
            c1x,c1y,c3x,c3y = self.get_rect(enlarge=True)
            if self.display_shape == "circle":
                self.highlight_tag = self.sel_area.canvas.create_oval(
                                c1x, c1y, c3x, c3y,
                                fill=SelectPart.corner_fill_highlight)
            else:
                self.highlight_tag = self.sel_area.canvas.create_rectangle(
                                c1x, c1y, c3x, c3y,
                                fill=SelectPart.corner_fill_highlight)
        else:
            loc = self.loc 
            SlTrace.lg("corner: %s" % str(loc), "display")
            c1x,c1y,c3x,c3y = self.get_rect()
            if self.display_size is not None:
                cwidth = self.display_size
                cheight = cwidth
                cx = (c3x-c1x)/2 + c1x 
                cy = (c3y-c1y)/2 + c1y
                c1x = cx - cwidth/2
                c3x = cx + cwidth/2
                c1y = cy - cheight/2
                c3y = cy + cheight/2
            if (self.display_shape is not None
                 or self.display_size is not None):
                if self.display_shape == "circle":
                    tags = []
                    tag = self.sel_area.canvas.create_oval(
                        c1x, c1y, c3x, c3y, fill=self.color)
                    tags.append(tag)
                    cc_x, cc_y, cc_sx, cc_sy = self.get_center_size()
                    SlTrace.lg("cc_x,y=%d,%d  cc_sx,y=%d,%d" % (cc_x,cc_y, cc_sx,cc_sy), "part_info")
                    tag = self.sel_area.canvas.create_line(cc_x,cc_y, cc_x,cc_y-cc_sy,
                                                        cc_x,cc_y, cc_x-cc_sx, cc_y,
                                                        cc_x,cc_y, cc_x+cc_sx, cc_y,
                                                        cc_x,cc_y, cc_x, cc_y+cc_sy,
                                                        cc_x,cc_y, cc_x, cc_y-cc_sy,
                                                          )
                    tags.append(tag)
                    self.display_tag = tags
                else:
                    tags = []
                    tag = self.sel_area.canvas.create_rectangle(
                                c1x, c1y, c3x, c3y, fill=self.color)
                    tags.append(tag)
                    cc_x, cc_y, cc_sx, cc_sy = self.get_center_size()
                    tag = self.sel_area.canvas.create_line(cc_x,cc_y, cc_x,cc_y-cc_sy,
                                                        cc_x,cc_y, cc_x-cc_sx, cc_y,
                                                        cc_x,cc_y, cc_x+cc_sx, cc_y,
                                                        cc_x,cc_y, cc_x, cc_y+cc_sy,
                                                        cc_x,cc_y, cc_x, cc_y-cc_sy,
                                                          )
                tags.append(tag)
                self.display_tag = tags
            else:
                self.display_tag = self.sel_area.canvas.create_rectangle(
                        c1x, c1y, c3x, c3y, fill=self.color)


    def distance(self, cx, cy):
        """ Distance between corner and coordinates cx,cy
        :cx: x coordinate
        :cy: y coordinate
        """
        co_x,co_y,co_xsize,co_ysize = self.get_center_size()
        return sqrt((co_x-cx)**2+(co_y-cy)**2)


    def get_nodes(self, indexes=None):
        """ Find nodes/points of part
        return pairs (index, node)
        """
        return [(0,self.loc.coord)]


    def set_node(self, index, node):
        """ Set node to new value
        """
        if index != 0:
            raise SelectError("set_node %s non-zero index %d"
                              % (self, index))
        self.loc.coord = node


    def edge_dxy(self):
        """ Get "edge direction" as x-increment, y-increment pair
        """
        return 0,0                  # No change
        
                     

    
    def get_rect(self, sz_type=None, enlarge=False):
        """ Get rectangle containing edge handle
        Use connected corners
        Coordinates returned are ordered ulx, uly, lrx,lry so ulx<=lrx, uly<=lry
        We leave room for the corners at each end
        :edge - selected edge
        :enlarge - True - enlarge rectangle
        """
        wlen = self.get_edge_width(sz_type=sz_type, enlarge=enlarge)
        
        c1x = self.loc.coord[0]
        c1y = self.loc.coord[1]
        c3x = c1x
        c3y = c1y
        if c1x >= wlen/2:     # Yes - widen the orthogonal dimension
            c1x -= wlen/2
        c3x += wlen
        if c1y >= wlen:     # Yes - widen the orthogonal dimension
            c1y -= wlen/2
        c3y += wlen
        if enlarge:
            wenlarge = self.edge_width_enlarge
            c1x -= wenlarge
            c1y -= wenlarge
            c3x += wenlarge
            c3y += wenlarge
                
        return c1x,c1y,c3x,c3y
    
    def highlight(self):
        """ Highlight and display
        """
        self.highlight_set()
        self.display()


    
    def loc_key(self):
        """ Return location of part as a key
        """
        key = self.loc.coord
        return (key)
