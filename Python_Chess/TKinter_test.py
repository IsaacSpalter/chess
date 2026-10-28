from tkinter import *
from tkinter import ttk



def calculate(*args):
    try:
        value = float(feet.get())
        meters.set(round(0.3048 * value, 4))
    except ValueError:
        pass

root = Tk()
root.title("Feet to Meters")
root.option_add('*tearOff', FALSE)

mainframe = ttk.Frame(root, padding=(3, 3, 12, 12))
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

feet = StringVar()
feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)
feet_entry.grid(column=2, row=1, sticky=(W, E))

meters = StringVar()
ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2, sticky=(W, E))

ttk.Button(mainframe, text="Calculate", command=calculate).grid(column=3, row=3, sticky=W)

ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=W)
ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
mainframe.columnconfigure(2, weight=1)
for child in mainframe.winfo_children(): 
    child.grid_configure(padx=5, pady=5)

feet_entry.focus()
root.bind("<Return>", calculate)

# testing other widgets:
image = PhotoImage(file="images/" + "bK" + ".png")
l1 = ttk.Label(mainframe, image=image, background='green').grid(column=1, row=2)
#l1['background'] = 'green'

# testing dialog box

def display_queening_selection():
        
    def dismiss ():
        print(f'Selected: {queen_peace_var.get()}')
        dlg.grab_release()
        dlg.destroy()

    dlg = Toplevel(root)
    dlg.title('Quinning Peace')
    dlg.geometry('350x100+100+400')
    dlgframe = ttk.Frame(dlg, padding=(3, 3, 3, 3))
    dlgframe.grid(column=0, row=0, sticky=(N, W, E, S))

    ttk.Label(dlgframe, text="Select a peace for quinning:  ").grid(column=1, row=1, sticky=W, pady=10)
    queen_peace_var = StringVar()
    queen_peace_var.set('Queen')
    queen_combo = ttk.Combobox(dlgframe, textvariable=queen_peace_var, values=('Queen', 'Rook', 'Bishop', 'Knight'),state=(['readonly'])).grid(column=2, row=1, sticky=W, pady=10)
    ttk.Button(dlgframe, text="Done", command=dismiss).grid(column=1,row=3,pady=10)
    dlg.protocol("WM_DELETE_WINDOW", dismiss) # intercept close button
    dlg.transient(root)   # dialog window is related to main
    dlg.wait_visibility() # can't grab until window appears, so we wait
    dlg.grab_set()        # ensure all input goes to our window
    dlg.wait_window()     # block until window is destroyed


ttk.Button(mainframe, text="Queening", command=display_queening_selection).grid(column=1, row=3, sticky=W)


root.mainloop()
