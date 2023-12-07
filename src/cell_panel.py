# cell_panel.py 03Nov2023  crs, contain wxpython versions for canvas
"""
Support for canvas type actions e.g., create_rectangle
"""
from select_trace import SlTrace

class CellPanel:
    def __init__(self, adw):
        self.adw = adw
        self.win_width = adw.win_width
        self.win_height = adw.win_height
        self.grid_width = adw.grid_width
        self.grid_height = adw.grid_height
        self.cell_height = adw.win_height/self.grid_height
        

    def create_rectangle(self, cx1,cy1,cx2,cy2,
                                    fill="dark gray",
                                    outline="dark gray",
                                    width=None):
        """Create rectangle ala canvas.create_rectangle
        in cell_panel
        """
        SlTrace.lg(f"TBD: cell_panel_create_rectangle(" 
                   f" {cx1},{cy1},{cx2},{cy2}," 
                   f" fill={fill}, outline={outline},"
                   f" width=outline_width)")

    def create_oval(self, x0,y0,x1,y1,
                                    fill=None, outline=None):
        """Create rectangle ala canvas.create_oval
        in canv_panel
        """
        SlTrace.lg(f"TBD: canv_panel_create_oval(" 
                   f" {x0},{y0},{x1},{y1}," 
                   f" fill={fill}, outline={outline})")

    def delete(self, obj):
        """ Delete object in panel
        :obj: object to be deleted
        """
        SlTrace.lg("canv_panel_delete({obj})")        