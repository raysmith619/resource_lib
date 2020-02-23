# select_stroke.py
from datetime import datetime
from cmath import rect

from select_trace import SlTrace
from select_error import SelectError

class SelectStroke:
    min_count = 2       # Minimum points
    min_distance = 5  # Minimum distance
    def __init__(self, part=None, x=None, y=None):
        self.setup(part=part, x=x, y=y)
    
    
    def setup(self, part=None, x=None, y=None):
        self.part = part    # None == not started
        self.x = self.x0 = x 
        self.y = self.y0 = y
        self.xmin = self.xmax = self.x
        self.ymin = self.ymax = self.y
        if part is None:
            self.count = 0
        else:
            self.count = 1
        self.prev_time = datetime.now()
        if x is not None: 
            SlTrace.lg("\nnew stroke setup x=%d y=%d" % (x,y), "in_stroke")
        else:
            SlTrace.lg("\nstroke reset", "in_stroke")
    
    def new_point(self, x, y):
        self.count += 1
        self.x = x 
        self.y = y 
        if x < self.xmin:
            self.xmin = x 
        if x > self.xmax:
            self.xmax = x 
        self.xlen = self.xmax - self.xmin
        if y < self.ymin:
            self.ymin = y 
        if y > self.ymax:
            self.ymax = y 
        self.ylen = self.ymax - self.ymin
        
    def same_part(self, part):
        """ Determine if this part is the same as the
        current stroke candidate part
        """
        if part.is_same(self.part):
            return True
        
        return False
    
    
        
        
    def in_stroke(self):
        """ Check if currently active stroke possibly
        """
        if self.part is None:
            return False
        
        return True
        
    
    def is_continued(self, part=None, x=None, y=None):
        """ Check if current addition is a candidate for continued stroke
        """
        if part is None or self.part is None or not part.is_same(self.part):
            return False
        self.part.sel_area.move_announce()
        return True         # A possible candidate
    
    
    
    def is_stroke(self):
        """ Check if current info indicates a stroke
        """
        if not self.in_stroke():
            return False
        
        if self.count < self.min_count:
            return False        # Requires at least 3

        if SlTrace.trace("in_stroke"):
            SlTrace.lg("stroke_count=%d, x=%d, y=%d xlen=%d ylen=%d"
                       % (self.count, self.x, self.y,
                           self.xlen, self.ylen))
        if self.part.is_edge():
            dir_x, dir_y = self.part.edge_dxy()
            if SlTrace.trace("in_stroke"):
                SlTrace.lg("stroke dir_x=%d dir_y=%d, xlen=%d ylen=%d"
                           % (dir_x, dir_y, self.xlen, self.ylen))
            if dir_x != 0 and self.xlen < self.min_distance:
                return False
            
            if dir_y != 0 and self.ylen < self.min_distance:
                return False
            
            if SlTrace.trace("in_stroke"):
                SlTrace.lg("stroke made count=%d, x=%d, y=%d xlen=%d ylen=%d"
                           % (self.count, self.x, self.y, self.xlen, self.ylen))
            return True 
                
        if (self.xlen < self.min_distance
             and self.ylen < self.min_distance):
            return False
        
        if SlTrace.trace("stroke"):
            SlTrace.lg("strokemade (%s) count=%d, x=%d, y=%d xlen=%d ylen=%d"
                           % (self.part, self.count, self.x, self.y, self.xlen, self.ylen))
        return True    
