# select_edge.py

import copy
        
from select_trace import SlTrace
from active_check import ActiveCheck
from select_error import SelectError
from select_loc import SelectLoc
from select_part import SelectPart
from select_blinker_state import BlinkerMultiState



class SelectEdge(SelectPart):
    width_display = 5      # Default edge display line width in pixels
    width_select = 3      # Default edge select line width in pixels
    width_standoff = 5     # Default edge buffer for adjacent parts
    width_enlarge = 2      # Enlarge number, added to width
    fill = "blue"   # Default edge color
    fill_highlight = "purple"   # Default edge highlight color


    '''Use default copy.deepcopy()
    def __deepcopy__(self, memo=None):
        """ provide deep copy as a custimized "constructor",
        reducing recusion
        """
        res = self.copy()        
        return res
    '''

    ''' Use SelectPart.copy
    def copy(self):
        """ Return copy of self, independent to allow independent modifications
        """
        self.part_check(prefix="copy before")
        new_copy = copy.copy(self)
        self.part_check(new_copy, prefix="copy before set_copy")
        new_copy.set_copy(self)
        self.part_check(new_copy)
        return new_copy
    '''
    
    def __init__(self, sel_area, **kwargs):
        """ Setup region
        :sel_area: reference to basis, Needed to display
        """
        super().__init__(sel_area, "edge", **kwargs)


    
    def display(self):
        """ Display edge as a rectangle
        We leave room for the corners at each end
        Highlight if appropriate
        """
        
        if not self.sel_area.display_game:
            return

        if ActiveCheck.not_active():
            return
        
        self.part_check(prefix="display")
        if SlTrace.trace("dbg"):
            SlTrace.lg("dbg")
        self.display_clear()
            
        '''
        if (self.invisible and not self.highlighted and not self.turned_on
                and not self.is_selected()):
            self.display_clear()
            return
        '''
        SlTrace.lg("%s: %s at %s" % (self.part_type, self, str(self.loc)), "display")
        if self.highlighted:
            self.set_view_highlighted()
        elif self.is_selected():
            self.set_view_selected()
        else:           # Not highlighted
            self.set_view_default()
        if SlTrace.trace("show_id"):
            dir_x, dir_y = self.edge_dxy()
            chr_w = 5
            chr_h = chr_w*2
            if dir_x != 0:      # sideways
                offset_x = -len(str(self.part_id))*chr_w/2 + chr_w
                offset_y = chr_h
            if dir_y != 0:      # up/down
                offset_x = len(str(self.part_id))*chr_w
                offset_y = 0    
        
            c1x,c1y,c3x,c3y = self.get_rect()
            cx = (c1x+c3x)/2 + offset_x
            cy = (c1y+c3y)/2 + offset_y
            self.name_tag = self.display_text((cx, cy), text=str(self.part_id))
            self.add_display_tags(self.name_tag)
        if self.move_no is not None and SlTrace.trace("show_move"):
            dir_x, dir_y = self.edge_dxy()
            chr_w = 5
            chr_h = chr_w*2
            if dir_x != 0:      # sideways
                offset_x = -len(str(self.move_no))*chr_w/2 + chr_w
                offset_y = chr_h
            if dir_y != 0:      # up/down
                offset_x = len(str(self.move_no))*chr_w + 2
                offset_y = 0    
        
            cx = (c1x+c3x)/2 + offset_x
            cy = (c1y+c3y)/2 + offset_y
            self.move_no_tag = self.display_text((cx, cy), text=str(self.move_no))
            self.add_display_tags(self.move_no_tag)
            SlTrace.lg("    part showing move_no %s" % self, "show_move_print")
        self.sel_area.mw.update_idletasks()

    def set_view_highlighted(self):
        """ Set highlighted view
        """
        if SlTrace.trace("edge_highlighted"):
            SlTrace.lg("selected %s" % self, "edge_highlighted")
        if self.turned_on:
            if self.on_highlighting:
                if self.player is not None:     # Check if indicators on
                    indicator_tags = self.display_indicator(player=self.player)
                    blinker = self.blink(indicator_tags)
                    self.add_display_objects(blinker)

            else:
                c1x,c1y,c3x,c3y = self.get_rect(enlarge=True)
                highlight_tag = self.sel_area.canvas.create_rectangle(
                                    c1x, c1y, c3x, c3y,
                                    fill=SelectPart.edge_fill_highlight, tag="highlights")
                self.add_display_tags(highlight_tag)
                blinker = self.blink(self.highlight_tag, off_fill="red")
                self.add_display_objects(blinker)
        else:
            if self.off_highlighting:
                indicator_tags = self.display_indicator(fills=["purple", "darkgray", "orange"])
                self.add_display_tags(indicator_tags)
                blinker = self.blinker_set(self.blink(indicator_tags))
                self.add_display_objects(blinker)

    def set_view_selected(self):
        """ Set view as selected
        """
        if SlTrace.trace("edge_selected"):
            SlTrace.lg("selected %s" % self, "edge_selected")
        if self.turned_on:
            if self.on_highlighting:
                if self.player is not None:     # Check if indicators on
                    indicator_tags = self.display_indicator(player=self.player, ditag="ditag:turned_on==%s" % self.turned_on)
                    blinker = self.blink(indicator_tags)
                    self.add_display_objects(blinker)

            else:
                c1x,c1y,c3x,c3y = self.get_rect(enlarge=True)
                highlight_tag = self.sel_area.canvas.create_rectangle(
                                    c1x, c1y, c3x, c3y,
                                    fill=SelectPart.edge_fill_highlight, tag="highlights")
                self.add_display_tags(highlight_tag)
                blinker = self.blink(self.highlight_tag, off_fill="red")
                self.add_display_objects(blinker)
        else:
            if self.off_highlighting:
                indicator_tags = self.display_indicator(fills=["purple", "darkgray", "orange"])
                self.add_display_tags(indicator_tags)
                blinker = self.blink(indicator_tags)
                self.add_display_objects(blinker)

    def set_view_default(self):
        """ Set default (non highlighted/selected) view of edge
        """
        if SlTrace.trace("edge_unselected"):
                SlTrace.lg("unselected %s" % self, "edge_unselected")
        if self.turned_on:
            if self.on_highlighting:
                if self.player is not None:     # Check if indicators on
                    indicator_tags = self.display_indicator(player=self.player)
                    self.add_display_tags(indicator_tags)
        
    def blink(self, tagtags,
                   on_time=None,
                   off_time=None,
                   off_fill="white"):
        """ Set tag blinking
        :tagtags: - single tag for on/off blinking
                    or
                    list of tag_lists for "ripple" blinking one after the next
        :on_time:  on time in seconds
        :off_time: off time in seconds default: on_time
        :off_fill: fill for off time
        :returns: blink object, caller is responsible for resource maintenance
        """
        if isinstance(tagtags, list):
            return self.blink_multi(tagtags, on_time=on_time)
        else:
            raise SelectError("Only supporting multi tag blink")

    def blink_multi(self, tagtags, on_time=.25):
        """ Blink list of tag lists rotating every on_time
        :on_time: time for each display before rotating fill colors
        :returns: blinker object
        """
        '''
        if self.blinker:
            SlTrace.lg("Replacing(stop) previous blinker")
            self.blinker.stop()
            self.blinker = None
        '''
        blinker = BlinkerMultiState(part=self, tagtags=tagtags,
                                        on_time=on_time)
        blinker.blink_on_first()      # Just to prime the delay
        return blinker

        

    def display_indicator(self, player=None, fills=None, ditag=None):
        """ Display edge with player indicator
        :player: player/owner
        fills[0], fills[1],...
        :fills: fill colors
                default: icolor, icolor2, icolor2
                If icolor2 None - white
                If icolor None - SelectPart.edge_fill_highlight
                If len(fills) == 2 fills[2] == fills[1]
        :ditag:    debugging tag default: None
        :returns: tags for possible blinking -  tags are stored here
                                                via add_display_tags
        """
        ###if self.blinker:
        ###    SlTrace.lg(f"display_indicator - blinker already on player:{player} {self}")
        display_multi_tags = []
        if player is None:
            player = self.player
        if player is not None:
            fills = [player.icolor, player.icolor2]
        if fills is None:
            fills = [self.icolor]
        if fills[0] is None:
            fills[0] = SelectPart.edge_fill_highlight
        if len(fills) == 1:
            fills.append(None)
        if fills[1] is None:
            fills[1] = "white"
        if len(fills) == 2:
            fills.append(fills[1])
            
        on_length = 10
        off_length = 10
        c1x, c1y, c3x, c3y = self.get_rect()
        multi_tags = [[], [], []]                 # Multiple sets for ripple
        if self.sub_type() == "h":
            lc1y = c1y
            lc3y = c3y
            lc1x = c1x
            while lc1x < c3x:
                lc3x = lc1x + on_length
                if lc3x > c3x:
                    lc3x = c3x      # cut to end
                tag = self.sel_area.canvas.create_rectangle(
                            lc1x, lc1y, lc3x, lc3y,
                            fill=fills[0], width=0, outline='', tags=("blinker", self.part_tag(), ditag))
                multi_tags[0].append(tag)
                
                lc1x += on_length
                if lc1x >= c3x:
                    break
                lc3x = lc1x + off_length
                if lc3x > c3x:
                    lc3x = c3x
                tag = self.sel_area.canvas.create_rectangle(
                            lc1x, lc1y, lc3x, lc3y,
                            fill=fills[1], width=0, outline='', tags=("blinker", self.part_tag(), ditag))
                multi_tags[1].append(tag)
                
                lc1x = lc3x
                if lc1x >= c3x:
                    break
                lc3x = lc1x + off_length
                if lc3x > c3x:
                    lc3x = c3x
                tag = self.sel_area.canvas.create_rectangle(
                            lc1x, lc1y, lc3x, lc3y,
                            fill=fills[2], width=0, outline='', tags=("blinker", self.part_tag(), ditag))
                multi_tags[2].append(tag)
                
                lc1x = lc3x+1
            self.add_display_tags(multi_tags)    
        else: # vertical edge
            lc1x = c1x
            lc3x = c3x
            lc1y = c1y
            while lc1y < c3y:
                lc3y = lc1y + on_length
                if lc3y > c3y:
                    lc3y = c3y      # cut to end
                tag = self.sel_area.canvas.create_rectangle(
                            lc1x, lc1y, lc3x, lc3y,
                            fill=fills[0], width=0, outline='', tags=("blinker", self.part_tag(), ditag))
                multi_tags[0].append(tag)
                
                lc1y += on_length
                if lc1y >= c3y:
                    break
                lc3y = lc1y + off_length
                if lc3y > c3y:
                    lc3y = c3y
                tag = self.sel_area.canvas.create_rectangle(
                            lc1x, lc1y, lc3x, lc3y,
                            fill=fills[1], width=0, outline='', tags=("blinker", self.part_tag(), ditag))
                multi_tags[1].append(tag)
                
                lc1y = lc3y
                if lc1y >= c3y:
                    break
                lc3y = lc1y + off_length
                if lc3y > c3y:
                    lc3y = c3y
                tag = self.sel_area.canvas.create_rectangle(
                            lc1x, lc1y, lc3x, lc3y,
                            fill=fills[2], width=0, outline='', tag=("blinker", self.part_tag(), ditag))
                multi_tags[2].append(tag)
                
                lc1y = lc3y+1
            self.add_display_tags(multi_tags)    
        return multi_tags
    

    def is_left(self, edge):
        """ Check if we are left of edge
        """
        c1x,_,c3x,_ = self.get_rect()
        edge_c1x,_,edge_c3x,_ = edge.get_rect()
        if c1x <= edge_c1x and c3x < edge_c3x:
            return True
        
        return False


    def is_right(self, edge):
        """ Check if we are left of edge
        """
        c1x,_,c3x,_ = self.get_rect()
        edge_c1x,_,edge_c3x,_ = edge.get_rect()
        if c1x > edge_c1x and c3x > edge_c3x:
            return True
        
        return False


    def is_above(self, edge):
        """ Check if we are above of edge/part
        """
        _,c1y,_,c3y = self.get_rect()
        _,edge_c1y,_,edge_c3y = edge.get_rect()
        if c1y < edge_c1y and c3y < edge_c3y:
            return True
        
        return False


    def is_below(self, edge):
        """ Check if we are above of edge
        """
        _,c1y,_,c3y = self.get_rect()
        _,edge_c1y,_,edge_c3y = edge.get_rect()
        if c1y > edge_c1y and c3y > edge_c3y:
            return True
        
        return False


    def sub_type(self):
        """ sub type v/h vertical/horizontal
        """
        edx,edy = self.edge_dxy()
        if edx != 0 and edy == 0:
            return "h"
        
        if edy != 0 and edx == 0:
            return "v"
        
        return ""
    
    
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
                     

    
    def get_rect(self, sz_type=None, enlarge=False):
        """ Get rectangle containing edge
        Use connected corners
        Coordinates returned are ordered ulx, uly, lrx,lry so ulx<=lrx, uly<=lry
        We leave room for the corners at each end
        :edge - selected edge
        :enlarge - True - enlarge rectangle
        """
        if sz_type is None:
            sz_type=SelectPart.SZ_DISPLAY
        c1x = self.loc.coord[0][0]
        c1y = self.loc.coord[0][1]
        c3x = self.loc.coord[1][0]
        c3y = self.loc.coord[1][1]
        c1x,c1y,c3x,c3y = SelectLoc.order_ul_lr(c1x,c1y,c3x,c3y)
        """ Leave room at each end for corner """
        corner1 = self.get_corner(c1x, c1y)
        if corner1 is not None:
            _, _, corner1_xsize, corner1_ysize = corner1.get_center_size()
            corner3 = self.get_corner(c3x, c3y)
            _, _, corner3_xsize, corner3_ysize = corner3.get_center_size()
        else:
            corner1_xsize = corner1_ysize = 0
            corner3_xsize = corner3_ysize = 0
        dir_x, dir_y = self.edge_dxy()
        wlen = self.get_edge_width(sz_type)/2
        if dir_y != 0:          # Check if in y direction
            if c1x >= wlen:     # Yes - widen the orthogonal dimension
                c1x -= wlen
            c3x += wlen
            c1y += corner1_ysize         # Yes - shorten ends to avoid corner
            c3y -= corner3_ysize
        if dir_x != 0:          # Check if in x direction
            if c1y >= wlen:     # Yes - widen the orthogonal dimension
                c1y -= wlen
            c3y += wlen
            c1x += corner1_xsize         # Yes - shorten ends to avoid corner
            c3x -= corner3_xsize
        if enlarge:
            wenlarge = SelectPart.edge_width_enlarge
            if dir_y != 0:
                c1x -= wenlarge
                c3x += wenlarge
            if dir_x != 0:
                c1y -= wenlarge 
                c3y += wenlarge
                
        return c1x,c1y,c3x,c3y


    def get_corner(self,cx, cy):
        """ Get corner closest to c1x,c1y
        :cx: end of rectangle
        :cy:  end of rectangle
        """
        min_corner = None
        min_distance = None
        corners = self.get_corners()
        if not corners:
            SlTrace.lg("No corners", "no_corners")
        for corner in corners:
            if min_corner is None or corner.distance(cx,cy) < min_distance:
                min_corner = corner
                min_distance = corner.distance(cx,cy) 
        return min_corner
    
        
    def highlight(self, display=True):
        """ Highlight and display
        """
        self.highlight_set(display=True)    #Just to remind ourselves that we do the display


    
    def loc_key(self):
        """ Return location of part as a key
        """
        key = tuple(self.loc.coord)
        return (key)
