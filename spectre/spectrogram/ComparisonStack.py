import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from matplotlib.figure import Figure
from datetime import datetime
import matplotlib.dates as mdates

from spectre.spectrogram.Panels import Panels
from spectre.utils import dict_helpers
 

class ComparisonStack:      
    def compare(self, 
                    fig: Figure,
                    S0, 
                    S1, 
                    override_S0_kwargs=None, 
                    override_S1_kwargs=None, 
                    spectrogram_type = "raw",
                    time_type = "datetimes",
                    **kwargs) -> None: 
        axs = fig.subplots(5, 2, 
                        gridspec_kw={'width_ratios': [2.5, 0.1], 
                                     'wspace': 0.05,
                                     'hspace': 0.4,
                                     },
                        squeeze=False)

        kwargs['time_type'] = time_type
        kwargs['normalise_line_plots'] = True

        S0_kwargs = kwargs.copy()
        if not override_S0_kwargs is None:
            S0_kwargs = dict_helpers.inject_dict(S0_kwargs, override_S0_kwargs)
        S0_panels = Panels(S0, **S0_kwargs)

        S1_kwargs = kwargs.copy()
        S1_kwargs['slice_color'] = 'fuchsia'
        S1_kwargs['annotation_vertical_offset'] = 0.8
        if not override_S1_kwargs is None:
            S1_kwargs = dict_helpers.inject_dict(S1_kwargs, override_S1_kwargs)
        S1_panels = Panels(S1, **S1_kwargs)

        # Turn the colorbar axis off
        axs[0,1].axis('off')
        S0_panels.frequency_slice(ax=axs[0,0], cax=axs[0,1])
        S1_panels.frequency_slice(ax=axs[0,0], cax=axs[0,1])

        axs[1,1].axis('off')
        axs[1,0].tick_params(labelbottom=False) 
        S0_panels.time_slice(ax=axs[1,0], cax=axs[1,1])
        S1_panels.time_slice(ax=axs[1,0], cax=axs[1,1])
        
        axs[2,1].axis('off')
        axs[2,0].tick_params(labelbottom=False) 
        S0_panels.integrate_over_frequency(ax=axs[2,0], cax=axs[2,1])
        S1_panels.integrate_over_frequency(ax=axs[2,0], cax=axs[2,1])
        axs[2,0].sharex(axs[1,0])  # Link x-axis with the first axis
        
        expected_spectrogram_types = ["dBb", "rawlog", "raw"]
        if spectrogram_type not in expected_spectrogram_types:
            raise ValueError(f"Received unexpected spectrogram_type: {spectrogram_type}. Expected one of {expected_spectrogram_types}.")
        
        axs[3,1].axis('off')
        axs[3,0].tick_params(labelbottom=False) 
        S0_spectrogram_plot_method = S0_panels.get_plot_method(spectrogram_type)
        S0_spectrogram_plot_method(axs[3,0], axs[3,1])
        axs[3,0].sharex(axs[1,0])

        axs[4,1].axis('off')
        S1_spectrogram_plot_method = S1_panels.get_plot_method(spectrogram_type)
        S1_spectrogram_plot_method(axs[4,0], axs[4,1])
        axs[4,0].set_xlabel(f'Time [UTC]', size = S1_panels.fsize_head)
        axs[4,0].sharex(axs[1,0])
        axs[4,0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    
        fig.align_ylabels() 
        return
    