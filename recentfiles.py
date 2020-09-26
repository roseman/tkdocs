from tkinter import *
from tkinter import ttk
import glob
import os
import os.path
root=Tk()

def openFile(f):
    print(f)

recent_files = glob.glob(os.getcwd()+'/*.py')
menubar = Menu(root)
root['menu'] = menubar
menu_file = Menu(menubar)
menu_edit = Menu(menubar)
menubar.add_cascade(menu=menu_file, label='File')
menubar.add_cascade(menu=menu_edit, label='Edit')
menu_recent = Menu(menu_file)
menu_file.add_cascade(menu=menu_recent, label='Open Recent')
for f in recent_files:
    menu_recent.add_command(label=os.path.basename(f), command=lambda: openFile(f))

root.mainloop()


