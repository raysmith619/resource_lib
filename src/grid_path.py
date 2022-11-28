# grid_path.py
"""
Determine predictive following moves
"""

class GridPath:
    def __init__(self, goto_path, pred_len=1, det_len=4, hv_len=2):
        """ Setup path determination
        :goto_path: list of (ix,iy) of recent movement most recent last
        :pred_len: maximum length of predictive cells (ix,iy)
                    default: 3
        :det_len: length of goto path used to determing prediction - usually
                direction of predictive cells
                default: 4
        :hv_len: length after which line is considered horizontal/vertical
        """
        self.goto_path = goto_path
        self.pred_len = pred_len
        self.det_len = det_len
        self.hv_len = hv_len
        
    def find_predictive_list(self, pred_len=None, det_len=None, 
                             goto_path=None, hv_len=None):
        """ Find likely next path (list of cell ixiy)
        :pred_len: maximum length of predictive cells (ix,iy)
                    default: self.pred_len(3)
        :det_len: length of goto path used to determing prediction - usually
                direction of predictive cells
                default: self.det_len(4
        :hv_len: horizontal/vertical run to force consideration as
                 horizontal/vertical
        :returns: list of cell ordered to be the likely next set of cells
        """
        if goto_path is None:
            goto_path = self.goto_path
        if pred_len is None:
            pred_len = self.pred_len
        if det_len is None:
            det_len = self.det_len
        if hv_len is None:
            hv_len = self.hv_len
        
        path_xy = self.find_path_dir_xy(det_len=det_len, 
                             goto_path=goto_path,
                             hv_len = hv_len)
        ##print(f"path_xy: {path_xy}")
        if path_xy == (0,0):
            return []       # No prediction if can't find direction
        
        cell = goto_path[-1]
        if cell is None:
            return []
        
        x_start, y_start = cell.ix, cell.iy
        x_chg, y_chg = path_xy
        x_major = True if abs(x_chg) >= abs(y_chg) else False
        pred_list = []
        if x_major:
            x_chg_norm = x_chg/abs(x_chg)
            y_chg_norm = y_chg/x_chg
        else:
            y_chg_norm = y_chg/abs(y_chg)
            x_chg_norm = x_chg/y_chg
        for i in range(1, pred_len+1):
            pred_x = int(i*x_chg_norm + x_start)
            pred_y = int(i*y_chg_norm + y_start)
            pred_list.append((pred_x,pred_y)) 
             
        return pred_list
        
    def find_path_dir_xy(self, det_len=None, 
                             goto_path=None,
                             hv_len = None):
        """ Get most recent path direction (x,y)
            1. If cells are horizontal or vertical for hv_len cells
            we return the corresponding horizontal/vertical x,y
            
        :det_len: determination length (max) used to determine slope
        :goto_path: list of most recent cells, last first
        :hv_len: length to determine horizontal/vertica
        :returns: (xchg, ychg) - (0,0) == indeterminate slope
        """
        if det_len is None:
            det_len = self.det_len
        if goto_path is None:
            goto_path = self.goto_path
        if hv_len is None:
            hv_len = self.hv_len
        if len(goto_path) < 2:
            return (0,0)        # Need at least two points
        
        cell = goto_path[-1]
        if cell is None:
            return 0,0          # Nothing
        
        x_end,y_end = cell.ix,cell.iy
        ##print(f"end: {x_end},{y_end}")
        if len(goto_path) >= hv_len:
            for i in range(hv_len-1):
                cell = goto_path[-i-2]
                if cell is None:
                    break
                x = cell.ix
                if x != x_end:
                    break
            else:
                cell = goto_path[-hv_len]
                if cell is None:
                    return 0,0
                
                y = cell.iy
                y_chg = y_end-y
                return(0, y_chg)
            
            for i in range(hv_len-1):
                cell = goto_path[-i-2]
                if cell is None:
                    return 0,0
                
                y = cell.iy
                if y != x_end:
                    break
            else:
                cell = goto_path[-hv_len]
                if cell is None:
                    return 0,0
                
                x = cell.ix
                x_chg = x_end-y
                return(x_chg, 0)
            
            det_len = min(det_len, len(goto_path))
            cell = goto_path[-det_len]
            if cell is None:
                return 0,0
            
            x = cell.ix
            x_chg = x_end-x
            y = cell.iy
            y_chg = y_end-y
            return x_chg, y_chg        
        

if __name__ == "__main__":
    print(f"Self Test: {__file__}")
    cells_set = {
            (2,6), (3,6), (4,6), (5,6), (6,6),
            (2,5),               (5,5),
            (2,4),               (5,4),
            (2,3), (3,3), (4,3), (5,3),
            (2,2), (3,2), (4,2), (5,2), (6,2),
         }
    cells = dict.fromkeys(cells_set, 0)
    goto_cells = [(2,6), (2,5), (2,4), (2,3)]
    
    gp = GridPath(goto_path=goto_cells)
    #pred_cells = gp.find_predictive_list()
    #print(f"goto_path:{goto_cells},\npred_cells:{pred_cells}")

    goto_cells = [(1,3), (2,3),
                  (1,2), (2,2), (3,2),
                                 (3,1)]
    pred_cells = gp.find_predictive_list(goto_path=goto_cells)
    print(f"goto_path:{goto_cells},\npred_cells:{pred_cells}")

        