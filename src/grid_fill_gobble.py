# grid_fill_gobble.py    23Nov2022, crs
"""
Grid Fill Gobble Algorithm
First Algorithm: "gobble - keep adding 
all adjacent ungroupped cells to to check_group,
till no ungrouped adjacent cells can be added.

"""
from grid_rot import GridRot as GR

class GridFillGobble:

    def __init__(self, cells, excluded=None):
        """ Setup gobble strategy
        :cells: dictionary (only the keys are used here)
                of occupied cells
        :excluded: extra cell exclusion list
                    dictionary, only the keys are used
        """
        self.cells = cells
        if excluded is None:
            excluded = []
        self.excluded = excluded
        self.travel_list = []   # List of cells (ixy),
                                # traversal order
                                # reset in find_region
        
    def find_region(self, ixy):
        """ Find a list of occupied cells,
        from self.cells which start with ixy,
        which cover a connected region
        Hopefully we get a good traversal list.

        :ixy: (ix,iy) tuple for one enclosed cell
        :returns: list of (ix,iy) in traversal order
        """
        self.checking_cells = {} # of ixy
                            # where:
                            # ixy - cell xy
        self.travel_list = [] # List in traversal order
        self.add_ck_cell(ixy)
        while self.check_if_filled():
            pass
        return self.travel_list

    def check_if_filled(self):
        n_added = 0      # Sum added
        for cell in list(self.checking_cells):
            neighbors_added = self.check_cell_neighbors(
                                     cell)
            n_added += neighbors_added
        if n_added > 0:
            return True 
        
        return False

    def check_cell_neighbors(self, cell):
        """ Check cell's neighbors
        for possible adding to region
        For each neighbor, if appropriate
            Add it
        :cell: who's neighbors to check
        :returns: number of cells added
        """
        n_added = 0
        cell_ixy = cell
        for idir in range(len(GR.idirs)):
            cell_n = GR.next_cell(cell_ixy, idir)
            if self.is_cell_part(cell_n):
                self.add_ck_cell(cell_n)
                n_added += 1
        return n_added
        
    def is_cell_part(self, ixy):
        """ Check if location is suitable for new addition
        to region.
        :checking_cells: dictionary of cells checked or
                in line to be checked
        :ixy: cell ixy to be checked
        :excluded: cells to not be considered
        :returns: True iff to be added else False
        """
        if ixy in self.checking_cells:
            return False# Already covered
        
        if ixy in self.excluded:
            return False # excluded
        
        if ixy not in self.cells:
            return False # Part of figure
        
        return True

    def add_ck_cell(self, ixy):
        """ Add new cell to fill region
        Currently just ixy.  At sometime we might include
        additional information
        
        :ixy:  cell to be added
        """
        self.checking_cells[ixy] = ixy
        self.travel_list.append(ixy)

if __name__ == "__main__":
    print(f"Self Test: {__file__}")
    cells_set = {
            (2,6), (3,6), (4,6), (5,6), (6,6),
            (2,5),               (5,5),
            (2,4),               (5,4),
            (2,3), (3,3), (4,3), (5,3),
            (2,2), (3,2), (4,2), (5,2), (6,2),
         }
    cells = dict.fromkeys(cells_set, 0)
    start_cell = (2,2)
    grfill = GridFillGobble(cells=cells, excluded={(4,3)})
    travel_cells = grfill.find_region(start_cell)
    print("travel_cells:", travel_cells)
    travel_cells_order = {}  # by ixy order number
    order = 0
    for tc in travel_cells:
        order += 1
        travel_cells_order[tc] = order
    for irow in reversed(range(10)):
        for icol in range(10):
            tc = (icol,irow)
            if tc in travel_cells_order:
                order = travel_cells_order[tc]
                print(f"({icol},{irow})/{order:<2} ", end="")
            else:
                print(" "*14, end="")
        print()
