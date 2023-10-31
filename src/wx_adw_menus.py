# adw_menus    09Mar2023  crs, Split off from adw_front_end

import wx

from select_trace import SlTrace
from trace_control_window import TraceControlWindow


class MenuDisp:
    """ Menu dispatch table entry
    Supporting multiple mode dispatch (e.g, Dropdown item plus command mode)
    """

    def __init__(self, label, command, underline):
        self.label = label
        self.command = command
        self.underline = underline
        self.shortcut = label[underline].lower()


class AdwMenus:
    def __init__(self, adw_front_end, frame=None):
        """ Setup menus for AudioDrawWindow
        :adw_front_end: (AdwFrontEnd)
        :frame: frame containing menus
        """
        self.fte = adw_front_end
        if frame is None:
            wx.Frame(None)
        self.frame = frame
        frame.Show()
        
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

    def on_alt_s(self, _):
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
                {"name" : "Exit",  "cmd" : self.pgm_exit},
                ],
            "magnify" :
                [
                {"name" : "Help", "cmd" : self.mag_help},
                {"name" : ("rem_pos","Remove Pos History"), "cmd" : self.erase_pos_history},
                {"name" : "Select", "cmd" : self.mag_select},
                {"name" : "Expand Right", "cmd" : self.mag_expand_right},
                {"name" : "Expand Top", "cmd" : self.mag_expand_top},
                {"name" : "View", "cmd" : self.mag_view},              
                ],
            "navigate" :
                [
                {"name" : ("help","Help"), "cmd" : self.nav_help},
                {"name" : ("add_loc","add At loc"), "cmd" : self.nav_add_loc},
                {"name" : ("no_add_loc","b-remove At loc"), "cmd" : self.nav_no_add_loc},
                {"name" : ("echo on","echo input on"), "cmd" : self.nav_no_add_loc},
                {"name" : ("hd","echo off"), "cmd" : self.nav_no_add_loc},
                {"name" : ("hd","visible cells"), "cmd" : self.nav_no_add_loc},
                {"name" : ("hd","invisible cells"), "cmd" : self.nav_no_add_loc},
                {"name" : ("hd","marked"), "cmd" : self.nav_no_add_loc},
                {"name" : ("hd","noisy"), "cmd" : self.nav_no_add_loc},
                {"name" : ("hd","silent"), "cmd" : self.nav_no_add_loc},
                {"name" : ("hd","talking"), "cmd" : self.nav_no_add_loc},
                {"name" : ("hd","log talk"), "cmd" : self.nav_no_add_loc},
                {"name" : ("hd","no log talk"), "cmd" : self.nav_no_add_loc},
                {"name" : ("hd","position"), "cmd" : self.nav_no_add_loc},
                {"name" : ("hd","redraw figure"), "cmd" : self.nav_no_add_loc},
                {"name" : ("hd","audio beep"), "cmd" : self.nav_no_add_loc},
                {"name" : ("hd","q no audio beep"), "cmd" : self.nav_no_add_loc},
                {"name" : ("hd","x enable mouse navigation"), "cmd" : self.nav_no_add_loc},
                {"name" : ("hd","y disable mouse navigation"), "cmd" : self.nav_no_add_loc},
                ],
            "draw" :
                [
                {"name" : "Help", "cmd" : self.draw_help},
                {"name" : "drawing", "cmd" : self.start_drawing},
                {"name" : "stop_drawing", "cmd" : self.stop_drawing},
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
        for menu_name in menu_name_list:
            menu = wx.Menu()
            menu_settings = menus_settings[menu_name]
            menu_heading = menu_settings["heading"]
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
                    menu_item = menu.Append(wx.ID_ANY, menu_item_heading)
                frame.Bind(wx.EVT_MENU, menu_cmd, menu_item)


        """###wxport###
        self.mw.bind('<Alt-a>', self.on_alt_f)  # Keep this from key cmds
        self.mw.bind('<Alt-d>', self.on_alt_f)  # Keep this from key cmds
        self.mw.bind('<Alt-f>', self.on_alt_f)  # Keep this from key cmds
        self.mw.bind('<Alt-n>', self.on_alt_n)  # Keep this from key cmds
        self.mw.bind('<Alt-M>', self.on_alt_m)  # Keep this from key cmds
        self.mw.bind('<Alt-m>', self.on_alt_m)  # Keep this from key cmds
        self.mw.bind('<Alt-N>', self.on_alt_n)  # Keep this from key cmds
        self.mw.bind('<Alt-n>', self.on_alt_n)  # Keep this from key cmds
        self.mw.bind('<Alt-S>', self.on_alt_s)  # Keep this from key cmds
        self.mw.bind('<Alt-s>', self.on_alt_s)  # Keep this from key cmds
        """
        ###wxport###menubar = tk.Menu(self.mw)
        ###wxport###self.menubar = menubar  # Save for future reference
        ###wxport###self.mw.config(menu=menubar)

        self.Properties = None

        ###wxport###file_menu = tk.Menu(menubar, tearoff=0)
        ###wxport###self.file_menu_setup(file_menu)
        ###wxport###menubar.add_cascade(label="File", menu=file_menu)
        '''###wxport###
        mag_menu = tk.Menu(menubar, tearoff=0)
        self.mag_menu_setup(mag_menu)
        menubar.add_cascade(label="Magnify", menu=mag_menu)

        nav_menu = tk.Menu(menubar, tearoff=0)
        self.nav_menu_setup(nav_menu)
        menubar.add_cascade(label="Navigate", menu=nav_menu)

        draw_menu = tk.Menu(menubar, tearoff=0)
        self.draw_menu_setup(draw_menu)
        menubar.add_cascade(label="Draw", menu=draw_menu)

        scan_menu = tk.Menu(menubar, tearoff=0)
        self.scan_menu_setup(scan_menu)
        menubar.add_cascade(label="Scanning", menu=scan_menu)

        aux_menu = tk.Menu(menubar, tearoff=0)
        aux_menu.add_command(label="Trace", command=self.trace_menu,
                             underline=0)
        menubar.add_cascade(label="Auxiliary", menu=aux_menu)
        '''
    """ File Menu setup package
    """
    '''
    menu_items.append(heading_menu.Append(wx.ID_ANY, lbl, "desc-" + lbl))
        menu_item = menu_items[-1]
        menu_cmds.append(get_menu_cmd(proc=menu_command, hi=hi, ddj=ddj))
        menu_cmd = menu_cmds[-1]
        print(f"menu_cmd: menu_cmd:{menu_cmd} hi:{hi} ddj:{ddj}")

        frame.Bind(wx.EVT_MENU, menu_cmd, id=menu_item.GetId())
    menubar.Append(heading_menu,  menu_lst[i%len(menu_lst)])
    '''
    def file_menu_setup(self, file_menu):
        self.file_menu = file_menu
        self.file_dispatch = {}
        self.file_menu_add_command(label="Open", command=self.File_Open_tbd,
                                   underline=0)
        self.file_menu_add_command(label="Save", command=self.File_Save_tbd,
                                   underline=0)
        file_menu.add_separator()
        self.file_menu_add_command(label="Log", command=self.LogFile,
                                   underline=0)
        self.file_menu_add_command(label="Properties", command=self.Properties,
                                   underline=0)
        file_menu.add_separator()
        self.file_menu_add_command(label="Exit", command=self.pgm_exit,
                                   underline=1)

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

    def TBD(self, _):
        SlTrace.lg("To be developed")

    def LogFile(self, _):
        SlTrace.lg("Show LogFile")

    def PropertiesFile(self, _):
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

    """ draw_menu setup
    """

    def draw_menu_setup(self, draw_menu):
        self.draw_menu = draw_menu
        self.draw_dispatch = {}
        self.draw_menu_add_command(label="Help", command=self.draw_help,
                                   underline=0)
        self.draw_menu_add_command(label="drawing", command=self.start_drawing,
                                   underline=0)
        self.draw_menu_add_command(label="stop_drawing", command=self.stop_drawing,
                                   underline=0)

    def draw_menu_add_command(self, label, command, underline):
        """ Setup menu commands, setup dispatch for direct call
        :label: add_command label
        :command: command to call
        :underline: short-cut index in label
        """
        self.draw_menu.add_command(label=label, command=command,
                                   underline=underline)
        menu_de = MenuDisp(label=label, command=command,
                           underline=underline)

        self.draw_dispatch[menu_de.shortcut] = menu_de

    def draw_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        if short_cut not in self.draw_dispatch:
            raise Exception(f"draw option:{short_cut} not recognized")
        menu_de = self.draw_dispatch[short_cut]
        menu_de.command()

    def draw_help(self, _):
        """ Help for drawing
        """
        """ Help - list command (Alt-d) commands
        """
        help_str = """
        Help - list drawing setup commands (Alt-d) commands
        h - say this help message
        d - Start/enable drawing
        s - stop/disable drawing
        Escape - flush pending report output
        """
        self.speak_text(help_str)

    """ Magnify support package
    """

    """ Magnify menu commands  """

    def mag_help(self, _):
        """ Help for Alt-m commands
        """
        """ Help - list command (Alt-m) commands
        """
        help_str = """
        Help - list magnify commands (Alt-m) commands
        h - say this help message
        t - expand magnify selected region left/right
        s - select/mark magnify region
        t - expand magnify selected region up/down top/bottom
        v - view region (make new window)
        """
        self.speak_text(help_str)

    def mag_menu_setup(self, mag_menu):
        self.mag_menu = mag_menu
        self.mag_dispatch = {}
        self.mag_menu_add_command(label="Help", command=self.mag_help,
                                  underline=0)
        self.mag_menu_add_command(label="Remove Pos History", command=self.erase_pos_history,
                                  underline=0)
        self.mag_menu_add_command(label="Select", command=self.mag_select,
                                  underline=0)
        self.mag_menu_add_command(label="Expand Right", command=self.mag_expand_right,
                                  underline=7)
        self.mag_menu_add_command(label="Expand Top", command=self.mag_expand_top,
                                  underline=7)
        self.mag_menu_add_command(label="View", command=self.mag_view,
                                  underline=0)

    def mag_menu_add_command(self, label, command, underline):
        """ Setup menu commands, setup dispatch for direct call
        :label: add_command label
        :command: command to call
        :underline: short-cut index in label
        """
        self.mag_menu.add_command(label=label, command=command,
                                  underline=underline)
        menu_de = MenuDisp(label=label, command=command,
                           underline=underline)

        self.mag_dispatch[menu_de.shortcut] = menu_de

    def mag_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        if short_cut not in self.mag_dispatch:
            raise Exception(f"mag option:{short_cut} not recognized")
        magde = self.mag_dispatch[short_cut]
        magde.command()

    """ End of Magnify support
    """

    """ Scanning support package
    """

    """ Scanning menu commands  """

    def scan_help(self, _):
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

    def scan_menu_setup(self, scan_menu):
        self.scan_menu = scan_menu
        self.scan_dispatch = {}
        self.scan_menu_add_command(label="Help", command=self.scan_help,
                                   underline=0)
        self.scan_menu_add_command(label="c -  combine wave - faster scan",
                                   command=self.scan_combine_wave,
                                   underline=0)
        self.scan_menu_add_command(label="d - disable combine wave",
                                   command=self.scan_disable_combine_wave,
                                   underline=0)
        self.scan_menu_add_command(label="f - flip skip space", command=self.flip_skip_space,
                                   underline=0)
        self.scan_menu_add_command(label="r - flip skip run", command=self.flip_skip_run,
                                   underline=0)
        self.scan_menu_add_command(label="Start scanning", command=self.start_scanning,
                                   underline=0)
        self.scan_menu_add_command(label="Stop scanning", command=self.stop_scanning,
                                   underline=1)
        self.scan_menu_add_command(label="No item wait", command=self.scan_no_item_wait,
                                   underline=0)
        self.scan_menu_add_command(label="Wait for item", command=self.scan_item_wait,
                                   underline=0)

    def scan_menu_add_command(self, label, command, underline):
        """ Setup menu commands, setup dispatch for direct call
        :label: add_command label
        :command: command to call
        :underline: short-cut index in label
        """
        self.scan_menu.add_command(label=label, command=command,
                                   underline=underline)
        menu_de = MenuDisp(label=label, command=command,
                           underline=underline)

        self.scan_dispatch[menu_de.shortcut] = menu_de

    def scan_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        if short_cut not in self.scan_dispatch:
            raise Exception(f"scan option:{short_cut} not recognized")
        scande = self.scan_dispatch[short_cut]
        scande.command()

    def scan_combine_wave(self, _):
        self.set_combine_wave()

    def scan_disable_combine_wave(self, _):
        self.set_combine_wave(val=False)

    def scan_no_item_wait(self, _):
        self.set_no_item_wait()

    def scan_item_wait(self, _):
        """clear no item wait
        """
        self.set_no_item_wait(val=False)

    """ End of Scanning support
    """

    """ Navigate support package
    """

    def nav_help(self, _):
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

    def nav_menu_setup(self, nav_menu):
        self.nav_menu = nav_menu
        self.nav_dispatch = {}
        self.nav_menu_add_command(label="Help", command=self.nav_help,
                                  underline=0)
        self.nav_menu.add_command(label="add At loc", command=self.nav_add_loc,
                                  underline=0)
        self.nav_menu_add_command(label="b-remove At loc", command=self.nav_no_add_loc,
                                  underline=0)
        self.nav_menu_add_command(label="echo input on", command=self.nav_echo_on,
                                  underline=0)
        self.nav_menu_add_command(label="echo off", command=self.nav_echo_off,
                                  underline=5)

        self.nav_menu_add_command(label="visible cells", command=self.nav_make_visible,
                                  underline=0)
        self.nav_menu_add_command(label="invisible cells", command=self.nav_make_invisible,
                                  underline=0)
        self.nav_menu_add_command(label="marked", command=self.nav_show_marked,
                                  underline=0)
        self.nav_menu_add_command(label="noisy", command=self.make_noisy,
                                  underline=0)
        self.nav_menu_add_command(label="silent", command=self.make_silent,
                                  underline=0)
        self.nav_menu_add_command(label="talking", command=self.nav_make_talk,
                                  underline=0)
        self.nav_menu_add_command(label="log talk", command=self.nav_logt,
                                  underline=0)
        self.nav_menu_add_command(label="no log talk", command=self.nav_no_logt,
                                  underline=10)
        self.nav_menu_add_command(label="position", command=self.nav_say_position,
                                  underline=0)
        self.nav_menu_add_command(label="redraw figure", command=self.nav_redraw,
                                  underline=2)
        self.nav_menu_add_command(label="audio beep", command=self.nav_audio_beep,
                                  underline=1)
        self.nav_menu_add_command(label="q no audio beep",
                                  command=self.nav_no_audio_beep,
                                  underline=0)
        self.nav_menu_add_command(label="x enable mouse navigation",
                                  command=self.nav_enable_mouse,
                                  underline=0)
        self.nav_menu_add_command(label="y disable mouse navigation",
                                  command=self.nav_disable_mouse,
                                  underline=0)

    def nav_menu_add_command(self, label, command, underline):
        """ Setup menu commands, setup dispatch for direct call
        :label: add_command label
        :command: command to call
        :underline: short-cut index in label
        """
        self.nav_menu.add_command(label=label, command=command,
                                  underline=underline)
        menu_de = MenuDisp(label=label, command=command,
                           underline=underline)

        self.nav_dispatch[menu_de.shortcut] = menu_de

    def nav_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        if short_cut not in self.nav_dispatch:
            raise Exception(f"nav option:{short_cut} not recognized")
        navde = self.nav_dispatch[short_cut]
        navde.command()

    """
    Trace support
    """

    def trace_menu(self, _):
        TraceControlWindow()

    """
    Links to front end 
    """
    """
    General
    """

    def erase_pos_history(self):
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

    def pgm_exit(self, _):
        self.fte.pgm_exit()

    """
    Magnification links
    """

    def mag_select(self):
        """ Select magnification region
            -rectangle including all figure cells traveled so far
            :returns: True if some selected else False
        """
        return self.fte.mag_select()

    def mag_expand_right(self):
        """ Expand selection region right and left by 20%
        """
        self.fte.mag_exapnd_right()

    def mag_expand_top(self):
        """ Expand selection region top/bottom by 20%
        """
        self.fte.mag_exapnd_top()

    def mag_view(self):
        """ View selected region, creating a new AudioDrawWindow
        """
        self.fte.mag_view()

    """ drawing
    """

    def start_drawing(self, _):
        """ Start/enable drawing
        """
        self.fte.start_drawing()

    def stop_drawing(self, _):
        """ Stop/disable drawing
        """
        self.fte.stop_drawing()

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

    def nav_add_loc(self):
        self.fte.nav_add_loc()

    def nav_no_add_loc(self):
        self.fte.nav_no_add_loc()

    def nav_echo_on(self):
        self.fte.nav_echo_on()

    def nav_echo_off(self):
        self.fte.nav_echo_off()

    def nav_make_visible(self):
        self.fte.nav_make_visible()

    def nav_make_invisible(self):
        self.fte.nav_make_invisible()

    def nav_show_marked(self):
        self.fte.nav_show_marked()

    def make_noisy(self):
        self.fte.make_noisy()

    def make_silent(self):
        self.fte.make_silent()

    def nav_make_talk(self):
        self.fte.nav_make_talk()

    def nav_logt(self):
        self.fte.nav_logt()

    def nav_no_logt(self):
        self.fte.nav_no_logt()

    def nav_say_position(self):
        self.fte.nav_say_position()

    def nav_redraw(self):
        self.fte.nav_redraw()

    def nav_audio_beep(self):
        self.fte.nav_audio_beep()

    def nav_no_audio_beep(self):
        self.fte.nav_no_audio_beep()

    def nav_enable_mouse(self):
        self.set_enable_mouse()

    def nav_disable_mouse(self):
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

    def flip_skip_space(self, _):
        """ Flip skipping spaces
        """
        self.fte.flip_skip_space()

    def flip_skip_run(self, _):
        """ Flip skipping run of equals
        """
        self.fte.flip_skip_run()

    def start_scanning(self, _):
        self.fte.start_scanning()

    def stop_scanning(self, _):
        self.fte.stop_scanning()

if __name__ == "__main__":
    class FteFake:
        def pgm_exit(self):
            SlTrace.lg("fte.pgm_exit()")
            
        def speak_text(self, msg, msg_type=None,
                       dup_stdout=True, rate=None,
                       volume=None):
            SlTrace.lg(f"fte.speak_text({msg},"
                       f"msg_type={msg_type}msg)"
                       f")")

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
                  
    app = wx.App()
    frame = wx.Frame(None)
    fte = FteFake()
    menus = AdwMenus(fte, frame=frame)

    app.MainLoop()