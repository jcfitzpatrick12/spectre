import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from spectre.chunks.Chunks import Chunks
from spectre.spectrogram import factory
from host.cfg import CONFIG
from spectre.spectrogram.Panels import Panels

class SPECTRECompanion:
    def __init__(self, master, initial_tag: str):
        self.master = master
        self.master.title("SPECTRE Companion")
        self.tag = initial_tag
        self.initialize_components()

    def initialize_components(self):
        self.load_chunks()
        self.setup_widgets()
        self.set_default_values()
        self.update_entry_fields()
        self.populate_panel_types()


    def load_chunks(self):
        self.chunks = Chunks(self.tag, CONFIG.chunks_dir, CONFIG.json_configs_dir)


    def setup_widgets(self):
        self.tag_entry = self.create_labeled_entry("tag:", self.tag, 0)
        tk.Button(self.master, text="Update", command=self.update_tag_from_entry).grid(row=0, column=2, sticky="ew")
        tk.Button(self.master, text="Plot", command=self.plot_data).grid(row=8, column=0, sticky="ew")

        self.figure = Figure(figsize=(10, 10))
        self.canvas = FigureCanvasTkAgg(self.figure, self.master)
        self.canvas.get_tk_widget().grid(row=9, column=0, columnspan=3)


    def create_labeled_entry(self, label, default, row):
        tk.Label(self.master, text=label).grid(row=row, column=0)
        entry = tk.Entry(self.master)
        entry.grid(row=row, column=1)
        entry.insert(0, default)
        return entry


    def update_tag_from_entry(self):
        self.tag = self.tag_entry.get()
        self.load_chunks()
        self.set_default_values()
        self.update_entry_fields()
        self.populate_panel_types()


    def set_default_values(self):
        chunks_list = list(self.chunks.dict.values())
        for chunk in reversed(chunks_list):
            if chunk.fits.exists():
                default_S = chunk.fits.load_spectrogram()
                self.default_values = {
                    'start': default_S.datetimes[0].strftime(CONFIG.default_time_format),
                    'end': default_S.datetimes[-1].strftime(CONFIG.default_time_format),
                    'lower_freq': round(default_S.freq_MHz[0], 2),
                    'upper_freq': round(default_S.freq_MHz[-1], 2),
                    'avg_over_int_time': 1,
                    'avg_over_int_freq': 1
                }
                self.panel_types = Panels(default_S).panel_type_dict.keys()
                return
        raise ValueError(f"No fits files exist for tag {self.tag}")


    def update_entry_fields(self):
        fields = ['start', 'end', 'lower_freq', 'upper_freq', 'avg_over_int_time', 'avg_over_int_freq']
        self.entries = {field: self.create_labeled_entry(field + ":", self.default_values[field], i + 1) for i, field in enumerate(fields)}


    def populate_panel_types(self):
        if not hasattr(self, 'panel_type_frame'):
            self.panel_type_frame = tk.LabelFrame(self.master, text="Plot Types:")
            self.panel_type_frame.grid(row=7, column=0, columnspan=3)

        for widget in self.panel_type_frame.winfo_children():
            widget.destroy()

        self.panel_type_vars = {ptype: tk.BooleanVar() for ptype in self.panel_types}
        for ptype in self.panel_types:
            tk.Checkbutton(self.panel_type_frame, text=ptype, variable=self.panel_type_vars[ptype]).pack(side=tk.LEFT)


    def get_selected_panel_types(self):
        return [ptype for ptype, var in self.panel_type_vars.items() if var.get()]


    def plot_data(self):
        S = self.get_spectrogram()
        self.figure.clear()
        S.stack_panels(self.figure, self.get_selected_panel_types())
        self.canvas.draw()


    def get_spectrogram(self):
        start, end = self.entries['start'].get(), self.entries['end'].get()
        lower_freq, upper_freq = float(self.entries['lower_freq'].get()), float(self.entries['upper_freq'].get())
        S = self.chunks.build_spectrogram_from_range(start, end)
        S = factory.frequency_chop(S, lower_freq, upper_freq)
        S = factory.frequency_average(S, int(self.entries['avg_over_int_freq'].get()))
        S = factory.time_average(S, int(self.entries['avg_over_int_time'].get()))
        return S


def main(tag):
    root = tk.Tk()
    app = SPECTRECompanion(root, tag)
    root.mainloop()