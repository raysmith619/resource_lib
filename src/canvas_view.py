#canvas_view.py    17Jun2022  crs
"""
tinker Canvas subclass with additional access to stored items
"""
import tkinter as tk

from select_trace import SlTrace

SlTrace.clearFlags()

win_height = 800
win_width = 800
    


class CanvasView(tk.Canvas):
    """ Support Canvas with more item viewing optons
        The most useful is the facility to track and list
        new canvas items
    """
    def __init__(self, master, mksz=10, drag_pen=False,
                 list_marks=True, annotate_tag=None,
                  **kwargs):
        """ Setup canvas
        :master: canvas master
        :list_marks: list new canvas items
        :mksz: mark size
                default: 10
        :drag_pen: drag pen from previous marker, if one
                    default: no dragging
        :annotate_tag: tag to avoid reporting as item
                        default="ANN"
        """
        super().__init__(master, **kwargs)
        self.list_marks = list_marks
        self.mksz = mksz
        self.drag_pen = drag_pen
        self.tk_item_samples = {}   # latest type options, for abbreviation
        self.last_new_item_id = 0   # id of last listed id
        self.mark_it_x = self.mark_it_y = 0
        self.mark_it_no = 0         # Simple numbering of mark_it calls
        self._color = "blue"
        self.annotate_tag = annotate_tag

    def get_color(self):
        return self._color
    
    def set_color(self, color):
        self._color = color
        return color

    def goto(self, x=None, y=None, drag_pen=None):
        """ mimic turtle goto
        :drag_pen: drag pen - temporary
                default: False no dragging
                previous drag_pen is restored
        """
        drag_pen_prev = self.drag_pen
        if drag_pen is None:
            drag_pen = False
        self.mark_it(x=x, y=y, drag_pen=False)
        self.drag_pen = drag_pen_prev
                   
    def mark_it(self, x=None, y=None, color=None, prefix=None,
                mksz=None, drag_pen=None,
                annotate_tag=None):
        """ Mark canvas and describe canvas object
        :x: x location
        :y: y location
        :color: color of marker
        :prefix: optional prefix on listings
        :mksz: marker size, in pixels
        :drag_pen: drag pen (make line) from previous marking
                default: use previous setting
                        False - no dragging
        :annoteate_tag: annotate tag to differentiate markings
                        default: previous
                        
        """
        if mksz is None:
            mksz = self.mksz    # Use previous
        self.mksz = mksz        # record as default
        if drag_pen is None:
            drag_pen = self.drag_pen
        self.drag_pen = drag_pen
        if color is None:
            color = self.get_color() 
        self.set_color(color)
        if annotate_tag is None:
            annotate_tag = self.annotate_tag
        self.annotate_tag = annotate_tag
        self.mark_it_no += 1
        if prefix is None:
            prefix = (f"mark_it {self.mark_it_no}:")

        if drag_pen:
            width = mksz//2
            if width < 2:
                width = 2
            
            self.create_line(self.mark_it_x, self.mark_it_y,
                             x,y, fill=color, width=width,
                             tags=self.annotate_tag)
        x1 = x-mksz/2
        x2 = x+mksz/2
        y1 = y-mksz/2
        y2 = y+mksz/2
        self.create_oval(x1,y1,x2,y2, fill=color)
        
        if self.list_marks:
            SlTrace.lg(f"{prefix} x={x} y={y} {color}:")
            new_items = self.get_new_items()
            for item in new_items:
                self.show_canvas_item(item)
        self.mark_it_x = x
        self.mark_it_y = y


    def show_coords(self, canvas_coords):
        if canvas_coords is None:
            return 
        if len(canvas_coords) == 0:
            return
        if len(canvas_coords) == 2:
            cc_x1,cc_y1 = canvas_coords
            cc_x2 = cc_y2 = ""
        elif len(canvas_coords) == 4:            
            cc_x1,cc_y1, cc_x2,cc_y2 = canvas_coords
        else:
            return
        SlTrace.lg(f"    win: x1:{cc_x1}, y1:{cc_y1} x2:{cc_x2}, y2:{cc_y2}", "point")

    def get_new_items(self):
        """ get items since last new_items call
        :returns: list of new items
        """
        items = sorted(self.find_all())
        new_items = []
        for item_id in items:
            if item_id > self.last_new_item_id:
                new_items.append(item_id)
        if len(new_items) > 0:
            self.last_new_item_id = new_items[-1]
        return new_items

    def show_canvas_item(self, item_id,
                          prefix=None):
        """ display changing values for item
        """
        if prefix is None:
            prefix = ""
        self.tracking_show_item_id = item_id
        iopts = self.itemconfig(item_id)
        itype = self.type(item_id)
        coords = self.coords(item_id)
        if itype in self.tk_item_samples:
            item_sample_iopts = self.tk_item_samples[itype]
        else:
            item_sample_iopts = None
     
        SlTrace.lg(f"{prefix} {item_id}: {itype} {coords}")
        self.show_coords(coords)
        always_list = ['fill', 'width']  # Check always list
        for key in iopts:
            val = iopts[key]
            is_changed = True     # assume entry option changed
            if key not in always_list:  
                if item_sample_iopts is not None:
                    is_equal = True # Check for equal item option
                    sample_val = item_sample_iopts[key]
                    if len(val) == len(sample_val):
                        for i in range(len(val)):
                            if val[i] != sample_val[i]:
                                is_equal = False
                                break
                        if is_equal:
                            is_changed = False
            if is_changed: 
                SlTrace.lg(f"    {key} {val}")
            self.tk_item_samples[itype] = iopts
        

if __name__ == "__main__":
    win_height = 800
    win_width = 800
    zero_centered = True
    zero_centered = False
    x_min = 0
    x_max = win_width
    y_min = 0
    y_max = win_height
    
    dsz = 20
    width = 10
    offset = 10      # offset from edge
    drag_pen = True
    drag_pen = False
    main_mw = tk.Tk()
    main_mw.title("CanvasView Testing")
    main_mw.geometry(f"{win_height}x{win_width}")
    canvas = CanvasView(main_mw, width=win_width, height=win_height,
                        drag_pen=drag_pen)
    canvas.pack(expand=1, fill='both')


    canvas.mark_it(x=x_min+offset, y=y_max-offset, color="red")
    canvas.mark_it(x=x_max-offset, y=y_min+offset, color="orange")
    canvas.mark_it(x=x_min+offset, y=y_min+offset, color="yellow")
    canvas.mark_it(x=x_max-offset, y=y_max-offset, color="green")


    tk.mainloop()