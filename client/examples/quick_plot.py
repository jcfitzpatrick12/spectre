# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre.chunks import Chunks
from spectre.plotting.panel_stack import PanelStack


def get_spectrogram(tag: str,
                    start_time: str, 
                    end_time: str):
    """ Read fits files and return the corresponding spectrogram """
    chunks = Chunks(tag)
    return chunks.get_spectrogram_from_range(start_time, end_time)


def main():
    # ------------------------ #  
    # Input                    #
    # ------------------------ #  
    tag = "rsp1a-sweep-example"
    start_time = "2024-11-01T14:00:00"
    end_time = "2024-11-01T14:15:00"

    # ------------------------ #  
    # Getting spectrogram      #
    # ------------------------ #  
    spectrogram = get_spectrogram(tag, 
                                  start_time, 
                                  end_time)
    
    # ------------------------ # 
    # Printing characteristics #
    # ------------------------ # 
    print(f"Frequency range: {spectrogram.frequency_range*1e-6} [MHz]")
    print(f"Frequency resolution: {spectrogram.frequency_resolution} [Hz]")
    print(f"Time range: {spectrogram.time_range} [s]")
    print(f"Time resolution: {spectrogram.time_resolution} [s]")

    # ------------------------ # 
    # Plotting                 #
    # ------------------------ #  
    panel_stack = PanelStack("seconds")
    panel_stack.add_panel("spectrogram", 
                          spectrogram,
                          log_norm=True)
    panel_stack.add_panel("integral_over_frequency",
                          spectrogram)
    panel_stack.show()
    return

if __name__ == "__main__":
    main()