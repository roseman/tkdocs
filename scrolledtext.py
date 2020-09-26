from tkinter import *
from tkinter import ttk

root=Tk()

t = Text(root, width = 40, height = 5, wrap = "none")
ys = ttk.Scrollbar(root, orient = 'vertical', command = t.yview)
xs = ttk.Scrollbar(root, orient = 'horizontal', command = t.xview)
t['yscrollcommand'] = ys.set
t['xscrollcommand'] = xs.set
t.insert('end', "Lorem ipsum...\n...\n... dolor sit amet, consectetur adipiscing elit. Cras tincidunt tortor sit amet pretium semper. Pellentesque ac laoreet nulla. Fusce quis sapien ut magna ornare lacinia condimentum vel dui. Pellentesque volutpat pulvinar facilisis. Nunc lacus justo, imperdiet a urna at, condimentum gravida erat. \nAliquam ornare mi id dui blandit laoreet. Donec sed \nelit pretium arcu elementum lobortis ac at est. Curabitur nec \nsapien quam. Duis sit amet lectus quis odio finibus viverra. Duis dapibus dui a tempus mollis. Vestibulum porta sem id tristique maximus. Fusce molestie purus ligula, eu auctor mi egestas quis.")
t.grid(column = 0, row = 0, sticky = 'nwes')
xs.grid(column = 0, row = 1, sticky = 'we')
ys.grid(column = 1, row = 0, sticky = 'ns')
root.grid_columnconfigure(0, weight = 1)
root.grid_rowconfigure(0, weight = 1)

root.mainloop()
