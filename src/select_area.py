"""
Created on Aug 23, 2018

@author: raysm
"""
from datetime import datetime
from cmath import rect
import copy

from select_trace import SlTrace
from select_fun import *

import tkinter as tk
    
from select_error import SelectError
from select_part import SelectPart
from select_corner import SelectCorner
from select_edge import SelectEdge
from select_region import SelectRegion
from select_mover import SelectMover, SelectMoveDisplay
from select_stroke import SelectStroke                    
from _ast import Or
                     
class SelectArea(object):
    """
    Selected region of image
    Candidate for selection.
    """

    def __deepcopy__(self, memo=None):
        """ provide deep copy by just passing shallow copy of self,
        avoiding tkparts inside sel_area
        """
        SlTrace.lg("SelectArea __deepcopy__", "copy")
        return self
   
    def __init__(self, canvas, mw=None,
                board=None,
                display_game=True,
                image=None, rects=None,
                region_width=0,
                show_moved=False, show_id=False,
                stroke_checking=False,
                highlight_limit=None,
                highlighting=True,
                check_mod=None,
                down_click_call=None,
                tbmove=.1,
                max_select = 1):
        """
        Rectangular selected/ing region,
        :canvas: Canvas containing the region
        :mw: Master/Parent widget, if one
        :board: playing board (SelectDots)
        :display_game: avoid display if False to minimize delays
                    default: True
        :highlighting: True highlight parts if mouse over
                        default: True
        :image: displayed in frame    Not necessary/used
        :rects: single, or list of Rectangles (upper left x,y), (lower right x,y)
                each being a region
                Default is no rectangles
        :highlight_limit: Limt higlighting to time (seconds)
                Default: no time limit
        :region_width: region boundary width
        :stroke_checking:  True-> check for stroking mouse/hand Default: False
        :check_mod: called, if present, before and after part is modified
        :down_click_call: processes down clicks if present'
                default: no remote processing
        :tbmove: minimum time (seconds) between move recognition
        :max_select: maximum number of simultaneous selections
                    allowed
                    default = 1
        """
        self.board = board
        self.display_game = display_game
        self.parts = []          # Parts of scene, corners, edges, regions
        self.parts_by_id = {}    # By part id
        self.parts_by_loc = {}      # By type, location: 
        """ hash/dictionary of parts by type, location
            type: edge, corner, region
            loc: (pt), (x,y)
                 (pt1 (upper right), pt2 (lower right)
        """
        self.image = image
        self.region_width = region_width
        if mw is None:
            mw = tk.Tk()
            mw.withdraw()       # Hide main window
        if not hasattr(mw, "update_idletasks"):
            SlTrace.lg("mw %s" % type(mw))
            raise SelectError("mw has no update_idletasks")
        
        self.mw = mw
        ###self.mw.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.running = True     # Set false on window delete
    
        self.check_mod = check_mod
        self.tbmove = tbmove
        self.highlight_limit = highlight_limit
        self.highlighting = highlighting                        
        self.show_id = show_id
        self.show_moved = show_moved
        self.record_md = SelectMoveDisplay(self, show_moved=show_moved)
        self.canvas = canvas
        self.is_enclosed = False
        self.inside = False
        self.is_down = False
        self.highlights = {}            # Highlighted handles object REFERENCE
        self.selects = {}               # Select objects(handle)  REFERENCE
        self.motion_xy = (-1,-1)
        self.regions = []               # list of regions
        self.down_click_call = down_click_call           # call for processing down events
        self.stroke_checking = stroke_checking     # Check for mouse/finger stroking
        self.stroke_info = SelectStroke()         # Any ongoing stroke
        self.stroke_call = None    # Call back if stroke
        self.max_select = max_select
        if rects is not None:
            if not isinstance(rects, list):
                rects = [rects]         # list of one
            for rect in rects:
                self.add_rect(rect)
        self.canvas.bind ("<Button-1>", self.button_click)
        self.canvas.bind ("<ButtonRelease-1>", self.up)
        self.canvas.bind ( "<Enter>", self.enter)
        self.canvas.bind ("<Leave>", self.leave)
        self.enable_moves_ = True

    def on_exit(self):
        """ Window destroyed
        """
        self.running = False

    def is_running(self):
        return self.running
    
        
    def add_down_click_call(self, down_click_call):
        """ Add processing function for down events
        :down_click_call: processing routine for down click over highlighted part
                    None - remove call function
        """
        SlTrace.lg("SelectArea.add_add_down_call %s" % down_click_call)
        self.down_click_call = down_click_call
        SlTrace.lg("SelectArea after add_down_click_call %s" % self.down_click_call)

    def add_rect(self, rect, color=None,
                on_color=None,
                off_color=None,
                row=None, col=None,
                do_corners=True,
                do_edges=True,
                draggable_edge=True,
                draggable_corner=True,
                draggable_region=True,   
                invisible_region=False,
                invisible_edge=False,
                region_width=None,
                edge_width=8,
                invisible_corner=False):
        """ Add rectangle to object as another region
        """
        if region_width is None:
            region_width = self.region_width                
        rec_ps = [None] * 4
        ulX, ulY = rect[0][0], rect[0][1]
        lrX, lrY = rect[1][0], rect[1][1]
        sr = SelectRegion(self, rect=[(ulX,ulY),(lrX,lrY)],
                        draggable=draggable_region,
                        do_corners=do_corners,
                        do_edges=do_edges,
                        invisible=invisible_region,
                        edge_width=edge_width,
                        edge_visible=not invisible_edge,
                        region_width=region_width,
                        on_color=on_color,
                        off_color=off_color,
                        color=color, row=row, col=col)
        self.regions.append(sr)         # Add region
        self.add_part(sr)
        edge_row_cols = 4*[(0,0)]          # row,col   tuples for square perimeter       
        rec_ps[0] = (ulX, ulY); edge_row_cols[0] = (row, col)   # Top horz edge 
        rec_ps[1] = (lrX, ulY); edge_row_cols[1] = (row, col+1)  # Right vert edge  
        rec_ps[2] = (lrX, lrY); edge_row_cols[2] = (row+1, col)  # Botom horz edge
        rec_ps[3] = (ulX, lrY); edge_row_cols[3] = (row, col)    # Left vert edge
        for pi1 in range(0, 3+1):
            pi2 = pi1 + 1
            if pi2 >= len(rec_ps):
                pi2 = 0          # Ends at first
            pt1 = rec_ps[pi1]
            pt2 = rec_ps[pi2]
            if do_edges:
                edge_row_col = edge_row_cols[pi1]
                edge_row = edge_row_col[0]
                edge_col = edge_row_col[1]
                self.add_edge(sr, pt1, pt2,
                            row=edge_row,
                            col=edge_col,
                            draggable_edge=draggable_edge,
                            draggable_corner=draggable_corner,
                            invisible_edge=invisible_edge,
                            edge_width=edge_width,
                            do_corners=do_corners,
                            invisible_corner=invisible_corner)

    def add_edge(self, region, pt1, pt2,
                 row=None,
                 col=None,
                 do_corners=True,
                 draggable_edge=True,
                 draggable_corner=True,
                 invisible_edge=False,
                 edge_width=1,
                 invisible_corner=False):
        """ Add edge handles to region
        Also adds corner handles
        :row: edge row 
        :col: edge column
        """
        edge = self.get_edge_with(pt1, pt2)
        if edge is None:
            edge = SelectEdge(self, rect=[pt1,pt2],
                            row=row,
                            col=col,
                            draggable=draggable_edge,
                            edge_width=edge_width,
                            invisible=invisible_edge)
            self.add_part(edge)
        if do_corners:
            self.add_corners(region, [pt1, pt2], edge=edge,
                            draggable=draggable_corner,
                            invisible=invisible_corner)     # So we get corners
        region.add_connected(edge)
        edge.add_adjacent(region)      # Connect region to edge
        
    def add_corners(self, region, points, edge=None,
                    draggable=True, invisible=False):
        """ Add corners to region
        :region: region to which to add corners
        :points: one or more corner locations
        If corner == first corner, set region enclosed
        but DON't add corner
        """
        if not isinstance(points, list):
            points = [points]     # Treat as an array of one
        for point in points:
            if self.is_first_corner(point):
                self.is_enclosed = True
            if self.has_corner(point):
                corner = self.get_corner_part(point[0], point[1])
            else:
                corner = SelectCorner(self, point=point,
                                        draggable=draggable,
                                        invisible=invisible)
            self.add_part(corner)       # Add new corners
            corner.add_connected(region)
                    
            region.add_connected(corner)
            if edge is not None:
                corner.add_connected(edge)      # Connect edge to corner
                edge.add_connected(corner)      # Connect corner to edge

    
    def add_turned_on_part_call(self, call_back):
        """ Add function to be called upon if edge is turned on
        :call_back: call back (part) - None - remove call back
        """
        self.turned_on_part_call = call_back

                    
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


    def is_square_complete(self, part, squares=None, ifadd=False):
        """ Determine if this edge completes one or more square(s) region(s)
        :part: - possibly completing edge
        :squares: - any squares completed are appended to this list
                default: no regions are appended
        :ifadd: If part is added
                default: part must already be added
        """
        if part.is_edge():
            SlTrace.lg("complete square testing %s" % part, "square_completion")
            regions = part.get_adjacents()      # Look if we completed any square
            ncomp = 0
            for square in regions:
                if (ifadd and square.is_complete(added=part)
                    or
                    square.is_complete()
                    ):
                    ncomp += 1
                    if squares is not None:
                        squares.append(square)
            if ncomp > 0:
                return True

        return False


    def square_complete_distance(self, edge,
                                  squares_distances=None):
        """ Determine minimum number of moves, including this
        move to complete a square
        :edge: - potential completing edge
        :squares_distances: list, of (distance, square) pairs
                Default: no entries returned
                if no connected squares - empty list returned
        :returns: closest distance, NOT_CLOSE if no squares
        """
        NOT_CLOSE = 99
        SlTrace.lg("square distance testing %s" % edge, "square_completion")
        regions = edge.get_adjacents()      # Look if we completed any square
        distances = []  # distances as found
        sqds = []       # distance, square pairs
        for square in regions:
            if not square.is_region():
                continue    # Not a region
            square_edges = square.get_edges()
            distance = 0
            for sq_edge in square_edges:
                if not sq_edge.is_turned_on():
                    distance += 1
            sqds.append((distance,square))
            distances.append(distance)
        if squares_distances is not None:
            squares_distances = sqds

        if len(distances) == 0:
            return NOT_CLOSE        # No squares at all
        
        return min(distances)

    
    def is_selected(self, part):
        """ Check if part is selected
        :part: part/part_id to check
        """
        if isinstance(part, int):
            part_id = part 
        else:
            part_id = part.part_id
        for selected_part_id in self.selects:
            if part_id == selected_part_id:
                return True
            
        return False
    
    def is_first_corner(self, point):
        """ Determine if this is the first point (equal to)
        """
        corner1 = None          # Set if found
        for part in self.parts:
            if part.is_corner():
                corner1 = part 
                break
        if corner1 is None:
            return False        # No corners to be had
        
        cpt = corner1.loc.coord
        if cpt[0] == point[0] and cpt[1] == point[1]:
            return True
        
        return False


    def get_color(self, row, col):
        """ Get color on square(region) at row, col
        :row: row in nx,ny
        :col: column in nx,ny
        :returns: current color None if none
        """
        square = self.get_square(row,col)
        if square is None:
            return None

        color = square.get_color()
        return color


    def color_set(self, color, row, col):
        """ Set color on square(region) at row, col
        :color: color to set square
        :row: row in nx,ny
        :col: column in nx,ny
        :returns: previous color None if none
        """
        square = self.get_square(row,col)
        if square is None:
            return None

        prev_color = square.set_color(color)
        square.display()
        return prev_color
        

    def current_edge(self, pt1, pt2):
        """ Return edge with these specifications, None if none found
        """
        return self.current_part("edge" )


    def current_part(self, part_type, pt1, pt2=None):
        """ Return part with this type, location, None if none found
        """
        loc_key = SelectPart.part_loc_key(part_type, pt1, pt2=None)
        if loc_key in self.parts_by_loc:
            return self.parts_by_loc[loc_key]   # current entry
        
        return None     # No entry at this location


    def destroy(self):
        """ Relinquish 
        """
        for part in self.parts:
            part.destroy()
            
            
    def display(self, parts=None):
        """ Display parts list
        :parts: list of parts to display
                default: all  parts
        """
        
        if not self.display_game:
            return
        
        if parts is None:
            parts = self.parts
        SlTrace.lg("\ndisplay %d parts" % (len(parts)), "display")
        for part in self.display_order(parts):
            part.display()


    def display_order(self, parts):
        """ return parts in display order: Do all regions, then edges, then corners
         so corners are not blocked by regions
         :parts: part/id list
        """
        if len(parts) == 0:
            return []
        
        pts = parts
        if isinstance(next(iter(parts)), int):
            pts = []
            for part in parts:
                pts.append(self.get_part(part)) # Convert id to part
                
        ordered = []
        for part in pts:
            if part is not None and part.is_region():
                ordered.append(part)
        for part in pts:
            if part is not None and part.is_edge():
                ordered.append(part)
        for part in pts:
            if part is not None and part.is_corner():
                ordered.append(part)
        return ordered
            
                
                
                
    def display_set(self, part=None):
        if part.is_corner():
            part.display()
        elif part.is_edge():
            part.display()
        elif part.is_region():
            part.display()
                    
            
    def display_corner(self, corner):
        """ Display corner on inside upper left corner
        """
        return corner.display()
    
        self.display_clear(corner)
        if self.is_highlighted(corner):
            """ Highlight given corner
            :hand: Corner handle
            :Returns: object tag for deletion
            """
            c1x,c1y,c3x,c3y = corner.get_rect(enlarge=True)
            corner.display_tag = self.canvas.create_rectangle(
                                c1x, c1y, c3x, c3y,
                                fill=SelectPart.corner_fill_highlight)
        else:
            loc = corner.loc 
            SlTrace.lg("corner: %s" % str(loc), "display")
            c1x,c1y,c3x,c3y = corner.get_rect()
            corner.display_tag = self.canvas.create_rectangle(
                        c1x, c1y, c3x, c3y, fill=SelectPart.corner_fill)
    
    
    def display_text(self, position, **kwargs):
        """ Add text to display, returning tag
        """
        tag = self.canvas.create_text(position, **kwargs)
        return tag

    def get_parts(self, pt_type=None):
        """ Get parts in figure
        :pt_type: part type, default: all parts
                "corner", "edge", "region"
        """
        parts = []
        for part in self.parts:
            if pt_type is None or pt_type == part.part_type:
                parts.append(part)
        return parts


    def get_part(self, id=None, type=None, sub_type=None, row=None, col=None):
        """ Get basic part
        :id: unique part id
        :type: part type e.g., edge, region, corner default: "edge"
        :sub_type: must match if present e.g. v for vertical, h for horizontal
        :row:  part row
        :col: part column
        :returns: part, None if not found
        """
        if id is not None:
            if id not in self.parts_by_id:
                SlTrace.lg(f"part id={id} not in parts_by_id")
                return None
            
            part = self.parts_by_id[id]
            return part
        
        if type is None:
            type = "edge"
        for part in self.parts:
            if part.part_type == type and (sub_type is None or part.sub_type() == sub_type):
                if part.row == row and part.col == col:
                    return part
                
    
    def get_parts_at(self, x, y, sz_type=SelectPart.SZ_SELECT):
        """ Check if any part is at canvas location provided
        If found list of parts
        :Returns: SelectPart[]
        """
        parts = []
        for part in self.parts:
            if not isinstance(part, SelectPart):
                SlTrace.lg("part(%s) is not SelectPart" % part)
            if part.is_over(x,y, sz_type=sz_type):
                parts.append(part)
        if len(parts) > 1:
            SlTrace.lg("get_parts at (%d, %d) sz_type=%d" % (x,y, sz_type), "get_parts")
            for part in parts:
                c1x,c1y,c3x,c3y = part.get_rect(sz_type=sz_type)
                SlTrace.lg("    %s : c1x:%d, c1y:%d, c3x:%d, c3y:%d"
                       % (part, c1x,c1y,c3x,c3y), "get_parts")
            SlTrace.lg("", "get_parts")
            olap_rect = SelectPart.get_olaps(parts, sz_type=SelectPart.SZ_SELECT)
            if olap_rect is not None:
                if SlTrace.trace("overlapping"):
                    SlTrace.lg("Overlapping %d,%d, %d,%d"
                       % (olap_rect[0][0], olap_rect[0][1],
                          olap_rect[1][0], olap_rect[1][1]), "overlapping")
                    SlTrace.lg("")
        return parts


    

    def get_corner_part(self, x, y):
        """ Returns corner SelectPart if at corner handle
        else None
        """
        for corner in self.parts:
            if not corner.is_corner():
                continue
            p1c1x,p1c1y,p1c3x,p1c3y = corner.get_rect(sz_type=SelectPart.SZ_SELECT)
            if p1c1x <= x and x <= p1c3x and p1c1y <= y and y <= p1c3y:
                return corner
            
        return None
    

    def get_edge_part(self, x, y):
        """ Returns edge object if at corner handle
        else None
        """
        for edge in self.parts:
            if not edge.is_edge():
                continue
            p1c1x,p1c1y,p1c3x,p1c3y = edge.get_rect()
            if p1c1x <= x and x <= p1c3x and p1c1y <= y and y <= p1c3y:
                return edge
            
        return None
    
    
    def get_edge_with(self, pt1, pt2):
        """ Get edge part with corners at pt1, pt2, if one
            :pt1:  end point uL or lR
            :pt2:  end point
            :Returns: edge or None
        """
        for part in self.parts:
            if not part.is_edge():
                continue
            points = part.get_points()
            if (SelectPart.is_point_equal(points[0], pt1)
                and SelectPart.is_point_equal(points[1], pt2)):
                return part
            if (SelectPart.is_point_equal(points[1], pt1)
                and SelectPart.is_point_equal(points[0], pt2)):
                return part

        return None
                    

    def get_region_part(self, x, y):
        """ Returns region object if at region handle
        else None
        """
        for region in self.parts:
            if not region.is_region():
                continue
            p1c1x,p1c1y,p1c3x,p1c3y = region.get_rect()
            if p1c1x <= x and x <= p1c3x and p1c1y <= y and y <= p1c3y:
                return region
            
        return None
        


    
    def get_square(self, row, col):
        """ return part for region at row, col
        :returns: part at row,col else None
        """
        
        """ Create dictionary only if we have to
        Maybe numpy would be better but we need to store parts, not numbers
        """
        if not hasattr(self, "parts_by_row_col") or self.parts_by_row_col is None:
            parts_by_row_col = {}
            for part in self.parts:
                if part.row != 0 and part.col != 0:
                    key = (part.row, part.col)
                    parts_by_row_col[key] = part
            self.parts_by_row_col = parts_by_row_col
        key = (row,col)
        
        if key not in self.parts_by_row_col:
            return None
        
        part = self.parts_by_row_col[key]
        
        return part

    def delete_tags(self, tags, quiet = False):
        """ Delete tag or list of tags
        :tags: tag or list of lists of tags
        :quiet: supress tracing
        """
        if SlTrace.trace("delete_tags"):
            SlTrace.lg(f"delete_tags: {self} tags:{tags}")
            
        if tags is None:
            return
        
        if isinstance(tags, list):
            for tag in tags:
                self.delete_tags(tag, quiet=True)
        else:
            self.canvas.delete(tags)
    
    
    def display_clear(self, handle):
        """ Clear display of this handle
        """
        if handle.display_tag is not None:
            self.delete_tags(handle.display_tag)
            handle.display_tag = None
        if handle.highlight_tag is not None:
            self.delete_tags(handle.highlight_tag)
            handle.highlight_tag = None

    
    def display_edge(self, edge):
        """ Display edge as a rectangle
        We leave room for the corners at each end
        Highlight if appropriate
        """
        
        loc = edge.loc
        rect = loc.coord
        SlTrace.lg("edge: %s" % str(loc), "display")
        if self.is_highlighted(edge):
            c1x,c1y,c3x,c3y = edge.get_rect(enlarge=True)
            edge.highlight_tag = self.canvas.create_rectangle(
                                c1x, c1y, c3x, c3y,
                                fill=SelectPart.edge_fill_highlight)
        else:
            self.display_clear(edge)
            c1x, c1y, c3x, c3y = edge.get_rect()
            edge.display_tag = self.canvas.create_rectangle(
                                c1x, c1y, c3x, c3y,
                                fill=SelectPart.edge_fill)
        if self.show_id:
            dir_x, dir_y = edge.edge_dxy()
            chr_w = 5
            chr_h = chr_w*2
            if dir_x != 0:      # sideways
                offset_x = -len(str(edge.part_id))*chr_w/2 + chr_w
                offset_y = chr_h
            if dir_y != 0:      # up/down
                offset_x = len(str(edge.part_id))*chr_w
                offset_y = 0    
        
            cx = (c1x+c3x)/2 + offset_x
            cy = (c1y+c3y)/2 + offset_y
            edge.name_tag = self.display_text((cx, cy), text=str(edge.part_id))
    
    
    def check_pick_part(self, event):
        """ Check for and process if part has been picked.  E.g., line/edge added to square
        :returns: True iff found a pick
        If so, and down_click_call has been set, we make the call
        """
        if self.has_highlighted():
            for highlight in self.highlights.values():
                part = highlight.part
                if self.down_click_call is not None:
                    res = self.down_click_call(part)
                    if res:
                        return res        # we've done the processing for this part
        return False                        # No processing

    def button_click(self, event):
        if SlTrace.trace("part_info"):
            cnv = event.widget
            x,y = cnv.canvasx(event.x), cnv.canvasy(event.y)
            parts = self.get_parts_at(x,y)
            if parts:
                SlTrace.lg("x=%d y=%d" % (x,y))
                for part in parts:
                    SlTrace.lg("    %s\n%s" % (part, part.str_edges()))
            
        if not self.enable_moves_:
            return                  # Low-level ignore

        self.is_down = True
        if self.inside:
            SlTrace.lg("Click in canvas event:%s" % event, "motion")
            cnv = event.widget
            x,y = cnv.canvasx(event.x), cnv.canvasy(event.y)
            SlTrace.lg("x=%d y=%d" % (x,y), "down")
                
        if self.has_highlighted():
            part_ids = list(self.highlights)
            for part_id in part_ids:
                part = self.parts_by_id[part_id]
                SlTrace.lg("highlighted %s" % (part), "highlight")
                if self.down_click_call is not None:
                    self.down_click_call(part, event=event)
                    continue        # we've done the processing for this part
                    
                self.select_set(part)
                if part.display_tag is None:
                    pt=str(part.part_type)
                    pdtag = str(part.display_tag)
                    SlTrace.lg("select %s tag=%s"
                           % (pt, pdtag,), "highlight")
                else:
                    SlTrace.lg("select %s tag=%s (%s)"
                           % (part.part_type, part.display_tag,
                              part), "highlight")
    
    

    def down (self, event):
        if SlTrace.trace("part_info"):
            cnv = event.widget
            x,y = cnv.canvasx(event.x), cnv.canvasy(event.y)
            parts = self.get_parts_at(x,y)
            if parts:
                SlTrace.lg("x=%d y=%d" % (x,y))
                for part in parts:
                    SlTrace.lg("    %s\n%s" % (part, part.str_edges()))
            
        if not self.enable_moves_:
            return                  # Low-level ignore

        self.is_down = True
        if self.inside:
            SlTrace.lg("Click in canvas event:%s" % event, "motion")
            cnv = event.widget
            x,y = cnv.canvasx(event.x), cnv.canvasy(event.y)
            SlTrace.lg("x=%d y=%d" % (x,y), "down")
                
        if self.has_highlighted():
            part_ids = list(self.highlights)
            for part_id in part_ids:
                part = self.parts_by_id[part_id]
                SlTrace.lg("highlighted %s" % (part), "highlight")
                if self.down_click_call is not None:
                    res = self.down_click_call(part, event=event)
                    continue        # we've done the processing for this part
                    
                self.select_set(part)
                if part.display_tag is None:
                    pt=str(part.part_type)
                    pdtag = str(part.display_tag)
                    SlTrace.lg("select %s tag=%s"
                           % (pt, pdtag,), "highlight")
                else:
                    SlTrace.lg("select %s tag=%s (%s)"
                           % (part.part_type, part.display_tag,
                              part), "highlight")
                    

    def draw_line(self, p1, p2, color=None, width=None, **kwargs):
        """ Draw line between two points on canvas
        :p1: point x,y canvas coordinates
        :p2: point x,y canvas coordinates
        :color: line color default: red
        :width: line width in pixels default:2
        :returns: canvas line object
        """
        if color is None:
            color = "red"
        if width is None:
            width = 2
        canvas = self.canvas
        return canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=color, width=width, **kwargs)

 
    def draw_outline(self, sq, color=None, width=None):
        sq.draw_outline(color=color, width=width)
    
    
    def motion (self, event):
        ###cnv.itemconfigure (tk.CURRENT, fill ="blue")
        cnv = event.widget
        x,y = float(cnv.canvasx(event.x)), float(cnv.canvasy(event.y))
        ###got = event.widget.coords (tk.CURRENT, x, y)
    
    def leave (self, event):
        SlTrace.lg("leave", "leave")
        self.inside = False
        if hasattr(self, 'motion_bind_id') and self.motion_bind_id is not None:
            self.canvas.unbind ("<Motion>", self.motion_bind_id)
            self.motion_bind_id = None

    
    def list_blinking(self, prefix=None):
        if prefix is None:
            prefix = ""
        else:
            prefix = prefix + " "
        part_ids = list(self.parts_by_id)
        n_on = 0
        for part_id in part_ids:
            part = self.get_part(id=part_id)
            if part.blinker is not None:
                n_on += 1
        SlTrace.lg("%s parts blinking on(%d of %d):" % (prefix, n_on, len(part_ids)))
        for part_id in part_ids:
            part = self.get_part(id=part_id)
            if part.blinker is not None:
                SlTrace.lg("    %s" % (part))

    
    def list_selected(self, prefix=None):
        if prefix is None:
            prefix = ""
        else:
            prefix = prefix + " "
        part_ids = list(self.parts_by_id)
        n_on = 0
        for part_id in part_ids:
            part = self.get_part(id=part_id)
            if part.is_selected():
                n_on += 1
        SlTrace.lg("%sparts selected on(%d of %d):" % (prefix, n_on, len(part_ids)))
        for part_id in part_ids:
            part = self.get_part(id=part_id)
            if part.is_selected():
                SlTrace.lg("    %s" % (part))
        if SlTrace.trace("selected_selects"):
            selecteds = self.get_selects()
            SlTrace.lg("parts in selecteds:")
            for part_id in selecteds:
                SlTrace.lg("    %s" % self.get_part(part_id))
    
    def enter (self, event):
        SlTrace.lg("enter", "enter")
        self.inside = True
        self.motion_bind_id = self.canvas.bind("<Motion>", self.on_motion)


    def disable_moves(self):
        """ Disable(ignore) moves by user
        """
        self.enable_moves_ = False
        
        
    def enable_moves(self):
        """ Enable moves by user
        """
        self.enable_moves_ = True


    def get_xy(self):
        """ get current mouse position (or last one recongnized
        :returns: x,y on area canvas, -1,-1 if never been anywhere
        """
        return self.motion_xy



    def on_motion(self, event):
        cnv = event.widget
        x,y = cnv.canvasx(event.x), cnv.canvasy(event.y)
        SlTrace.lg("on_motion: x,y=%d,%d" % (x,y), "on_motion")
        if not self.enable_moves_:
            return                  # Low-level ignore
        
        prev_xy = self.motion_xy
        self.motion_xy = (x,y)
        if prev_xy is None:
            prev_xy = self.motion_xy
        SlTrace.lg("on_motion enable_moves: x,y=%d,%d" % (x,y), "on_motion")
        if self.is_down:
            if self.has_selected():
                parts = self.get_selected_parts(only_draggable=True)
                if len(parts) > 0 and len(parts) <= self.max_select:
                    self.record_move_setup()
                    for part in parts:
                        xinc = x - prev_xy[0]
                        yinc = y - prev_xy[1]
                        SlTrace.lg("motion on(%s) at xy=(%d,%d) by xinc=%d yinc=%d"
                               % (part.part_type, x,y, xinc, yinc), "on_motion")
                        self.move_part(part, xinc, yinc)
                        if self.highlighting:
                            self.highlight_set(part)
                    self.record_move_display()
        parts = self.get_parts_at(x,y, sz_type=SelectPart.SZ_SELECT)        # NOTE: this is reference
        if len(parts) > 0:
            s = ""
            part_str = "NONE" if len(parts) == 0 else str(parts[0])
            if len(parts) != 1:
                s = "s"
                for part in parts[1:]:      # first is already present
                    part_str += "\n" + " "*len(" over 2 parts: ") + str(part)
            SlTrace.lg(f"over {len(parts)} part{s}: {part_str}", "motion")
            ncheck = 1
            if len(parts) > ncheck:
                if SlTrace.trace("motion_over_n"):
                    SlTrace.lg("on parts(%d) > %d " % (len(parts), ncheck))
                    for pa in parts:
                        SlTrace.lg("part: %s" % pa)
                    SlTrace.lg("")
            if self.highlighting:
                self.highlight_clear(parts=parts, others=True) # First clear all highlighted parts
            for part in parts:
                if not part.is_region():
                    SlTrace.lg("motion over %s" % part, "is_over")
                if SlTrace.trace("part_info_over"):
                    part.display_info(tag="over:")
                if self.highlighting:
                    self.highlight_set(part, xy=(x,y))
                self.stroke_check(part, x=x, y=y)
        else:
            if self.highlighting:
                if self.has_highlighted():    
                    self.highlight_clear()
            
            
    def highlight_set(self, part, xy=None,
                       highlight_limit=None):
        """ highlight specified part
        Save handle in highlight to allow easy access
        Clear previous highlight, if one
        :highlight_limit: clear highlight after this (seconds)
                    Default: self.highlight_limit
        """
        if highlight_limit is None:
            highlight_limit = self.highlight_limit
        if part.turned_on and not part.on_highlighting:
            return                  # Don't highlight if turned on
        
        part.highlight_set(highlight_limit=highlight_limit)

    
    
    def get_highlighted(self):
        if not self.has_highlighted():
            return None
        
        highlighted = self.highlighted
        return highlighted


    
    
    def get_highlighted_part(self):
        highlighted = self.get_highlighted()
        if highlighted is None:
            return None
        
        return highlighted.part


    def has_highlighted(self):
        """ Determine if any highlighted parts
        """
        if bool(self.highlights):
            return True
        return False


    def is_highlighted(self, part):
        """ Check if part is highlighted
        """
        return part.is_highlighted()


    def is_highlighted_others(self, part):
        """ Check if non-overlapping parts are highlighted
        """
        if not self.has_highlighted():
            return False                # Nobody highlighted
        
        for highlight in self.highlights.values():
            if highlight.part.part_type != part.part_type:
                return True             # Another type is highlighted
            
            if not highlight.part.is_covering(part):
                return True
            
        return False

    def clear_highlighted(self, parts=None, others=False, display=True):
        """ alternate
        """
        
        self.highlight_clear(parts=parts, others=others, display=display
                             )
    def highlight_clear(self, parts=None, others=False, display=True):
        """ Clear highlighted parts
            Remove part form  highlights
            :parts:  parts to consider
            :others:   False - clear these parts
                        True - clear other parts
            :display: display updated, default: True
        """
        if parts is None:
            if not others:
                SlTrace.lg("highlight_clear ALL", "highlight")
            parts = []
            for highlight in self.highlights.values():
                parts.append(highlight.part)
        if not isinstance(parts, list):
            parts = [parts]
        
        if others:
            parts_dict = {}
            for part in parts:
                parts_dict[part.part_id] = part
            other_parts = []
            for highlight in self.highlights:
                if highlight not in parts_dict:
                    other_parts.append(self.highlights[highlight].part)
            parts = other_parts
                
        for part in parts:
            part.highlight_clear(display=display)
        
        
    def select_clear(self, parts=None):
        """ Select part(s)
        :parts: part/id or list of parts
                default: all selected
        """
        '''parts = select_copy(parts)'''
        if parts is None:
            parts = []
            for selects_part_id in self.selects:
                parts.append(selects_part_id) 
        if not isinstance(parts, list):
            parts = [parts]
        if SlTrace.trace("selected"):
            self.list_selected("select_clear BEFORE")
        for part in parts:
            if isinstance(part, int):
                part_id = part 
            else:
                part_id = part.part_id
            if part_id in self.selects:
                del(self.selects[part_id])
        if SlTrace.trace("selected"):
            self.list_selected("select_clear AFTER")

        
    def select_set(self, parts, keep=False):
        """ Select part(s)
        :parts: part/id or list
        :keep: keep previously selected default: False
        """
        parts = copy.copy(parts)
        if not keep:
            self.select_clear()
        if not isinstance(parts, list):
            parts = [parts]
        for part in parts:
            part_id = part.part_id
            self.selects[part_id] = part
        if SlTrace.trace("selected"):
            self.list_selected("select_set AFTER")

    
    
    def get_selects(self):
        """ Get list of selected parts
        :returns: list, empty if none
        """
        return self.selects.keys()


    
    
    def get_selected_part(self):
        if not self.selects:
            return None
        
        return self.get_part(next(iter(self.selects)))


    def has_selects(self):
        """ Determine if any highlighted parts
        """
        if self.selects:
            return True
        return False
    
    
    def set_stroke_move(self, use_stroke=True):
        """ Enable/Disable use of stroke moves
        Generally for use in touch screens
        """
        self.stroke_checking = use_stroke
        
        
    def select_remove(self, selects):
        """ Remove one or more of selections
        :select: one or list of  selections to remove
                Default: all
        """
        if not isinstance(selects,list):
            selects = [selects]
        for part_id in list(self.selects):
            self.selects.pop(part_id)


    def add_stroke_call(self, call_back=None):
        """ Add callback for completed stroke
        :call_back: call(part=part, x=, y=)
        """
        self.stroke_call = call_back
        
        
        
    def stroke_check(self, part, x=None, y=None):
        """ Check if user stroked part
        Used for stroking edges on touch screen
        in "squares" game
        :part: inside this part
        :x: - x coordinate
        :y: - y coordinate
        :returns: True iff got stroke
        Detection starts self.btmove seconds after the
        most recent 
        """
        if not self.stroke_checking:
            return False
        
        now = datetime.now()
        time_diff = (now - self.stroke_info.prev_time).total_seconds()
        if  time_diff < self.tbmove:
            return

        if self.stroke_info.in_stroke():
            SlTrace.lg("in_stroke x=%d y=%d" % (x,y), "in_stroke")
            if part.is_edge() and not self.stroke_info.same_part(part):
                self.stroke_info.setup()
                return
            
            SlTrace.lg("same stroke x=%d y=%d" % (x,y), "in_stroke")
            if self.stroke_info.is_continued(part=part, x=x, y=y):
                self.stroke_info.new_point(x,y)
                if self.stroke_info.is_stroke():
                    SlTrace.lg("got stroke x=%d y=%d\n" % (x,y), "in_stroke")
                    if self.down_click_call is not None:
                        res = self.down_click_call(part)
                        self.stroke_info.setup()      # Reset
                        return res
                    
        if part.is_edge():
            self.stroke_info.setup(part, x=x, y=y)
            
        return False


    def stroke_init(self, part=None, x=None, y=None):
        if part is None:
            self.stroke_info.setup()
            return
        
        self.stroke_info.setup(part=part, x=x, y=y)

                    
    def get_selecteds(self, only_draggable=False):
        """ Return list of selected info or [] if none
        :only_draggable: True- include only if draggable
                            default: False - all
        """
        sels = []
        for part in self.selects.values():
            if not only_draggable or part.draggable:
                sels.append(part)
        return sels
    
    
    def get_selected_parts(self, only_draggable=False):
        """ Returns all selected parts
        [] if non selected
        :only_draggable: True- include only if draggable
                            default: False - all
        """
        parts = self.get_selecteds(
            only_draggable=only_draggable)
        return parts
    
    
    def has_selected(self):
        """ Check if any selected parts
        """
        if bool(self.selects):
            return True
        return False
        

    def move_part(self, part, xinc, yinc):
        """ Move selected handle, adjusting connected parts
        """
        
        self.display_clear(part)      # Clear display before moveing
        if part.is_region():
            self.move_region(part, xinc, yinc)
        elif part.is_edge():
            self.move_edge(part, xinc, yinc)
        
        elif part.is_corner():
            self.move_corner(part, xinc, yinc)
        
        self.display_set(part)

    
    def move_announce(self):
        import winsound
        
        winsound.Beep(100, 10)


    def move_edge(self, edge, xinc,  yinc, adjusts=None):
        
        
        """ Move selected edge, adjusting connected parts
        Direction of movement is constrained to perpendicular to edge
        Connected parts are:
            the corners at each edge end
            the end-points of the edges, not including this edge,
                connected to the end-corners
        :edge:  selected edge
        :xinc:  x destination delta
        :yinc:  y destination delta
        :adjusts: adjusted connections
                    Default: all connections
        :highlight: True - highlight after move
        """
        self.display_clear(edge)      # Clear display before moveing
        delta_x = xinc
        delta_y = yinc
        edge_dx, edge_dy = edge.edge_dxy()
        if edge_dx == 0:
            delta_y = 0     # No movement parallel to edge
        if edge_dy == 0:
            delta_x = 0     # No movement parallel to edge
        coord = edge.loc.coord
        p1, p2 = coord[0], coord[1]
        SlTrace.lg("move_edge: %s by delta_x=%d,delta_y=%d"
               % (edge, delta_x, delta_y), "move_part")
        """ Collect moves group:
            Collect all parts which need to be moved in whole or part.
            Each part is present once.  If an edge end is moved only the other edge's
            ends need to be adjusted
                 
        """
        mover = SelectMover(self, delta_x=delta_x, delta_y=delta_y)
        mover.add_moves(parts=edge)
        ###mover.add_moves(parts=edge.connecteds)
        ###mover.add_adjusts(edge.connecteds)      # Adjust those connected to corners and so on
        mover.move_list(delta_x, delta_y)

        
    def move_corner(self, corner, xinc,  yinc):
        """ Move selected corner, adjusting connected edges
        :corner: selected corner
        :xinc: x destination increment
        :yinc: y destination increment
        """
        delta_x = xinc
        delta_y = yinc
        SlTrace.lg("move: %s  by delta_x=%d,delta_y=%d"
               % (corner, delta_x, delta_y), "move_part")
        """ Split movements in to two directions to restrict propagation
        of affected parts
        """
        if delta_x != 0:
            mover = SelectMover(self, delta_x=delta_x)
            mover.add_moves(parts=corner)
            ###mover.add_moves(parts=edge.connecteds)
            ###mover.add_adjusts(edge.connecteds)      # Adjust those connected to corners and so on
            mover.move_list(delta_x, 0)
        if delta_y != 0:
            mover = SelectMover(self, delta_y=delta_y)
            mover.add_moves(parts=corner)
            ###mover.add_moves(parts=edge.connecteds)
            ###mover.add_adjusts(edge.connecteds)      # Adjust those connected to corners and so on
            mover.move_list(0, delta_y)


    def move_region(self, region, xinc,  yinc, adjusts=None):
        """ Move region
        Currently all parts
        Implement via move all corners
        """
        for part in region.connecteds:
            if part.is_corner():
                self.move_corner(part, xinc, yinc)
            
                 
    def adjust_corner_edge(self, corner, edge, delta_x, delta_y):
        """ Adjust edge's endpoint connected to this corner by the delta x,y
        """
        indexes = edge.get_connected_loc_indexes(corner)
        if indexes is None:
            raise(SelectError("adjust_corner_edge: corner(%s) not connected to edge(edge)"
                              % (corner, edge)))
        coord = edge.loc.coord
        coord.move_nodes(delta_x, delta_y, indexes[0])
        self.display_set(edge)

    def add_part(self, part):
        """ Add new part to area
        :part: partially completed to add
        Not added if already present
        Hash updates and pointers added to part
        We are considering adding this to the SelectPart
        constructor but have, so far, refrained because of 
        the possibility of having multiple lists as is the
        fact in EnhancedModeler
        """
        if part.part_id in self.parts_by_id:
            return
        
        SlTrace.lg("add_part: %s" % part, "add_part")
        """ Provide pointers to other entries
        in the parts_by_id entry to aid do/undo
        """
        loc_key = part.loc_key()
        if loc_key in self.parts_by_loc:
            SlTrace.lg("add_part %s already present", "add_part")
            return
        
        part.loc_key_ = loc_key
        part.parts_index = len(self.parts)
        self.parts.append(part)
        self.parts_by_id[part.part_id] = part
        self.parts_by_loc[loc_key] = part
        
                            
    def up (self, event):
        self.is_down = False
        ###event.widget.itemconfigure (tk.CURRENT, fill =self.defaultcolor)
        cnv = event.widget
        x,y = cnv.canvasx(event.x), cnv.canvasy(event.y)
        ###got = event.widget.coords (tk.CURRENT, x, y)
        SlTrace.lg("up at x=%d y=%d" % (x,y), "on_up")
        SlTrace.lg("up is ignored", "on_up")
        return
    
        if self.has_selected():
            ids = list(self.selects)
            for sel_id in ids:
                self.select_remove(sel_id)
        if SlTrace.trace("selected"):
            self.list_selected("up AFTER")
        
        
    def record_move(self, move):
        """ Record move for display or subsequent action
        :move: SelectMove to be recorded
        """
        self.record_md.record_move(move)
        
            
    def record_move_setup(self):
        """ Setup for move record display
        """
        self.record_md.record_move_setup()
        
        
    def record_move_display(self):
        self.record_md.record_move_display()
        
        
        
    
