# wx_adw_menus    20May2023  crs, adapt from adw_menus
#                 09Mar2023  crs, Split off from adw_front_end
import os

import wx

from select_trace import SlTrace
from trace_control_window import TraceControlWindow

def new_id():
    """ Repalcement for deprecated wx.NewId()
    :returns: unique id
    """
    return wx.NewIdRef(count=1)

class MenuDisp:
    """ Menu dispatch table entry
    Supporting multiple mode dispatch (e.g, Dropdown item plus command mode)
    """

    def __init__(self, label, command):
        self.label = ""
        def two_arg_command(self, _=None):
            """ Intermediary to ignore event arg, so we don't need
            to change all our menu action calls developed for tkinter
            """
            command()
        self.command = two_arg_command
        self.shortcut = None
        prev_cl = None
        for cl in label:           # XXX&<shortcut>XXXX
            if prev_cl == '&':
                self.shortcut = cl.lower()
            if cl != '&':
                self.label += cl
            prev_c = cl


class AdwMenus:
    def __init__(self, frame, adw_front_end):
        """ Setup menus for AudioDrawWindow
        :frame: window frame
        :adw_front_end: (AdwFrontEnd)
        """
        self.frame = frame
        self.fte = adw_front_end
        self.menu_setup()

    def menu_setup(self):
        """ Setup menu system
        """

        self.Properties = None
        self.LogFile = None

        self.menubar = wx.MenuBar()
        self.frame.SetMenuBar(self.menubar)

        file_menu = wx.Menu()
        self.file_menu_setup(file_menu)
        self.menubar.Append(file_menu, '&File')

        mag_menu = wx.Menu()
        self.mag_menu_setup(mag_menu)
        self.menubar.Append(mag_menu,"&Magnify")

        nav_menu = wx.Menu()
        self.nav_menu_setup(nav_menu)
        self.menubar.Append(nav_menu, "&Navigate")

        draw_menu = wx.Menu()
        self.draw_menu_setup(draw_menu)
        self.menubar.Append(draw_menu, "&Draw")

        scan_menu = wx.Menu()
        self.scan_menu_setup(scan_menu)
        self.menubar.Append(scan_menu, "&Scanning")

        aux_menu = wx.Menu()
        self.aux_menu_setup(aux_menu)
        self.menubar.Append(aux_menu, "&Auxiliary")

    """ File Menu setup package
    """

    def file_menu_setup(self, file_menu):
        self.file_menu = file_menu
        self.file_dispatch = {}

        self.file_menu_add_command(label="&Open", command=self.File_Open_tbd)
        self.file_menu_add_command(label="&Save", command=self.File_Save_tbd)
        file_menu.AppendSeparator()
        self.file_menu_add_command(label="&Log", command=self.LogFile)
        self.file_menu_add_command(label="&Properties", command=self.Properties)
        file_menu.AppendSeparator()
        self.file_menu_add_command(label="E&xit", command=self.pgm_exit)

    def file_menu_add_command(self, label, command):
        """ Setup menu commands, setup dispatch for direct call
        :label: add_command label, with leading & before accelerator key
        :command: command to call
        """
        item = self.file_menu.Append(new_id(), label)
        menu_de = MenuDisp(label=label, command=command)
        self.file_dispatch[menu_de.shortcut] = menu_de
        self.frame.Bind(wx.EVT_MENU, menu_de.command, item)

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
        self.draw_menu_add_command(label="&Help", command=self.draw_help)
        self.draw_menu_add_command(label="&drawing", command=self.start_drawing)
        self.draw_menu_add_command(label="&stop_drawing", command=self.stop_drawing)

    def draw_menu_add_command(self, label, command):
        """ Setup menu commands, setup dispatch for direct call
        :label: add_command label
        :command: command to call
        """
        item = self.draw_menu.Append(new_id(), label)
        menu_de = MenuDisp(label=label, command=command)
        self.draw_dispatch[menu_de.shortcut] = menu_de
        self.frame.Bind(wx.EVT_MENU, menu_de.command, item)

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

    def mag_menu_setup(self, menu):
        self.mag_menu = menu
        self.mag_dispatch = {}
        self.mag_menu_add_command(label="&Help", command=self.mag_help)
        self.mag_menu_add_command(label="&Remove Pos History", command=self.erase_pos_history)
        self.mag_menu_add_command(label="&Select", command=self.mag_select)
        self.mag_menu_add_command(label="Expand &Right", command=self.mag_expand_right)
        self.mag_menu_add_command(label="Expand &Top", command=self.mag_expand_top)
        self.mag_menu_add_command(label="Vie&w", command=self.mag_view)

    def mag_menu_add_command(self, label, command):
        """ Setup menu commands, setup dispatch for direct call
        :label: add_command label, including &<shortcut-letter>
        :command: command to call
        """
        menu_de = MenuDisp(label=label, command=command)
        self.mag_dispatch[menu_de.shortcut] = menu_de
        file_item = self.mag_menu.Append(new_id(), label)
        self.frame.Bind(wx.EVT_MENU, menu_de.command, file_item)
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
        self.scan_menu_add_command(label="&Help", command=self.scan_help)
        self.scan_menu_add_command(label="&c -  combine wave - faster scan",
                                   command=self.scan_combine_wave)
        self.scan_menu_add_command(label="&d - disable combine wave",
                                   command=self.scan_disable_combine_wave)
        self.scan_menu_add_command(label="&f - flip skip space", command=self.flip_skip_space)
        self.scan_menu_add_command(label="&r - flip skip run", command=self.flip_skip_run)
        self.scan_menu_add_command(label="&Start scanning", command=self.start_scanning)
        self.scan_menu_add_command(label="S&top scanning", command=self.stop_scanning)
        self.scan_menu_add_command(label="&No item wait", command=self.scan_no_item_wait)
        self.scan_menu_add_command(label="&Wait for item", command=self.scan_item_wait)

    def scan_menu_add_command(self, label, command):
        """ Setup menu commands, setup dispatch for direct call
        :label: add_command label
        :command: command to call
        """
        item = self.scan_menu.Append(new_id(), label)
        menu_de = MenuDisp(label=label, command=command)
        self.scan_dispatch[menu_de.shortcut] = menu_de
        self.frame.Bind(wx.EVT_MENU, menu_de.command, item)

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
        self.nav_menu_add_command(label="Help", command=self.nav_help)
        self.nav_menu_add_command(label="&add At loc", command=self.nav_add_loc)
        self.nav_menu_add_command(label="&b-remove At loc", command=self.nav_no_add_loc)
        self.nav_menu_add_command(label="&echo input on", command=self.nav_echo_on)
        self.nav_menu_add_command(label="echo &off", command=self.nav_echo_off)

        self.nav_menu_add_command(label="&visible cells", command=self.nav_make_visible)
        self.nav_menu_add_command(label="&invisible cells", command=self.nav_make_invisible)
        self.nav_menu_add_command(label="&marked", command=self.nav_show_marked)
        self.nav_menu_add_command(label="&noisy", command=self.make_noisy)
        self.nav_menu_add_command(label="&silent", command=self.make_silent)
        self.nav_menu_add_command(label="&talking", command=self.nav_make_talk)
        self.nav_menu_add_command(label="&log talk", command=self.nav_logt)
        self.nav_menu_add_command(label="no log tal&k", command=self.nav_no_logt)
        self.nav_menu_add_command(label="&position", command=self.nav_say_position)
        self.nav_menu_add_command(label="re&draw figure", command=self.nav_redraw)
        self.nav_menu_add_command(label="a&udio beep", command=self.nav_audio_beep)
        self.nav_menu_add_command(label="&q no audio beep", command=self.nav_no_audio_beep)
        self.nav_menu_add_command(label="&x enable mouse navigation", command=self.nav_enable_mouse)
        self.nav_menu_add_command(label="&y disable mouse navigation", command=self.nav_disable_mouse)

    def nav_menu_add_command(self, label, command):
        """ Setup menu commands, setup dispatch for direct call
        :label: add_command label
        :command: command to call
        """
        item = self.nav_menu.Append(new_id(), label)
        menu_de = MenuDisp(label=label, command=command)
        self.nav_dispatch[menu_de.shortcut] = menu_de
        self.frame.Bind(wx.EVT_MENU, menu_de.command, item)

    def nav_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        if short_cut not in self.nav_dispatch:
            raise Exception(f"nav option:{short_cut} not recognized")
        navde = self.nav_dispatch[short_cut]
        navde.command()


    """ Aux Menu setup package
    """

    def aux_menu_setup(self, menu):
        self.aux_menu = menu
        self.aux_dispatch = {}

        self.aux_menu_add_command(label="Trace", command=self.trace_menu)

    def aux_menu_add_command(self, label, command):
        """ Setup menu commands, setup dispatch for direct call
        :menu: menu object
        :label: add_command label, with leading & before accelerator key
        :command: command to call
        """
        item = self.aux_menu.Append(new_id(), label)
        menu_de = MenuDisp(label=label, command=command)
        self.file_dispatch[menu_de.shortcut] = menu_de
        self.frame.Bind(wx.EVT_MENU, menu_de.command, item)

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


    """
    Trace support
    """

    def trace_menu(self, dummy=None):
        TraceControlWindow(tcbase=None)     # Standalone window

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

    def pgm_exit(self, dummy=None):
        if self.fte is not None:
            self.fte.pgm_exit()

        SlTrace.lg("wx_adw_menus.exit")
        SlTrace.onexit()  # Force logging quit
        os._exit(0)

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


if __name__ == "__main__":
    app = wx.App()
    fr = wx.Frame(None, title="wx_adw_menus.py")
    fr.Show()
    fr.SetSize((300, 200))
    fr.Centre()

    adw_front_end = None
    adw_menus = AdwMenus(fr, adw_front_end)
    app.MainLoop()
    print("After app.MainLoop()")
