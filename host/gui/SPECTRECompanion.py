import tkinter as tk
from host.gui.ui_components import create_labeled_entry, setup_plot, create_tickbox_frame
from host.gui.ChunksHandler import ChunksHandler

class SPECTRECompanion:
    def __init__(self, master, initial_tag: str):
        self.master = master
        self.master.title("SPECTRE Companion")
        self.tag = initial_tag
        self.chunks_handler = ChunksHandler(self.tag)
        self.entries = {}
        self.setup_widgets()

    def setup_widgets(self):
        self.update_widgets()
        self.update_entries(self.chunks_handler.get_field_defaults())


    def update_widgets(self):
        tk.Button(self.master, text="Update", command=self.update_tag_from_entry).grid(row=0, column=2, sticky="ew")
        tk.Button(self.master, text="Plot", command=self.plot_data).grid(row=8, column=0, sticky="ew")
        self.figure, self.canvas = setup_plot(self.master)
        self.panel_type_frame, self.panel_type_vars = create_tickbox_frame(self.master, self.chunks_handler.get_panel_types(), "Plot Types")


    def update_tag_from_entry(self):
        self.tag = self.entries['tag'].get()
        self.chunks_handler.update_tag(self.tag)
        self.update_entries(self.chunks_handler.get_field_defaults())


    def update_entries(self, field_values):
        field_labels = self.chunks_handler.get_field_labels()
        for i, (field, value) in enumerate(field_values.items(), start=0):
            if field in self.entries:
                entry = self.entries[field]
                entry.delete(0, tk.END)
                entry.insert(0, value)
            else:
                self.entries[field] = create_labeled_entry(self.master, field_labels[field], value, i)

    def plot_data(self):
        selected_panels = [ptype for ptype, var in self.panel_type_vars.items() if var.get()]
        spectrogram = self.chunks_handler.get_spectrogram(self.entries)
        self.figure.clear()  # Clear the existing plot
        spectrogram.stack_panels(self.figure, selected_panels)
        self.canvas.draw()


def main(tag):
    root = tk.Tk()
    app = SPECTRECompanion(root, tag)
    root.mainloop()
