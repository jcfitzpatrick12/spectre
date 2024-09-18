# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

 

class PanelStack(Panels):  
    def __init__(self, S, **kwargs):
        super().__init__(S, **kwargs)
    
    def create_figure(self, fig: Figure, panel_types: str):
            # Create a figure with subplots for plots and colorbars
            axs = fig.subplots(len(panel_types), 2, 
                            gridspec_kw={'width_ratios': [3, 0.1], 
                                         'wspace': 0.05,
                                         'hspace': 0.4,
                                         },
                            squeeze=False)

            # Store the first axis to link subsequent axes
            first_ax = None

            # if the user has requested "frequency_slices" we consider this first
            # this is handled differently since it does not share the time axes with the other panels
            if "frequency_slice" in panel_types:
                # move this to the front
                panel_types = array_helpers.move_to_front(panel_types, "frequency_slice")
                # ax and cax will be the first panels
                ax, cax = axs[0, 0], axs[0, 1]
                # Turn the colorbar axis off
                cax.axis('off')
                # Call the plotting function with its specific kwargs
                self.frequency_slice(ax=ax, cax=cax)
 

            # Iterate over the plot types with Time on the x-axis, and plot
            for i, (ax, cax) in enumerate(zip(axs[:, 0], axs[:, 1])):
                panel_type = panel_types[i]

                # frequency slices panel (if specified)
                # has already been handled, so ignore
                if panel_type == "frequency_slice":
                    continue

                # Turn the colorbar axis off initially; it will be turned on if needed
                cax.axis('off')
                # Get the plotting method
                plot_method = self.get_plot_method(panel_type)

                # Call the plotting function with its specific kwargs
                plot_method(ax=ax, cax=cax)

                if first_ax is not None:
                    ax.sharex(first_ax)  # Link x-axis with the first axis
                else:
                    first_ax = ax  # Set the first axis

                # depending on the time type, label the final panel
                if i == len(panel_types) - 1:
                    if self.time_type == "datetimes":
                        ax.set_xlabel(f'Time [UTC]', size=self.fsize_head)

                    elif self.time_type == "time_seconds":
                        ax.set_xlabel(f'Time [s]', size=self.fsize_head) 
                    
                    else:
                        raise ValueError(f"Must set a valid time type. Received {self.time_type}, expected one of {self.valid_time_types}.")
            # Hide x-tick labels for all but the last ax
                else:
                    ax.tick_params(labelbottom=False) 
    
            fig.align_ylabels() 


            