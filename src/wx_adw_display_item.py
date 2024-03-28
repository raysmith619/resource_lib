#wx_adw_display_item.py 21Mar2024  crs from wx_adw_display_pending.py
""" Display Item
"""
class AdwDisplayItem:
    DI_CELL = 1         # BrailleCell
    DI_CURSOR = 2       # Cursor
    DI_MAG_SEL = 3      # Magnification selection
    DI_CPAN_ITEM = 4    # Canvas Panel item
    
    def __init__(self, item):
        """ Pending display item
        :dpend: AdwDisplayPending instance
        :ditype: display item type
        :did: display id
        :item: display item/id
        """
        self.item = item

    def get_id(self):
        """ Get display id
        :returns: display item id
        """
        return self.item.did
