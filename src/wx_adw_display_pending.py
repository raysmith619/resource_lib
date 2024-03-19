#wx_adw_display_pending.py  10Mar2024  crs  Author
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
class AdwDisplayPendingItem:
    DI_CELL = 1         # BrailleCell
    DI_CURSOR = 2       # Cursor
    DI_MAG_SEL = 3      # Magnification selection
    DI_CPAN_ITEM = 4    # Canvas Panel item
    
    def __init__(self, ditype, item):
        self.ditype = ditype,
        self.item = item
        
class AdwDisplayPending:
    def __init__(self):
        self.items = []         # one-time list for update
        self.perm_items = {}    # permanent list, for redrawing
        self.disp_fun = None    # Set as user's item displaying function
        
    
    def add_item(self, ditype, item):
        """ Add display item
        :ditype: item type
        :item: item
        """
        di_item = AdwDisplayPendingItem(ditype, item)
        self.items.append(di_item)
        self.add_perm_item(item)
        
    def add_perm_item(self, item):
        """ Add permanent item to support redrawing
        TBD handling item changes, overlay etc.
        
        :di_item: item to be added for redrawing
        """
        self.perm_items[item.canv_id] = item
        
    def add_cell(self, cell):
        """ Add cell to be displayed
        :cell: BrailleCell
        """            
        self.add_item(AdwDisplayPendingItem.DI_CELL, cell)
        
    def add_cursor(self, cursor):
        """ Add cell to be displayed
        :cell: BrailleCell
        """            
        self.add_item(AdwDisplayPendingItem.DI_CURSOR, cursor)
        
    def add_mag_sel(self, mag_sel):
        """ Add magnification selection to be displayed
        :mag_sel: magnification selection
        """            
        self.add_item(AdwDisplayPendingItem.DI_MAG_SEL, mag_sel)
        
    def add_cpan_item(self, cpan_item):
        """ Add cell to be displayed
        :cpan_item: CanvasPanelItem item to display
        """            
        self.add_item(AdwDisplayPendingItem.DI_CPAN_ITEM, cpan_item)
    
    def display_pending(self):
        """ Display list and clear it
        """
        for diitem in self.items:
            self.display_item(diitem)
        self.items = []     # Clear list
    
    def display_item(self, diitem):
        """ Display item
        :diitem: DisplayListItem item to display
        """
        if self.disp_fun is None:
            SlTrace.lg("No DisplayList function for item")
            return
        
        self.disp_fun(diitem)
            
    def set_display_item_fun(self, disp_fun):
        """ Set display item function
        :disp_fun: display function for dispaly item
        """
        self.disp_fun = disp_fun
        