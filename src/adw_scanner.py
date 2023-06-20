#adw_scanner.py    09Mar2023  crs, Author
"""
Scanning support
The idea is to rapidly scan the grid giving audio tonal feedback as to the 
contents
"""
import math
import time
import copy
import cProfile, pstats, io         # profiling support

from sinewave_numpy import SineWaveNumPy

from select_trace import SlTrace
from sinewave_beep import SineWaveBeep
from adw_perimeter import AdwPerimeter

"""
scan path item to facilitate fast display, sound and operation
"""
class ScanPathItem:
    
    def __init__(self, ix, iy, cell=None,
                 sinewave_numpy=None,      # if not scan_use_tone
                 pitch=None,
                 dur=None,
                 dly=None,
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
        self.sinewave_numpy = sinewave_numpy  # Setup after init
        self.pitch = pitch          # Setup if scan_use_tone
        self.dur = dur              # Setup if scan_use_tone
        self.dly = dly
        self.sinewave_left = sinewave_left      # ??? OBSOLETE
        self.sinewave_right = sinewave_right    # ??? OBSOLETE

    def __str__(self):
        st = f"ScanPathItem: {self.ix},{self.iy}"
        st += f" {self.cell}" if self.cell is not None else " space"
        return st
    
class AdwScanner:

    def __init__(self, fte, cell_time=.1, space_time=.1,
                 skip_space=True, skip_run=True, scan_len=10,
                 skip_run_max = 10,        # Maximum to run skip at a time
                 skip_space_max = 3,             # Maximum to space skip at a time
                 sample_rate = 44100,
                 space_pitch=None,
                 no_item_wait=False, scan_use_tone=True,
                 scan_coverage="perimeter",
                 add_tone_preamble=False,
                 combine_wave=False,
                 n_combine_wave=2):
        """ Setup scanning
        :fte: front end instance
        :cell_time: time (seconds) to beep cell
        :space_time: time (seconds) to beep space
        :skip_space: True - skip space default: True
        :skip_space_max: maximum number of spaces to skip per time
        :skip_run: True - skip run of equals default: True
        :skip_run_max: maximum number run per time
        :scan_len: number of items to add to scan list
        :sample_rate: default tone sample rate
        :space_pitch: scanning space pitch default: "SCAN_BLANK"
        :no_item_wait: True - don't wait for items to complete
        :scan_use_tone: True use play_tone for scanning
                        same as cursor movements
                        default: True
        :scan_coverage: cell coverage strategy
                            "area" - cover rectangular region
                            "perimeter" - cover perimeter of figure
                        default: perimeter
        :add_tone_preamble: Add tone to sync beginning of scan wave
                        default: No tone preamble added
        :combine_wave: waveforms are combined to speed presentation
                        default: False
        :n_combine_wave: number of sections combined wave 
                        default: 4
        """
        #space_time = 1      # TFD
        #cell_time = 2      # TFD
        self.fte = fte
        self.adw = fte.adw
        self.speaker_control = self.adw.speaker_control
        self.mw = self.adw.mw
        self.canvas = self.adw.canvas
        self.cell_time = cell_time
        self.space_time = space_time
        self.sample_rate = sample_rate
        self._scan_item = None          # Scanning image
        self._display_item = None       # Currently displayed item, if any
        self._scan_item_tag = None             # Scanning item tag
        self._report_item = None        # Latest scanning report item
        self._scanning = False          # Currently scanning
        self.set_skip_space(skip_space)
        self.set_skip_space_max(skip_space)
        self.set_skip_run(skip_run)
        self.set_skip_run_max(skip_run_max)
        self.set_scan_len(scan_len)
        self.skip_color = None          # color of run if any
        self._display_item = None
        self.profile_running = False    # Setup disabled profiling
        self.set_no_item_wait(no_item_wait)
        self._in_display_item = False   # Avoid recursion
        self._in_update = 0
        self.sound_queue_back_log = 1  # Target to keep
        self.scan_loop_proc_time_ms = 200   # queue cking loop time
        self.scan_use_tone = scan_use_tone
        self.add_tone_preamble = add_tone_preamble
        self.set_combine_wave(combine_wave)
        self.n_combine_wave = n_combine_wave
        if space_pitch is None:
            self.space_pitch = SineWaveBeep.color2pitch("SCAN_SPACE")
            self.scan_loop_checking = None      # set if after alive
        self.scan_coverage = scan_coverage

    def set_cell_time(self, time):
        """ Set cell tone duration hoped
        :time: cell time in seconds
        """
        self.cell_time = time

    def set_space_time(self, time):
        """ Set space tone duration hoped
        :time: cell time in seconds
        """
        self.space_time = time

    def set_space_pitch(self, pitch):
        """ Set space tone duration hoped
        :tone: space tone (pitch)
        """
        self.space_pitch = pitch

    def set_combine_wave(self, val=True):
        """ Set/clear combine_wave mode
        :val: set combine_wave default: True - do combine wave
        """
        self.combine_wave = val

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

    def set_skip_space_max(self, val):
        self.skip_space_max = val


    def is_skip_run(self):
        return self.skip_run

    def set_skip_run(self, val):
        self.skip_run = val

    def set_skip_run_max(self, val):
        self.skip_run_max = val

    def flip_skip_run(self):
        """ Flip skipping runs
        """
        skip_run = self.is_skip_run()
        self.set_skip_run(not skip_run)

    def set_scanning(self, cells=None):
        """ Setup for scanning or any other cell based operation
        which requires cell placement informations
        e.g. volume vs position
        :cells: cells to scan
            default: self.get_cells()
        """
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

    def start_scanning(self, cells=None):
        """ Start scanning process
        eye(center) is bottom / middle
        """
        SlTrace.lg("start_scanning")
        self.set_scanning()
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

        run_color = None                            # color in run
        while len(items_raw_left) > 0:              # Loop over raw items
            n_skip = 0                              # avoid too long a skip
            while len(items_raw_left) > 0:          # In skipping loop
                item = items_raw_left.pop(0)
                if self.skip_space and item.cell is None:
                    if n_skip == 0:
                        scan_items.append(item) # Include first space
                    else:
                        if len(items_raw_left) > 0:
                            next_item = items_raw_left[0]
                            if next_item.cell is not None:
                                #scan_items.append(item)     # Include last space
                                break                       # Quit space run
                    n_skip += 1
                    if n_skip > self.skip_space_max:
                        scan_items.append(item)     # Add in space in long 
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
                    if n_skip > self.skip_run_max:
                        break
                else:
                    break
                SlTrace.lg(f"skipping {item}", "scanning")
            SlTrace.lg(f"scanning {item}", "scanning")
            if item.cell is None:
                SlTrace.lg(f"None: scanning {item}")

            scan_items.append(item)
        if SlTrace.trace("scanning"):
            SlTrace.lg(f"get_scan_items returns:")
            for si in scan_items:
                SlTrace.lg(f"  {si}")
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

        if self.scan_coverage == "perimeter":
            self.skip_run = False   # skip_run is too aggressive
            scan_items = self.get_perimeter_items(cells=cells)
            return scan_items

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

    def get_perimeter_items(self, cells=None):
        """ get items on the perimeter
        :cells: cells on which perimeter is based
                default: self.get_cells()
        :returns: Raw list of ScanPathItem based on perimeter
        """
        if cells is None:
            cells = self.get_cells()
        adwp = AdwPerimeter(adw=self.adw, cells=cells)
        cell_list = adwp.get_perimeter()
        scan_items = []
        for cell in cell_list:
            ix,iy = (cell.ix,cell.iy)
            scan_items.append(ScanPathItem(ix=ix, iy=iy, cell=cell))
        return scan_items

    def get_more_scan_path(self, nitem=10, use_sinewave_numpy=False):
        """ Get ordered list of scanning locations
            Scanning order is bottom to top, with alternating
            left-to-right then right-to-left so as to make a contiguous
            path
        :cells: cells dictionary by ix,iy default: self.cells
        :nitem; number of items to return
        :use_sinewave_numpy: if present add sinewave_numpy entry to each item
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
        vol_adj = self.get_vol_adj()
        SlTrace.lg(f"Scanning vol_adj: {vol_adj}")
        for _ in range(nitem):
            if self.scan_items_index >= self.scan_items_end:
                return next_items
            sp_ent = self.scan_items[self.scan_items_index]
            next_items.append(sp_ent)
            self.scan_items_index += 1
            ix,iy = sp_ent.ix,sp_ent.iy
            volume = self.get_vol(ix=ix, iy=iy)
            vol_left, vol_right = volume
            vol_adj = self.get_vol_adj()
            if abs(vol_adj) > 1.e-10:  # Only if non-trivial
                vol_left += vol_adj
                vol_right += vol_adj
            if sp_ent.cell is None:
                pitch = self.space_pitch
                item_time = self.space_time
            else:
                pitch = self.get_pitch(ix=ix, iy=iy)
                item_time = self.cell_time
            sp_ent.pitch = pitch
            sp_ent.dur = item_time
            sp_ent.vol = (vol_left, vol_right)
            if not self.scan_use_tone or use_sinewave_numpy:
                sinewave_numpy = SineWaveNumPy(pitch = pitch,
                                               duration=item_time,
                                               decibels_left=vol_left,
                                               decibels_right=vol_right)
                sp_ent.sinewave_numpy = sinewave_numpy
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

    def get_vol(self, ix, iy, eye_ixy_l=None, eye_ixy_r=None):
        """ Get tone volume for cell at ix,iy
        volume(left,right)
        Volume(in decibel): k1*(k2-distance from eye), k1=1, k2=0
        :ix: cell ix
        :iy: cell iy
        :eye_xy_l: left eye/ear at x,y default: self.eye_xy_l
        :eye_xy_r: right eye/ear at x,y  default: self.eye_xy_r
        return: volume(left,right) in decibel
        """
        if eye_ixy_l is None:
            eye_ixy_l = self.eye_ixy_l
        if eye_ixy_r is None:
            eye_ixy_r = self.eye_ixy_r
        eye_ix_l, eye_iy_l = eye_ixy_l
        eye_ix_r, eye_iy_r = eye_ixy_r
        eye_ix = (eye_ix_l+eye_ix_r)/2
        eye_iy = (eye_iy_l+eye_iy_r)/2
        dist = math.sqrt((ix-eye_ix)**2 + (iy-eye_iy)**2)   # average dist
        k1 = 15
        k1 = 2     # TFD - quieter
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
        self.first_scan = True      # Used if combine_wave
        self.using_forward_path = True
        self.forward_path = []
        self.reverse_path = []
        self.current_scan_path = []     # let scan_path_item setup
        self.scan_loop_checking = self.mw.after(0, self.scan_loop_proc)
        self.mw.after(0,self.scan_path_item)

    def scan_loop_proc(self):
        """ Keep speaker_control moderately full of scan path items
        """
        if self._scanning and not self.combine_wave:
            #while (self.get_sound_queue_size()
            #        < self.sound_queue_back_log):
            #    self.scan_path_item()
            if self.get_sound_queue_size() < 1:
                self.scan_path_item()
            self.scan_loop_checking = self.mw.after(self.scan_loop_proc_time_ms,
                                                    self.scan_loop_proc)

    def stop_scan(self):
        """ Stop current scan
        """
        if not self._scanning:
            return      # Not scanning - no disrupting 

        self._scanning = False
        if self.scan_loop_checking is not None:
            self.mw.after_cancel(self.scan_loop_checking)
            self.scan_loop_checking = None
        self.remove_display_item()
        self.remove_report_item()
        self.speaker_control.stop_scan()


    def scan_path_item(self):
        """Process next entry in self.current_path, removing item from
        list.  If at end of path, add next path, switching between
        forward_path and reverse_path
        """
        if not self._scanning:
            return

        if self.combine_wave:
            self.do_combine_wave()
            return

        self.more_to_get = True if (
                self.scan_items_index < self.scan_items_end) else False
        item = None             # Set iff found
        if len(self.current_scan_path) == 0:
            if self.more_to_get:
                new_items = self.get_more_scan_path(nitem=self.scan_len)
                self.forward_path.extend(new_items)
                self.reverse_path = list(reversed(self.forward_path))
                self.current_scan_path = new_items   # do new ones
            else:
                if self.scan_coverage == "perimeter":
                    self.current_scan_path = self.forward_path[:]   # used up
                else:
                    if self.using_forward_path:
                        self.current_scan_path = self.forward_path[:]   # used up
                        self.using_forward_path = False
                    else:
                        self.current_scan_path = self.reverse_path[:]   # used up
                        self.using_forward_path = True

        if len(self.current_scan_path) > 0:
            item = self.current_scan_path.pop(0)
            SlTrace.lg(f"\nitem: {item}", "scanning")
            self._display_item = item
            self.display_item(item)
            if self.scan_use_tone:
                self.speaker_control.play_tone(
                    pitch=item.pitch, dur=item.dur,
                    volume=item.vol, dly=item.dly)
                self.update()
                self.speaker_control.wait_while_busy()
                self.update()

            else:
                ###if self.no_item_wait and not self.more_to_get:
                if self.no_item_wait:
                    self.report_item(item, no_wait = True)
                    self.mw.after(int(self.cell_time*1000),
                                  self.scan_path_item_complete)
                else:
                    self.report_item(item, after=self.scan_path_item_complete)


    def scan_path_item_complete(self):
        """ Complete current item where necessary
        """
        self.report_item_complete()
        if not self.no_item_wait:
            if self._scanning:
                self.mw.after(0, self.scan_path_item)

    def do_combine_wave(self):
        """ Do combined wave scan
            creating wave(s) before first scan
        """
        if not self._scanning:
            return

        if self.first_scan:
            self.first_scan = False
            self.wave_index = -1        # Bumped before do_wave
            if self.scan_loop_checking is not None:
                self.mw.after_cancel(self.scan_loop_checking)
                self.scan_loop_checking = None
            self.forward_path = self.get_more_scan_path(nitem=
                                                        len(self.scan_items),
                                                        use_sinewave_numpy=True)
            self.forward_paths = self.divide_path(self.forward_path,
                                                  n_section=self.n_combine_wave)
            if self.add_tone_preamble:
                self.forward_path[0] = self.add_preamble(self.forward_path[0])
            self.forward_waves = []
            for path in self.forward_paths:
                wave = self.make_combine_wave(path)
                self.forward_waves.append(wave)
        self.wave_index += 1
        if self.wave_index >= self.n_combine_wave:
            self.wave_index = 0     # Restart around
        self.do_wave(self.forward_waves[self.wave_index],
                     index=self.wave_index)
        '''
        else:
            self.do_wave(self.reverse_wave)
        self.using_forward_path = not self.using_forward_path
        '''

    def divide_path(self, path, n_section):
        """ Divide scan path into almost even sections
        :path: scan path
        :n_section: number of sections
        :returns: list of list of ScanPathItems
        """
        path_sects = []         # path sections
        items_left = path[:]    # Depopulate using all but no more
        n_per_sect = len(path)//n_section
        if n_per_sect*n_section < len(path):
            n_per_sect += 1     # Use them up
        for _ in range(n_section):
            path_sect = []
            for _ in range(n_per_sect):
                if len(items_left) > 0:
                    path_sect.append(items_left.pop(0))
            path_sects.append(path_sect)
        SlTrace.lg(f"divide_path: {len(path)} items in {n_section} sections")
        for i in range(n_section):
            item = path_sects[i][0]
            SlTrace.lg(f"{i}: row: {item.iy+1} col: {item.ix+1}")

        return path_sects


    def add_preamble(self, items, ptype="BEGINNING"):
        """ Add preamble to item list to aid in identification
        :items: item list of (ScanPathItem)
        :ptype: preamble type default: "BEGINNING"
        """
        items_new = items[:]
        # beginning
        if len(items) == 0:
            item_model = ScanPathItem(ix=0, iy=0, sinewave_numpy=None)
            SlTrace.lg("Empty list")
        else:
            item_model = copy.copy(items[0])
        ix_start,iy_start = item_model.ix,item_model.iy
        sinewave_numpy = item_model.sinewave_numpy
        if sinewave_numpy is None:
            sample_rate = self.sample_rate
        else:
            sample_rate =  sinewave_numpy.sample_rate
        nitem = 5
        cpsp = SineWaveBeep.cpsp        # Pitch spacing
        pitch_start = SineWaveBeep.color2pitch("SPACE") + 15*cpsp
        preamble_items = []
        vol_adj = self.get_vol_adj()
        SlTrace.lg(f"Scanning vol_adj: {vol_adj}")
        for i in range(nitem):
            ix = ix_start
            iy = iy_start-i
            volume = self.get_vol(ix=ix, iy=iy)
            vol_left, vol_right = volume
            pitch = pitch_start
            duration = self.cell_time*2
            if abs(vol_adj) > 1.e-10:  # Only if non-trivial
                vol_left += vol_adj
                vol_right += vol_adj
            sinewave_numpy = SineWaveNumPy(pitch = pitch,
                                           duration=duration,
                                           decibels_left=vol_left,
                                           decibels_right=vol_right,
                                           sample_rate=sample_rate)
            preamble_item = ScanPathItem(ix=ix, iy=iy,
                                         sinewave_numpy=sinewave_numpy)
            preamble_items.append(preamble_item)
        items_new[:0] = preamble_items[:]
        return items_new

    def do_wave(self, scan_wave,  index):
        """ Process sound wave, returning when completed
        :index:  index into self.forward_path for identification
        """
        if not self._scanning:
            return

        current_path = self.forward_paths[index]
        if len(current_path) > 0:
            current_item = current_path[0]
            current_ix,current_iy = current_item.ix,current_item.iy
            self.speak_text(msg=f"r{current_iy+1} c{current_ix+1}",
                            dup_stdout=False, rate=350, volume=1)
        self.play_waveform(sinewave_numpy=scan_wave, calculate_dur=True,
                           after=self.do_wave_end)
        #self.speaker_control.wait_while_busy()

    def do_wave_end(self):
        if not self._scanning:
            return

        self.mw.after(0, self.do_combine_wave)

    def make_combine_wave(self, item_path):
        """ Create a SinewaveNumpy.sinewave_numpy ndarray of the items components
        :itempath: list of ScanPathItem s with  sinewave_numpy   field set 
                        Note that get_scan_items_raw needs self.
        :returns: SpeakerWaveform of combined item waveforms
        """
        SlTrace.lg(f"make_combine_wave: {len(item_path)} items")
        swnps = [sp_ent.sinewave_numpy for sp_ent in item_path]
        cw_swnp = SineWaveNumPy.concatinate(swnps)
        return cw_swnp

    def color2pitch(self, color):
        return SineWaveBeep.color2pitch(color)


    def display_item(self, item):
        """ Update current scanner position display
        :item: current scan path item
        """
        if self._in_display_item:
            return

        if self._display_item is not None:
            self.remove_display_item()
        canvas = self.canvas
        ixy = item.ix, item.iy
        x_left,y_top, x_right,y_bottom = self.get_win_ullr_at_ixy_canvas(ixy)
        self._scan_item_tag = canvas.create_rectangle(x_left,y_top,
                                                      x_right,y_bottom,
                                                      outline="black", width=2)
        self.update()
        self._display_item = item
        self._in_display_item = False

    def remove_display_item(self):
        """ remove current display item, if any
        """
        if  self._display_item is not None:
            canvas = self.canvas
            if self._scan_item_tag is not None:
                self.canvas.delete(self._scan_item_tag)
                self._scan_item_tag = None
        self._display_item = None

    def remove_report_item(self):
        """ Remove any noise for reported item
        """
        if self._report_item is not None:
            self._report_item.sinewave_numpy.stop()
            self._report_item = None        # TBD - turn tone off

    def report_item(self, item, after=None, no_wait=False):
        """ Report scanned item
        start tone, to be stopped via report_item_complete
        :item: item being reported via tone
        :after: Function to call (win.after) after report completes
                default: no call
        :no_wait: True - no waiting for completion
                default: False - wait for completion
        """
        if no_wait:
            #self.remove_display_item()  # Remove previous item, if any
            if item is not None and item.cell is not None:
                sinewave_numpy = item.sinewave_numpy
                if sinewave_numpy is not None:
                    self._report_item = item
                    self.play_waveform(sinewave_numpy=sinewave_numpy)
            self.mw.after(int (self.cell_time*1000), self.scan_path_item_complete)
        else:
            sinewave_numpy = item.sinewave_numpy
            if sinewave_numpy is not None:
                self._report_item = item
                self.play_waveform(sinewave_numpy=sinewave_numpy,
                                   after=after)
            else:
                self.mw.after(0, after) # Just go on


    def report_item_complete(self):
        """ Report scanned item
        start tone, to be stopped via report_item_complete
        """
        self.remove_report_item()


    def stop_scanning(self):
        SlTrace.lg("stop_scanning")
        self.stop_scan()

    def set_no_item_wait(self, val=True):
        """ set/clear no_item_wait mode
        :val: True set value True default: True
        """
        self.no_item_wait = val


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

    def get_speaker_control(self):
        """ Get speech control
        """
        return self.speaker_control

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

    def speak_text(self, msg, dup_stdout=True,
                   msg_type=None,
                   rate=None, volume=None):
        """ Speak text, if possible else write to stdout
        :msg: text message, iff speech
        :dup_stdout: duplicate to stdout default: True
        :msg_type: type of speech default: 'REPORT'
            REPORT - standard reporting
            CMD    - command
            ECHO - echo user input
        :rate: speech rate words per minute
                default: 240
        :volume: volume default: .9            
        """
        self.adw.speak_text(msg=msg, msg_type=msg_type,
                            dup_stdout=dup_stdout,
                            rate=rate, volume=volume)

    def update(self):
        """ Update display
        """
        if self._in_update>3:
            return
        self._in_update += 1
        self.adw.update()
        self._in_update -= 1

    def mainloop(self):
        self.mw.mainloop()

    """
    ############################################################
                       Links to speaker_control
    ############################################################
    """

    def clear(self):
        """ Clear pending output
        """
        self.speaker_control.clear()

    def force_clear(self):
        """ Clear all pending and reset
        """
        self.speaker_control.force_clear()

    def get_vol_adj(self):
        """ Get current volume adjustment
        :returns: current vol_adjustment in db
        """
        return self.speaker_control.get_vol_adj()

    def get_sound_queue_size(self):
        return self.speaker_control.get_sound_queue_size()

    def play_waveform(self, sinewave_numpy,
                      calculate_dur=False,
                      after=None):
        """ play waveform
        :sinewave_numpy: waveform (SinewaveNumPy stereo_waveform)
        :after: function to call after play completes
                default: no call
        """
        swnp = sinewave_numpy
        self.speaker_control.play_waveform(ndarr=swnp.wf_ndarr,
                                           dur=swnp.duration,
                                           dly=swnp.delay,
                                           calculate_dur=calculate_dur,
                                           after=after)

    