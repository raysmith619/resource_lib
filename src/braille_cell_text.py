# braille_cell_text.py    11Apr2023  crs, Author
"""
BrailleCell group to text picture
Text picture to BrailleCell group
For testing / Diagnostics
Plan:
Build BrailleCell dictionary/list from text picture
Text picture examples:
"""
import re 

from select_trace import SlTrace
from braille_cell import BrailleCell

yellow_circle ="""
,,,,,,,,,,,,yy
,,,,,,,,,,yyyyy
,,,,,,,,,,yyyyy
,,,,,,,,,,yyyyy
,,,,,,,,,,,yyy
"""
yellow_circle_modified ="""
,,,,,,,,,,,,yy
,,,,,,,,,,yyyyy
,,,,,,,,,,ygivy
,,,,,,,,,,yyyyy
,,,,,,,,,,,yyy
"""

spokes_picture="""
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

class BrailleCellText:
    """ translator between Cells and text picture
    """
    def __init__(self, text=None, cells=None,
                 grid_height=25, grid_width=32,
                 cell_nch=1):
        """ Setup text/cells, given the other
        :text: text string portraying the cells
                either "," or " " (space) is supported
                for input
        :cells: dictionary by ix,iy or list of BrailleCell
        Only one of text or cells is allowed_attributes
        :grid_height: assumed window height default: 25
        :grid_width: assumed window width default: 32
        :cell_nch: number of chars per cell default:1
        """
        if text is not None and cells is not None:
            SlTrace.lg("Only one of text or cells may be specified")
            return
        
        self.text = text
        self.cells = cells
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.cell_nch = cell_nch
        
        if text is not None:
            self.build_from_text(self.text)
        else:
            self.build_from_cells(cells=self.cells) 


    def build_from_cells(self, cells=None,
                         shift_to_edge=True, blank_char=",",
                         cell_nch=None):
        """ Build text from cells
        :cells: list/dictionary by ix,iy cells to build text
            default: use self.cells
        :shift_to_edge: shift figure towards edge to ease finding figure
                        default: self.shift_to_edge
        :blank_char: convert leading blanks to this
                    default: ","
        :cell_nch:    Number of text chars per cell
                    default: from BrailleCellText init
        """
        if cell_nch is None:
            cell_nch = self.cell_nch
        if cells is None:
            cells = self.cells
        if isinstance(cells, list):
            cdict = {}
            for cell in cells:
                cdict[(cell.ix,cell.iy)] = cell
            cells = cdict
        self.cells = cells
        self.text = self.get_text(shift_to_edge=shift_to_edge,
                                  blank_char=blank_char,
                                  cell_nch=cell_nch)
        
    def get_text(self, cells=None, shift_to_edge=None, blank_char= ",",
                 marker_ixy=None, marker=None, marker_space=None,
                 cell_nch=None):
        """ get text picture for braille display from cells
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
        :cell_nch:    Number of text chars per cell
                    default: from __init__
        """
        if cell_nch is None:
            cell_nch = self.cell_nch
        if cells is None:
            cells = self.cells
        if shift_to_edge is None:
            shift_to_edge = True
        self.blank_char = blank_char
        self.find_edges(cells=cells)
        left_edge = self.left_edge
        right_edge = self.right_edge
        top_edge = self.top_edge
        bottom_edge = self.bottom_edge
        
        if not shift_to_edge:
            left_edge = 0
            top_edge = 0

        braille_text = ""
        for iy in range(top_edge, bottom_edge+1):
            line = ""
            for ix in range(left_edge, right_edge+1):
                cell_ixy = (ix,iy)
                if cell_ixy in self.cells:
                    cell = self.cells[cell_ixy]
                    color = cell.color_string()
                    if cell.pi_number is not None:
                        mark = str(cell.pi_number)
                        if len(mark) < cell_nch:
                            mark = color[0] + mark
                        while len(mark) < cell_nch:
                            mark += color[0]
                    else:
                        mark = color[0]
                        while len(mark) < cell_nch:
                            mark += color[0]
                    if marker_ixy == cell_ixy:
                        if marker == "uppercase" or marker is None:
                            mark = mark.upper()
                        else:
                            mark = f"[{mark}]" 
                else:
                    mark = " "
                    if  marker_ixy == cell_ixy:
                        mark = marker_space
                if len(mark) == 1 and cell_nch > 1:
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
                    
    def build_from_text(self, text):
        cells = {}
        ix = 0
        iy = 0
        for ch in text:
            if ch == "," or ch == " ":
                ix += 1             
            elif ch in BrailleCell.dots_for_character:
                color = BrailleCell.ch2color(ch=ch)
                cell = BrailleCell(ix=ix, iy=iy, color=color)
                cells[(ix,iy)] = cell
                ix += 1
            elif ch == "\n":
                ix = 0
                iy += 1
            else:
                ix += 1     # Ignore but keep alignment
        self.cells = cells
                 
    def print_text(self, shift_to_edge=None, blank_char= ",",
                 marker_ixy=None, marker=None, marker_space=None,
                 cell_nch=None):
        """ Print out (to log) text rendition
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
        :cell_nch: cell number of characters
                    default: self.cell_nch
        """
        if cell_nch is None:
            cell_nch = cell_nch
        SlTrace.lg()
        text = self.get_text(shift_to_edge=shift_to_edge,
                              blank_char= blank_char,
                              marker_ixy=marker_ixy, marker=marker,
                              marker_space=marker_space,
                              cell_nch=cell_nch)
        SlTrace.lg(text)

    def diff_text(self, text, space_comma=None, trim_spaces=True,
                  shift_to_edge=True,
                  blank_char= ",",
                  cell_nch=None):
        """ Return difference in text line by line
        :space_comma: space and comma replaced with this
                        default: " "  None -> no replacement
        :trim_spaces: trim leading/trailing whitespace before comparison
                        default: True
                        Done after any space_comma replacement
        :returns: lines with differences
        :shift_to_edge: shift figure towards edge to ease finding figure
                        default: self.shift_to_edge
        :blank_char: convert leading blanks to this
                    default: ","
        :cell_nch:    Number of text chars per cell
                    default: from __init__
        """
        if cell_nch is None:
            cell_nch = self.cell_nch
        if space_comma is None:
            space_comma = blank_char
        our_text = self.get_text(shift_to_edge=shift_to_edge,
                                 blank_char= blank_char,
                                 cell_nch=cell_nch)
        our_lines = our_text.splitlines()
        if shift_to_edge:
            text_bct = BrailleCellText(text=text, cell_nch=cell_nch)
            text = text_bct.get_text(shift_to_edge=shift_to_edge)
        text_lines = text.splitlines()
        diff = ""
        while len(our_lines)>0 and our_lines[0] == '':
            our_lines.pop(0)
        while len(our_lines)>0 and our_lines[-1] == '':
            our_lines.pop()
        while len(text_lines)>0 and text_lines[0] == '':
            text_lines.pop(0)
        while len(text_lines)>0 and text_lines[-1] == '':
            text_lines.pop()

        while len(our_lines) >0 or len(text_lines) > 0:
            our_line = "" if len(our_lines)==0 else our_lines.pop(0)
            text_line = "" if len(text_lines)==0 else text_lines.pop(0)
            if space_comma is not None:
                our_line = our_line.replace(',', space_comma)
                our_line = our_line.replace(' ', space_comma)
                text_line = text_line.replace(',', space_comma)
                text_line = text_line.replace(' ', space_comma)
            if trim_spaces:
                our_line = our_line.strip()
                text_line = text_line.strip()
            if our_line != text_line:
                our_diff  = " < " + our_line + "\n"
                text_diff = " > " + text_line + "\n"
                diff += our_diff + text_diff
        return diff
    
    def get_cells(self):
        """ Returns cells(dictionary by ixy) created
        """
        return self.cells
            
    def print_cells(self):
        """ Print our cells a line at a time
        """
        ix_max = self.get_ix_max()
        iy_max = self.get_iy_max()
        for iy in range(iy_max+1):
            st_line = ""
            for ix in range(ix_max+1):
                ixy = (ix,iy)
                if ixy in self.cells:
                    st_line += f" {self.cells[ixy]}"
            if st_line != "":
                SlTrace.lg(st_line)

    """
         From audio_draw_window
         with the ix_min.... adjusted for local
    """
    def get_ix_min(self):
        """ get minimum ix on grid
        :returns: min ix
        """
        return 0

    def get_ix_max(self):
        """ get maximum ix on grid
        :returns: min ix
        """
        return self.grid_width-1

    def get_iy_min(self):
        """ get minimum iy on grid
        :returns: min iy
        """
        return 0

    def get_iy_max(self):
        """ get maximum ix on grid
        :returns: min ix
        """
        return self.grid_height-1

    def find_edges(self, cells=None):
        """Find  top, left, bottom, right non-blank edges
        so we can shift picture to left,top for easier
        recognition
        :cells: cells default:self.cells
        """
        if cells is None:
            cells = self.cells
        left_edge,top_edge, right_edge,bottom_edge = self.bounding_box_ci(
                                cells=cells)
        if bottom_edge is None:
            bottom_edge = self.grid_height-1
                    
        if left_edge > 0:           # Give some space
            left_edge -= 1
        if left_edge > 0:
            left_edge -= 1
        self.left_edge = left_edge
        
        if top_edge > 0:           # Give some space
            top_edge -= 1
        if bottom_edge  < self.grid_height-1:
            bottom_edge += 1        
        self.top_edge = top_edge
        self.bottom_edge = bottom_edge
        
        self.left_edge = left_edge
        self.right_edge = right_edge
         
        return left_edge, top_edge, right_edge, bottom_edge
    
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
        """
        if cells is None:
            if not hasattr(self, "cells"):
                return None,None,None,None         # Not yet setup
            else:
                cells = self.cells
        
        ix_min, iy_max, ix_max,iy_min = None,None,None,None
        for cell in cells:
            cell_ixy = cell if isinstance(cell, tuple) else (cell.ix,cell.iy)
            cell_ix, cell_iy = cell_ixy
            if ix_min is None or cell_ix < ix_min:
                ix_min = cell_ix
            if ix_max is None or cell_ix > ix_max:
                ix_max = cell_ix
            if iy_min is None or cell_iy < iy_min:
                iy_min = cell_iy
            if iy_max is None or cell_iy > iy_max:
                iy_max = cell_iy

        if ix_min is None:
            ix_min = 0
        if ix_max is None:
            ix_max = self.grid_width-1
        if iy_min is None:
            iy_min = 0
        if iy_max is None:
            ix_max = self.grid_height-1
        
        if add_edge is not None:    # Extend/Shrink box
            ext_ix_min = ix_min - add_edge
            bd_ix_max = self.get_ix_max() # protect against too large of negative add_edge
            if ext_ix_min > bd_ix_max: ext_ix_min = bd_ix_max
            ix_min = max(ext_ix_min, self.get_ix_min()) # limit to bounds

            ext_iy_min = iy_min - add_edge
            bd_iy_max = self.get_iy_max()
            if ext_iy_min > bd_iy_max: ext_iy_min = bd_iy_max
            iy_min = max(ext_iy_min, self.get_iy_min())
            
            ext_ix_max = ix_max + add_edge
            bd_ix_min = self.get_ix_min()
            if ext_ix_max < bd_ix_min: ext_ix_max = bd_ix_min
            ix_max = min(ext_ix_max, self.get_ix_max())
            
            ext_iy_max = iy_max + add_edge
            bd_iy_min = self.get_iy_min()
            if ext_iy_max < bd_iy_min: ext_ix_max = bd_iy_min
            iy_max = min(ext_iy_max, self.get_iy_max())
            
        return ix_min,iy_min, ix_max,iy_max

        
        
