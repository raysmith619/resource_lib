# dots_shadow.py
"""
Support for shadow dots game board - logical function of the game without display
"""
import numpy as np

from select_error import SelectError
from select_edge import SelectEdge
from select_region import SelectRegion
from matplotlib.mlab import dist
import random    

"""
Dots Square / Edge numbering
Squares are numbered row, col starting at 1,1 in upper left
Edges, bordering a square are numbered as follows:

    Lve_row = sq_row          (Left vertical edge)
    Lve_col = sq_col
    
    Rve_row = sq_row          (Right vertical edge)
    Rve_col = sq_col + 1
     
    The_row = sq_row          (Top horizontal edge)
    The_col = sq_col
    
    Bhe_row = sq_row + 1      (Botom horizontal edge)
    Bhe_col = sq_col

"""
class MoveList:
    """ List of moves (edge specifications) which can be efficiently manipulated
    """
    def __init__(self, shadow, max_move=None, moves=None):
        """ Setup list
        :shadow:  Playing shadow data control
        :max_move: Maximum number of moves
        :list: if present, initialize list
        """
        self.shadow = shadow
        if max_move is None:
            if moves is not None:
                max_move = len(moves)
            else:
                max_move = 225
        self.moves = np.zeros([max_move, 3], dtype=int)     #  [row, col, hv(0-horizontal, 1-vertical]
        self.nmove = 0                          # Empty
        if moves is not None:
            for i, mv in enumerate(moves):
                hv = 0 if mv.sub_type() == 'h' else 1
                self.moves[i, 0] = mv.row
                self.moves[i, 1] = mv.col
                self.moves[i, 2] = hv
            self.nmove = len(moves)


    def add_move(self, move):
        """ Add move (tuple) to move list
        Currently no check or handling for overflow
        :move: move (tuple) to add
        """
        for i, mval in enumerate(move):
            self.moves[self.nmove, i] = mval
        self.nmove += 1
            
    
    def number(self):
        """ Get number in list
        :returns: number in list
        """
        return self.nmove
    
    
    def rand_move(self):
        """ Get random list entry
        """
        ir = random.randint(0,self.nmove-1)
        return (self.moves[ir,0], self.moves[ir,1], self.moves[ir,2])
    
    
    def rand_obj(self):
        """ Get random list entry object e.g. edge
        """
        irt = self.rand_move()
        obj = self.shadow.lines_obj[irt]
        return obj


    def list_moves(self):
        """ Provide python list of moves
        """
        moves = []
        for i in range(self.nmove):
            row = self.moves[i,0]
            col = self.moves[i,1]
            hv = self.moves[i,2]
            move = self.shadow.get_edge(row, col, hv)
            moves.append(move)
        return moves
            
            
