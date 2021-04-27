#chat_window.py    08Dec2020  crs
"""
Window With
    Entry for user text input
    Text area for conversation text display
"""
from tkinter import *

from select_trace import SlTrace
from select_window import SelectWindow

class ChatWindow(SelectWindow):
    """ Control chat window
    """
    @staticmethod
    def chat_window_exit():     # Default exit function
        print("chat_window_exit")
        ChatWindow.mgr.destroy()
        SlTrace.onexit()
        exit()

    def __init__(self, mgr,
                 title=None, control_prefix=None,
                 on_input=None,
                 **kwargs):
        """ Setup chat window
        :mgr: parent object
        :title: window title
        :control_prefix: properties prefix
        :on_input: called, if present, with user text
        :addtext: add text to display
        :cleartext: clear text area
        """
        ChatWindow.mgr = mgr
        self.on_input = on_input
        if 'pgmExit' not in kwargs:
            kwargs['pgmExit'] = ChatWindow.chat_window_exit
        super().__init__(mgr,title=title,
                         control_prefix=control_prefix,
                         **kwargs)
        input_frame = Frame(self)
        input_frame.pack(side="top", fill="x")
        
        self.input_var = StringVar()

        self.input_entry = Entry(input_frame, textvariable=self.input_var)
        self.input_entry.pack(side="left", fill="x", expand=True)
        self.input_entry.bind("<KeyRelease-Return>", self.entry_return_key)
        send_button = Button(master=input_frame, text="Send", command=self.send_cmd)
        send_button.pack(side="left")
        self.on_enter_var = BooleanVar()
        self.on_enter_var.set(True)
        send_on_enter_ckbox = Checkbutton(input_frame, text="on ENTER",
                                          variable=self.on_enter_var)
        send_on_enter_ckbox.pack(side="left")
        text_frame = Frame(self, bg="white", bd=10, relief="groove",
                           highlightbackground="red", highlightcolor="green")
        text_frame.pack(side="top", fill="both", expand=True)
        self.text_range = Text(text_frame)
        self.text_range.pack(side="top", fill="both", expand=True)
        
    def entry_return_key(self, event):
        """ Called when return key is pressed in input entry
        """
        if self.on_enter_var.get():
            self.send_cmd()
        else:
            text = self.input_var.get()
            text += "\n"
            self.input_var.set(text)
                     
    def send_cmd(self):
        """ Send input text
        """
        if self.on_input is not None:
            text = self.input_var.get()
            self.on_input(text)
            self.input_var.set("")
        else:
            SlTrace.lg("No on_input cmd")

    def add_text(self, text):
        """ Add text to text region
        :text: text to add
        """
        if not text.endswith("\n"):
            text += "\n"
        self.text_range.insert(END, text)
#########################################################################
#          Self Test                                                    #
#########################################################################
if __name__ == "__main__":
        
    # root window created. Here, that would be the only window, but
    # you can later have windows within windows.
    mw = Tk()
    SlTrace.lg("Startup")
    
    def user_exit():
        print("user_exit")
        print("Calling SlTrace.onexit()")
        SlTrace.onexit()
        exit()
            
    SlTrace.setProps()
    set_flags = True
    set_flags = False
    if set_flags:
        SlTrace.lg("setFlags")
        SlTrace.setFlags("flag1=1,flag2=0,flag3=1,flag4=0, flag5=1, flag6=1")
    else:
        SlTrace.lg("no setFlags")
        
    mw.geometry("400x300")
    app = None 
    
    def user_input(text):
        """ Process user input line(s)
        :text: text entered by user
        """
        if app is None:
            return
        
        app.add_text(text)
        
    #creation of an instance
    app = ChatWindow(mw,
                    title="ChatWindow Testing",
                    pgmExit=user_exit,
                    on_input=user_input
                    )

    
    #mainloop 
    mw.mainloop()  