if __name__ == "__main__":
    SlTrace.clearFlags()
    SlTrace.lg("\n\nTest: yellow_circle")
    test_text = yellow_circle
    ycir_bct = BrailleCellText(text=test_text)
    SlTrace.lg(f"{test_text} cells:")
    ycir_bct.print_cells()
    SlTrace.lg(f"{test_text} unmodified text:")
    ycir_bct.print_text(shift_to_edge=False)

    SlTrace.lg("Testing text diff")
    SlTrace.lg(f"yellow_circle_modified:")
    SlTrace.lg(yellow_circle_modified)
    diff = ycir_bct.diff_text(yellow_circle_modified)
    for line in diff.splitlines():
        SlTrace.lg(f"diff: {line}")
    
    SlTrace.lg("\n\nTest: spokes_picture")
    test_text = spokes_picture
    spokes_bct = BrailleCellText(text=test_text)
    SlTrace.lg("to cells:")
    spokes_bct.print_cells()
    SlTrace.lg("From text:")
    spokes_bct.print_text(shift_to_edge=False)

    chg_ix, chg_iy = 5,10
    chg_ixy = (chg_ix,chg_iy)
    chg_color = "w"
    SlTrace.lg(f"Changing {chg_ixy} color to {chg_color}")
    if chg_ixy in spokes_bct.cells:
        cell = spokes_bct.cells[chg_ixy]
        SlTrace.lg(f"Color:{cell.color.string()} to {chg_color}")
    else:
        SlTrace.lg(f"New cell at {chg_ixy} color={chg_color}")
        cell = BrailleCell(ix=chg_ix, iy=chg_iy, color=chg_color)
        spokes_bct.cells[chg_ixy] = cell
    SlTrace.lg()
    SlTrace.lg("Converting cells back to text")
    bct2 = BrailleCellText(cells=spokes_bct.get_cells())
    SlTrace.lg("Comparing with original text")
    diff_spokes = bct2.diff_text(spokes_picture)
    for line in diff_spokes.splitlines():
        SlTrace.lg(f"diff: {line}")
    
    SlTrace.lg("Printing resulting text")
    bct2.print_text()
    
    cell_nch = 4
    SlTrace.lg(f"Displaying text with cell_nch = {cell_nch}")
    spokes_bct.print_text(cell_nch=4)