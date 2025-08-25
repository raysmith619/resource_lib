# adw_menus    09Mar2023  crs, Split off from adw_front_end

import wx

from select_trace import SlTrace
from wx_trace_control_window import TraceControlWindow


class MenuDisp:
    """ Menu dispatch table entry
    Supporting multiple mode dispatch (e.g, Dropdown item plus command mode)
    """

    def __init__(self, label, command, underline):
        self.label = label
        self.command = command
        self.underline = underline
        self.shortcut = label[underline].lower()
        self.Properties = None


class AdwMenus:
    def __init__(self, adw_front_end, frame=None):
        """ Setup menus for AudioDrawWindow
        :adw_front_end: (AdwFrontEnd)
        :frame: frame containing menus
        """
        self.fte = adw_front_end
        if frame is None:
            frame = wx.Frame(None)
        self.frame = frame
        self.frame.Show()
        
        self.menu_setup()

    def on_alt_a(self, event):
        """ keep from key-press
        """
        SlTrace.lg("on_alt_a")

    def on_alt_m(self, event):
        """ keep from key-press
        """
        SlTrace.lg("on_alt_m")

    def on_alt_n(self, event):
        """ keep from key-press
        """
        SlTrace.lg("on_alt_n")

    def on_alt_f(self, event):
        """ keep from key-press
        """
        SlTrace.lg("on_alt_f")

    def on_alt_s(self, _=None):
        """ keep from key-press
        """
        SlTrace.lg("on_alt_s")

    def menu_setup(self):
        """ Setup menu system
        """
        # creating a menu instance
        menubar = wx.MenuBar()
        menu_name_list = [
            "file", "magnify","navigate",
            "draw", "scanning", "auxiliary"
            ]
            
        # Settings for each menu    
        menus_settings = {
            "file" : {"heading" : "File"},
            "magnify" : {"heading" : "Magnify"},
            "navigate" : {"heading" : "Navigate"},
            "draw" : {"heading" : "Draw"},
            "scanning" : {"heading" : "Scanning"},
            "auxiliary" : {"heading" : "Auxiliary"},
        }
        
        """ menus_items defines all the menu drop downs
        SEP - specifies a separator line
        
        "name" specifies name and heading
        if value is a str the heading == name
        else name is a tuple with
            name = tuple[0]
            heading = tuple[1]
        """
        
        SEP = {"sep": "sep"}    # Menu item separator
          
        menus_items = {
            "file":
                [
                {"name" : "Open",  "cmd" : self.TBD},
                {"name" : "Save",  "cmd" : self.TBD},
                SEP,
                {"name" : "Log",   "cmd" : self.LogFile},
                {"name" : "Properties",   "cmd" : self.PropertiesFile},
                SEP,
                {"name" : "E&xit",  "cmd" : self.pgm_exit},
                ],
            "magnify" :
                [
                {"name" : "Help", "cmd" : self.mag_help},
                {"name" : ("rem_pos","Remove Pos History"), "cmd" : self.erase_pos_history},
                {"name" : "Select", "cmd" : self.mag_select},
                {"name" : "Expand To &Fill", "cmd" : self.mag_expand_to_fill},
                {"name" : "Expand &Top", "cmd" : self.mag_expand_top},
                {"name" : "View", "cmd" : self.mag_view_cmd},              
                ],
            "navigate" :
                [
                {"name" : ("help","Help"), "cmd" : self.nav_help},
                {"name" : ("add_loc","add At loc"), "cmd" : self.nav_add_loc},
                {"name" : ("no_add_loc","b-remove At loc"), "cmd" : self.nav_no_add_loc},
                {"name" : ("echo on","echo input on"), "cmd" : self.nav_echo_on},
                {"name" : ("hd","echo &off"), "cmd" : self.nav_echo_off},
                {"name" : ("hd","visible cells"), "cmd" : self.nav_make_visible},
                {"name" : ("hd","invisible cells"), "cmd" : self.nav_make_invisible},
                {"name" : ("hd","marked"), "cmd" : self.nav_show_marked},
                {"name" : ("hd","noisy"), "cmd" : self.make_noisy},
                {"name" : ("hd","silent"), "cmd" : self.make_silent},
                {"name" : ("hd","talking"), "cmd" : self.nav_make_talk},
                {"name" : ("hd","log talk"), "cmd" : self.nav_logt},
                {"name" : ("hd","no log tal&k"), "cmd" : self.nav_no_logt},
                {"name" : ("hd","position"), "cmd" : self.nav_say_position},
                {"name" : ("hd","redraw figure"), "cmd" : self.nav_redraw},
                {"name" : ("hd","a&udio beep"), "cmd" : self.nav_audio_beep},
                {"name" : ("hd","q no audio beep"), "cmd" : self.nav_no_audio_beep},
                {"name" : ("hd","x enable mouse navigation"), "cmd" : self.nav_enable_mouse},
                {"name" : ("hd","y disable mouse navigation"), "cmd" : self.nav_disable_mouse},
                ],
            "draw" :
                [
                {"name" : "Help", "cmd" : self.draw_help},
                {"name" : "drawing", "cmd" : self.start_drawing},
                {"name" : "stop_drawing", "cmd" : self.stop_drawing},
                {"name" : "count_cells", "cmd" : self.count_cells},
                ],
            "scanning" :
                [
                {"name" : "Help", "cmd" : self.scan_help},
                {"name" : "c -  combine wave - faster scan", "cmd" : self.scan_combine_wave},
                {"name" : "d - disable combine wave", "cmd" : self.scan_disable_combine_wave},
                {"name" : "f - flip skip space", "cmd" : self.flip_skip_space},
                {"name" : "r - flip skip run", "cmd" : self.flip_skip_run},
                {"name" : "Start scanning", "cmd" : self.start_scanning},
                {"name" : "S&top scanning", "cmd" : self.stop_scanning},
                {"name" : "No item wait", "cmd" : self.scan_no_item_wait},
                {"name" : "Wait for item", "cmd" : self.scan_item_wait},
                ],
            "auxiliary" :
                [
                {"name" : "Trace", "cmd" : self.trace_menu},
                ],
            
        }
        
        self.frame.SetMenuBar(menubar)
        self.menus_cmd_menu_item = {}   # by menu short cut by cmd short cut
                                        # m[menu_sc][menu_item_sc] = cmd
        
        for menu_name in menu_name_list:
            menu_settings = menus_settings[menu_name]
            menu_heading = menu_settings["heading"]
            if "&" not in menu_heading:
                menu_heading = "&" + menu_heading
            menu_sci = menu_heading.find("&")
            menu_sc = menu_heading[menu_sci+1].lower()
            if menu_sc in self.menus_cmd_menu_item:     # Is shortcut in use ?
                raise Exception(f"Duplicate menu shortcut {menu_sc} for"
                        f" menu {menu_heading}")
            else:
                menu_items_scs = self.menus_cmd_menu_item[menu_sc] = {}
            menu = wx.Menu()
            menubar.Append(menu,  menu_heading)
            menu_items = menus_items[menu_name]
            for menu_item_specs in menu_items:
                if "sep" in menu_item_specs:
                    menu_item = menu.Append(wx.ID_SEPARATOR)
                else:
                    menu_cmd = menu_item_specs["cmd"]
                    name_heading = menu_item_specs["name"]
                    if isinstance(name_heading,str):
                        menu_item_heading = menu_item_name = name_heading
                    elif len(name_heading)==1:
                        menu_item_name = menu_item_heading = name_heading[0]
                    elif len(name_heading) == 2:
                        menu_item_name = name_heading[0]
                        menu_item_heading = name_heading[1]
                    if "&" not in menu_item_heading:
                        menu_item_heading = "&" + menu_item_heading
                    menui_sci = menu_item_heading.find("&")
                    menui_sc = menu_item_heading[menui_sci+1].lower()
                    if menui_sc in menu_items_scs:
                        raise Exception(f"Duplicate menu {menu_heading} item {menu_item_heading}"
                                        f" \nshortcut {menui_sc}"
                                f" \nshortcuts in use {list(menu_items_scs)}")
                    else:
                        menu_items_scs[menui_sc] = menu_cmd
   
                    menu_item = menu.Append(wx.ID_ANY, menu_item_heading)
                self.frame.Bind(wx.EVT_MENU, menu_cmd, menu_item)

    def get_menu_cmd(self, menu_sc, mi_sc):
        """ get menu cmd
        :menu_cs: menu shortcut case insensitive
        :mi_cs: menu item shortcut case insensitive
        :returns: menu cmd, if none - None
        """
        menu_sc = menu_sc.lower()
        if menu_sc not in self.menus_cmd_menu_item:
            return None # no menu shortcut
        mcmis = self.menus_cmd_menu_item[menu_sc]
        if mi_sc not in mcmis:
            return None
        
        return mcmis[mi_sc]

    def get_menu_scs(self):
        """ Get list of menu short cuts
        :returns: list of menu shortcuts
        """
        menu_scs = list(self.menus_cmd_menu_item)
        return menu_scs

    def get_menu_item_scs(self, menu_sc):
        """ Get list of menu item short cuts
        :menu_sc: menu shortcut
        :returns: list of menu itme shortcuts
        """
        if menu_sc not in self.menus_cmd_menu_item:
            return None
        
        menu_items = self.menus_cmd_menu_item[menu_sc]
        return list(menu_items) 
              
        
    def file_menu_add_command(self, label, command, underline):
        """ Setup menu commands, setup dispatch for direct call
        :label: add_command label
        :command: command to call
        :underline: short-cut index in label
        """
        self.file_menu.add_command(label=label, command=command,
                                   underline=underline)
        menu_de = MenuDisp(label=label, command=command,
                           underline=underline)

        self.file_dispatch[menu_de.shortcut] = menu_de

    def TBD(self, _=None):
        SlTrace.lg("To be developed")

    def LogFile(self, _=None):
        SlTrace.lg("Show LogFile")

    def PropertiesFile(self, _=None):
        SlTrace.lg("Show PropertiesFile")
                
    def file_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        if short_cut not in self.file_dispatch:
            raise Exception(f"file option:{short_cut} not recognized")
        menu_de = self.file_dispatch[short_cut]
        menu_de.command()

    def File_Open_tbd(self):
        print("File_Open_menu to be determined")

    def File_Save_tbd(self):
        print("File_Save_menu to be determined")


    def draw_help(self, _=None):
        """ Help for drawing
        """
        """ Help - list command (Alt-d) commands
        """
        help_str = """
        Help - list drawing setup commands (Alt-d) commands
        h - say this help message
        d - Start/enable drawing
        s - stop/disable drawing
        c - count cells (squares)
        Escape - flush pending report output
        """
        self.speak_text(help_str)

    """ Magnify support package
    """

    """ Magnify menu commands  """

    def mag_help(self, _=None):
        """ Help for Alt-m commands
        """
        """ Help - list command (Alt-m) commands
        """
        help_str = """
        Help - list magnify commands (Alt-m) commands
        h - say this help message
        l - expand magnify selected region left/right
        s - select/mark magnify region
        u - expand magnify selected region up/down top/bottom
        v - view region (make new window)
        """
        self.speak_text(help_str)

    """ End of Magnify support
    """

    """ Scanning support package
    """

    """ Scanning menu commands  """

    def scan_help(self, _=None):
        """ Help for Alt-s commands
        """
        """ Help - list command (Alt-s) commands
        """
        help_str = """
        Help - list scanning commands (Alt-s) commands
        h - say this help message
        c - combine wave - faster scan
        d - disable combine wave - viewing in window
        k - toggle skip space
        s - Start scanning mode
        t - Stop scanning mode
        n - no_item_wait
        w - wait for items
        """
        self.speak_text(help_str)

    def scan_combine_wave(self, _=None):
        self.set_combine_wave()

    def scan_disable_combine_wave(self, _=None):
        self.set_combine_wave(val=False)

    def scan_no_item_wait(self, _=None):
        self.set_no_item_wait()

    def scan_item_wait(self, _=None):
        """clear no item wait
        """
        self.set_no_item_wait(val=False)

    """ End of Scanning support
    """

    """ Navigate support package
    """

    def nav_help(self, _=None):
        """ Help for Alt-n commands
        """
        """ Help - list command (Alt-n) commands
        """
        help_str = """
        Help - list navigate commands (Alt-n) commands
        h - say this help message
        a - Start reporting position
        b - remove 
        z - stop reporting position
        e - echo input on
        o - echo off
        v - visible cells
        i - invisible cells
        r - redraw figure
        s - silent speech
        t - talking speech
        l - log speech
        m - show marked(even if invisible)
        n - no log speech
        p - report position
        u - audio beep
        d - no audio beep
         Escape - flush pending report output
        """
        self.speak_text(help_str)

    """
    Trace support
    """

    def trace_menu(self, _=None):
        TraceControlWindow()

    """
    Links to front end 
    """
    
    """
    General
    """

    def erase_pos_history(self, _=None):
        self.fte.erase_pos_history()

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
        self.fte.speak_text(msg=msg, msg_type=msg_type,
                            dup_stdout=dup_stdout,
                            rate=rate, volume=volume)

    """
     File links
      most local
    """

    def pgm_exit(self, _=None):
        self.fte.pgm_exit()

    """
    Magnification links
    """

    def mag_select(self, _=None):
        """ Select magnification region
            -rectangle including all figure cells traveled so far
            :returns: True if some selected else False
        """
        return self.fte.mag_select()

    def mag_expand_to_fill(self, _=None):
        """ Expand selection region to enclose figure
        """
        self.fte.mag_expand_to_fill()

    def mag_expand_top(self, _=None):
        """ Expand selection region top/bottom by 20%
        """
        self.fte.mag_expand_top()

    def mag_view(self, cells=None, _=None):
        """ View selected region, creating a new AudioDrawWindow
        """
        self.fte.mag_view(cells=cells)

    def mag_view_cmd(self, _=None):
        """ View selected region (menu dispatch cmd)
        creating a new AudioDrawWindow menu cmd
        _ : event - not used
        """
        self.fte.mag_view()

    """ drawing
    """

    def start_drawing(self, _=None):
        """ Start/enable drawing
        """
        self.fte.start_drawing()

    def stop_drawing(self, _=None):
        """ Stop/disable drawing
        """
        self.fte.stop_drawing()

    def count_cells(self, _=None):
        """ report number of cells in figure
        """
        ###???self.fte.count_cells()
    
    """ End of Magnification links """

    """
     Navigation / Front End links
     """

    def set_enable_mouse(self, val=True):
        """ Enable/Disable mouse dragging operation
        :val: value to set default: True - enable
        """
        self.fte.set_enable_mouse(val=val)

    def is_enable_mouse(self):
        """ Check if mouse dragging enabled
        """
        return self.fte.is_enable_mouse()

    def nav_add_loc(self, _=None):
        self.fte.nav_add_loc()

    def nav_no_add_loc(self, _=None):
        self.fte.nav_no_add_loc()

    def nav_echo_on(self, _=None):
        self.fte.nav_echo_on()

    def nav_echo_off(self, _=None):
        self.fte.nav_echo_off()

    def nav_make_visible(self, _=None):
        self.fte.nav_make_visible()

    def nav_make_invisible(self, _=None):
        self.fte.nav_make_invisible()

    def nav_show_marked(self, _=None):
        self.fte.nav_show_marked()

    def make_noisy(self, _=None):
        self.fte.make_noisy()

    def make_silent(self, _=None):
        self.fte.make_silent()

    def nav_make_talk(self, _=None):
        self.fte.nav_make_talk()

    def nav_logt(self, _=None):
        self.fte.nav_logt()

    def nav_no_logt(self, _=None):
        self.fte.nav_no_logt()

    def nav_say_position(self, _=None):
        self.fte.nav_say_position()

    def nav_redraw(self, _=None):
        self.fte.nav_redraw()

    def nav_audio_beep(self, _=None):
        self.fte.nav_audio_beep()

    def nav_no_audio_beep(self, _=None):
        self.fte.nav_no_audio_beep()

    def nav_enable_mouse(self, _=None):
        self.set_enable_mouse()

    def nav_disable_mouse(self, _=None):
        self.set_enable_mouse(False)

    """ End of Navigation links """

    """
    Scanning support
        through fte
    """

    def set_combine_wave(self, val=True):
        """ Enable/disable combine wave scanning mode
        :val: value for mode
        """
        self.fte.set_combine_wave(val=val)

    def set_no_item_wait(self, val=True):
        """ Set/clear scanning no_wait option
        :val: True - no waiting
        """
        self.fte.set_no_item_wait(val=val)

    def flip_skip_space(self, _=None):
        """ Flip skipping spaces
        """
        self.fte.flip_skip_space()

    def flip_skip_run(self, _=None):
        """ Flip skipping run of equals
        """
        self.fte.flip_skip_run()

    def start_scanning(self, _=None):
        self.fte.start_scanning()

    def stop_scanning(self, _=None):
        self.fte.stop_scanning()

