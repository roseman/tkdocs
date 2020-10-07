from tkinter import *
from tkinter import ttk
root = Tk()

ttk.Entry(root).grid()   # something to interact with
def dismiss ():
    dlg.grab_release()
    dlg.destroy()

dlg = Toplevel(root)
ttk.Button(dlg, text="Done", command=dismiss).grid()
dlg.protocol("WM_DELETE_WINDOW", dismiss) # intercept close button
dlg.transient(root)   # dialog window is related to main
dlg.wait_visibility() # can't grab until window appears, so we wait
dlg.grab_set()        # ensure all input goes to our window
dlg.wait_window()     # block until window is destroyed

root.mainloop()


