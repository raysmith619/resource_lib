#braille_cell.py    27Nov2022
"""
Basis for Braille cell (6 dot pattern)
"""

class BrailleCell:
    """ braille cell info augmented for analysis
    """
    # Marking type
    MARK_UNMARKED = 1
    MARK_SELECTED = 2
    MARK_TRAVERSED = 3

    
    dots_for_character = {
        " ": (),    # blank
        "a": (1),
        "b": (1,2),
        "c": (1,4),
        "d": (1,4,5),
        "e": (1,5),
        "f": (1,2,5),
        "g": (1,2,4,5),
        "h": (1,2,5),
        "i": (2,4),
        "j": (2,4,5),
        "k": (1,3),
        "l": (1,2,3),
        "m": (1,3,4),
        "n": (1,3,4,5),
        "o": (1,3,5),
        "p": (1,2,3,4),
        "q": (1,2,3,4,5),
        "r": (1,2,3,5),
        "s": (2,3,4),
        "t": (2,3,4,5),
        "u": (1,3,6),
        "v": (1,2,3,6),
        "w": (2,4,5,6),
        "x": (1,3,4,6),
        "y": (1,3,4,5,6),
        "z": (1,3,5,6),
        }

    @classmethod
    def braille_for_letter(cls, c):
        """ convert letter to dot number seq
        :c: character
        :returns: dots tupple (1,2,3,4,5,6)
        """
        if c not in cls.dots_for_character:            c = " " # blank
        dots = cls.dots_for_character[c]
        return dots

    @classmethod
    def color_str(cls, color):
        """ convert turtle colors arg(s) to color string
        :color: turtle color arg
        """
        color_str = color
        if isinstance(color_str,tuple):
            if len(color_str) == 1:
                color_str = color_str[0]
            else:
                color_str = "pink"  # TBD - color tuple work
        return color_str
    
    
    def __init__(self, dots=None,
                 color=None, color_bg=None,
                 ix=0, iy=0,
                 mtype=None,
                 points=None):
        """ setup braille cell
        :dots: list of set dots default: none - blank
        :color: color str or tuple
        :ix: cell index(from 0) from left side
        :iy: cell index from bottom
        :mtype: marked type
                default: MARK_UNSELECTED
        :points: initial set of points, if any
            default: empty
        """
        self.ix = ix    # Include to make self sufficient
        self.iy = iy
        if mtype is None:
            mtype = BrailleCell.MARK_SELECTED
        self.mtype = mtype
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
            st += " bg:" + self._color_bg
        return st
        
    
    def braille_for_color(self, color):
        """ Return dot list for color
        :color: color string or tuple
        :returns: list of dots 1,2,..6 for first
                letter of color
        """
        
        if color is None:
            color = self._color
        if color is None:
            color = ("black")
        color = self.color_str(color)
        c = color[0]
        dots = self.braille_for_letter(c)
        return dots

    def color_string(self, color=None):
        """ convert turtle colors arg(s) to color string
        :color: turtle color arg
        """
        if color is None:
            color = self._color
        return self.color_str(color)
    
    def color_cell(self, color=None):
        """ Color cell
        :color: turtle color
        """
        if color is None:
            color = self._color
        dots = self.braille_for_color(color=color)
        self.dots = dots
        self._color = color