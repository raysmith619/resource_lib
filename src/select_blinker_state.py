# select_blinker_state.py
from select_trace import SlTrace
from active_check import ActiveCheck


class BlinkerMultiState:
    """ Blinking multi tag group item state
    
    The group will display for on_time then rotated one group and redisplayed
    """
    enable_blinking = True
    
    
    def __deepcopy__(self, memo=None):
        """ provide deep copy by just passing shallow copy of self,
        avoiding tkparts inside sel_area
        """
        SlTrace.lg("SelectArea __deepcopy__", "copy")
        return self

    @classmethod
    def enable(cls, enable=True):
        cls.blinking_enabled = enable
    
    @classmethod
    def disable(cls):
        cls.enable(enable=False)
        
        
    def __init__(self, part, tagtags=None,
                 on_time=None):
        """ Setup multi state blinker
        :part: part to blink
        :tagtags:  list of tag lists
        :on_time: length of the display before rotating the fill colors
        """
        self.part = part
        self.canvas = part.sel_area.canvas
        if on_time is None:
            on_time = .25
        self.on_time = on_time
        self.multitags = tagtags
        self.multifills = []
        for taggroup in tagtags:
            tg_fills = []
            for tag in taggroup:
                fill = self.canvas.itemcget(tag, "fill")
                tg_fills.append(fill)
            self.multifills.append(tg_fills)
        self.first_fill_index = 0      # Where the first fills go
        

    def is_blinking(self):
        """ Check if still blinking
        """
        if self.part is None:
            return False
        
        if not self.enable_blinking:
            return False
        
        if SlTrace.trace("no_blink"):
            return False
        
        if SlTrace.trace("dbg"):
            SlTrace.lg("is_blinking")
            
        if not self.part.is_highlighted() and not self.part.is_selected():
            return False                    # Only blink highlighted
        
        if not self.multitags:
            return False
        
        if not self.multifills:
            return False
        
        return True


    def blink_on_first(self):
        """ Just set going - assumes first is displayed
        """
        if ActiveCheck.not_active():
            return  False   # We're at the end
        
        if not self.is_blinking():
            return False
        
        self.first_fill_index = 1
        if self.first_fill_index >= len(self.multitags):
            self.first_fill_index = 0            # Wrap around
        si = self.first_fill_index
        SlTrace.lg("blink_on_first first_fill_index=%d in %s"
                   % (si, self.part), "blink_on_first")
        self.canvas.after(int(1000*self.on_time), self.blink_on_next)
        return True
 
                       
    def blink_on_next(self):
        if ActiveCheck.not_active():
            return False     # We're at the end
        
        if not self.is_blinking():
            return False

        si = self.first_fill_index       # Source of new state(e.g. fill)
        SlTrace.lg("blink_on_next first_fill_index=%d in %s"
                   % (si, self.part), "blink")
        for taggroup in self.multitags:
            if si >= len(self.multitags):
                si = 0                      # Wrap around
            src_fill_group = self.multifills[si]
            for i in range(len(taggroup)):
                itag = ifill = i            # May have different lengths
                if itag >= len(taggroup):
                    itag = len(taggroup)-1  # Use last
                if ifill >= len(src_fill_group):
                    ifill = len(src_fill_group)-1
                try:
                    self.canvas.itemconfigure(taggroup[itag], fill=src_fill_group[ifill])
                except:
                    SlTrace.lg("Out of range")
                    return
                
            si += 1                         # Go to next fill group
        self.first_fill_index += 1
        if self.first_fill_index >= len(self.multitags):
            self.first_fill_index = 0            # Wrap around
        self.canvas.after(int(1000*self.on_time), self.blink_on_next)
        return True
                        
    def blink_off(self):
        if ActiveCheck.not_active():
            return False # We're at the end
        
        if not self.is_blinking():
            return False
        
        if self.on_state:
            self.canvas.itemconfigure(self.tag, fill=self.off_fill)
            self.on_state = False
        self.canvas.after(int(1000*self.off_time), self.blink_on)
        return True


    def stop(self):
        """ Stop blinking
        """
        self.part = None
        for taggroup in self.multitags:
            for tag in taggroup:
                if tag is not None:
                    self.canvas.delete(tag)
                    tag  = None
        self.multitags = []

    def destroy(self):
        """ Remove
        """
        self.stop()
        