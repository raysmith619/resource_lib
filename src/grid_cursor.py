#grid_cursor.py    01Dec2022  crs
from _sqlite3 import Cursor
from grid_fill_gobble import cells

class GridCursor:
    """ Supports moving "cursor" wich can vary from one point
    to n-cell b y m-cell in size
    """
    
    def __init__(self, cells):
        """ Setup access to cells
        :cells: hash by ix,iy of cells (only keys used)
        """
        self.expanded = False   # True - cursor is expanded 
        self.ix_exp = None    # Expanded cursor, from ixy of cursor 
        self.iy_exp = None 
        self.ix_step = None     # Change per step 
        self.iy_step = None 
        
    def resize_cursor(self, key_cmd):
        """ Cursor resize
        :key_cmd: 1 - double in x direction, starting => 2N+1
                  2 - double in y direction
                  3 - double in both x and  y directions
                  4 - halve in x direction
                  5 - halve in y direction
                  6 - halve in both x and y direction
                not expanded => 5 -> 9 -> 17 ->31
        """
        if key_cmd in ['1','2','3']:
            if not self.expanded:
                self.expanded  = True
                self.ix_exp = .5
                self.iy_exo = .5
            if key_cmd == '1':
                self.ix_exp *= 2
            elif key_cmd == '2':
                self.iy_exp *= 2
            elif key_cmd == '3':
                self.ix_exp *= 2
                self.iy_exp *= 2
        else:
            if key_cmd == '4':
                self.ix_exp /= 2
            elif key_cmd == '5':
                self.iy_exp /= 2
            elif key_cmd == '6':
                self.ix_exp /= 2
                self.iy_exp /= 2
        if self.ix_exp <= 1 or self.iy_exp <= 1:
            self.expanded = False
        else:
            self.ix_step = self.ix_exp + 1   # half step
            self.iy_step = self.iy_exp + 1

    def contained_cells(self, ixy):
        """ Collect keys of cells within Cursor
        :ixy: ixy key of central Cursor
        :returns: list of contained cells ixy
        """
        ix,iy = ixy
        ix_min = ix - self.ix_exp
        ix_max = ix + self.ix_exp
        iy_min = iy - self.iy_exp
        iy_max = iy + self.iy_exp
        clist = []
        for ixc in range(ix_min, ix_max+1):
            for iyc in range(iy_min, iy_max+1):
                cxy = (ixc,iyc)
                if cxy in self.cells:
                    clist.append(cxy)
                    
        return clist