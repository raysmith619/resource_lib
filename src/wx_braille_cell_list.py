#wx_braille_cell_list.py 16Jan2024  crs, Author
"""Conversion of braille cell display lists
Facilitate command line specification/testing plus interprocess
communication
"""
import copy

from select_trace import SlTrace

from braille_error import BrailleError
from braille_cell import BrailleCell

class BrailleCellList:
    """ List of braille cells for display
    """
    def __init__(self, cells_or_string=None):
        """ Create cell list
        :cells_or_string: array of BrailleCell
                        or
                          dictionary by ixy of BrailleCell
                        or
                          formatted string
                default: empty
        """
        self.cells = [] # List of BrailleCell
        if cells_or_string is not  None:
            SlTrace.lg(f"\nBrailleCellList:{cells_or_string}\n")
            if isinstance(cells_or_string, str):
                self.cells = self.get_from_string(cells_or_string)
            elif isinstance(cells_or_string,list):
                self.cells = [self.tuple_to_braille_cell(tp)
                            for tp in cells_or_string]
            elif isinstance(cells_or_string, dict):
                for ixy in cells_or_string:
                    tp = cells_or_string[ixy]
                    self.cells.append(self.tuple_to_braille_cell(tp))
            else:
                raise BrailleError("Unsupported BrailleCellList init"
                                f" type:{type(cells_or_string)})")
        
    
    def get_cells(self):
        """ Returns list
        """
        return self.cells
        
    def get_from_string(self, string):
        """ Convert formatted string, placing result
        internally. Cells are added as found
        :string: formatted text representing a list of cells
            (ix, iy, color)*
            where:
                ix is x (horizontal index)
                iy is y (vertical index)
                color is a color string
                whitespace is ignored
        :returns: list of BrailleCell
        """
        self.gs_set_string(string)
        while True:
            bc = self.gs_get_cell()
            if bc is None:
                break   # End of list
            self.cells.append(bc)
        return self.cells
    
    def tuple_to_braille_cell(self, tp):
        """ Create BrailleCell from (ix,iy,color)
        if given BrailleCell return it unchanged
        """
        if isinstance(tp, BrailleCell):
            return tp
        
        ix,iy,color = tp
        bc = BrailleCell(ix=ix, iy=iy, color=color)
        return bc
        
    def get_from_cells(self, cells):
        """ Convert cells dictionary to list, placing result
            converts (ix,iy,color) to BrailleCell
        internally. Cells are added as found
        :cells: list/dictionary of BrailleCells/(ix,iy,color)
        :returns: updated list of BrailleCell
        """
        cell_list = cells
        if type(cells) == dict:
            cell_list = []
            for ixy in cells:
                cell = cells[ixy]
                self.cells.append(self.tp_to_braille_cell(cell))
        else:
            clist = [self.tp_to_braille_cell(tp) for tp in cell_list]
            self.cells.extend(clist)    
        return self.cells

    def get_from_text_map(self, text):
        """ Get from text map string
        :text: map using blanks, and single char colors e.g. "r" for red
        :returns: list of BrailleCell
        """
        ix = 0
        iy = 0
        
    def to_string(self, inc=False):
        """ Return parseable string
        :inc: incremental True-just show changed values
                default: False-show absolute values
        :returns: parseable string
        """
        st = ""
        prev_cell = None
        for cell in self.cells:
            ix = cell.ix 
            iy = cell.iy 
            color = cell._color
            ix_str = str(ix)
            iy_str = str(iy)
            color_str = str(cell._color)
            if inc and prev_cell is not None:
                if ix == prev_cell.ix:
                    ix_str = ""
                if iy == prev_cell.iy:
                    iy_str = ""
                if color == prev_cell._color:
                    color_str = ""
            cs = f"({ix_str},{iy_str},{color_str})"
            st += cs
            prev_cell = cell        
        return st         
        
        """
        Parsing functions
        Used to parse string to cell list
        start with "gs_"
        """
    def gs_get_cell_prev(self):
        """ Return most recently added cell
        :returns: BrailleCell added, None if none
        """
        if len(self.cells) == 0:
            return None
        
        return self.cells[-1]   # Last added
            
    def gs_set_string(self, string=""):
        """ Initialize string conversion
        :string: string to process default: empty
        """
        self.gs_string = string
        self.gs_index = 0       # Index of next character
        self.gs_end_index = len(self.gs_string)
        self.gs_cell = None     # Current cell, if any
        self.gs_new_cell()

    def gs_new_cell(self):
        """ Start new cell
        """
        self.gs_cell_prev = copy.copy(self.gs_cell)
        self.gs_cell = BrailleCell()

    def gs_error(self, string="Unknown"):
        """ Generate diagnostic error in string parsing
        """
        string  += ": "
        err_str = ( "\n" + f"{string}"
                  + "\n" + len(string)*" " + self.gs_string
                  + "\n" + len(string)*" " + self.gs_index*" " + "^"                  
                    )
        raise BrailleError(err_str)
                     
    def gs_get_cell(self):
        """ Get next cell from string, if one
        :returns: BrailleCell if one, None if no more cells
        """
        self.gs_new_cell()
        if self.gs_get_start_cell() is None:
            return None
        ix = self.gs_get_index()
        if ix is None:
            self.gs_error(f"ix missing")
        self.gs_cell.set_ix(ix)
        iy = self.gs_get_index()
        if iy is None:
            self.gs_error(f"iy missing")
        self.gs_cell.set_iy(iy)
        color = self.gs_get_color()
        if color is None or color == "":
            cell_prev = self.gs_get_cell_prev()
            if cell_prev is not None:
                color = cell_prev.color_string()
        if color is not None and color != '':
            self.gs_cell.color_cell(color)
        if self.gs_get_end_cell() is None:
            self.gs_error(f"cell end missing")
        cell = copy.copy(self.gs_cell)
        self.gs_new_cell()
        return cell

    def gs_get_index(self):
        """ Get next index
        :returtns: index, None if none
        """
        st = self.gs_get_string()
        if st == "":
            return None

        return int(st)
    
    def gs_skip_space(self):
        """ Skip past whitespace
        :returns: character after whitespace, None if end of string
        """
        while self.gs_index < self.gs_end_index:
            ch = self.gs_string[self.gs_index]
            if not ch.isspace():
                return ch
            self.gs_index += 1
        return None

    def gs_get_start_cell(self):
        """ Position after start of cell "("
        :returns: first character, None if no more string
        """
        ch = self.gs_skip_space()
        if ch != '(':
            if ch is None:
                return None # End of string
            
            self.gs_error(f"{ch} found instead of ( for cell start")    
        self.gs_index += 1
        return ch
    
    def gs_get_end_cell(self):
        """ Position at end of cell ")"
        :returns: end character, error if not found
        """
        ch = self.gs_skip_space()
        if ch != ')':
            self.gs_error(f"{ch} found instead of ) for cell end")    
        self.gs_index += 1
        return ch

    def gs_get_color(self):
        """ Get color
        Using gs_get_string needs to be changed
        if support of #.... is wanted"""
        return self.gs_get_string()
                
    def gs_get_string(self):
        """ Get string digits/or alpha
        skips leading whitespace, stops at whitespace or
        non alphanumeric char
        :returns: string
        """
        st = ""
        self.gs_skip_space()
        while self.gs_index < self.gs_end_index:
            ch = self.gs_string[self.gs_index]
            if not ch.isalnum():
                break
            st += ch
            self.gs_index += 1
        if self.gs_index < self.gs_end_index:
            ch = self.gs_string[self.gs_index]
            if ch != ")":
                self.gs_index += 1  # pass arg delimiter unless end                
        return st        
                
if __name__ == "__main__":
    
    strs = [
        "(1,1,red) (2,2) (3,3) (4,4,green) (4,3) (4,2,blue)",
        "(100,1,red) (100,2,) (100,3,) (100,4,blue) (100,5,)",
        ]
    
    def str_test(st, inc=None):
        SlTrace.lg(f"st: {st}")
        cl = BrailleCellList(st)        
        cells = cl.get_cells()
        for cell in cells:
            SlTrace.lg(str(cell))
        if inc is None:
            inct = False
            st_2 = cl.to_string(inc=inct)
            SlTrace.lg(f"Recover inc:{inct} {st_2}")
            inct = True
            st_2 = cl.to_string(inc=inct)
            SlTrace.lg(f"Recover inc:{inct} {st_2}")
        else:
            inct = True
            st_2 = cl.to_string(inc=inct)
            SlTrace.lg(f"Recover inc:{inct} {st_2}")
            
        
    for st in strs:
        str_test(st,inc=None)        