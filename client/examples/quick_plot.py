# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime

from spectre.cfg import DEFAULT_DATETIME_FORMAT
from spectre.chunks import Chunks
from spectre.spectrograms.spectrogram import Spectrogram
from spectre.spectrograms.transform import (
    frequency_average, 
    frequency_chop, 
    time_average
)
from spectre.plotting.panel_stack import PanelStack


def get_spectrogram(tag: str, 
                    start_time: str, 
                    end_time: str) -> Spectrogram:
    start_datetime = datetime.strptime(start_time, 
                                       DEFAULT_DATETIME_FORMAT)
    chunks = Chunks(tag, 
                    year=start_datetime.year, 
                    month=start_datetime.month,
                    day=start_datetime.day)
    return chunks.get_spectrogram_from_range(start_time, end_time)


def main():
    start_time, end_time = "2024-10-03T12:19:30", "2024-10-03T12:25:00" # [UT]
    start_background, end_background = "2024-10-03T12:19:31", "2024-10-03T12:19:35" # [UT]
    lower_frequency, upper_frequency = 120e6, 150e6 # [Hz]
    cut_at = 124e6 # [Hz]

    spectrogram = get_spectrogram("RSP1A-sweeper", 
                                   start_time,
                                   end_time)
    spectrogram = frequency_average(spectrogram, 5)
    spectrogram = time_average(spectrogram, 1)
    spectrogram = frequency_chop(spectrogram, 
                                 lower_frequency,
                                 upper_frequency)
    spectrogram.set_background(start_background, end_background)
 
    egypt_spectrogram = get_spectrogram("callisto-egypt-alexandria-01",
                                         start_time,
                                         end_time)
    egypt_spectrogram = frequency_chop(egypt_spectrogram , 
                                       lower_frequency,
                                       upper_frequency)
    egypt_spectrogram.set_background(start_background, end_background)


    panel_stack = PanelStack("datetimes", 
                             figsize=(10,10))
    

    panel_stack.add_panel("spectrogram", egypt_spectrogram, 
                          dBb=True, vmin=0, vmax=13)
    
    panel_stack.add_panel("spectrogram", spectrogram, 
                          dBb=True, vmin=0, vmax=2)
    
    panel_stack.add_panel("time_cuts", spectrogram, 
                          cut_at,
                          peak_normalise = True,
                          background_subtract = True)

    panel_stack.superimpose_panel("time_cuts", egypt_spectrogram, 
                                  cut_at,
                                  peak_normalise=True,
                                  background_subtract = True,
                                  cmap = "summer")
    
    panel_stack.show()


if __name__ == "__main__":
    main()






        
