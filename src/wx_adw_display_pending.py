#wx_adw_display_pending.py  10Mar2024  crs  Author
import wx

from select_trace import SlTrace

"""
AudioDrawWindow display pending
Facilitate the construction of items to display and their display
Items of interest
    1. BrailleCells, initial and traversed
    2. Large lists of BrailleCells
    3. Cursor, indicator of current traversal position inside cell, outside cell
    4. Magnification Selection - rectangle surrounding region to magnify

User sets function to do actual item display
by calling set_display_fun(<user's item display function>)    
"""
            
class AdwDisplayPending:
    def __init__(self, canv_pan):
        """ pending display items
        :canv_pan: canvas panel (CanvPanel)
        """
        self.canv_pan = canv_pan
        self.disp_fun = None    # Set as user's item displaying function
        self.clear()

    def clear(self):
        """ Clear/initialize pending
        """
        self.items = []         # one-time list for update
        self.perm_items = {}    # permanent dictionary, by id, for redrawing
        self.prev_npending = None   # Track changes
                
    
    def add_item(self, item):
        """ Add display item
        :item: item/id (CanvasPanelItem)
        """
        if type(item) == int:
            itm = self.canv_pan.id_to_item(item)
        else:
            itm = item
        if type(itm) == int:
            SlTrace.lg("item: {item}")
        self.items.append(itm)
        self.add_perm_item(itm)
        ##self.canv_pan.refresh_item(itm)
        
    def add_perm_item(self, item):
        """ Add permanent item to support redrawing
        TBD handling item changes, overlay etc.
        
        :item: item to be added for redrawing
        """
        self.perm_items[item.canv_id] = item
        
    def add_cell(self, di_item):
        """ Add cell to be displayed
        :cell: display item (AdwDisplayPendingItem)
        """            
        self.add_item(di_item)
        
    def add_cursor(self, cursor):
        """ Add cell to be displayed
        :cell: BrailleCell
        """            
        self.add_item(cursor)
        
    def add_mag_sel(self, mag_sel):
        """ Add magnification selection to be displayed
        :mag_sel: magnification selection
        """            
        self.add_item(mag_sel)
        
    def add_cpan_item(self, cpan_item):
        """ Add cell to be displayed
        :cpan_item: CanvasPanelItem item to display
        """            
        self.add_item(cpan_item)

    def get_displayed_items(self):
        """ Get list of displayed items
        :returns: list of permanently displayed values (AdwDisplayPendingItem)
        """
        return self.perm_items.values()

    def is_overlapping(self, item1, item2):
        """ Check if two display items are overlapping
        :returns: True iff overlapping
        """
        
        
    def display_pending(self, dc):
        """ Display list and clear it
        :dc: wx.PaintDC(self)
        """
        if len(self.items) > 0:
            self.npending = len(self.items)
            
            color = self.canv_pan.color
            #dc = wx.PaintDC(self.canv_pan.grid_panel)
            dc.SetPen(wx.Pen(color))
            style = wx.SOLID
            dc.SetBrush(wx.Brush(color, style))
            if self.prev_npending is None or self.npending != self.prev_npending:
                SlTrace.lg(f"{self.npending} display_pending prev = {self.prev_npending}",
                           "display_pending")
                self.prev_npending = self.npending
            for diitem in self.items:
                self.display_item(diitem)
            #self.items = []     # Clear list
    
    def display_item(self, item):
        """ Display item
        :diitem: DisplayListItem item to display
        """
        if self.disp_fun:
            self.disp_fun(item)
            return
        self.draw_item(item)

    def draw_item(self, item):
        """ Draw item
        :item: CanvasPanalItem/canv_id item to draw
        """
        self.canv_pan.draw_item(item)
            
    def set_display_item_fun(self, disp_fun):
        """ Set display item function
        :disp_fun: display function for dispaly item
        """
        self.disp_fun = disp_fun
        