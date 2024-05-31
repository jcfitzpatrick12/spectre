from datetime import datetime
import numpy as np
import typer

from spectre.json_config.CaptureConfigHandler import CaptureConfigHandler
from spectre.receivers.Receiver import Receiver
from spectre.chunks.Chunks import Chunks
from spectre.spectrogram.AnalyticalSpectrogramFactory import AnalyticalSpectrogramFactory
from spectre.spectrogram.Spectrogram import Spectrogram

def times_of_failed_spectral_slices(S: Spectrogram, is_close: np.array) -> list:
    failed_indices = np.where(~is_close)
    index_set_of_failed_spectral_slices = set(failed_indices[1])
    times = []
    for index in index_set_of_failed_spectral_slices:
        time_of_failed_spectral_slice = S.time_seconds[index]
        times.append(time_of_failed_spectral_slice)
    return times


def compare_spectrograms(S: Spectrogram, analytical_S: Spectrogram) -> None:
    if not S.shape == analytical_S.shape:
        raise ValueError(f"Shape mismatch between synthesised spectra: {S.shape}, and analytical spectra: {analytical_S}.")
    
    synthesised_dynamic_spectra = S.dynamic_spectra
    analytical_dynamic_spectra = analytical_S.dynamic_spectra

    num_time_samples = S.shape[1]
    
    is_close = np.isclose(
        S.dynamic_spectra,
        analytical_S.dynamic_spectra,
        atol = 1e-7,
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
            typer.secho(f"Chunk:{S.chunk_start_time} failed validation.", fg=typer.colors.RED)
        # otherwise, we had a partial success (at least one isclose evaluated to true)
        else:
            typer.secho(f"Chunk:{S.chunk_start_time} partial success", fg=typer.colors.YELLOW)
            failure_times = times_of_failed_spectral_slices(S, is_close)
            print(f"Comparison failed for spectral slice at t={failure_times}.")

        # return

def main(test_tag: str) -> None:
    # load the capture config corresponding to the input test tag
    capture_config_handler = CaptureConfigHandler(test_tag)
    capture_config = capture_config_handler.load_as_dict()
    
    # first check the receiver specified in the capture config is a Test receiver
    receiver = capture_config['receiver']
    if receiver != "Test":
        raise ValueError(f"Receiver for the specified capture config must be \"Test\". Got {receiver}")
    
    # check that the user specified mode is that specified in the capture config
    test_mode = capture_config['mode']    
    # check the mode is a defined mode for the Test receiver
    test_receiver = Receiver("Test")
    if test_mode not in test_receiver.valid_modes:
        raise ValueError(f"{test_mode} is not a valid mode. Expected one of {test_receiver.valid_modes}.")
    
    asf = AnalyticalSpectrogramFactory()

    today = datetime.now()
    my_chunks = Chunks(test_tag, year=today.year, month=today.month, day=today.day)
    chunkf = None
    for chunk_start_time, chunk in my_chunks.dict.items():
        if chunk.fits.exists():
            chunkf = chunk
            S = chunkf.fits.load_spectrogram()  
            analytical_S = asf.get_spectrogram(test_mode, S.shape, capture_config)

            compare_spectrograms(S, analytical_S,)

    if chunkf is None:
        raise ValueError(f"No .fits files found with the tag \"{test_tag}\" in {my_chunks.chunks_dir}.")

    return

    return
