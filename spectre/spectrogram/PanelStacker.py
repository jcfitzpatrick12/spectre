import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from spectre.spectrogram.Panels import Panels
 

class PanelStacker(Panels):  
    def __init__(self, S, **kwargs):
        self.time_type = kwargs.get("time_type", "time_seconds")

        self.valid_time_types = ["datetimes", "time_seconds"]
        if self.time_type not in self.valid_time_types:
            raise ValueError(f"Must set a valid time type. Received {self.time_type}, expected one of {self.valid_time_types}.")
             
        super().__init__(S, self.time_type, **kwargs)
    
    def create_figure(self, fig: Figure, panel_types: str):
            # Create a figure with subplots for plots and colorbars
            axs = fig.subplots(len(panel_types), 2, 
                            gridspec_kw={'width_ratios': [3, 0.1], 'wspace': 0.05},
                            squeeze=False)

            # Store the first axis to link subsequent axes
            first_ax = None

            # Iterate over the plot types and their respective axes
            for i, (ax, cax) in enumerate(zip(axs[:, 0], axs[:, 1])):
                # Turn the colorbar axis off initially; it will be turned on if needed
                cax.axis('off')

                # Get the plotting function
                plot_method = self.get_plot_method(panel_types[i])

                # Call the plotting function with its specific kwargs
                plot_method(ax=ax, cax=cax)

                # Manage x-axis visibility and linking
                if first_ax is not None:
                    ax.sharex(first_ax)  # Link x-axis with the first axis
                else:
                    first_ax = ax  # Set the first axis

                if i == len(panel_types) - 1:

                    if self.time_type == "datetimes":
                        ax.set_xlabel(f'Time (Start Time: {self.S.chunk_start_time}) [GMT]', size=self.fsize_head)

                    elif self.time_type == "time_seconds":
                        ax.set_xlabel(f'Time [s]', size=self.fsize_head) 
                    
                    else:
                        raise ValueError(f"Must set a valid time type. Received {self.time_type}, expected one of {self.valid_time_types}.")
                else:
                    ax.tick_params(labelbottom=False)  # Hide x-tick labels for all but the last ax

            # Align all x-axes and labels
            plt.subplots_adjust(hspace=0)  # Adjust horizontal space to zero


            