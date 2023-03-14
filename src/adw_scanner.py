#adw_scanner.py    09Mar2023  crs, Author
"""
Scanning support
The idea is to rapidly scan the grid giving audio tonal feedback as to the 
contents
"""
import math

from sinewave import SineWave

from select_trace import SlTrace
from sinewave_beep import SineWaveBeep

"""
scan path item to facilitate fast display, sound and operation
"""
class ScanPathItem:
    
    def __init__(self, ix, iy, cell=None,
                 sinewave_left=None,
                 sinewave_right=None):
        """ Setup scan item
        :ix: ix index
        :iy: iy index
        :cell: BrailleCell if one else None
        """
        self.ix = ix
        self.iy = iy
        self.cell = cell
        self.sinewave_left = sinewave_left
        self.sinewave_right = sinewave_right

class AdwScanner:
    
    def __init__(self, fte, cell_time=.05, space_time=.01):
        self.fte = fte
        self.adw = fte.adw
        self.mw = self.adw.mw
        self.canvas = self.adw.canvas
        self.cell_time = cell_time
        self.space_time = space_time
        self._scan_item = None          # Scanning image
        self._scan_item_tag = None             # Scanning item tag
        self._report_item = None        # Latest scanning report item
        self._scanning = False          # Currently scanning
        
    def start_scanning(self, cells=None):
        """ Start scanning process
        eye(center) is bottom / middle
        """
        SlTrace.lg("start_scanning")
        if cells is None:
            cells  = self.get_cells()
        self.cells = cells
        eye_sep_half = 15    # Half separation
        eye_ix = (self.get_ix_min() + self.get_ix_max())//2
        if eye_ix > self.get_ix_min() - eye_sep_half:
            eye_ix_l = eye_ix - eye_sep_half
        else:
            eye_ix_l = self.get_ix_min()
        if eye_ix < self.get_ix_max() - eye_sep_half:
            eye_ix_r = eye_ix + eye_sep_half
        else:
            eye_ix_r = self.get_ix_max()
            
        eye_iy_l = eye_iy_r = self.get_iy_max()
        self.eye_ixy_l = (eye_ix_l, eye_iy_l)
        self.eye_ixy_r = (eye_ix_r, eye_iy_r)
        fig_x_ul,fig_y_ul,fig_x_lr,fig_y_lr = self.bounding_box_ci()
        self.view_left = fig_x_ul if fig_x_ul <= eye_ix_l else eye_ix_l
        self.view_right  = fig_x_lr if fig_x_lr >= eye_ix_r else eye_ix_r
        
        self.forward_path = self.get_scan_path(cells=cells)
        self.reverse_path = list(reversed(self.forward_path))
        self.start_scan()

    def get_scan_path(self, cells=None):
        """ Get ordered list of scanning locations
            Scanning order is bottom to top, with alternating
            left-to-right then right-to-left so as to make a contiguous
            path
        :cells: cells dictionary by ix,iy default: self.cells
        :returns: list of ScanPathItem in the order to scan
        """
        if cells is None:
            cells = self.get_cells()
        ix_ul, iy_ul, ix_lr, iy_lr = self.bounding_box_ci(cells=cells)
        scan_path = []
        left_to_right = True    # Start going left to right
        for iy in range(iy_lr, iy_ul-1, -1):    # bottom to top
            if left_to_right:
                for ix in range(ix_ul, ix_lr+1):
                    cell = cells[(ix,iy)] if (ix,iy) in cells else None
                    scan_path.append(ScanPathItem(ix=ix, iy=iy, cell=cell))
            else:
                for ix in reversed(range(ix_ul, ix_lr+1)):
                    cell = cells[(ix,iy)] if (ix,iy) in cells else None
                    scan_path.append(ScanPathItem(ix=ix, iy=iy, cell=cell))
            left_to_right = not left_to_right
        """ Populate with sinewave appropriate with locations
        We assume we can hold enough pysinewave instances each set for stereo.
        """
        for sp_ent in scan_path:
            ix,iy = sp_ent.ix,sp_ent.iy
            vol_left, vol_right = self.get_vol(ix=ix, iy=iy,
                                               eye_ixy_l=self.eye_ixy_l,
                                               eye_ixy_r=self.eye_ixy_r)
            if sp_ent.cell is None:
                pitch = self.color2pitch("OTHER")
            else:
                pitch = self.get_pitch(ix=ix, iy=iy)
            ''' 
            sinewave_left = SineWave(pitch = pitch,
                                     channels=2, channel_side='l')

            sinewave_right = SineWave(pitch=pitch,
                                      channels=2, channel_side='r')
            '''
            sinewave_left = SineWave(pitch = pitch,
                                     channels=2, channel_side='l',
                                     decibels=vol_left,
                                     pitch_per_second=10/self.cell_time,
                                     decibels_per_second=10/self.cell_time)

            sinewave_right = SineWave(pitch=pitch,
                                      channels=2, channel_side='r',
                                      decibels=vol_right,
                                     decibels_per_second=10/self.cell_time)

            sp_ent.sinewave_left = sinewave_left
            sp_ent.sinewave_right = sinewave_right
            
        return scan_path

    def get_pitch(self, ix, iy):
        """ Get pitch for cell (color)
        :ix: cell ix
        :iy: cell iy
        """
        cell = self.get_cell_at_ixy((ix,iy))
        color = cell.color_string()
        pitch = self.color2pitch(color)
        return pitch
        
    def get_vol(self, ix, iy, eye_ixy_l, eye_ixy_r):
        """ Get tone volume for cell at ix,iy
        volume(left,right)
        Volume(in decibel): k1*(k2-distance from eye), k1=1, k2=0
        :ix: cell ix
        :iy: cell iy
        :eye_xy_l: left eye/ear at x,y
        :eye_xy_r: right eye/ear at x,y
        return: volume in decibel
        """
        eye_ix_l, eye_iy_l = eye_ixy_l
        eye_ix_r, eye_iy_r = eye_ixy_r
        eye_ix = (eye_ix_l+eye_ix_r)/2
        eye_iy = (eye_iy_l+eye_iy_r)/2
        dist = math.sqrt((ix-eye_ix)**2 + (iy-eye_iy)**2)   # average dist
        k1 = 15
        k2 = 10
        kd = .5
        vol = k1*(k2-dist*kd)
        SILENT = -100
        width = abs(self.view_right - self.view_left)
        vol_l = (vol*abs(self.view_right-ix)/width
                 + SILENT*abs(self.view_left-ix)/width)
        vol_r = (vol*abs(self.view_left-ix)/width
                 + SILENT*abs(self.view_right-ix)/width)
        '''
        if vol_l > vol_r:
            vol_r = SILENT           # HACK to enphasize stereo
        else:
            vol_l = SILENT
        vol_l,vol_r = vol_r,vol_l   # HACK - got things reversed!
        '''
        SlTrace.lg(f"\nl-r: {vol_l-vol_r:.2f}")
        SlTrace.lg(f"{ix},{iy} left vol:{vol_l:.2f}  dist:{dist:.2f} eye_ixy_l:{eye_ixy_l}")
        SlTrace.lg(f"{ix},{iy} right vol:{vol_r:.2f}  dist:{dist:.2f} eye_ixy_r:{eye_ixy_r}")
        return vol_l,vol_r
        
    
    def start_scan(self):
        """ Start actualscanning, which continues until stop_scan
        is called.
        Path self.forward_path is used, then alternating self.reverse_path,
        and forward_path
        """
        self._scanning = True
        self.using_forward_path = True 
        self.current_scan_path = []     # let scan_path_item setup 
        self.mw.after(0,self.scan_path_item)

    def stop_scan(self):
        """ Stop current scan
        """
        self._scanning = False 
        self.remove_display_item()
        self.remove_report_item()
        
        
    def scan_path_item(self):
        """Process next entry in self.current_path, removing item from
        list.  If at end of path, add next path, switching between
        forward_path and reverse_path
        """
        if not self._scanning:
            return
        
        if len(self.current_scan_path) == 0:
            if self.using_forward_path:
                self.current_scan_path = self.forward_path[:]   # used up
                self.using_forward_path = False 
            else:
                self.current_scan_path = self.reverse_path[:]   # used up
                self.using_forward_path = True 
        item = self.current_scan_path.pop(0)
        self.display_item(item)
        self.report_item(item)
        if item.cell is None:
            self.mw.after(int(self.space_time*1000), self.scan_path_item_complete)
        else:
            self.mw.after(int(self.cell_time*1000), self.scan_path_item_complete)

    def scan_path_item_complete(self):
        """ Complete current item where necessary
        """
        self.report_item_complete()
        if self._scanning:
            self.mw.after(0, self.scan_path_item)

    def color2pitch(self, color):
        return SineWaveBeep.color2pitch(color)


    def display_item(self, item):
        """ Update current scanner position display
        :item: current scan path item
        """
        canvas = self.canvas
        self.remove_display_item()
        ixy = item.ix, item.iy    
        x_left,y_top, x_right,y_bottom = self.get_win_ullr_at_ixy_canvas(ixy)
        self._scan_item_tag = canvas.create_rectangle(x_left,y_top,
                                                  x_right,y_bottom,
                                                  outline="black", width=2)
        self.update()

    def remove_display_item(self):
        """ remove current display item, if any
        """
        canvas = self.canvas
        if self._scan_item_tag is not None:
            self.canvas.delete(self._scan_item_tag)
            self._scan_item_tag = None

    def remove_report_item(self):
        """ Remove any noise for reported item
        """
        if self._report_item is not None:
            self._report_item.sinewave_left.stop()
            self._report_item.sinewave_right.stop()
            self._report_item = None        # TBD - turn tone off
                
    def report_item(self, item):
        """ Report scanned item
        start tone, to be stopped via report_item_complete
        :item: item being reported via tone
        """
        if item.sinewave_left is not None:
            self._report_item = item
            item.sinewave_left.play()
            item.sinewave_right.play()
        

    def report_item_complete(self):
        """ Report scanned item
        start tone, to be stopped via report_item_complete
        """
        self.remove_report_item()
            
     
    def stop_scanning(self):
        SlTrace.lg("stop_scanning - TBD")
        self.stop_scan()
        

    """
    ############################################################
                       Links to fte
    ############################################################
    """

    """ None so far """

    """
    ############################################################
                       Links to adw
    ############################################################
    """
    
    def bounding_box_ci(self, cells=None):
        """ cell indexes which bound the list of cells
        :cells: list of cells, (with cell.ix,cell.iy) or (ix,iy) tuples
                default: list of all cells in figure
        :returns: 
                    None,None,None,None if no figure
                    upper left ix,iy  lower right ix,iy
        """
        return self.adw.bounding_box_ci(cells=cells)
            
    def get_cell_at_ixy(self, cell_ixy):
        """ Get cell at (ix,iy), if one
        :cell_ixy: (ix,iy)
        :returns: BrailleCell if one, else None
        """
        return self.adw.get_cell_at_ixy(cell_ixy=cell_ixy)

    def get_cells(self):
        """ Get cell dictionary (by (ix,iy)
        """
        return self.adw.cells

    def get_xy_canvas(self, xy=None):
        """ Get current xy pair on canvas (0-max)
        :xy: xy tuple default: current xy
        :returns: (x,y) tuple
        """
        return self.adw.get_xy_canvas(xy=xy) 

    def set_grid_path(self):
        self.adw.set_grid_path()
        
    def get_grid_path(self):
        return self.adw.get_grid_path()
        
    def get_ix_min(self):
        """ get minimum ix on grid
        :returns: min ix
        """
        return self.adw.get_ix_min()

    def get_ix_max(self):
        """ get maximum ix on grid
        :returns: min ix
        """
        return self.adw.get_ix_max()

    def get_iy_min(self):
        """ get minimum iy on grid
        :returns: min iy
        """
        return self.adw.get_iy_min(())

    def get_iy_max(self):
        """ get maximum ix on grid
        :returns: min ix
        """
        return self.adw.get_iy_max()

    def get_win_ullr_at_ixy(self, ixy):
        """ Get window rectangle for cell at ixy
        :ixy: cell index tupple (ix,iy)
        :returns: (x_left,y_top, x_right,y_bottom)
        """
        return self.adw.get_win_ullr_at_ixy(ixy)


    def get_win_ullr_at_ixy_canvas(self, ixy):
        """ Get window rectangle for cell at ixy
        :ixy: cell index tupple (ix,iy)
        :returns: (x_left,y_top, x_right,y_bottom) canvas coords
        """
        return self.adw.get_win_ullr_at_ixy_canvas(ixy)

    def update(self):
        """ Update display
        """
        self.adw.update()
    