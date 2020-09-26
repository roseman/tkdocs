from tkinter import *
from tkinter import ttk, messagebox

root = Tk()
ttk.Entry(root).grid()
m = Menu(root)
m_edit = Menu(m)
m.add_cascade(menu=m_edit, label="Edit")
m_edit.add_command(label="Paste", command=lambda: root.focus_get().event_generate("<<Paste>>"))
m_edit.add_command(label="Find...", command=lambda: root.event_generate("<<OpenFindDialog>>"))
root['menu'] = m

def launchFindDialog(*args):
    messagebox.showinfo(message="I hope you find what you're looking for!")
    
root.bind("<<OpenFindDialog>>", launchFindDialog)
root.mainloop()
