import tkinter as tk


from argparse import ArgumentParser
from client.devgui.ui_components import create_labeled_entry, setup_plot, create_tickbox_frame
from client.devgui.ChunksHandler import ChunksHandler

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
        tk.Button(self.master, text="Update", command=self.update).grid(row=7, column=0, sticky="ew")
        tk.Button(self.master, text="Plot", command=self.plot_data).grid(row=8, column=0, sticky="ew")
        self.figure, self.canvas = setup_plot(self.master)
        self.panel_type_frame, self.panel_type_vars = create_tickbox_frame(self.master, self.chunks_handler.get_panel_types(), "Plot Types")


    def update(self):
        self.tag = self.entries['tag'].get()
        # get the start time so we can optimise chunks file finding
        start_time = self.entries['start_time'].get()
        self.chunks_handler.set_attrs(self.tag, start_time=start_time)
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
        spectrogram.stack_panels(self.figure, selected_panels, time_type = "time_seconds")
        self.canvas.draw()


def main(tag: str):
    root = tk.Tk()
    app = SPECTRECompanion(root, tag)
    root.mainloop()

if __name__=="__main__":
    parser = ArgumentParser()
    parser.add_argument("--tag", type=str, help="")
    args = parser.parse_args()
    tag = args.tag

    if tag is None:
        raise ValueError(f"Tag must be specified, received {tag}. Use --tag [TAG]")
    
    main(tag)

