import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from matplotlib.figure import Figure
from datetime import datetime

from spectre.spectrogram.Panels import Panels
from spectre.utils import array_helpers
 

class ComparisonStack:  
    def compare_with_callisto(self, fig: Figure, S, callisto_S, **kwargs):
        # Create a figure with subplots for plots and colorbars
        # order of comparison plots:

        ###
        # 0 - frequency slices
        # 1 - time slices
        # 2 - integrated frequency comparison
        # 3 - S spectrogram
        # 4 - callisto_S spectrogram
        ###

        if "callisto" not in callisto_S.tag:
            raise ValueError(f"Expected comparison with a callisto spectrogram! Received an unexpected tag {callisto_S.tag}")
        
        axs = fig.subplots(5, 2, 
                        gridspec_kw={'width_ratios': [2.5, 0.1], 
                                        'wspace': 0.05,
                                        'hspace': 0.4,
                                        },
                        squeeze=False)
        
        kwargs['normalise_line_plots'] = True
        kwargs['add_tag_to_annotation'] = True

        S_kwargs = kwargs.copy()
        S_kwargs['slice_color'] = 'fuchsia'
        S_kwargs['dB_vmin']=-1
        S_kwargs['dB_vmax']=4
        
        callisto_S_kwargs = kwargs.copy()
        callisto_S_kwargs['slice_color'] = 'dodgerblue'
        callisto_S_kwargs['dB_vmin']=-1
        callisto_S_kwargs['dB_vmax']=14
        callisto_S_kwargs['annotation_vertical_offset'] = 0.8

        S_panels = Panels(S, **S_kwargs)
        callisto_S_panels = Panels(callisto_S, **callisto_S_kwargs)

        # Turn the colorbar axis off
        axs[0,1].axis('off')
        # axs[0,0].tick_params(labelleft=False)
        # axs[0,0].tick_params(labelbottom=False) 
        S_panels.frequency_slice(ax=axs[0,0], cax=axs[0,1])
        callisto_S_panels.frequency_slice(ax=axs[0,0], cax=axs[0,1])

        axs[1,1].axis('off')
        axs[1,0].tick_params(labelbottom=False) 
        # axs[1,0].tick_params(labelleft=False) 
        S_panels.time_slice(ax=axs[1,0], cax=axs[1,1])
        callisto_S_panels.time_slice(ax=axs[1,0], cax=axs[1,1])
        spectrogram_type = kwargs.get("spectrogram_type", "raw")
        
        axs[2,1].axis('off')
        axs[2,0].tick_params(labelbottom=False) 
        # axs[2,0].tick_params(labelleft=False)
        S_panels.integrate_over_frequency(ax=axs[2,0], cax=axs[2,1])
        callisto_S_panels.integrate_over_frequency(ax=axs[2,0], cax=axs[2,1])
        axs[2,0].sharex(axs[1,0])  # Link x-axis with the first axis
        
        expected_spectrogram_types = ["dBb", "rawlog", "raw"]
        if spectrogram_type not in expected_spectrogram_types:
            raise ValueError(f"Received unexpected spectrogram_type: {spectrogram_type}. Expected one of {expected_spectrogram_types}.")
        
        axs[3,1].axis('off')
        axs[3,0].tick_params(labelbottom=False) 
        # axs[3,0].tick_params(labelleft=False)
        S_spectrogram_plot_method = S_panels.get_plot_method(spectrogram_type)
        S_spectrogram_plot_method(axs[3,0], axs[3,1])
        axs[3,0].sharex(axs[1,0])

        axs[4,1].axis('off')
        callisto_S_spectrogram_plot_method = callisto_S_panels.get_plot_method(spectrogram_type)
        callisto_S_spectrogram_plot_method(axs[4,0], axs[4,1])
        axs[4,0].sharex(axs[1,0])

        axs[4,0].set_xlabel(f'Time [UTC]', size = callisto_S_panels.fsize_head)
    
        fig.align_ylabels() 
        return