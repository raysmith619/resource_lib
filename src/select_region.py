# select_region.py        

import copy

from select_trace import SlTrace
from select_error import SelectError
from select_loc import SelectLoc
from select_part import SelectPart
from select_edge import SelectEdge
from select_part import color_to_fill
from select_centered_text import CenteredText        
###from select_area import SelectArea
        
class SelectRegion(SelectPart):
    fill = "clear"                  # Default region color
    fill_highlight = "lightgray"   # Default region highlight color
    partno = 0                       # Incremented each new region

    @classmethod
    def reset(cls):
        cls.partno = 0

    '''Use default copy.deepcopy()
    def __deepcopy__(self, memo=None):
        """ provide deep copy as a custimized "constructor",
        reducing recusion
        """
        res = self.copy()        
        return res
    '''
        
            
    def __init__(self, sel_area, region_outline="", region_width=0, **kwargs):
        """ Setup region
        :sel_area: reference to basis, Needed to display
        """
        self.region_outline = region_outline
        self.region_width = region_width
        super().__init__(sel_area, "region", **kwargs)
        SelectRegion.partno += 1
        self.partno = SelectRegion.partno
        c1x,c1y,c3x,c3y = self.get_rect()
        if self.color is None:
            self.color= "light gray"
        
        if not self.sel_area.display_game:
            return
        
        self.color_bg_tag = self.sel_area.canvas.create_rectangle(
                                    c1x, c1y, c3x, c3y,
                                    width=self.region_width,
                                    fill=self.get_color())
        self.add_display_tags(self.color_bg_tag)

    '''
    def add_rect(self, rect, color=None):
        """ Add rectangle 
        """                
        rec_ps = [None] * 4
        ulX, ulY = rect[0][0], rect[0][1]
        lrX, lrY = rect[1][0], rect[1][1]
        rec_ps[0] = (ulX, ulY)
        rec_ps[1] = (lrX, ulY) 
        rec_ps[2] = (lrX, lrY)
        rec_ps[3] = (ulX, lrY)
        for pi1 in range(0, 3+1):
            pi2 = pi1 + 1
            if pi2 >= len(rec_ps):
                pi2 = 0          # Ends at first
            pt1 = rec_ps[pi1]
            pt2 = rec_ps[pi2]
            self.add_edge(pt1, pt2)
    '''
        

    def add_edge(self, pt1, pt2):
        """ Add edge, creating edge if new to area
        Also adds corners, creating corners if new to area
        Add self to adjacent to added edges
        """
        edge = self.get_edge(pt1, pt2)  # get, create if new
        self.add_connects(edge)
        corners = edge.get_corners()
        self.add_connects(corners)
        edge.add_adjacent(self)         # Associate with all connecteds
        for corner in corners:
            corner.add_adjacent(self)

        
    def add_corners(self, corners):
        """ Add corners to region
        :corners: one or more corner locations
        """
        if not isinstance(corners, list):
            corners = [corners]     # Treat as an array of one
        for corner in corners:
            self.add_part(corner)
                    
    def has_corner(self, point):
        """ Check if corner already present in region
        """
        for corner in self.parts:
            if not corner.is_corner():
                continue
            loc = corner.loc
            pt = loc.coord
            if pt[0] == point[0] and pt[1] == point[1]:
                return True     # Corner already present
        return False            # No such corner present
        

    def get_nodes(self, indexes=None):
        """ Find nodes/points of part
        return pairs (index, node)
        """
        nodes = []
        if indexes is None:
            nodes = [(0,self.loc.coord[0]), (1,self.loc.coord[1])]
        else:
            if not isinstance(indexes, list):
                indexes = [indexes]     # Make a list of one
            for index in indexes:
                nodes.append((index,self.loc.coord[index]))
        return nodes


    def set_node(self, index, node):
        """ Set node to new value
        """
        self.loc.coord[index] = node


    def current_edge(self, pt1, pt2):
        """ Return edge with these specifications, None if none found
        """
        return self.sel_area.current_edge(pt1, pt2)

    
    def display(self):
        """ Display region as a rectangle
        We leave room for the corners at each end
        Highlight if appropriate
        :region: Corner handle
        :Returns: object tag for deletion
        """
        
        if not self.sel_area.display_game:
            return

        ###if self.invisible and not self.centered_text:   # hack to show
        ###    return
        self.display_clear()
        
        SlTrace.lg("%s: %s at %s" % (self.part_type, self, str(self.loc)), "display")
        c1x,c1y,c3x,c3y = self.get_rect()
        if self.is_turned_on():
            fill = self.on_color
        else:
            fill = self.off_color
        if fill is None:
            fill = self.color
        if fill is None:
            fill = 'PeachPuff3'
        SlTrace.lg("region fill=%s" % fill, "get_color")
        ###self.display_clear()
        if SlTrace.trace("region_rect"):
            SlTrace.lg("region: %d c1x=%d c1y=%d c3x=%d c3y=%d"
                       % (self.partno, c1x, c1y, c3x, c3y))
            if c3y < c1y:
                SlTrace.lg ("region: %d c3y(%d) < c1y(%d)" % (self.partno, c3y, c1y))
                SlTrace.lg("Strange?")
        if self.is_highlighted():
            self.highlight_on_stripe_width = 4
            self.highlight_off_stripe_width = 2
            """ Horozontal strips of on width separated by
            off width """
            hfill = self.get_highlight_fill()
            coords = []
            stx_beg = c1x + self.highlight_on_stripe_width
            stx_end = c3x - self.highlight_on_stripe_width
            sty_beg = c1y + self.highlight_on_stripe_width
            sty_end = sty_beg
            coord_tr = stx_end, sty_end 
            coord_lr = [stx_beg, sty_beg, stx_end, sty_end]
            while sty_end < c3y:
                coord_lr = [stx_beg, sty_beg, stx_end, sty_end]
                coords.extend(coord_lr)
                coord_rl = [stx_end, sty_end, stx_beg, sty_beg]     # Go back before down
                coords.extend(coord_rl)
                sty_beg += (self.highlight_on_stripe_width    
                            + self.highlight_off_stripe_width)
                sty_end = sty_beg
            coords.extend(coord_lr)
            coords.extend(coord_tr)
            if hfill is None:
                hfill = 'light goldenrod yellow'
            try:
                tag = self.sel_area.canvas.create_line(
                                    coords,
                                    width=self.highlight_on_stripe_width,
                                    fill=hfill)
                self.add_display_tags(tag)
                self.highlight_tag = tag
            except:
                SlTrace.lg("Possible bad hfill: %s for region %d" % (hfill, self.partno))
        else:
            if fill is None:
                fill = 'PeachPuff3'
            try:
                tag = self.sel_area.canvas.create_rectangle(
                                    c1x, c1y, c3x, c3y,
                                    width=self.region_width,
                                    fill=fill)
                self.add_display_tags(tag)
                self.display_tag = tag
            except:
                SlTrace.lg("Possible bad fill: %s for region %d" % (fill, self.partno))
        
        if self.centered_text:
            self.do_centered_text()
                
        if SlTrace.trace("regno"):
            cx = (c1x+c3x)/2
            cy = (c1y+c3y)/2
            disp_str = "%d" % self.partno
            self.partno_tag = self.sel_area.display_text((cx, cy), text=disp_str)
            SlTrace.lg("region: %d  %s row=%d, col=%d (%d,%d) %s"
                       % (self.partno, self.part_type,
                          self.row, self.col, cx,cy, disp_str))
            self.add_display_tags(self.partno_tag)

    def edge_dxy(self):
        """ Get "edge direction" as x-increment, y-increment pair
        """
        loc = self.loc
        rect = loc.coord
        p1 = rect[0]
        p2 = rect[1]
        edx = p2[0] - p1[0]             # Find edge direction
        edy = p2[1] - p1[1]
        return edx, edy

    def get_color(self):
        """ Return color for tkinter fill, etc.
        """
        color = self.color
        if type(color) is int:
            color = "#%06X" % color
        return color
    

    def get_edge(self, pt1, pt2):
        """ Get edge, creating edge if new to area
        Also adds corners, creating corners if new to area
        """
        edge = self.current_edge(pt1, pt2)
        if edge is None:
            edge = SelectEdge(rect=[pt1, pt2])             
        return edge
    
    
    def get_rect(self, sz_type=None, enlarge=False):
        """ Get upper left x,y and lower right x,y region
        :sz_type: type of rect 
        :enlarge: true - enlarge
        """
        if sz_type is None:
            sz_type=SelectPart.SZ_DISPLAY
        if self.do_corners:
            corners = []
            for part in self.connecteds:
                if part.is_corner():
                    corners.append(part)
            if len(corners) < 4:
                SlTrace.lg("Region with %d corners %s" % (len(corners), self), "region_few_corners")
                co = self.loc.coord
                c1x = co[0][0]
                c1y = co[0][1]
                c3x = co[1][0]
                c3y = co[1][1]
            else:
                c1x = corners[0].loc.coord[0]
                c1y = corners[0].loc.coord[1]
                c3x = corners[2].loc.coord[0]
                c3y = corners[2].loc.coord[1]
        else:
            co = self.loc.coord
            c1x = co[0][0]
            c1y = co[0][1]
            c3x = co[1][0]
            c3y = co[1][1]            
        c1x,c1y,c3x,c3y = SelectLoc.order_ul_lr(c1x,c1y,c3x,c3y)
        wlen = self.get_edge_width(sz_type)
        c1x += wlen
        c1y += wlen
        c3x -= wlen
        c3y -= wlen
        if enlarge:
            c1x -= self.edge_width_enlarge
            c1y -= self.edge_width_enlarge 
            c3x += self.edge_width_enlarge
            c3y += self.edge_width_enlarge
        if SlTrace.trace("region_rect"):
            SlTrace.lg("region.get_rect: %d c1x=%d c1y=%d c3x=%d c3y=%d"
                       % (self.partno, c1x, c1y, c3x, c3y))
            if c3y < c1y:
                SlTrace.lg ("region: %d c3y(%d) < c1y(%d)" % (self.partno, c3y, c1y))
                SlTrace.lg("Strange?")
                for connected in self.connecteds:
                    SlTrace.lg("%d: %s loc_key: %s"
                                % (connected.part_id, connected.part_type, connected.loc_key()))
            
            
            
        return c1x,c1y,c3x,c3y

    

    def highlight(self):
        """ Highlight and display
        """
        self.highlight_set()
        self.display()


    def is_complete(self, added=None):
        """ Check if this is complete
            == all edges are turned on
        :added: one or list of parts to add for completion
        """
        if added is not None:
            if not isinstance(added, list):
                added = [added]
            for conn in self.get_connecteds():
                if not conn.is_edge():
                    continue
                if conn.is_turned_on():
                    continue
                if conn in added:
                    continue
                return False
                
        else:        
            for conn in self.get_connecteds():
                if conn.is_edge() and not conn.is_turned_on():
                    return False
        if SlTrace.trace("complete_test"):
            SlTrace.lg("%s is complete" % self)
            self.display_info(tag="  complete")
            pass    
        return True         # No non-turned on


    def would_complete(self, edge):
        """ Check if this edge, if turned on, would complete this region
            == all edges are turned on
        """
        for conn in self.get_connecteds():
            if conn.is_edge():
                if not conn.is_turned_on() and not conn.same_part(edge):
                    return False
        if SlTrace.trace("complete_test"):
            SlTrace.lg("%s is complete" % self)
            self.display_info(tag="  complete")
            pass    
        return True         # No non-turned on
    
    
    def loc_key(self):
        """ Return location of part as a key
        """
        key = tuple(self.loc.coord)
        return (key)