class DotsShadow:
    """ Shadow of Dots structure to facilitate testing speed when display is not required
    """
    def __init__(self, select_dots, nrows=None, ncols=None):
        self.select_dots = select_dots
        self.nrows = nrows
        self.ncols = ncols
        self.squares = np.zeros([nrows, ncols])
        self.lines = np.zeros([nrows+1, ncols+1, 2])     # row, col, [horiz=0, vert=1]

        self.squares_obj =  np.zeros([nrows, ncols], dtype=SelectRegion)
        self.lines_obj = np.zeros([nrows+1, ncols+1, 2], dtype=SelectEdge)     # row, col, [horiz=0, vert=1]
        self.nopen_line = 2*nrows*ncols + nrows + ncols


    def get_legal_moves(self):
        """ Return list of legal moves
        :give_edges: True retun list of edges (legacy values)
        :returns: list of moves(MoveList)
        """
        legals = MoveList(self, max_move=None)
        for ir in range(0, self.nrows+1):
            for ic in range(0, self.ncols+1):
                if ic < self.ncols:
                    if self.lines[ir, ic, 0] == 0:
                        legals.add_move((ir, ic, 0))    # Horizontal till last
                
                if ir < self.nrows:
                    if self.lines[ir, ic, 1] == 0:
                        legals.add_move((ir, ic, 1))    # Vertical till last row
        return legals


    def get_num_legal_moves(self):
        """ Fast check on number of legal moves
        """
        return self.nopen_line


    def get_square_moves(self, move_list=None):
        """ Get moves that will complete a square
        :move_list: list of candidate moves(MoveList)
                    default: use legal moves (get_legal_moves)
        :returns: list(MoveList) of moves that will complete a square
        """
        if move_list is None:
            move_list = self.get_legal_moves()
        square_move_list = MoveList(self, max_move=move_list.nmove)
        
        moves = move_list.moves
        for im in range(move_list.nmove):
            nr = moves[im, 0]
            nc = moves[im, 1]
            hv = moves[im, 2]    
            if self.does_complete_square(nr, nc, hv):
                square_move_list.add_move((nr, nc, hv))
        return square_move_list


    def get_square_distance_moves(self, min_dist=2, move_list=None):
        """ Get moves give a minimum distance(additional number of
        moves to complete a square) to square completion
        :min_dist: minimum distance requested, e.g. 1: next move can
                complete a square, 2: two moves required to complete
                a square default: 2 moves
        :move_list: list of candidate moves(MoveList)
                    default: use legal moves (get_legal_moves)
        :returns: list(MoveList) of moves that will complete a square
        """
        if move_list is None:
            move_list = self.get_legal_moves()
        dist_move_list = MoveList(self, max_move=move_list.nmove)
        
        for im in range(move_list.nmove):
            nr = move_list.moves[im, 0]
            nc = move_list.moves[im, 1]
            hv = move_list.moves[im, 2]    
            if self.distance_from_square(nr, nc, hv) >= min_dist:
                dist_move_list.add_move((nr, nc, hv))
        return dist_move_list
    

    def distance_from_square(self, nr, nc, hv):
        """ Find the minimum number of meves, after this edge, to complete square
        :nr: row number, starting at 1
        :nc: col number starting at 1
        0 => a completed square
        1 => sets up opponent to complete square
        """
        ir = nr - 1     # index
        ic = nc - 1
        min_dist = None
        if hv == 0:     # Horizontal
            if ir > 0:
                                                            # Square above
                dist = 0
                if self.lines[ir, ic, 1] == 0:               # left vertical edge
                    dist += 1
                if self.lines[ir-1, ic, 0] == 0:            # top horizontal edge
                    dist += 1
                if self.lines[ir, ic+1, 1] == 0:            # right vertical edge
                    dist += 1
                if dist == 0:
                    return dist                             # At min
                            
                if min_dist is None or dist < min_dist:
                    min_dist = dist


            if ir < self.nrows:     
                                                            # Square below
                dist = 0
                
                if self.lines[ir+1, ic, 1] == 0:            # left vertical edge
                    dist += 1
                if self.lines[ir+1, ic, 0] == 0:            # bottom horizontal edge
                    dist += 1
                if self.lines[ir+1, ic, 1] > 0:             # right vertical edge
                    dist += 1
                if dist == 0:
                    return dist                             # At min

                if min_dist is None or dist < min_dist:
                    min_dist = dist
                    
        else:     # Vertical
            if ic > 0:
                                                            # Square to left
                dist = 0
                if self.lines[ir+1, ic-1, 0] > 0:           # bottom horizontal edge
                    dist += 1
                if self.lines[ir, ic-1, 1] > 0:             # left vertical edge
                    dist += 1
                if self.lines[ir, ic-1, 0] > 0:   # top horizontal edge
                    dist += 1
                if dist == 0:
                    return dist                             # At min
                if min_dist is None or dist < min_dist:
                    min_dist = dist

            if ic < self.ncols:            
                                                            # Square to right
                dist = 0
                if self.lines[ir+1, ic, 0] == 0:            # bottom horizontal edge
                    dist += 1
                if self.lines[ir+1, ic, 1] == 0:            # right vertical edge
                    dist += 1     
                if self.lines[ir+1, ic, 0] == 0:            # top horizontal edge
                    dist += 1
                if dist == 0:
                    return dist                             # At min
                if min_dist is None or dist < min_dist:
                    min_dist = dist
                    
        return min_dist
        
    
    def does_complete_square(self, nr, nc, hv):
        """ Check if edge will complete square
        :nr: row number, starting at 1 for top of board
        :nc: col number, starting at 1 for left of board
        :hc: horizontal/vertical 0- horizontal, 1-vertical
        """
        ir = nr - 1
        ic = nc - 1
        if hv == 0:     # Horizontal
            if ir > 0:
                                                            # Square above
                if (self.lines[ir, ic, 1] > 0               # left vertical edge
                        and self.lines[ir-1, ic, 0] > 0     # top horizontal edge
                        and self.lines[ir, ic+1, 1] == 0):  # right vertical edge
                    return True            
                
                                                            # Square below
                if (self.lines[ir+1, ic, 1] > 0             # left vertical edge
                        and self.lines[ir+1, ic, 0] > 0     # bottom horizontal edge
                        and  self.lines[ir+1, ic, 1] > 0): # right vertical edge
                    return True
                
        else:     # Vertical
            if ic > 0:
                                                            # Square to left
                if (self.lines[ir+1, ic-1, 0] > 0           # bottom horizontal edge
                        and self.lines[ir, ic-1, 1] > 0     # left vertical edge
                        and self.lines[ir, ic-1, 0] > 0):   # top horizontal edge
                    return True     # complete sq on left
                
                                                            # Square to right
                if (self.lines[ir+1, ic, 0] > 0             # bottom horizontal edge
                        and self.lines[ir+1, ic, 1] > 0     # right vertical edge     
                        and self.lines[ir+1, ic, 0] > 0):    # top horizontal edge
                    return True     # complete sq on right
                    
        return False            # Completed squares            


    def get_edge(self, row=None, col=None, hv=None):
        """ Retrieve actual edge part from shadow
        :row: row number, starting with 1
        :col: col number, starting with 1
        :hv: horizontal==0, vertical==1
        """
        return self.lines[row-1, col-1, hv]
        


    def set_part(self, part):
        """ Add reference to actual part for reference / conversion
        :part: Part to add to shadow
        """
        row = part.row 
        col =  part.col
        if part.is_region():
            self.squares_obj[row-1,col-1] = part 
        elif part.is_edge():
            if part.sub_type() == 'h':
                self.lines_obj[row-1, col-1, 0] = part
            elif part:
                self.lines_obj[row-1, col-1, 1] = part

    def turn_on(self, part=None, player=None, move_no=None):
        """ Shadow part turn on operation to facilitate speed when display is not required
        :part: part to turn on
        :player: who made operation
        :move_no: current move number
        """
        if player is None:
            return              # Short circuit if no player
        
        pn = player.play_num
        row = part.row 
        col = part.col
        sub_type = part.sub_type()
        if part.is_edge():
            if sub_type == 'h':
                self.lines[row-1, col-1, 0] = pn
            else:
                self.lines[row-1, col-1, 1] = pn
        elif part.is_region():
            self.squares[row-1, col-1] = pn
        else:
            raise SelectError("turn_on Can't shadow part type {} at row={:d} col={;d}"
                              .format(part, row, col))
        self.nopen_line -= 1            # Reduce number of open lines by 1
        
        
    def turn_off(self, part=None):
        """ Shadow part turn on operation to facilitate speed when display is not required
        :part: part to turn on
        :player: who made operation
        :move_no: current move number
        """
        row = part.row 
        col = part.col
        sub_type = part.sub_type()
        if part.is_edge():
            if sub_type == 'h':
                if self.lines[row-1, col-1, 0] > 0:
                    self.nopen_line += 1
                self.lines[row-1, col-1, 0] = 0
            else:
                self.lines[row-1, col-1, 1] = 0
                if self.lines[row-1, col-1, 1] > 0:
                    self.nopen_line += 1
        elif part.is_region():
            self.squares[row-1, col-1] = 0
        else:
            raise SelectError("turn_off Can't shadow part type {} at row={:d} col={;d}"
                              .format(part, row, col))
