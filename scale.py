from tkinter import *
from tkinter import ttk

root=Tk()

# label tied to the same variable as the scale, so auto-updates
num = StringVar()
ttk.Label(root, textvariable=num).grid(column=0, row=0, sticky='we')

# label that we'll manually update via the scale's command callback
manual = ttk.Label(root)
manual.grid(column=0, row=1, sticky='we')

def update_lbl(val):
   manual['text'] = "Scale at " + val

scale = ttk.Scale(root, orient='horizontal', length=200, from_=1.0, to=100.0, variable=num, command=update_lbl)
scale.grid(column=0, row=2, sticky='we')
scale.set(20)

root.mainloop()


