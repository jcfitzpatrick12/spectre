# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime
import numpy as np
import typer

from spectre.json_config.CaptureConfigHandler import CaptureConfigHandler
from spectre.chunks.Chunks import Chunks
from spectre.spectrogram.AnalyticalSpectrogramFactory import AnalyticalSpectrogramFactory
from spectre.spectrogram.Spectrogram import Spectrogram
from spectre.receivers.factory import get_receiver

def print_slice_status(S: Spectrogram, is_close: np.array) -> None:
    for i, time in enumerate(S.time_seconds):
        formatted_time = f"{time:.4f}"
        is_close_slice = is_close[:,i]
        successful_slice = np.all(is_close_slice)
        if successful_slice:
            typer.secho(f"spectral-slice:t={formatted_time} analytically validated", fg=typer.colors.GREEN)
        else:
            if np.all(~is_close_slice):
                typer.secho(f"spectral-slice:t={formatted_time} failed validation", fg=typer.colors.RED)
            else:
                typer.secho(f"spectral-slice:t={formatted_time} partially validated", fg=typer.colors.YELLOW)


def compare_spectrograms(S: Spectrogram, analytical_S: Spectrogram, show_slice_status = False) -> None:
    if not S.dynamic_spectra.shape == analytical_S.dynamic_spectra.shape:
        raise ValueError(f"Shape mismatch between synthesised spectra: {S.dynamic_spectra.shape}, and analytical spectra: {analytical_S}.")
    
    is_close = np.isclose(
        S.dynamic_spectra,
        analytical_S.dynamic_spectra,
        atol = 1e-4,
        rtol = 0,
    )

    analytically_verified = np.all(is_close)

    # if all are true, we have had a total success
    if analytically_verified:
        typer.secho(f"Chunk:{S.chunk_start_time} analytically validated", fg=typer.colors.GREEN)
    else:
        total_failure = np.all(~is_close)
        # if every value does not match (according to isclose) then we have a total failure
        if total_failure:
            typer.secho(f"Chunk:{S.chunk_start_time} failed validation", fg=typer.colors.RED)
        # otherwise, we had a partial success (at least one isclose evaluated to true)
        else:
            typer.secho(f"Chunk:{S.chunk_start_time} partially validated", fg=typer.colors.YELLOW)
            if show_slice_status:
                print_slice_status(S, is_close)


def main(test_tag: str, show_slice_status = False) -> None:
    # load the capture config corresponding to the input test tag
    capture_config_handler = CaptureConfigHandler(test_tag)
    capture_config = capture_config_handler.load_as_dict()
    
    # first check the receiver specified in the capture config is a Test receiver
    receiver_name = capture_config['receiver']
    if receiver_name != "Test":
        raise ValueError(f"To do analytical verifications, the receiver in the specified capture config must be \"Test\". Received: {receiver_name}")
    
    # check that the user specified mode is that specified in the capture config
    test_mode = capture_config['mode']    
    
    # check the mode is a defined mode for the Test receiver
    test_receiver = get_receiver("Test")
    if test_mode not in test_receiver.valid_modes:
        raise ValueError(f"{test_mode} is not a valid mode. Expected one of {test_receiver.valid_modes}.")
    
    asf = AnalyticalSpectrogramFactory()

    today = datetime.now()
    my_chunks = Chunks(test_tag, year=today.year, month=today.month, day=today.day)
    chunk_list = my_chunks.get_chunk_list()
    current_chunk = None
    for chunk in chunk_list:
        current_chunk = chunk
        if current_chunk.fits.exists():
            S = chunk.fits.read()  
            analytical_S = asf.get_spectrogram(test_mode, S.dynamic_spectra.shape, capture_config)
            compare_spectrograms(S, analytical_S, show_slice_status = show_slice_status)

    if current_chunk is None:
        raise ValueError(f"No .fits files found with the tag \"{test_tag}\" in {my_chunks.chunks_dir}.")

    return


