#adw_menus    09Mar2023  crs, Split off from adw_front_end

import tkinter as tk

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
    def __init__(self, adw_front_end):
        """ Setup menus for AudioDrawWindow
        :adw_front_end: (AdwFrontEnd)
        """
        self.fte = adw_front_end
        self.mw = adw_front_end.mw 
        
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
        
        menubar = tk.Menu(self.mw)
        self.menubar = menubar      # Save for future reference
        self.mw.config(menu=menubar)
        
        self.Properties = None
        self.LogFile = None
        
        file_menu = tk.Menu(menubar, tearoff=0)
        self.file_menu_setup(file_menu)
        menubar.add_cascade(label="File", menu=file_menu)
            
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
        
        aux_menu = tk.Menu(menubar,tearoff=0)
        aux_menu.add_command(label="Trace", command=self.trace_menu,
                             underline=0)
        menubar.add_cascade(label="Auxiliary", menu=aux_menu)

    """ File Menu setup package
    """

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

    def draw_help(self):
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
    def mag_help(self):
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
    def scan_help(self):
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

    def scan_combine_wave(self):
        self.set_combine_wave()

    def scan_disable_combine_wave(self):
        self.set_combine_wave(val=False)
        
    def scan_no_item_wait(self):
        self.set_no_item_wait()
        
    def scan_item_wait(self):
        """clear no item wait
        """
        self.set_no_item_wait(val=False)
                        
    """ End of Scanning support
    """


    """ Navigate support package
    """
                           
    def nav_help(self):
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
    def trace_menu(self):
        TraceControlWindow(tcbase=self.mw)
        

    """
    Links to front end 
    """
    """
    General
    """
    def erase_pos_history(self):
        self.fte.erase_pos_history()    
                
    def speak_text(self, msg, dup_stdout=True,
                   speech_type='REPORT'):
        """ Speak text, if possible else write to stdout
        :msg: text message
        :dup_stdout: duplicate to stdout default: True
        :speech_type: type of speech default: "report"
            REPORT - standard reporting
            CMD    - command
            ECHO
        """
        self.fte.speak_text(msg=msg, speech_type=speech_type,
                             dup_stdout=dup_stdout)

    """
     File links
      most local
    """
    def pgm_exit(self):
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
    def start_drawing(self):
        """ Start/enable drawing
        """
        self.fte.start_drawing() 

    def stop_drawing(self):
        """ Stop/disable drawing
        """
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

    def flip_skip_space(self):
        """ Flip skipping spaces
        """
        self.fte.flip_skip_space()

    def flip_skip_run(self):
        """ Flip skipping run of equals
        """
        self.fte.flip_skip_run()
        
    def start_scanning(self):
        self.fte.start_scanning()

     
    def stop_scanning(self):
        self.fte.stop_scanning()
        

