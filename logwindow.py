from tkinter import *
from tkinter import ttk
from datetime import datetime

root = Tk()
log = Text(root, state='disabled', width=80, height=24, wrap='none')
log.grid()

def writeToLog(msg):
    numlines = int(log.index('end - 1 line').split('.')[0])
    log['state'] = 'normal'
    if numlines == 24:
        log.delete(1.0, 2.0)
    if log.index('end-1c')!='1.0':
        log.insert('end', '\n')
    log.insert('end', msg)
    log['state'] = 'disabled'


def writemsg():
    writeToLog(str(datetime.now())+": all is well")
    root.after(200, writemsg)
    
root.after(200, writemsg)

root.mainloop()
