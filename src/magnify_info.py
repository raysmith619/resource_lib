# magnify_info.py     18Feb2023   crs, Split from audio_draw_window.py

"""
Information supporting the magnification of a segment of CanvasGrid (canvas_grid.py)
Communication packet between CanvasGrid and AudioDrawWindow
"""
import copy

class MagnifyDisplayRegion:
    """ Region of display, from which a selection may be created """
    def __init__(self, win_fract=True,
                    x_min=None,y_min=None,
                    x_max=None,y_max=None,
                    ncols=40, nrows=25,
                    dup=None):
        """ Setup region of display
        :win_fract: True - values are fraction (0. to 1.) of whole display area
        :x_min: minimum x value - left side 
        :y_min: minimum y value - top side
        :x_max: maximum x value - right side
        :y_max: maximum  y value - bottom side
        :ncols: number of grid columns
        :nrows: number of grid rows
        :dup: if not none use this (MagnifyDisplayRegion) for None entries
        """
        if dup is not None:
            win_fract = dup.win_fract
            if x_min is None:
                x_min = dup.x_min
            if y_min is None:
                y_min = dup.y_min
            if x_max is None:
                x_max = dup.y_max
            if y_max is None:
                y_max = dup.y_max
            if ncols is None:
                ncols = dup.ncols
            if nrows is None:
                nrows = dup.nrows
        self.win_fract = win_fract
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.ncols = ncols
        self.nrows = nrows

    def __str__(self):
        ret =  (f"win_fract:{self.win_fract}"
                f" x_min:{self.x_min}"
                f" y_min:{self.y_min}"
                f" x_max:{self.x_max}"
                f" y_max:{self.y_max}"
                f" ncols:{self.ncols}"
                f" nrows:{self.nrows}")
        return ret

 
class MagnifySelect:
    """ Selection info """
    def __init__(self, ix_min=None, iy_min=None,
                        ix_max=None, iy_max=None,):
        self.ix_min = ix_min
        self.iy_min = iy_min
        self.ix_max = ix_max
        self.iy_max = iy_max
        
    def __str__(self):
        ret =  (f"ix_min:{self.ix_min}"
                f" iy_min:{self.iy_min}"
                f" ix_max:{self.ix_max}"
                f" iy_max:{self.iy_max}")
        return ret
        
class MagnifyInfo:
    """ Magnification info
        For sending info from and to original canvas
    """
    info_number = 0         # Ascending unique number
                            # Bumped by __init__, make_child
    def __init__(self, select=None,
                 top_region=None,
                 display_region=None,
                 description="",
                 display_window=None,
                 parent_info=None,
                 child_infos=[],
                 mag_nrows=None,
                 mag_ncols=None,
                 base_canvas=None
                 ):
        """
        Setup magnification information, to be modified
        :select: (MagnifySelect) selection cell indexes
        :top_region: (MagnifyDisplayRegion) - top display region
        :display_region: (MagnifyDisplayRegion) display region on which selection is made
        :display_window: (AudioDrawWindow) - display window
        :parent_info: (MagnifyInfo) - display from which this info was selected
        :child_infos: (list of MagnifyInfo) - children from this info
        :mag_nrows: magnified number of rows default: display_region.nrows 
        :mag_ncols: magnified number of columns default: display_region.nrows 
        :base_canvas: canvas with base info/control
        """
        MagnifyInfo.info_number += 1
        self.info_number = MagnifyInfo.info_number
        if select is None:
            select = MagnifySelect()
        self.select = select
        if top_region is None:
            top_region = MagnifyDisplayRegion()
        self.top_region = top_region
        if display_region is None:
            display_region = MagnifyDisplayRegion(dup=self.top_region)
        self.display_region = display_region
        self.description = description
        if mag_nrows is None:
            mag_nrows = display_region.nrows
            if mag_nrows is None:
                mag_nrows = top_region.nrows
        self.mag_nrows = mag_nrows
        if mag_ncols is None:
            mag_ncols = display_region.ncols
            if mag_ncols is None:
                mag_ncols = top_region.ncols
        self.mag_ncols = mag_ncols
        self.parent_info = parent_info
        self.child_infos = child_infos
        self.base_canvas = base_canvas

    def __str__(self):
        ret = f"MagI[{self.info_number}]:"
        if self.description:
            ret += f" self.description"
        if self.select is not None:
            ret += f" select: {self.select}"
        if self.top_region is not None:
            ret += f"\n    top:{self.top_region}"
        if self.display_region is not None:
            ret += f"\n    display:{self.display_region}"
        if self.mag_ncols != self.display_region.ncols:
            ret += f" mag_ncols:{self.mag_ncols}"    
        if self.mag_nrows != self.display_region.nrows:
            ret += f" mag_ncols:{self.mag_nrows}"
        if self.parent_info is None:
            ret += f"\n    no parent"
        else:
            np = 0      # count levels
            parent = self.parent_info
            while parent is not None:
                np += 1
                parent = parent.parent_info
            ret += f"\n parent level: {np}"
        nc = len(self.child_infos)
        ret += f"\n    {nc}"
        ret += " child" if nc == 1 else " children"
        return ret

    def make_child(self):
        """ Create child info with us as parent and child added to children
        :returns: (MagnifyInfo) child
        """
        child = copy.copy(self)     # Don't expect changing except as below
        MagnifyInfo.info_number += 1
        child.info_number = MagnifyInfo.info_number
        child.description = ""
        child.select = MagnifySelect()  # Initialize as unselected
        child.display_window = None     # Set when used
        child.parent_info = self
        child.child_infos = []         
        self.child_infos.append(child)
        return child
        

if __name__ == '__main__':
    mag_info = MagnifyInfo()
    print(f"mag_info: {mag_info}")        