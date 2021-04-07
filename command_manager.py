# command_manager.py
""" move manager morphed from Java ExtendedModeler: EMBCCommandManager
"""
from select_trace import SlTrace
from command_stack import CommandStack
from drawing_command import DrawingCommand

"""
 * Implement basic Command Interface/command to support Undo/Redo
 * @author raysm
 *
"""
class CommandManager:
    """
    SceneControler sceneControler
    EMBCommand currentCmd                # Currently executing command
    Stack<EMBCommand> commandStack        # Commands done
    Stack<EMBCommand> undoStack            # Commands undone
    """
    
    def __init__(self, drawing_controller):
        self.current_command = None
        self.drawing_controller = drawing_controller
        self.command_stack = CommandStack()
        self.undo_stack = CommandStack()
        DrawingCommand.set_command_manager(self)    # Ensure a manager is in place
        SlTrace.lg(f"command_manager - DC: {DrawingCommand.command_manager}")
        ###if (EMBCommand.commandManager is None)
        ###    EMBCommand.setManager(this)    # Ensure a manager is in place


    """
     * Check if command stack is empty
    """
    
    def is_empty(self):
        return self.command_stack.is_empty()


    """
     * Check if undo command stack is empty
    """
    def is_undo_empty(self):
        return self.undo_stack.is_empty()

    
    def last_command(self):
        """ Peek at last command
        :returns: DrawingCommand
        """
        if self.command_stack.is_empty():
            return None
        
        return self.command_stack.peek()
    
    def last_visible_command(self):
        """ Peek at last visible command
        :returns: DrawingCommand
        """
        cs_size = self.command_stack.size()
        for sidx in range(cs_size):
            cmd = self.command_stack.element_at(sidx)
            if cmd.is_visible():
                return cmd
            
        return None

    
    def last_undo_command(self):
        """ Peek at undo command
        :returns: DrawingCommand
        """
        return self.undo_stack.peek()

    

    """
     * Check if can redo this command
    """
    def can_redo(self):
        if self.undo_stack.is_empty():
            return False
        cmd = self.last_undo_command()
        return cmd.can_redo()


    """
     * Check if can repeat this command
    """
    def can_repeat(self):
        if self.command_stack.is_empty():
            return False
        cmd = self.last_command()
        return cmd.can_repeat()


    """
     * Check if can undo this command
    """
    def can_undo(self):
        if self.command_stack.is_empty():
            return False
        cmd = self.last_command()
        if not cmd.can_undo():
            return False        # Can't undo
        return True

    
    """
     * Get newest block index
    """
    def cbIndex(self):
        return self.drawing_controller.cbIndex()

    

    """
     * Get block, given index
    """
    def cb(self, id):
        return self.drawing_controller.getCb(id)


    
    """
     * Check point command state
     * by pushing command, which upon undo, will create current state
    """
    def check_point(self):
        SlTrace.lg("check_point", "execute")
        '''TBD
        try:
            cmd = EMBCommand.check_pointCmd()
            self.undo_stack.push(cmd)
        except EMBlockError as e:
            # TODO Auto-generated catch block
            e.printStackTrace()
        '''

    
    """
     * Undo if possible
     * command and select stack modifications are done through EMBCommand functions
    """
    def undo(self):
        SlTrace.lg("undo", "execute")
        if (not self.can_undo()):
            SlTrace.lg("Can't undo")
            return False

        cmd = self.command_stack.pop()
        return cmd.undo()

    def undo_all(self):
        """ Undo all commands in stack
        """
        while self.command_stack.size() > 0:
            self.undo()

    """
     * Re-execute the most recently undone command
    """
    def redo(self):
        SlTrace.lg("redo", "execute")
        if (not self.can_redo()):
            SlTrace.lg("Can't redo")
            return False

        cmd = self.undo_stack.pop()
        return cmd.redo()

    def get_repeat(self):
        """ Get command copy which would, if executed,
        "repeat" last command
        :returns command which would repeat
            or None if none 
        """       
        if (not self.can_repeat()):
            return None

        cmd = self.last_visible_command()
        if cmd is None:
            return None
        
        cmd_last = self.last_command()
        cmd = cmd.use_locale(cmd_last)  # Update for changes
        
        return cmd.get_repeat()


    def repeat(self):        
        """ Re execute the most recently done visible
        command
        """
        SlTrace.lg("repeat", "execute")
        cmd = self.get_repeat()
        if cmd is None:
            SlTrace.lg("Can't repeat")
            return False

        return cmd.repeat()


    """
     * Save command for undo/redo...
    """
    def save_cmd(self, bcmd):
        self.command_stack.push(bcmd)

    


    def any_selected(self):
        select = self.get_selected()
        return len(select) > 0


    
    def get_current_command(self):
        """ get most recent command, if one
        :returns: current command, if one, else None
        """
        if self.command_stack.is_empty():
            return None
        
        return self.command_stack.peek()


    """
     * Get previous command, if any
     * Return previous command, if one else
     * return current command if one else
     * return None
    """
    def get_prev_commad(self):
        if self.command_stack.is_empty():
            return None
        if self.command_stack.size() < 2:
            return self.command_stack.peek()
        return self.command_stack.element_at(1)


    """
     * Get previously executed command's selection
    """
    def get_prev_selected(self):
        prev_cmd = self.get_prev_commad()
        if prev_cmd is None:
            return []
        return prev_cmd.new_select


    
    """
     * Get previously executed command's selected block
     * Use current command if command stack only has one 
    """
    def get_prev_selected_marker(self):
        prev_select = self.get_prev_selected()
        if len(prev_select)== 0:
            return None
        return prev_select[0]


    
    """
     * Get currently selected blocks
    """
    def get_selected_markers(self):
        select = self.get_selected()
        return select

    
    """
     * Get currently selected
    """
    def get_selected(self):
        cmd = self.get_current_command()
        if cmd is None:
            return []        # Empty when none
        
        return cmd.new_select

    """
     * Get currently selected block if any
    """
    def get_selected_marker(self):
        select = self.get_selected()
        if len(select) == 0:
            return None
        return select[0]

    
    
    """
     * Check select stack
    """
    def select_is_empty(self):
        return len(self.get_selected()) == 0

    
    
    def select_pop(self):
        SlTrace.lg("No select stack")
        return self.get_selected()

    

    """
     * Set selection
    """
    def set_selected(self, select):
        cmd = self.get_current_command()
        cmd.set_select(select)



    

    """
     * Print displayed blocks
    """
    def display_print(self, tag, trace):
        self.drawing_controller.display_print(tag, trace)


    
    """
     * Update selection display
     * For now we just unselect all previous and select all new
    """
    def display_update(self, cmd=None):
        return self.drawing_controller.display_update(cmd=cmd)

    

    """
     * Print command stack
    """
    def cmd_stack_print(self, tag, trace=None):
        max_print = 5
        stack_str = ""
        if self.command_stack.is_empty():
            SlTrace.lg(f"{tag} self.command_stack: Empty", trace)
            return

        cmds = self.command_stack.get_cmds()
        nprint = max_print
        if SlTrace.trace("verbose"):
            nprint = 9999
        for cmd in cmds:
            if stack_str != "":
                stack_str += "\n"
            stack_str +=     "   " + str(cmd)

        SlTrace.lg(f"{tag} cmd Stack: {self.command_stack.size()}\n"
                   f" {stack_str}", trace)

    
    
    def select_print(self, tag, trace=None):
        """ Print select select state
        """

        self.drawing_controller.select_print(tag, trace=trace)

if __name__ == "__main__":
    from tkinter import *
    from keyboard_draw import KeyboardDraw
    from kbd_cmd_proc import KbdCmdProc
    
    root = Tk()
    
    kb_draw = KeyboardDraw(root,  title="Testing DmImage",
                hello_drawing_str="",
                draw_x=100, draw_y=50,
                draw_width=1500, draw_height=1000,
                kbd_win_x=50, kbd_win_y=25,
                kbd_win_width=600, kbd_win_height=300,
                show_help=False,        # No initial help
                with_screen_kbd=False   # No screen keyboard
                           )
    mgr = CommandManager(kb_draw)
    mgr.cmd_stack_print("cmd_stack_print")
    
    root.mainloop()
