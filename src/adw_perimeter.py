# adw_perimeter.py    04Apr2023  crs, Author
"""
Create / Manipulate figure perimiters
"""
import re 

from select_trace import SlTrace
from braille_cell import BrailleCell 



class SurroundingSquare:
    """ A potential surrounding square
    """
    def __init__(self, ssqs, ixy, prev_square=None, next_square=None):
        self.ssqs = ssqs
        self.adwp = ssqs.adwp
        self.ixy = ixy
                                        # Traversal links
        self.prev_square = prev_square  # (SurroundingSquare)
        self.next_square = next_square  # (SurroundingSquare)

    def __str__(self):
        st = f"SurroundingSquare:{self.ixy}"
        return st 
    
    def expand_if_possible(self):
        """ move cell, expanding surrounding cells, if possible
        :returns: True if expansion made, else False
        """
        expansion_conn_spaces = self.get_expansion_conn_spaces()
        if len(expansion_conn_spaces) > 0:
            expansion_conn_space = expansion_conn_spaces[0]   # take highest prioity
            self.move_to_expansion(expansion_conn_space)
            return True 
        
        return False
        
     
    def get_expansion_conn_spaces(self):
        """ Get possible expansion spaces
        return expand_spaces
        :returns: list of (connectors,space_ixy)
        """
        return self.adwp.get_expansion_conn_spaces(ixy=self.ixy)

    def is_neighbor(self, sp_ixy):
        """ Check if square is our neighbor
            Could be out of bounds
        :sp_ixy: candidate's location tuple
        :returns: True iff a neighbor
        """
        n_ixys = self.get_n_ixys(ixy=sp_ixy)
        return self.ixy in n_ixys

    def move_to_expansion(self, conn_space):
        """ Adjust the self.ssqs.surounding squares to convert ixy
        square to surrounding and, possibly remove current square,
        placing it in the outside region
        FOR NOW we won't reduce, but rather let the reduction pass
        take care of that.
        WE, FOR NOW, assume one and only one connectors is
        flat with the expansion space
        :conn_space: (conns, space_ixy) tuple:
                        connected surrounding squares
                        candidate for expansion ixy
        """
        conns, space_ixy = conn_space
        sp_ix, sp_iy = space_ixy
        if len(conns) == 2:
            """ Inside space becomes new surrounding square
                adjacent to flat_conn
                NOTE we do not do any minimizing surrounding
                at this time.
            """
            
            prev_conn = conns[0]
            new_ssquare = SurroundingSquare(ssqs=self.ssqs, ixy=space_ixy)
            self.ssqs.insert_square(square=new_ssquare,
                                           after_ixy=prev_conn.ixy)
        elif len(conns) == 3:       # In the middle?
            prev_trav = conns[0]
            new_surr = SurroundingSquare(ssqs=self.ssqs, ixy=space_ixy)
            self.ssqs.insert_square(square=new_surr, after_ixy=prev_trav.ixy)
            """ NOTE: we do not do any minimizing surrounding at this time
            """

        
    """
    links to ssqs - SurroundingSquares
    """
       
    def get_square(self, ixy):
        """ Get (SurroundingSquare) at ixy
        :ixy: (ix,iy) location
        :returns: SurroundingSquare
        """
        return self.ssqs.squares[ixy]

        
    """
    links to adwp
    """

    def get_n_ixys(self,ixy=None):
        """ Get neighboring index (ixy) pairs
        :ixy: middle index pair
        :returns: list of (ixy) surrounding ixy
        """
        if ixy is None:
            ixy = self.ixy
        return self.adwp.get_n_ixys(ixy=ixy)
    
    def get_inside_space_neighbors(self, ixy=None):
        """ Get neighbor space squares
        :ixy: square ix,iy tuple
                default: our ixy
        :returns: list of neighboring spaces
        """
        if ixy is None:
            ixy = self.ixy
        return self.adwp.get_inside_space_neighbors(ixy=ixy)
    
    def is_inside(self, ixy=None):
        """ Check if square(ixy) is in outside region
        :ixy: square ix,iy tuple
                default: our ixy
        """
        if ixy is None:
            ixy = self.ixy
        return self.adwp.is_inside(ixy=ixy)

    def is_outside(self, ixy=None):
        """ Check if square(ixy) is in outside region
        :ixy: square ix,iy tuple
                default: our ixy
        """
        if ixy is None:
            ixy = self.ixy
        return self.adwp.is_outside(ixy=ixy)

    def is_surrounding(self, ixy=None):
        """ Check if square(ixy) is in surrounding region
        :ixy: square ix,iy tuple
                default: our square
        """
        if ixy is None:
            ixy = self.ixy
        return self.adwp.is_surrounding(ixy=ixy)
    
    def reduce_extra(self, ixy=None):
        """ Reduce cell if not necessary for surrounding,
        by making it an outside
        :ixy: ix,iy tuple
                default: self
        :returns: True iff reduced
        """
        if ixy is None:
            ixy = self.ixy
        return self.adwp.reduce_extra(ixy=ixy)
        
    def remove_surrounding_square(self, ixy=None, square=None):
        """ remove ixy or move square
            ONLY ixy for new or square for moved
        :ixy: (ixy) ixy of square
        :square: (SurroundingSquare) moved square
        :returns: removed square
        """
        return self.adwp.remove_surrounding_square(ixy=ixy, square=square)

