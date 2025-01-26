# canvas_copy.py    22Jan2025  crs
"""
Approximate deep copy of tkinter Canvas object
"""
import tkinter as tk

def deep_copy_canvas(canvas, root=None, trace=False):
    """ copy canvas
    :canvas: tk.Canvas
    :root: tk root
            default: create tk.Tk()
    :trace: debug tracing
        default: False
    """
    if root is None:
        root = tk.Tk()
        root.withdraw() # hide window of copy
        
    new_canvas = tk.Canvas(root, width=canvas.winfo_width(), height=canvas.winfo_height())
    new_canvas.pack()
    new_canvas.unsupported = []
    for item in canvas.find_all():
        item_type = canvas.type(item)
        coords = canvas.coords(item)
        options = canvas.itemconfig(item)
        ###for i in range(len(coords)):
        ###    coords[i] = int(coords[i])
        if trace: print(f"\n{item_type}: coords:{coords}")
        #if trace: print(f"{item_type}: options:{options}")
        our_options = {}
        our_opts = ['fill', 'width']
        for opt in our_opts:
            if opt in options:
                our_val = (options[opt])[1:]
                if opt == 'fill' and our_val[-1] == '':
                    continue
                our_options[opt] = our_val[-1]    
        if trace: print(f"{item_type}: our_options:{our_options}")
        if item_type == "rectangle":
            new_canvas.create_rectangle(coords, **options)
        elif item_type == "oval":
            new_canvas.create_oval(coords, **options)
        elif item_type == "line":
            new_canvas.create_line(coords,**our_options)
            #new_canvas.create_line(coords, options)
            pass

        elif item_type == "polygon":
            #new_canvas.create_polygon(coords)
            new_canvas.create_polygon(coords, **our_options)
            
        # Add more item types as needed
        else:
            if trace:
                print(f"\n\nUnsupported item_type:{item_type}")
            new_canvas.unsupported.append(item_type)

    return new_canvas

def canvas_exclude_types(cv, exclude):
    """ Exclude item types
    :cv: canvas
    :items: list of item ids to use
    :exclude: list of types
            default: ['image']
    :returns: list of non-excluded types
    """
    if exclude is None:
        exclude = ['image']
    ok_items = []
    for item in cv.find_all():
        item_type = cv.type(item)
        if item_type not in exclude:
            ok_items.append(item)
    return ok_items

def is_set_opt(option_list):
    """ Check if opt is set, i.e. not default
    :option: option val list (opt_name, v, v,...)
    """
    is_set = False  # Set if any not ''
    opt_name = option_list[0]
    opt_vals = option_list[1:]
    for opt_val in opt_vals:
        if opt_val != '':
            is_set = True
            break
    return is_set

option_settings_cache = {}  # by type by option        
def canvas_show_items(cv, exclude_types=None, show_coords=True,
                      show_options=False,
                      use_value_cache=True):
    """ Show canvas items
    :exclude_types: list of types to exclude
            default: that of canvas_exclude_types
    :show_coords: show coordinates for each item
    :show_options: show item's options as best we can
    :use_value_cache: True - only list settings if
                    different from option_settings_cache
                    update cache with new settings
    :returns: items in canvas
    """
    res = ""
    items = canvas_exclude_types(cv, exclude_types)
    for item in items:
        item_type = cv.type(item)
        if item_type not in option_settings_cache:
            option_settings_cache[item_type] = {}
        item_option_settings_cache = option_settings_cache[item_type]
        coords = cv.coords(item)
        options = cv.itemconfig(item)
        res += "\n   "  # Each item begins new line indented
        res += f" {item_type}:"
        if show_coords:
            res += f"({coords})"
        if show_options:
            for option in options:
                opt_val_is_new = False
                option_list = options[option]
                opt_name = option_list[0]
                val_list = option_list[1:]   # [0] is option name
                if is_set_opt(option_list):
                    if opt_name not in item_option_settings_cache:
                        opt_val_is_new = True
                        item_option_settings_cache[opt_name] = val_list
                    if (not use_value_cache
                        or opt_val_is_new
                        or val_list != item_option_settings_cache[opt_name]):
                        res += f" {opt_name}={val_list}"
                item_option_settings_cache[opt_name] = val_list  # force updates
            
    return res

