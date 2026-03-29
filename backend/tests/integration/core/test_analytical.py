# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing
import pytest

import spectre_server.core.receivers
import spectre_server.core.config
import spectre_server.core.batches


@pytest.fixture
def signal_generator() -> spectre_server.core.receivers.SignalGenerator:
    """Get a signal generator, with mode not yet set."""
    return spectre_server.core.receivers.get_receiver("signal_generator")


ATOL = 1e-4
DURATION = 5
USE_DEFAULT_PARAMETERS: dict[str, typing.Any] = {}
COSINE_WAVE_MODE = "cosine_wave"
COSINE_WAVE_PARAMETERS = {
    "batch_size": 1,
    "amplitude": 3.0,
    "frequency": 16000.0,
    "window_hop": 256,
    "window_size": 256,
    "window_type": "boxcar",
    "sample_rate": 128000,
}

CONSTANT_STAIRCASE_MODE = "constant_staircase"
CONSTANT_STAIRCASE_PARAMETERS = {
    "batch_size": 1,
    "window_hop": 512,
    "window_size": 512,
    "window_type": "boxcar",
    "frequency_hop": 128000.0,
    "max_samples_per_step": 5000,
    "min_samples_per_step": 4000,
    "sample_rate": 128000,
    "step_increment": 200,
}


@pytest.mark.parametrize(
    ("modes", "parameters"),
    [
        ([COSINE_WAVE_MODE], [USE_DEFAULT_PARAMETERS]),
        ([COSINE_WAVE_MODE], [COSINE_WAVE_PARAMETERS]),
        ([CONSTANT_STAIRCASE_MODE], [USE_DEFAULT_PARAMETERS]),
        ([CONSTANT_STAIRCASE_MODE], [CONSTANT_STAIRCASE_PARAMETERS]),
        (
            [COSINE_WAVE_MODE, CONSTANT_STAIRCASE_MODE],
            [USE_DEFAULT_PARAMETERS, USE_DEFAULT_PARAMETERS],
        ),
    ],
)
def test_analytical(
    modes: list[str],
    parameters: list[dict[str, typing.Any]],
    spectre_config_paths: spectre_server.core.config.Paths,
    signal_generator: spectre_server.core.receivers.SignalGenerator,
) -> None:
    """Test end-to-end execution of the program using the signal generator, comparing
    the results to analytically derived solutions."""
    configs: list[spectre_server.core.receivers.Config] = []
    for mode, p in zip(modes, parameters):
        # Set the mode of the receiver.
        signal_generator.mode = mode

        # Make a new config, with the tag dynamically created based on the receiver mode.
        tag = mode.replace("_", "-")
        signal_generator.write_config(
            tag,
            p,
            configs_dir_path=spectre_config_paths.get_configs_dir_path(),
        )

        # Read the config back from the filesystem.
        configs.append(
            signal_generator.read_config(
                tag, configs_dir_path=spectre_config_paths.get_configs_dir_path()
            )
        )

    # Record some spectrograms.
    spectre_server.core.receivers.record_spectrograms(
        configs,
        DURATION,
        spectre_data_dir_path=spectre_config_paths.get_spectre_data_dir_path(),
    )

    for config in configs:
        # Check that we've found some spectrograms.
        found_spectrograms = False

        signal_generator.mode = config.receiver_mode

        # Compare each spectrogram to the corresponding analytically derived solutions.
        for batch in spectre_server.core.batches.Batches(
            config.tag,
            signal_generator.batch_cls,
            spectre_config_paths.get_batches_dir_path(),
        ):
            if batch.spectrogram_file.exists:

                spectrogram = batch.read_spectrogram()
                found_spectrograms = True

                result = signal_generator.validate_analytically(
                    spectrogram,
                    signal_generator.model_validate(config.parameters),
                    ATOL,
                )

                assert result["frequencies_validated"]
                assert result["times_validated"]

                # Permit at most one invalid spectrum (usually the first, due to window effects)
                assert 0 <= result["num_invalid_spectrums"] <= 1

            assert found_spectrograms