class SurroundingSquares:
    """ Holder of list of squares empty or not, e.g. outside, surrounding
    This can be used to manipulate surrounding regions and perimeters of
    a figure.
    Primary data components are:
        1. dictionary, by ixy, of squares
        2. traversal list made up of:
            a. starting_ixy
            b. doublely linked list contained in the
                SurroundingSquare entry
                    before_ixy - refering  to the previous SurroundingSquare
                    after_ixy - revering to the following SurroundingSquare

    """
    def __init__(self, adwp, cells=None):
        """ Setup
        :adwp: AdwPerimeter instance
        :cells: dictionary of cells or list with .ix,.iy
            default: use self.cells
            if list (with elements having .ix,.iy) create
            dictionary by (ix,iy)
        """
        self.adwp = adwp
        if cells is None:
            cells = self.cells
        if isinstance(cells, list):
            cdict = {}
            for cell in cells:
                ixy = (cell.ix,cell.iy)
                cdict[ixy] = cell
            cells = cdict
        self.cells = cells
        self.squares = {}               # Dictionary by ix,iy
                                        # Links for traversal
        self.first_square = None        # First (SurroundSquare)
        
    def add_square(self, ixy=None, square=None):
        """ Add/Create ixy or move square
            ONLY ixy for new or square for moved
        :ixy: (ixy) ixy of new square
        :square: (SurroundingSquare) moved square
        """
        if ixy is None and square is None:
            raise Exception("One of ixy or square is Required") 
        if ixy is not None and square is not None:
            raise Exception("Including BOTH ixy and square")
        
        if ixy is not None: 
            ssq = SurroundingSquare(ssqs=self, ixy=ixy)
        elif square is not None:
            ssq = square
        self.insert_square(square=ssq)
       
    def insert_square(self, square, after_ixy=None):
        """ Insert square
        :square: (SurroundingSquare) to insert
        :afer_ixy:  tuple, after which we insert
                    default: insert at end of list
        """
        
        self.squares[square.ixy] = square
        if self.first_square is None:
            self.first_square = square  # Just store it
            return
        
        if after_ixy is None:
            after_square = self.first_square
            next_square = after_square
            while next_square is not None:
                after_square = next_square
                next_square = after_square.next_square
        else:
            after_square = self.get_square(ixy=after_ixy)
        if after_square is None:
            self.first_square = square
            prev_square = next_square = None
        else:
            prev_square = after_square
            next_square = after_square.next_square
            square.prev_square = prev_square
            square.next_square = next_square            
        if prev_square is not None:
            prev_square.next_square = square
        if next_square is not None:
            next_square.prev_square = square
        
    def remove_square(self, ixy=None, square=None):
        """ remove ixy or move square
            ONLY ixy for new or square for moved
            NOTE we relink previous neighbors
        :ixy: (ixy) ixy of square
        :square: (SurroundingSquare) moved square
        :returns: removed square
        """
        if ixy is None and square is None:
            raise Exception("One of ixy or square is Required") 
        if ixy is not None and square is not None:
            raise Exception("Including BOTH ixy and square")
        
        if ixy is not None: 
            ssq = self.squares[ixy]
        elif square is not None:
            ixy = square.ixy
            ssq = square            # return given square
            
        del self.squares[ixy]
        # Update linking references
        prev_square = ssq.prev_square
        next_square = ssq.next_square
        if prev_square is not None:
            prev_square.next_square = next_square
        if next_square is not None:
            next_square.prev_square = prev_square            
        return ssq
        
    def get_square(self, ixy):
        """ Get (SurroundingSquare) at ixy
        :ixy: (ix,iy) location
        :returns: SurroundingSquare if present else None
        """
        if ixy in self.squares:
            return self.squares[ixy]
        
        return None

    def get_squares_list(self):
        """ list of SurroundingSquare in traversal order
        :return: list of (SurroundingSquare)
        """
        squares_list = []
        ssq = self.first_square
        while ssq is not None:
            squares_list.append(ssq)
            ssq = ssq.next_square
            
        return squares_list
        
    def get_squares_as_cells(self, color=None):
        """ Return cell dictionary by ix,iy
        :color: cell color default: keep color of cell, else "x" if emptyl
        :returns: cell (BrailleCell) dictionary
        """
        cells = {}
        for sq_ixy in self.squares:
            if sq_ixy in self.cells:
                cell = self.cells[sq_ixy]
                if color is not None:
                    cell.color = color
            else:
                ix,iy = sq_ixy
                if color is None:
                    color = "x"
                cell = BrailleCell(ix=ix, iy=iy, color=color)
            cells[sq_ixy] = cell
        return cells

    def is_part (self, ixy):
        """ Check if square(ixy) is part of this region
        :ixy: square ix,iy tuple
        :returns: True if ixy is part of this region
        """
        is_part = ixy in self.squares
        return is_part

    
