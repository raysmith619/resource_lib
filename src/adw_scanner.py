#adw_scanner.py    09Mar2023  crs, Author
"""
Scanning support
The idea is to rapidly scan the grid giving audio tonal feedback as to the 
contents
"""
import math
import time
import cProfile, pstats, io         # profiling support

from sinewave_numpy import SineWaveNumPy

from select_trace import SlTrace
from sinewave_beep import SineWaveBeep
from Lib.pickle import TRUE

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

    def __str__(self):
        st = f"ScanPathItem: {self.ix},{self.iy}"
        st += f" {self.cell}" if self.cell is not None else " space"
        return st
    
class AdwScanner:
    
    def __init__(self, fte, cell_time=.05, space_time=.01,
                 skip_space=True, skip_run=True, scan_len=10):
        """ Setup scanning
        :cell_time: time (seconds) to beep cell
        :space_time: time (seconds) to beep space
        :skip_space: True - skip space default: True
        :skip_run: True - skip run of equals default: True
        :scan_len: number of items to add to scan list
        """
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
        self.set_skip_space(skip_space)
        self.set_skip_run(skip_run)
        self.set_scan_len(scan_len)
        self.skip_color = None          # color of run if any
        self._display_item = None
        self.profile_running = False    # Setup disabled profiling


    def set_scan_len(self, scan_len):
        """ Set number of items to current scan list
        :scan_len: number of items to add each trip
        """
        self.scan_len = scan_len

    def flip_skip_space(self):
        """ Flip skipping spaces
        """
        skip_space = self.get_skip_space()
        self.set_skip_space(not skip_space)


    def is_skip_space(self):
        return self.skip_space 

    def get_skip_space(self):
        return self.skip_space 
    
    def set_skip_space(self, val):
        self.skip_space = val


    def is_skip_run(self):
        return self.skip_run  
    
    def set_skip_run(self, val):
        self.skip_run = val

    def flip_skip_run(self):
        """ Flip skipping runs
        """
        skip_run = self.is_skip_run()
        self.set_skip_run(not skip_run)
                
    def start_scanning(self, cells=None):
        """ Start scanning process
        eye(center) is bottom / middle
        """
        SlTrace.lg("start_scanning")
        if cells is None:
            cells  = self.get_cells()
        self.scan_cells = cells
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
        SlTrace.lg("Calculating scan_items")
        ###self.forward_path = self.get_scan_path(cells=self.scan_cells)
        ###self.reverse_path = list(reversed(self.forward_path))
        self.setup_get_scan_path()
        self.more_to_get = True
        SlTrace.lg(f"start_scan ")
        self.start_scan()


    def setup_get_scan_path(self, cells=None):
        """ Setup getting path in parts
        :cells: cells to scan
        """
        self.scan_items = self.get_scan_items(cells=cells)
        self.scan_items_index = 0
        self.scan_items_end = len(self.scan_items)      # < end

    def get_scan_items(self, cells=None):
        """ Get ordered list of scanning locations, skipping based
        on settings self.skip_space, self.skip_run
        :cells: cells dictionary by ix,iy default: self.cells
        :returns: Rqw list of ScanPathItem in the order to scan
        """
        scan_items_raw = self.get_scan_items_raw(cells=cells)
        items_raw_left = scan_items_raw[:]    # Depleated as we go
        scan_items = []         # Populated with used scan items
        
        max_run_skip = 10               # Maximum to run skip at a time
        max_space_skip = 50             # Maximum to space skip at a time     
        run_color = None                # color in run
        while len(items_raw_left) > 0:              # Loop over raw items
            n_skip = 0                              # avoid too long a skip
            while len(items_raw_left) > 0:          # In skipping loop
                item = items_raw_left.pop(0)
                if self.skip_space and item.cell is None:
                    n_skip += 1
                    if n_skip > max_space_skip:
                        break
                    continue
                
                elif self.skip_run and item.cell is not None:
                    if len(items_raw_left) == 0:
                        break               # Don't skip end of path
                    color = item.cell.color_string()
                    if run_color is None or run_color != color:
                        run_color = color
                        break                   # Starting run
                    next_item = items_raw_left[0]
                    if next_item.cell is None or next_item.cell.color_string() != color:
                        break       # Include end of run
                    if next_item.cell.iy != item.cell.iy:
                        break       # Include new row
                    n_skip += 1
                    if n_skip > max_run_skip:
                        break
                else:
                    break
                SlTrace.lg(f"skipping {item}", "scanning")
            SlTrace.lg(f"scanning {item}", "scanning")
            if item.cell is None:
                SlTrace.lg(f"None: scanning {item}")
                
            scan_items.append(item)
        return scan_items
                
    def get_scan_items_raw(self, cells=None):
        """ Get ordered list of scanning locations, no skipping
            Scanning order is bottom to top, with alternating
            left-to-right then right-to-left so as to make a contiguous
            path
        :cells: cells dictionary by ix,iy default: self.cells
        :returns: Rqw list of ScanPathItem in the order to scan
        """
        if cells is None:
            cells = self.get_cells()
        if len(cells) == 0:
            return []       # No cells to scann
        ix_ul, iy_ul, ix_lr, iy_lr = self.bounding_box_ci(cells=cells)
        scan_items = []
        left_to_right = True    # Start going left to right
        for iy in range(iy_lr, iy_ul-1, -1):    # bottom to top
            if left_to_right:
                for ix in range(ix_ul, ix_lr+1):
                    cell = cells[(ix,iy)] if (ix,iy) in cells else None
                    scan_items.append(ScanPathItem(ix=ix, iy=iy, cell=cell))
            else:
                for ix in reversed(range(ix_ul, ix_lr+1)):
                    cell = cells[(ix,iy)] if (ix,iy) in cells else None
                    scan_items.append(ScanPathItem(ix=ix, iy=iy, cell=cell))
            left_to_right = not left_to_right
        return scan_items

    def get_more_scan_path(self, nitem=10):
        """ Get ordered list of scanning locations
            Scanning order is bottom to top, with alternating
            left-to-right then right-to-left so as to make a contiguous
            path
        :cells: cells dictionary by ix,iy default: self.cells
        :nitem; number of items to return
        :returns: list of ScanPathItem in the order to scan at most
                    nitem per call
                    Last return len < nitem
        """
        """ Populate with sinewave appropriate with locations
        We assume we can hold enough pysinewave instances each set for stereo.
        """
        SlTrace.lg(f"Add {nitem} new items at {self.scan_items_index} with sound")
        if self.profile_running:
            self.pr = cProfile.Profile()
            self.pr.enable()
        begin_time = time.time()
        next_items = []
        for _ in range(nitem):
            if self.scan_items_index >= self.scan_items_end:
                return next_items
            sp_ent = self.scan_items[self.scan_items_index]
            next_items.append(sp_ent)
            self.scan_items_index += 1
            ix,iy = sp_ent.ix,sp_ent.iy
            vol_left, vol_right = self.get_vol(ix=ix, iy=iy,
                                               eye_ixy_l=self.eye_ixy_l,
                                               eye_ixy_r=self.eye_ixy_r)
            if sp_ent.cell is None:
                pitch = self.color2pitch("OTHER")
            else:
                pitch = self.get_pitch(ix=ix, iy=iy)
            sinewave_stereo = SineWaveNumPy(pitch = pitch,
                                    duration_s=self.cell_time*4,
                                    decibels_left=vol_left,
                                    decibels_right=vol_right)
            sp_ent.sinewave_stereo = sinewave_stereo
        end_time = time.time()
        dur_time = end_time-begin_time
        if self.profile_running:
            self.pr.disable()
            s = io.StringIO()
            sortby = 'cumulative'
            ps = pstats.Stats(self.pr, stream=s).sort_stats(sortby)
            ps.print_stats()
            SlTrace.lg(s.getvalue())
        
        SlTrace.lg(f"{nitem} cells: time: {dur_time:.3f} seconds")
        return next_items
    
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
        SlTrace.lg(f"\nl-r: {vol_l-vol_r:.2f}", "sound_volume")
        SlTrace.lg(f"{ix},{iy} left vol:{vol_l:.2f}  dist:{dist:.2f} eye_ixy_l:{eye_ixy_l}",
                   "sound_volume")
        SlTrace.lg(f"{ix},{iy} right vol:{vol_r:.2f}  dist:{dist:.2f} eye_ixy_r:{eye_ixy_r}",
                   "sound_volume")
        return vol_l,vol_r
        
    
    def start_scan(self):
        """ Start actualscanning, which continues until stop_scan
        is called.
        Path self.forward_path is used, then alternating self.reverse_path,
        and forward_path
        """
        self._scanning = True
        self.using_forward_path = True
        self.forward_path = []
        self.reverse_path = [] 
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
        self.more_to_get = True if (
                self.scan_items_index < self.scan_items_end) else False
        n_skip = 0            # avoid too long
        item = None             # Set iff found
        if len(self.current_scan_path) == 0:
            if self.more_to_get:
                new_items = self.get_more_scan_path(nitem=self.scan_len)
                self.forward_path.extend(new_items)
                self.reverse_path = list(reversed(self.forward_path))
                self.current_scan_path = new_items   # do new ones
            else:
                if self.using_forward_path:
                    self.current_scan_path = self.forward_path[:]   # used up
                    self.using_forward_path = False 
                else:
                    self.current_scan_path = self.reverse_path[:]   # used up
                    self.using_forward_path = True
        if len(self.current_scan_path) > 0: 
            item = self.current_scan_path.pop(0)
            self._display_item = item    
            self.display_item(item)
            self.report_item(item)

        if item is None or item.cell is None:
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
            self._report_item.sinewave_stereo.stop()
            self._report_item = None        # TBD - turn tone off
                
    def report_item(self, item):
        """ Report scanned item
        start tone, to be stopped via report_item_complete
        :item: item being reported via tone
        """
        if item.sinewave_stereo is not None:
            self._report_item = item
            item.sinewave_stereo.play()
        

    def report_item_complete(self):
        """ Report scanned item
        start tone, to be stopped via report_item_complete
        """
        self.remove_report_item()
            
     
    def stop_scanning(self):
        SlTrace.lg("stop_scanning - TBD")
        self.stop_scan()
        

    def set_profile_running(self, val=True):
        """ Set/clear profiler running
        :val: True set profiling default: True
        """
        self.profile_running = val

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
    