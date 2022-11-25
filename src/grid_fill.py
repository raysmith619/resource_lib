# grid_fill.py    22Nov2022  crs, Author
"""
Logic anf Functions to facilitate
traversing and filling gridded regions of AudioWindow
"""
import math

from grid_rot import GridRot as GR

class GridFill:
        
    
    def __init__(self, awin):
        """ Establish grid area
        :awin: AudioWindow instance
        """
        self.awin = awin
        
    def find_edge(self, ixy, isdir=4):
        """ Find appropriate edge point
        Currently closest edge searching horizontally
        
        :ixy: Internal, including possibly on edge,
            cell (ix,iy)
        :isdir: integer search direction
                default: 4 == left
        :returns: ixy, ixy_off where ixy is (ix,iy)
                    and ixy_off is first (ix,iy) square
                    in search direction off figure
        """
        
        ix_prev = ixy[0]
        iy_prev = ixy[1]
        sdir = GR.idirs[isdir]
        while True:
            ix = ix_prev + sdir[0]
            iy = iy_prev + sdir[1]
            ixy_ck = (ix, iy)
            if ixy_ck not in self.awin.cells:
                return (ix_prev, iy_prev), (ix, iy)
            
            ix_prev = ix
            iy_prev = iy
            
    def find_edge_direction(self, ixy, isdir):
        """ Find edge direction
            defined as the direction, orthogonal
            to the edge search (sdir[1],sdir[0])
            
            
        :ixy: cell (x,y) of edge point
        :isdir: edge search direction -3 to 4
        :returns:edge direction: -3 to 4
        """
        sdir = GR.idirs[isdir]
        sdir_ck = (sdir[1], sdir[0])
        ixy_fwd,ixy_fwd_off = self.find_edge(ixy, sdir_ck)
        sdir_ck_back = (-sdir_ck[0], -sdir_ck[1])
        ixy_back,ixy_back_off = self.find_edge(ixy,)
        len_fwd = math.sqrt((ixy_fwd[0]-ixy[0])**2
                             + (ixy_fwd[1]-ixy[1])**2)
        len_back = math.sqrt((ixy_back[0]-ixy[0])**2
                             + (ixy_back[1]-ixy[1])**2)
        if len_fwd >= len_back:
            edir = self.dir_rot(isdir, GR.RIGHT)
        else:
            edir = self.dir_rot(isdir, GR.LEFT)
        return edir

    def find_perimiter(self, ixy, excluded=None):
        """ Find a list of cells which form a perimeter to
        a closed group of cells.
        :ixy: (ix,iy) tuple for one enclosed cell
        :excluded: set of (ix,iy) of cells considered as
        "out-of-bounds" 
        :returns: ordered list of perimiter cell (ix,iy)
        """
        ixy_edge, ixy_off = self.find_edge(ixy)
        
                
    