class AdwPerimeter:
    
    def __init__(self, adw, cells=None):
        """ Setup for perimeter calculation 
        :adw: Acces to AudioDrawWindow
        :cells: list/dictionary of BrailleCell by (ixy)
                default: adw cells (adw.get_cells()
        """
        self.adw = adw
        if cells is None:
            cells = self.get_cells()
        else:
            if isinstance(cells, list):
                cdict = {}
                for cell in cells:
                    cdict[(cell.ix,cell.iy)] = cell
                cells = cdict
        self.cells = cells
        
    def get_perimeter(self):
        """ Get perimeter list of cells
        Starts with:
            1. a rectangular region, labeled outside, of empty squares 2 squares
            outside the bounding box 2. a rectangular region, labeled
            surrounding, of empty squares 1 square outside the bounding box 3. a
            rectangular region, laveled inside, of all the squares within the
            bounding box
            
        The surrounding region squares are repeatedly traversed, resetting
        adjacent inside empty squares to surrounding squares and surrounding
        squares to outside squares so as to closely surround all remaining non-
        space inside squares as surrounding squares.
            
        When no more inside empty squares can be converted to surrounding,
        the perimeter consists of the non-empty inside squares adjacent to
        the surrounding squares.
             
        :returns: list of cells(BrailleCell) which is the perimeter of the figure             
        """
        surrounding,outside = self.get_surroundings()
        self.surrounding = surrounding
        self.outside = outside
        loop_count = 0
        while True:
            loop_count += 1
            self.print_text(title=f"get_perimetr loop {loop_count}")
            # Minimize surrounding squares to one square thick
            minimize_loop_count = 0
            while True:
                minimize_loop_count += 1
                self.print_text(
                    title=f"minimize loop {minimize_loop_count}")
                minimize_count = 0
                ssquare_list = self.surrounding.get_squares_list()
                for ssquare in ssquare_list:
                    if ssquare.reduce_extra():
                        minimize_count += 1
                if minimize_count == 0:
                    break           # No improvement - quit minimization
                
            ssquare_list = self.surrounding.get_squares_list()
            new_count = 0
            for ssquare in ssquare_list:
                SlTrace.lg(f"sq: {ssquare.ixy}", "track_perimeter")
                if ssquare.expand_if_possible():
                    new_count += 1
            if new_count == 0:
                break           # No more expansion

        ssquare_list = self.surrounding.get_squares_list()
        if SlTrace.trace("ssquare_list"):
            st = ""
            for ssquare in ssquare_list:
                st += f" {ssquare}"
            SlTrace.lg("ssquare list - closest surrounding squares")
            SlTrace.lg(st)
            
        perimeter_cell_list = self.surrounding_to_perimeter(ssquare_list)
        if SlTrace.trace("ssquare_list"):
            st = ""
            for cell in perimeter_cell_list:
                st += f" {cell.pi_number}: {cell}"
            SlTrace.lg("perimeter cell list")
            SlTrace.lg(st)
        
        return perimeter_cell_list

    def surrounding_to_perimeter(self, ssquares):
        """ Given surrounding, a list of SurroundingSquare adjacent to
         get adjacent cells
        :ssquares: list of SurroundingSquares
        :returns: list of cells in traversal order
                Sets perimeter cells
                         pi_number=position number
                         pi_type = "p"
        """
        cells = self.get_cells()
        cells_used = {}
        perimeter_poss = []     # Possible squares for each possition
        for ssquare in ssquares:
            SlTrace.lg(f"ssquare: {ssquare.ixy}", "ssquares_list")
            poss_for_sq = {}
            st = ""
            for cell in self.get_cell_neighbors(ssquare.ixy):
                ixy = (cell.ix,cell.iy)
                poss_for_sq[ixy] = cell
                st += f" {cell}"
            SlTrace.lg(f"    poss: {st}", "ssquares_list")
            perimeter_poss.append(poss_for_sq)
        cell_list = []
        
        pi_number = 0           # incremented to traversal position
        for sq_p in perimeter_poss:
            for cell_ixy in sq_p:
                if cell_ixy not in cells_used:
                    cell = cells[cell_ixy]
                    pi_number += 1
                    cell.pi_number = pi_number
                    cell.pi_type = "p"
                    cell_list.append(cell)
                    cells_used[cell_ixy] = cell_ixy
                    break
        return cell_list        
        
    def get_surroundings(self):
        """ create one square thick surrounding square list plus an adjacent
        a surrounding set of outside squares to aid "directing" movement away
        form the outside squares toward the inside squares

        It is assumed that the figure of non-space squares is at least
        two cells within the display limits.  If not the outer two squares
        will be treated as empty.

        :returns: tuple (
                surrounding empty squaress (SurroundingSquares),
                
                outside_squares (SurroundingSquares)
                    of squares encompasing  the surrounding
                    empty squares returned
                )
                ALSO sets figure boundary, plus edge:
                    self.ix_min, self.iy.min
                    self.ix_max, self.iy_max
        """
        # edge of 2:
        #            outer: encompassing outside squares
        #            inner: starting list of surrounding squares
         
        ix_min,iy_min, ix_max,iy_max = self.bounding_box_ci(
                        cells=self.cells, add_edge=2)
        self.ix_min = ix_min
        self.iy_min = iy_min
        self.ix_max = ix_max
        self.iy_max = iy_max
        surrounding = SurroundingSquares(adwp=self, cells=self.cells)
        outside = SurroundingSquares(adwp=self, cells=self.cells)
        # top edge outside
        iy = iy_min
        for ix in range(ix_min, ix_max+1):
            ixy = (ix,iy)
            outside.add_square(ixy)
        # top edge surrounding
        iy = iy_min+1
        for ix in range(ix_min+1, ix_max):
            ixy = (ix,iy)
            surrounding.add_square(ixy)
            
        # right edge outside
        ix = ix_max
        for iy in range(iy_min, iy_max+1):
            ixy = (ix,iy) 
            outside.add_square(ixy)
        # right edge surrounding
        ix = ix_max-1
        for iy in range(iy_min+1, iy_max):
            ixy = (ix,iy) 
            surrounding.add_square(ixy)
                            
        # bottom edge outside
        iy = iy_max
        for ix in range(ix_max, ix_min-1, -1):
            ixy = (ix,iy)
            outside.add_square(ixy)
        # bottom edge surrounding
        iy = iy_max-1
        for ix in range(ix_max-1, ix_min, -1):
            ixy = (ix,iy)
            surrounding.add_square(ixy)
            
        # left edge outside
        ix = ix_min
        for iy in range(iy_max, iy_min-1, -1):
            ixy = (ix,iy) 
            outside.add_square(ixy)
        # left edge surrounding
        ix = ix_min+1
        for iy in range(iy_max-1, iy_min, -1):
            ixy = (ix,iy) 
            surrounding.add_square(ixy)
        
        return (surrounding, outside)
           
    def get_start_cell(self):
        """ Get starting cell
        :returns: BrailleCell at leftest cell at lowest row 
        """
        ix_min,iy_min, ix_max,iy_max = self.bounding_box_ci(cells=self.cells)
        for ix in reversed(range(ix_min, ix_max+1)):
            ixy = (ix-1,iy_min) 
            if self.is_space(ixy):
                break       # ixy is left most  
        
        return self.get_cell_at_ixy(cell_ixy=ixy)

    def get_cell(self, ixy, cells=None):
        """ Get cell(BrailleCell) at (ixy) if one else None
        :ixy: ix,iy pair
        :cells: cells to search default: self.cells
        :returns: BrailleCell iff one else None
        """
        if cells is None:
            cells = self.cells
        return self.get_cell_at_ixy(cell_ixy=ixy, cells=cells)


    def is_outside(self, ixy):
        """ Check if square(ixy) is in outside region
        :ixy: square ix,iy tuple
        """
        return self.outside.is_part(ixy=ixy)

    def is_inside(self, ixy):
        """ Check if square(ixy) is inside figure
        that is within figure boundaries and not is_outside()
        and not is_surrounding()
        :ixy: square ix,iy tuple
        :returns: True iff inside else False
        """
        if not self.is_in_figure_boundary(ixy=ixy):
            return False

        if self.is_surrounding(ixy=ixy):
            return False 
        
        if self.is_outside(ixy=ixy):
            return False 
        
        return True

    def is_in_figure_boundary(self, ixy):
        """ Check if within bounding rectangle + edge
        of most recent get_surrounding() call
        :ixy: ix,iy tuple
        :returns: True if within bounding rectangle
        """
        ix,iy = ixy
        if ix < self.ix_min:
            return False 
        
        if ix > self.ix_max:
            return False 
        
        if iy < self.iy_min:
            return False 
        
        if iy > self.iy_max:
            return False 
        
        return True
        
    def is_surrounding(self, ixy):
        """ Check if square(ixy) is surrounding region
        :ixy: square ix,iy tuple
        """
        return self.surrounding.is_part(ixy=ixy)
        
    def is_touching_inside(self, ixy):
        """ Check if square(ixy) is next to inside
        :ixy: square ix,iy tuple
        """
        for n_ixy in self.get_n_ixys(ixy=ixy):
            if self.is_inside(n_ixy):
                return True
        
    def is_touching_outside(self, ixy):
        """ Check if square(ixy) is next to outside
        :ixy: square ix,iy tuple
        """
        for n_ixy in self.get_n_ixys(ixy=ixy):
            if self.is_outside(n_ixy):
                return True
                

    def add_edge_cell(self, ixy):
        """ Add edge cell to dictionary
        :ixy: ixy coordinate
        """
        cell = self.get_cell_at_ixy(cell_ixy=ixy)
        self.edge_cells[ixy] = cell
        
        
        
    def get_cell_neighbors(self, ixy):
        """ get neighbors that are non-empty cells
        :ixy: (ix,iy) cell index
        :returns: list of BrailleCell
        """
        ngh_ixys = self.get_n_ixys(ixy=ixy)
        ngh_cells = []
        for ixy in ngh_ixys:
            cell = self.get_cell_at_ixy(ixy)
            if cell is not None:
                 ngh_cells.append(cell)
        return ngh_cells

     
    def get_expansion_conn_spaces(self, ixy):
        """ Get possible expansion spaces for surrounding square
        To be a candidate surrounding space, we must have two concecutive
        surrounding spaces between which this candidate may be inserted
        to maintain a connected string of surrounding squares
        
        :ixy: our location tuple
        :returns: list of (surrounding connectors, inside space)
        Must be:
            1. adjacent (touching us)
            2. inside
            3. Have our adjacent surrounding neighbors as neighbors.
        That is this expansion must not break the chain
        of surrounding squares
        [s1]   [i]    2 conn neighbors =>  [s1]  [s1-s2] new surrounding
        *s2*]  [ ]                         *s2*  [ ]    
        [s3]   [ ]                         [s3]  [ ]

        [s1]  [ ]                          [s1]  [ ]
        *s2*  [i]    3 conn neighbors =>   *o*   [s1-s3] s2 at new location    
        [s3]  [ ]                          [s3]  [ ]

        [s1]  [ ]                          [s1]  [ ]
        *s2*  [ ]                          *s2*  [ ]    
        [s3]  [i]    2 conn neighbors =>   [s3]  [s2-s3] new surrounding

        :returns: list of possible expansion spaces [(cons, sp_ixy),...]
        decreasing probability
        NO prioritization yet TBD
        """
        
        inside_neighbors = self.get_inside_space_neighbors(ixy=ixy)
        if len(inside_neighbors) == 0:
            return []
        
        expand_spaces = []
        our_connectors = self.get_surrounding_connectors(ixy=ixy)
        st = [str(s) for s in our_connectors]
        SlTrace.lg(f"our_connectors:{st}")
        for sp_ixy in inside_neighbors:
            if True:
                SlTrace.lg(f"expansion_space:{sp_ixy}")
                self.print_text(marker_ixy=sp_ixy)
            conn_neighbors = []
            for conn in our_connectors:
                if conn.is_neighbor(sp_ixy):
                    conn_neighbors.append(conn)
            if len(conn_neighbors) > 1:
                expand_spaces.append((conn_neighbors,sp_ixy)) 
        return expand_spaces

    def get_surrounding_connectors(self, ixy):
        """ Get connecting (part of the chain)of which we are apart
        including our self (1,2, or 3)
        :ixy: ix,iy tuple  default: our ixy
        :returns: list of squares of connectors
        """
        conns = []
        square = self.surrounding.get_square(ixy=ixy)
        neighbors = [square.prev_square, square, square.next_square]
        for neighbor in neighbors:
            if neighbor is not None:
                if neighbor.is_surrounding():
                    conns.append(neighbor)
                
        return conns

    def insert_surrounding_square(self, square, after_ixy=None):
        """ Insert square into surrounding
        :square: (SurroundingSquare) to insert
        :afer_ixy:  tuple, after which we insert
                    default: insert at end of list
        """
        self.surrounding.insert_square(square=square,
                                        after_ixy=after_ixy)

        
    def remove_surrounding_square(self, ixy=None, square=None):
        """ remove ixy or move square
            ONLY ixy for new or square for moved
        :ixy: (ixy) ixy of square
        :square: (SurroundingSquare) moved square
        :returns: removed square
        """
        return self.surrounding.remove_square(ixy=ixy, square=square)

        
    def get_inside_space_neighbors(self, ixy):
        """ get neighbors that are non-empty cells
        :ixy: (ix,iy) cell index
        :returns: list of (ix,iy)  tuples which are empty spaces
        """
        ngh_ixys = self.get_n_ixys(ixy=ixy)
        ngh_spaces = []
        for ngh_ixy in ngh_ixys:
            if self.is_inside(ngh_ixy):
                cell = self.get_cell_at_ixy(ngh_ixy)
                if cell is None:
                    ngh_spaces.append(ngh_ixy)
        return ngh_spaces

    def get_n_ixys(self,ixy):
        """ Get neighboring index (ixy) pairs
        :ixy: middle index pair
        :returns: list of (ixy) surrounding ixy
        """
        nixys = []
        ix_m,iy_m = ixy
        for ix in range(-1,2):
            for iy in range(-1,2):
                if ix != 0 or iy != 0:
                    ix_s = ix_m + ix
                    iy_s = iy_m + iy
                    nixys.append((ix_s, iy_s))
        return nixys

        
    def get_text(self, cells=None, shift_to_edge=None, blank_char= ",",
                 marker_ixy=None, marker=None, marker_space=".",
                 cell_nch=4):
        """ get text picture for braille display from regions.
        This function was adapted from get_text member in BrailleCellText.
        :shift_to_edge: shift figure towards edge to ease finding figure
                        default: self.shift_to_edge
        :blank_char: convert leading blanks to this
                    default: ","
        :marker_ixy: ixy tuple to mark default: No marking
        :marker: Type marking
                "uppercase" - uppercase the expected character
                ONE char - e.g. X - use this character
                default: "uppercase"
        :marker_space: Marker for space default: "."
        :cell_nch: Number of characters per cell default: 1
        """
        if cells is None:
            cells = self.get_cells()
        if shift_to_edge is None:
            shift_to_edge = True
        self.blank_char = blank_char
        left_edge, top_edge, right_edge, bottom_edge =self.bounding_box_ci(
            cells=cells, add_edge=2)
        
        if not shift_to_edge:
            left_edge = 0
            top_edge = 0

        braille_text = ""
        for iy in range(top_edge, bottom_edge+1):
            line = ""
            for ix in range(left_edge, right_edge+1):
                cell_ixy = (ix,iy)
                if cell_ixy in cells:
                    cell = self.cells[cell_ixy]
                    color = cell.color_string()
                    mark = color[0]
                elif self.is_outside(cell_ixy):
                    mark = "-"      # Outside
                    if  marker_ixy == cell_ixy:
                        mark = marker_space
                elif self.is_surrounding(cell_ixy):
                    mark = "+"
                elif self.is_inside(cell_ixy):
                    mark = ":"
                else:
                    mark = '@'      # Other
                if cell_ixy == marker_ixy:
                    if mark == " ":
                        mark = marker_space
                    elif mark in BrailleCell.color_for_character:
                         mark.upper()
                    elif mark in "-+:":
                        mark = f"[{mark}]"
                    else:
                        mark = mark[0]
                if len(mark) == 1 and cell_nch > 1 and mark[0] != "[]":
                    mark *= cell_nch
                while len(mark) < cell_nch:
                    mark += "_"

                line += mark
            line = line.rstrip()
            if self.blank_char != " ":
                line = line.replace(" ", self.blank_char)
            ###print(f"{iy:2}", end=":")
            if not re.match(r"^\s*$", line):
                braille_text += line + "\n"
        return braille_text
    
    def print_text(self, title=None,
                   shift_to_edge=None, blank_char= ",",
                 marker_ixy=None, marker=None, marker_space="."):
        """ Print out (to log) text rendition
        :title: optional title default: no title
        :shift_to_edge: shift figure towards edge to ease finding figure
                        default: self.shift_to_edge
        :blank_char: convert leading blanks to this
                    default: ","
        :marker_ixy: ixy tuple to mark default: No marking
        :marker: Type marking
                "uppercase" - uppercase the expected character
                ONE char - e.g. X - use this character
                default: "uppercase"
        :marker_space: Marker for space default: "."
        """
        if title is None:
            title = ""
        SlTrace.lg(f"\n{title}")
        text = self.get_text(shift_to_edge=shift_to_edge,
                              blank_char= blank_char,
                              marker_ixy=marker_ixy, marker=marker,
                              marker_space=marker_space)
        SlTrace.lg(f"\n{text}")
        pass
    
    
    def reduce_extra(self, ixy):
        """ Reduce cell if not necessary for surrounding,
        by making it an outside
        :ixy: ix,iy tuple
                default: REQUIRED
        :returns: True iff reduced
        """
        if not self.is_surrounding(ixy=ixy):
            return False 
        
        if not self.is_touching_outside(ixy=ixy):
            return False
        
        if self.is_touching_inside(ixy=ixy):
            return False
        
        ssquare = self.remove_surrounding_square(ixy=ixy)
        self.outside.add_square(square=ssquare)
        return True
    
    def set_cell_ip_type(self, ixy=None, square=None, type=None):
        """ Set/clear perimeter type
        One and only one of cell_ixy, sauare is allowed
        :cell_ixy: cell ix,iy tuple
        :square: SurroundingSquare 
        :type: perimeter type i - inside, o - outside, p - perimeter
        """
        assert not (cell_ixy is None and square is None), "One must be here"
        assert not (cell_ixy is not None and square is not None), "Only one"
        if cell_ixy is None:
            cell_ixy = square.ixy
        cell = self.get_cell(cell_ixy)
        cell.ip_type = type
        
    """
    ############################################################
                       Links to adw
    ############################################################
    """

    def annotate_cell(self, cell_ixy=None, color=None,
                      outline="blue", outline_width=2,
                      text=None):
        """ Annotate cell to highlight it
        Possibly for perimeter viewing
        :cell_xy: ix,iy tuple default: current location
        :color: rectangle color default: no fill
        :outline: add outline color
                    default: no special outline
        :outline_width: outline width
                    default: 2
        :text: added text default: no text added
        """
        self.adw.annotate_cell(cell_ixy=cell_ixy,
                               color=color, outline=outline,
                               outline_width=outline_width,
                               text=text)
    
    def bounding_box_ci(self, cells=None, add_edge=None):
        """ cell indexes which bound the list of cells
        :cells: list of cells, (with cell.ix,cell.iy) or (ix,iy) tuples
                default: list of all cells in figure
        :add_edge: number of cells to add/subtract (if possible)
                     to enlarge/shrink box
                    default: no change
        :returns: 
                    None,None,None,None if no figure
                    upper left ix,iy  lower right ix,iy
                    that is ix_min,iy_min, ix_max,iy_max
        """
        return self.adw.bounding_box_ci(cells=cells, add_edge=add_edge)


    def find_edges(self):
        """Find  top, left, bottom, right non-blank edges
        so we can shift picture to left,top for easier
        recognition
        :returns: left_edge, top_edge, right_edge, bottom_edge
                    Also sets self.left_edge,...
        """
        return self.adw.find_edges()
    
            
    def get_cell_at_ixy(self, cell_ixy, cells=None):
        """ Get cell at (ix,iy), if one
        :cells: dictionary of cells by (ix,iy)
                default: self.get_cells()
        :cell_ixy: (ix,iy)
        :returns: BrailleCell if one, else None
        """
        return self.adw.get_cell_at_ixy(cell_ixy=cell_ixy, cells=cells)
    
            
    def get_ix_min(self):
        """ get minimum ix on grid
        :returns: min ix
        """
        return self.adw.get_ix_min()

    def get_ix_max(self):
        """ get maximum ix on grid
        :returns: max ix
        """
        return self.adw.get_ix_max()

    def get_iy_min(self):
        """ get minimum iy on grid
        :returns: min iy
        """
        return self.adw.get_iy_min()

    def get_iy_max(self):
        """ get maximum ix on grid
        :returns: max iy
        """
        return self.adw.get_iy_max()

    def get_cells(self):
        """ Get cell dictionary (by (ix,iy)
        """
        return self.adw.get_cells()
    
    def is_space(self, ixy=None):
        """ Are we at a space
        :ixy: cell ix,iy indexes 
        :returns: True if a space (not a cell) 
        """
        return self.adw.is_space(ixy=ixy)
    
    
