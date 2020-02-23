# gr_input.py   07Mar2019   crs Author
"""
Prompt User and accept input
"""
import tkinter as tk       # Get some tkinter functions

def gr_input(prompt="Enter"):
    global entry_var, entry_text
    mw = tk.Tk()
    entry_text = None               # Set if OK
    entry_var = tk.StringVar()         # Holds the entry text
   
    def ok_cmd():
        """ Function called  upon "OK" button
        """
        global entry_var, entry_text
        entry_text = entry_var.get()    # Retrieve
        mw.quit()                       # Exit tk mainloop
        
    
    label = tk.Label(mw, text=prompt)    # Create Label with prompt
    label.pack(side=tk.LEFT)

    entry = tk.Entry(mw, textvariable=entry_var, bd=3)        # Create Entry space on right
    entry.pack(side=tk.LEFT)

    button = tk.Button(mw, text="OK", command=ok_cmd, fg="blue", bg="light gray")
    button.pack(side=tk.RIGHT)
    mw.mainloop()                   # Loop till quit
    mw.destroy()                    # cleanup
    return entry_text 

"""
Testing Code which only gets run if this file is
executed by itself
"""
if __name__ == '__main__':
    inp = gr_input("Enter Number:")
    print(inp, " Entered")



