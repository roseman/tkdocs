from tkinter import *
from tkinter import ttk
root = Tk()

def start():
    b.configure(text='Stop', command=stop)
    l['text'] = 'Working...'
    global interrupt; interrupt = False
    root.after(1, step)
    
def stop():
    global interrupt; interrupt = True
    
def step(count=0):
    p['value'] = count
    if interrupt:
        result(None)
        return
    root.after(100)  # next step in our operation; don't take too long!
    if count == 20: # done!
        result(42)
        return
    root.after(1, lambda: step(count+1))
    
def result(answer):
    p['value'] = 0
    b.configure(text='Start', command=start)
    l['text'] = "Answer: " + str(answer) if answer else "No Answer"
    
f = ttk.Frame(root); f.grid()
b = ttk.Button(f, text="Start!", command=start); b.grid(column=1, row=0, padx=5, pady=5)
l = ttk.Label(f, text="No Answer"); l.grid(column=0, row=0, padx=5, pady=5)
p = ttk.Progressbar(f, orient="horizontal", mode="determinate", maximum=20); 
p.grid(column=0, row=1, padx=5, pady=5)

root.mainloop()


