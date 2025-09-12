from tkinter import *
root = Tk()
if (root.tk.call('tk', 'windowingsystem')=='aqua'):
    root.event_add('<<ContextMenu>>', '<Control-Button-1>')
menu = Menu(root)
for i in ('One', 'Two', 'Three'):
    menu.add_command(label=i)
root.bind('<<ContextMenu>>', lambda e: menu.post(e.x_root, e.y_root))
root.mainloop()