"""
Used to stub out FTE
"""
class FteFake:
    def pgm_exit(self):
        SlTrace.lg("fte.pgm_exit()")
        import sys
        sys.exit()
        
    def speak_text(self, msg, msg_type=None,
                    dup_stdout=True, rate=None,
                    volume=None):
        SlTrace.lg(f"fte.speak_text({msg},"
                    f"msg_type={msg_type}msg)"
                    f")")

    """ mag support"""
    def erase_pos_history(self):
        SlTrace.lg("fte.erase_pos_history")
    def mag_select(self):
        SlTrace.lg("mag_select")    
    def mag_expand_to_fill(self):
        SlTrace.lg("mag_expand_to_fill")    
    def mag_exapnd_top(self):
        SlTrace.lg("mag_exapnd_top")    
    def mag_view(self):
        SlTrace.lg("mag_view")    

    """ nav support"""

    def nav_audio_beep(self, _=None):
        SlTrace.lg("fte.nav_audio_beep")

    def nav_no_audio_beep(self, _=None):
        SlTrace.lg("fte.nav_no_audio_beep")

    def nav_make_visible(self, _=None):
        SlTrace.lg("fte.nav_make_visible")

    def nav_make_invisible(self, _=None):
        SlTrace.lg("fte.nav_make_invisible")

    def set_enable_mouse(self, _=None,val=None):
        SlTrace.lg("fte.set_enable_mouse")

    def nav_show_marked(self, _=None):
        SlTrace.lg("fte.nav_show_marked")

    def nav_redraw(self, _=None):
        SlTrace.lg("fte.nav_redraw")

    def nav_say_position(self, _=None):
        SlTrace.lg("fte.nav_say_position")

    def nav_make_talk(self, _=None):
        SlTrace.lg("fte.nav_make_talk")

    def nav_logt(self, _=None):
        SlTrace.lg("fte.nav_logt")

    def nav_no_logt(self, _=None):
        SlTrace.lg("fte.nav_no_logt")

    def make_noisy(self, _=None):
        SlTrace.lg("fte.make_noisy")

    def make_silent(self, _=None):
        SlTrace.lg("fte.make_silent")
    
    def nav_add_loc(self):
        SlTrace.lg("fte.nav_add_loc()")
    
    def nav_no_add_loc(self):
        SlTrace.lg("fte.nav_no_add_loc()")
    
    def nav_echo_on(self):
        SlTrace.lg("fte.nav_echo_on()")
    
    def nav_echo_off(self):
        SlTrace.lg("fte.nav_echo_off()")
        
    def start_drawing(self):
        SlTrace.lg(f"fte.start_drawing()")

    def stop_drawing(self):
        SlTrace.lg(f"fte.stop_drawing() is this in fte?")
    
    def set_combine_wave(self, val=True):
        SlTrace.lg("fte.set_combine_wave")
    
    def  flip_skip_space(self):
        SlTrace.lg("fte.flip_skip_space")
    
    def  flip_skip_run(self):
        SlTrace.lg("fte.flip_skip_run")
    
    def start_scanning(self):
        SlTrace.lg("fte.start_scanning")
                                                                                                                                        
    def stop_scanning(self):
        SlTrace.lg("fte.stop_scanning") 

    def set_no_item_wait(self, val=True):
        SlTrace.lg(f"fte.set_no_item_wait(val={val})") 


if __name__ == "__main__":
    from wx_adw_menus import AdwMenus, FteFake
                  
    app = wx.App()
    frame = wx.Frame(None)
    fte = FteFake()
    menus = AdwMenus(fte, frame=frame)

    men_scs = menus.get_menu_scs()
    SlTrace.lg(f"Menus: {men_scs}")
    for men_sc in men_scs:
        SlTrace.lg(f"menu {men_sc}")    
        menu_item_scs = menus.get_menu_item_scs(men_sc)    
        SlTrace.lg(f"menu {men_sc} items: {menu_item_scs}")

    SlTrace.lg("Calling each function")
    for men_sc in men_scs:
        SlTrace.lg(f"menu {men_sc}")    
        men_item_scs = menus.get_menu_item_scs(men_sc)
        for menui_sc in men_item_scs:    
            cmd_command = menus.get_menu_cmd(men_sc, menui_sc)
            SlTrace.lg(f"Menu:{men_sc} Item:{menui_sc}", "menu")
            if men_sc == "f" and menui_sc.lower() == "x":
                SlTrace.lg(f"Skipping Menu:{men_sc} Item:{menui_sc}")
                continue
            cmd_command()
            
        
        
    app.MainLoop()