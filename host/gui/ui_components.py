import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def create_labeled_entry(master, label, default, row):
    tk.Label(master, text=label).grid(row=row, column=0)
    entry = tk.Entry(master)
    entry.grid(row=row, column=1)
    entry.insert(0, default)
    return entry


def setup_plot(master):
    figure = Figure(figsize=(17, 10))
    canvas = FigureCanvasTkAgg(figure, master)
    canvas.get_tk_widget().grid(row=9, column=0, columnspan=4)
    return figure, canvas


def create_tickbox_frame(master, options, title="Options", row=7, column=0, columnspan=3):
    frame = tk.LabelFrame(master, text=title)
    frame.grid(row=row, column=column, columnspan=columnspan)

    var_dict = {}
    for option in options:
        var = tk.BooleanVar()
        tk.Checkbutton(frame, text=option, variable=var).pack(side=tk.LEFT)
        var_dict[option] = var

    return frame, var_dict