class SelBound(object):
    """
    Select boundary - part of Region
    """
    
    def __init__(self, region, rect, part_type='edge'):
        """
        Rectangular region, part of a selection region which can be used to modify
        the position/size of the region
        :region: region of which this  boundary is part
        :rect: Rectangle (upper left x,y), (lower right x,y)
        :part_type: Type region - determines range of movement, and effect
                    'corner' - free x,y adjusting adjacent legs
                    'edge' - movement perpendicular to edge, adjusting
                            placement of this edge and size of adjacent
                            edges
                    'region' - free x,y, adjusting position of whole
                            region, keeping dimensions fixed
        """
     
     
          
        
if __name__ == "__main__":
    import os
    import sys
    from tkinter import *    
    import argparse
    from PIL import Image, ImageDraw, ImageFont
    
    
    nx = 2          # Number of x divisions
    ny = 2          # Number of y divisions
    show_id = False  # Display component id numbers
    show_moved = True  # Display component id numbers
    width = 600     # Window width
    height = width  # Window height

    parser = argparse.ArgumentParser()
    
    parser.add_argument('--nx=', type=int, dest='nx', default=nx)
    parser.add_argument('--ny=', type=int, dest='ny', default=ny)
    parser.add_argument('--show_id', type=bool, dest='show_id', default=show_id)
    parser.add_argument('--show_moved', type=bool, dest='show_moved', default=show_moved)
    parser.add_argument('--width=', type=int, dest='width', default=width)
    parser.add_argument('--height=', type=int, dest='height', default=height)
    args = parser.parse_args()             # or die "Illegal options"
    
    nx = args.nx
    ny = args.ny
    show_id = args.show_id
    show_moved = args.show_moved
    width = args.width
    height = args.height
    
    SlTrace.lg("%s %s\n" % (os.path.basename(sys.argv[0]), " ".join(sys.argv[1:])))
    SlTrace.lg("args: %s\n" % args)
    
    
    
    
    
    rect1 = ((width*.1, height*.1), (width*.5, height*.5))
    rect2 = ((width*.5, height*.5), (width*.9, height*.9))
    rects =  []
    ###rects.append(rect1)
    ###rects.append(rect2)
    xmin = .1*width
    xmax = .9*width
    xlen = (xmax-xmin)/nx
    ymin = .1*height
    ymax = .9*height
    ylen = (ymax-ymin)/ny
    for j in range(ny):
        y1 = ymin + j*ylen
        y2 = y1 + ylen
        for i in range(nx):
            x1 = xmin + i*xlen
            x2 = x1 + xlen
            rect = ((x1, y1), (x2, y2))
            rects.append(rect)
            
    im = Image.new("RGB", (width, height))
    frame = Frame(width=width, height=height, bg="", colormap="new")
    frame.pack(expand=YES, fill=BOTH)
    canvas = Canvas(frame, width=width, height=height)
    canvas.pack(expand=YES, fill=BOTH)   
    sr = SelectArea(canvas, image=im, rects=rects,
                      show_moved=show_moved, show_id=show_id)
    sr.display()
    mainloop()