import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from matplotlib.figure import Figure
from datetime import datetime

from spectre.spectrogram.Panels import Panels
from spectre.utils import array_helpers
 

class ComparisonStack:  
    def compare(self, fig: Figure, S0, S1, **kwargs):
        # Create a figure with subplots for plots and colorbars
        # order of comparison plots:
        ###
        # 0 - frequency slices
        # 1 - time slices
        # 2 - integrated power comparison
        # 3 - S0 spectrogram
        # 4 - S1 spectrogram
        ###
        axs = fig.subplots(5, 2, 
                        gridspec_kw={'width_ratios': [3, 0.1], 
                                        'wspace': 0.05,
                                        'hspace': 0.4,
                                        },
                        squeeze=False)
        
        kwargs["fsize_head"] = 14
        S0_kwargs = kwargs.copy()
        S0_kwargs['slice_cmap'] = cm.summer
        
        S1_kwargs = kwargs.copy()
        S1_kwargs['slice_cmap'] = cm.winter

        S0_panels = Panels(S0, **S0_kwargs)
        S1_panels = Panels(S1, **S1_kwargs)

        # Turn the colorbar axis off
        axs[0,1].axis('off')
        S0_panels.frequency_slices(ax=axs[0,0], cax=axs[0,1])
        S1_panels.frequency_slices(ax=axs[0,0], cax=axs[0,1])

        axs[1,1].axis('off')
        S0_panels.time_slices(ax=axs[1,0], cax=axs[1,1])
        S1_panels.time_slices(ax=axs[1,0], cax=axs[1,1])
        spectrogram_type = kwargs.get("spectrogram_type", "raw")
        
        axs[2,1].axis('off')
        S0_panels.integrated_power(ax=axs[2,0], cax=axs[2,1])
        S1_panels.integrated_power(ax=axs[2,0], cax=axs[2,1])
        axs[2,0].sharex(axs[1,0])  # Link x-axis with the first axis
        
        expected_spectrogram_types = ["dBb", "rawlog", "raw"]
        if spectrogram_type not in expected_spectrogram_types:
            raise ValueError(f"Received unexpected spectrogram_type: {spectrogram_type}. Expected one of {expected_spectrogram_types}.")
        
        axs[3,1].axis('off')
        S0_spectrogram_plot_method = S0_panels.get_plot_method(spectrogram_type)
        S0_spectrogram_plot_method(axs[3,0], axs[3,1])
        axs[3,0].sharex(axs[1,0])

        axs[4,1].axis('off')
        S1_spectrogram_plot_method = S1_panels.get_plot_method(spectrogram_type)
        S1_spectrogram_plot_method(axs[4,0], axs[4,1])
        axs[4,0].sharex(axs[1,0])

        time_type = kwargs.get("time_type", "time_seconds")
        if time_type == "time_seconds":
            axs[4,0].set_xlabel(f'Time [s]', size = S1_panels.fsize_head) 

        elif time_type == "datetimes":
            axs[4,0].set_xlabel(f'Time [UTC]', size = S1_panels.fsize_head)
        
        else:
            raise ValueError(f"Must set a valid time type. Received {self.time_type}, expected one of {self.valid_time_types}.")
        

        fig.align_ylabels() 
        return