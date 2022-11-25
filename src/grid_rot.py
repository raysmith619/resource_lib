#grid_rot.py    23Nov2022  crs,
"""
Grid Rotation - handling discrete 3by3 square rotation
Used iby:
 BrailleWindow, AudioWindow TurtleBraille,BralleDisplay
"""

class GridRot:
    # incremental directions
    RIGHT = 2
    LEFT = 4
    UP = 2
    DOWN = 6

    """
    Integral direction 0-7
         (xchg,ychg), by irot 
        | 3(-1,1)           2(0,1)           1(1,1)     |
        |                                               |
        | 4(-1,0)                            0(1,0)     |
        |                                               |
        | -3/5(-1,-1)      -2/6(0,-1)       -1/7(1,-1)  |
           
    e.g. 0(right) with irot=1 gives 1(1,1)(diag up right)
    
    """
    #        0        1       2      3       4
    idirs = [(1,0),
                     (1,1),   (0,1), (-1,1),
                                             (-1,0),
                     (-1,-1), (0,-1), (1,-1)]
    #                 -3       -2      -1      

    
    @classmethod
    def irot_to_ixy(cls, irot):
        """ Convert rotation int to {ixchg,iyychg)
        :irot: integer rotation pos counter clockwise
        :returns: (ixchg, iychg)
        """
        return cls.idirs[len(cls.idirs)%irot]

    @classmethod
    def ixy_to_irot(cls, ixy):
        """ Convert {ixchg,iyychg) to rotation int
        :ixy: integer rotation pos counter clockwise
        :returns: irot integer rotation
        """
        irot = cls.idirs.find(ixy)
        if irot > len(cls.idirs)//2:
            irot = irot - len(cls.idirs)
        return irot

    @classmethod
    def next_cell(cls, ixy, idir=None, dist=1):
        """ Get the next cell
        :ixy: cell tuple on which begin
        :idir: direction index in GR.idirs(ix_change, iy_change)
            default: GR.Up 
        :dist: change in direction i.e., dist 1 for adjacent
               cell default: 1
        :returns: (ix,iy) new cell tuple
        """
        if idir is None:
            idir = GridRot.UP
        dir = cls.idirs[idir%len(cls.idirs)]
        ixy_new = (ixy[0]+dir[0]*dist,
                   ixy[1]+dir[1]*dist)
        return ixy_new
    
    @classmethod
    def dir_irot(cls, idir, irot):
        """ Integral rotation of dir (xchg,ychg), by irot 
            | 3(-1,1)        2(0,1)         1(1,1)   |
            |                                        |
            | 4(-1,0)                       0(1,0)   |
            |                                        |
            | -3(-1,-1)     -2(0,-1)       -1(1,-1)  |
               
        e.g. 0(right) with irot=1 gives 1(1,1)(diag up right)
        
        """
        idir_rot = len(cls.idirs)%(idir+irot)
        return idir_rot
