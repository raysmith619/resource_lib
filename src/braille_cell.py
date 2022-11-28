#braille_cell.py    27Nov2022
"""
Basis for Braille cell (6 dot pattern)
"""

class BrailleCell:
    """ braille cell info augmented for analysis
    """
    def __init__(self, dots=None,
                 color=None, color_bg=None,
                 ix=0, iy=0,
                 points=None):
        """ setup braille cell
        :dots: list of set dots default: none - blank
        :color: color str or tuple
        :ix: cell index(from 0) from left side
        :iy: cell index from bottom
        :points: initial set of points, if any
            default: empty
        """
        self.ix = ix    # Include to make self sufficient
        self.iy = iy
        self.dots = dots
        if color is None:
            color = "black"
        if color_bg is None: 
            color_bg = "white"
        self._color = color
        self._color_bg = color_bg
        if points is None:
            points = set()
        self.points = points
        self.canv_items = []        # canvas items

    def __str__(self):
        st = f"BCell: [{self.ix},{self.iy}]"
        if self._color is not None:
            st += " " + self._color
        if self._color_bg is not None:
            st += " " + self._color_bg
        return st
        

    def color_str(self, color=None):
        """ convert turtle colors arg(s) to color string
        :color: turtle color arg
        """
        color_str = color
        if (color_str is None
             or (isinstance(color_str, tuple)
                  and len(color_str) == 0)
             ):
            color_str = self._color
        if isinstance(color_str,tuple):
            if len(color_str) == 1:
                color_str = color_str[0]
            else:
                color_str = "pink"  # TBD - color tuple work
        return color_str
