import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from spectre.spectrogram.Panels import Panels
 

class PanelStacker(Panels):  
    def __init__(self, S):
        super().__init__(S)
    
    def create_figure(self, fig: Figure, panel_types: str):
        if len(panel_types)==1:
            is_one_panel=True
        else:
            is_one_panel=False
        
        # # Create a figure with subplots for plots and colorbars
        # two columns, one for the panels, and an optional column for the colorbars
        axs = fig.subplots(len(panel_types), 2, 
                            gridspec_kw={'width_ratios': [3, 0.1], 
                            'wspace': 0.05},
                            squeeze=False
                            )
        # Iterate over the plot types and their respective axes
        for panel_index, panel_type in enumerate(panel_types):
            ax = axs[panel_index, 0]  # Plot on the first column
            cax = axs[panel_index, 1]  # Colorbar on the second column

            # by default, turn the color axis off
            cax.axis('off')  # Initially turn off the colorbar axis; it will be turned on if needed

            # Get the plotting function
            plot_method = self.get_plot_method(panel_type)

            # Call the plotting function with its specific kwargs
            plot_method(ax=ax, cax=cax)  # Pass both plot and colorbar axes

            # Hide x-axis labels for all but the bottom plot
            if panel_index < len(panel_types) - 1:
                ax.tick_params(labelbottom=False)
            
            if panel_index ==len(panel_types)-1 or is_one_panel:
                ax.set_xlabel('Time [GMT]', size=self.fsize_head)


        