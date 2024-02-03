#wx_adw_create.py   24Jan2024   crs, Split off from wx_canvas_grid.py
""" AudioDrawWindow creation code
To support magnification windows
Collected to aid transformation to collecting tkinter window display
access from wxPython window display process
"""

from select_trace import SlTrace
from braille_error import BrailleError
from braille_cell import BrailleCell
from magnify_info import MagnifySelect, MagnifyInfo, MagnifyDisplayRegion

class AdwCreate:
    """ Creation / recreation code
    """
    def __init__(self, adw):
        """ Creation/Extension code
        """
        self.adw = adw
        self.tkr = adw.tkr      # Direct access

    def create_magnify_info(self, x_min=None,y_min=None,
                    x_max=None,y_max=None,
                    ncols=None, nrows=None):
        """ Create a MagnifyInfo, using our values as defaults
        :x_min: minimum x value - left side 
        :y_min: minimum y value - top side
        :x_max: maximum x value - right side
        :y_max: maximum  y value - bottom side
        :ncols: number of grid columns
        :nrows: number of grid rows
        """
        if x_min is None:
            x_min = self.g_xmin
        if y_min is None:
            y_min = self.g_ymin
        if x_max is None:
            x_max = self.g_xmax
        if y_max is None:
            y_max = self.g_ymax
        if ncols is None:
            ncols = self.g_ncols
        if nrows is None:
            nrows = self.g_nrows
        
        top_region = MagnifyDisplayRegion(x_min=x_min, y_min=y_min,
                                          x_max=x_max, y_max=y_max,
                                          ncols=ncols, nrows=nrows)
        mag_info = MagnifyInfo(top_region=top_region,
                               base_canvas=self)
        return mag_info
                   
    def create_magnification_window(self, mag_info):
        """ Create magnification
        :mag_info: MagnificationInfo containing info
        :returns: instance of AudioDrawWinfow or None if none was created
        """
        select = mag_info.select
        disp_region = mag_info.display_region
        disp_x_cell = (disp_region.x_max-disp_region.x_min)/disp_region.ncols
        disp_y_cell = (disp_region.y_max-disp_region.y_min)/disp_region.nrows
        xmin = select.ix_min*disp_x_cell + disp_region.x_min
        ymin = select.iy_min*disp_y_cell + disp_region.y_min
        xmax = (select.ix_max+1)*disp_x_cell + disp_region.x_min
        ymax = (select.iy_max+1)*disp_y_cell + disp_region.y_min
        SlTrace.lg(f"create_magnification_window:"
                   f" xmin:{xmin} ymin:{ymin} xmax:{xmax} ymax:{ymax}"
                   f" nrows:{disp_region.nrows} ncols:{disp_region.ncols}")
        child_info = mag_info.make_child()
        child_info.display_region = MagnifyDisplayRegion(x_min=xmin, x_max=xmax,
                                        y_min=ymin, y_max=ymax)
        child_info.description = (f"region minimum x: {xmin:.0f}, minimum y: {ymin:.0f},"
                                  + f" maximum x: {xmax:.0f}, maximum y: {ymax:.0f}")
        adw = self.create_audio_window(xmin=xmin, xmax=xmax,
                                       ymin=ymin, ymax=ymax,
                                       nrows=disp_region.nrows,
                                       ncols=disp_region.ncols,
                                       mag_info=child_info,
                                       require_cells=True)            
        return adw 

    def get_braille_cells(self, 
                        x_min=None, y_min=None,
                        x_max=None, y_max=None,
                        ncols=None, nrows=None):
        """ Get braille cells from tk canvas
        """
        braille_cells = self.tkr.get_braille_cells(
                        x_min=x_min, y_min=y_min,
                        x_max=x_max, y_max=y_max,
                        ncols=ncols, nrows=nrows)
        
    