if __name__ == "__main__":
    from braille_cell_text import BrailleCellText
    from audio_draw_window import AudioDrawWindow
    
    ts1_str = """
    
     rrr 
    ooooo
     ggg
     
"""
     
    ts2_str = """
    
    
    
                        r 
                       rrr
                       rrr 
                       rrr
                ooooooooryyyyyyyyy
                ooooooooryyyyyyyyy
                       ggg 
                       ggg
                       ggg
                        g
                        
                         
    """
    
    ts3_str = """
     
,,,,,,,,,,,iii
,,,,,,,,,,iiiii
,,,,,,,,,,iiiii,,,,,,vvv
,,,,,,,,,,iiiii,,,,,vvvvv
,,,,,,,,,,,,ii,,,,,,vvvvv
,,,bb,,,,,,,,i,,,,,,vvvvv
,,bbbbb,,,,,,i,,,,,vv
,,bbbbb,,,,,,i,,,,vv
,,bbbbbbb,,,,ii,,vv
,,,,,,,,bbbb,,i,vv,,,,,,,,rr
,,,,,,,,,,bbbbivv,,,,,,,,rrrr
,,,,,,,,,,,,,bvvrrrrrrrrrrrrr
,,,,,,,,,,ggggyoo,,,,,,,,rrrr
,,,,,,,,gggg,,y,oo,,,,,,,,rr
,,ggggggg,,,,yy,,oo
,,ggggg,,,,,,y,,,,oo
,,ggggg,,,,,,y,,,,,oo
,,,gg,,,,,,,,y,,,,,,ooooo
,,,,,,,,,,,,yy,,,,,,ooooo
,,,,,,,,,,yyyyy,,,,,ooooo
,,,,,,,,,,yyyyy,,,,,,ooo
,,,,,,,,,,yyyyy
,,,,,,,,,,,yyy
"""

    ts4_str = """
,,ggrrrrrro
,,ggrrrrrro
,,ggrrrrrro
,,gg,,,,,,o
,,gg,,,,,,o
,,gg,,,,,,o
,,gg,,,,,,o
,,ggyyyyyyy
,,ggyyyyyyy
"""
    adw = None
    test_it_num = 0
    def test_it(figure_str, desc=None):
        """ Test figure producing perimeter
        :figure_str: figure text string
        :desc: test decription default: generated
        """
        global adw
        global test_it_num
        cell_nch = 4
        test_it_num += 1
        if desc is None:
            desc = ""
        title = f"{desc} test: {test_it_num}"
        adw = AudioDrawWindow(title=title)
        SlTrace.lg(f"\n{title}")
        bct = BrailleCellText(text=figure_str, cell_nch=4)
        cells = bct.get_cells()
        adw.draw_cells(cells=cells)
        SlTrace.lg("\nOriginal Figure")
        bct.print_text()
        figure_cells = bct.get_cells()    # Avoiding origin change
        ssq = AdwPerimeter(adw)
        perimeter_cells = ssq.get_perimeter()
        perim_num = 0
        for cell in perimeter_cells:
            perim_num += 1
            ssq.annotate_cell(cell_ixy=(cell.ix,cell.iy))
            
        
        for pcell in perimeter_cells:
            pcell_ixy = (pcell.ix,pcell.iy)
            pcolor = pcell.color_string().upper()
            pcell.color = "violet"
            figure_cells[pcell_ixy] = pcell
        pp_bct = BrailleCellText(cells=figure_cells, cell_nch=cell_nch)
        pp_bct_text = pp_bct.get_text()
        SlTrace.lg(f"With perimeter accented")
        SlTrace.lg(pp_bct_text)
        
    SlTrace.clearFlags()
    #test_it(figure_str=ts1_str, desc="simplest")    
    test_it(figure_str=ts2_str, desc="colored cross")    
    test_it(figure_str=ts3_str, desc="spokes")    
    test_it(figure_str=ts4_str, desc="square colors")    

    adw.mainloop()          # To keep AudioDrawWindow responsive