def canvas_diff(cv1, cv2, show_same=True, exclude_types=None,
                show_items=False, show_coords=False,
                show_options=False,
                use_value_cache=True):
    """ Find differences between canvases
    :cv1: first canvas
    :cv2: second canvas
    :show_same: Show if same
                default: True
    :show_items: List items
                defalut: False
    :show_coords: show coordinates
                default: False
    :show_options: show items' options
                default: False
    :exclude_types: list of types to exclude
            default: canvas_exclude_types default
    :use_value_cache: True - use value cache to 
                    minimize output
                default: True
    :returns: string with description
    """
    res = ""    # Result string
    items1 = canvas_exclude_types(cv1, exclude_types)
    items2 = canvas_exclude_types(cv2, exclude_types)
    cmp_len = len(items1) - len(items2) # < 0, == 0, > 0
    if cmp_len == 0:
        if show_same:
            res += f"same len: {len(items1)}"
    else:
        res += f"lengths differ"
        res += f" (1): {len(items1)}"
        res += f" (2): {len(items2)}"
    
    if cmp_len == 0:
        nsame = 0
        first_same = -1
        last_same = -1
        first_diff = -1
        first_diff_type1 = ""
        first_diff_coords1 = ""
        first_diff_type2 = ""
        first_diff_coords2 = ""
        last_diff = -1
        for i in range(len(items1)):
            item1_type = cv1.type(i)
            item1_coords = cv1.coords(i)
            item1_options = cv1.itemconfig(i)
            item2_type = cv2.type(i)
            item2_coords = cv2.coords(i)
            item2_options = cv2.itemconfig(i)
            same_type = False
            same_coords = False
            if item1_type == item2_type:
                same_type = True
                if item1_coords == item2_coords:
                    same_coords = True
            if same_type and same_coords:
                nsame += 1
                if first_same == -1:
                    first_same = i
                last_same = i
            else:
                if first_diff < 0:
                    first_diff = i
                    first_diff_type1 = item1_type
                    first_diff_type2 = item2_type
                    first_diff_coords1 = item1_coords
                    first_diff_coords2 = item2_coords
                last_diff = i
        if first_diff < 0:
            if show_same:
                res += " all same type, coords"
        else:
            res += f" first diff at {i}"
            if first_diff_type1 == first_diff_type2:            
                res += f" types both: {first_diff_type1}"
                res += f" coords: (1){first_diff_coords1} (2){first_diff_coords2}"
            else:
                res += " type (1) {first_diff_type1} != (2) {first_diff_type2}"
    if show_items:
        cv1_show = canvas_show_items(cv1, show_coords=show_coords,
                                     show_options=show_options,
                                     use_value_cache=use_value_cache)
        res += f"\n    (1) {cv1_show}"
        cv2_show = canvas_show_items(cv2, show_coords=show_coords,
                                     show_options=show_options)
        res += f"\n    (2) {cv2_show}"                  
    return res

if __name__ == '__main__':
    from turtle import *    # Bring in turtle graphic functions
    speed("fastest")
    colors = ["red","orange","yellow",
            "green"]

    canvas_copies = []     # snapshots 
    screen = getscreen()
    cv = screen.getcanvas()

    cvc = deep_copy_canvas(cv)
    canvas_copies.append(cvc)
    for colr in colors:
        width(40)
        color(colr)
        forward(200)
        right(90)
        cvc = deep_copy_canvas(cv)
        canvas_copies.append(cvc)
    #done()
    
    #Look for unsupported types in last copy
    for ut in canvas_copies[-1].unsupported:
        print(f"Unsupported type: {ut}")
    

    for i, cvc in enumerate(canvas_copies):
        cv = cvc
        if i < 1:
            cv2 = cv
            continue
        else:
            cv1 = cv2
            cv2 = cvc
        res = canvas_diff(cv1, cv2, show_items=True,
                          show_coords=False,
                          show_options=True,
                          use_value_cache=True)
        print(f"\ncv(diff {i-1} to {i}: {res}")    