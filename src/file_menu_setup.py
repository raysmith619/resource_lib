
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
        self.file_menu_add_command(label="Exit", command=self.LogFile,
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
            raise Exception(f"draw option:{short_cut} not recognized")
        menu_de = self.file_dispatch[short_cut]
        menu_de.command()
