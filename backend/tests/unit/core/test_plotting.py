# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import os

import numpy as np
import pytest

import spectre_server.core.config
import spectre_server.core.plotting
import spectre_server.core.spectrograms

ARBITRARY_DATETIME = datetime.datetime(2025, 2, 13, 6, 0, 0)
TAG = "tag"


@pytest.fixture(autouse=True)
def setup_random_seed():
    np.random.seed(42)


@pytest.fixture
def spectrogram() -> spectre_server.core.spectrograms.Spectrogram:
    dynamic_spectra = np.random.uniform(-1, 1, (64, 20)).astype(np.float32)
    times = np.linspace(0, 10, 20).astype(np.float32)
    frequencies = np.linspace(90e6, 110e6, 64).astype(np.float32)
    return spectre_server.core.spectrograms.Spectrogram(
        dynamic_spectra,
        times,
        frequencies,
        spectre_server.core.spectrograms.SpectrumUnit.AMPLITUDE,
        ARBITRARY_DATETIME,
    )


@pytest.fixture
def panel(
    spectrogram: spectre_server.core.spectrograms.Spectrogram,
) -> spectre_server.core.plotting.SpectrogramPanel:
    return spectre_server.core.plotting.SpectrogramPanel(spectrogram)


@pytest.fixture
def panel_stack() -> spectre_server.core.plotting.PanelStack:
    return spectre_server.core.plotting.PanelStack(non_interactive=True)


class TestSpectrogramPanel:
    def test_stores_spectrogram(
        self,
        panel: spectre_server.core.plotting.SpectrogramPanel,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        assert panel.spectrogram is spectrogram

    def test_default_options(
        self,
        panel: spectre_server.core.plotting.SpectrogramPanel,
    ) -> None:
        assert panel.log_norm is False
        assert panel.dBb is False
        assert panel.vmin is None
        assert panel.vmax is None

    def test_custom_options(
        self,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        panel = spectre_server.core.plotting.SpectrogramPanel(
            spectrogram, log_norm=True, dBb=True, vmin=-2, vmax=5
        )
        assert panel.log_norm is True
        assert panel.dBb is True
        assert panel.vmin == -2
        assert panel.vmax == 5


class TestPanelStack:
    def test_add_panel_increments_count(
        self,
        panel_stack: spectre_server.core.plotting.PanelStack,
        panel: spectre_server.core.plotting.SpectrogramPanel,
    ) -> None:
        assert panel_stack.num_panels == 0
        panel_stack.add_panel(panel)
        assert panel_stack.num_panels == 1
        panel_stack.add_panel(panel)
        assert panel_stack.num_panels == 2

    def test_save_creates_file(
        self,
        spectre_config_paths: spectre_server.core.config.Paths,
        panel: spectre_server.core.plotting.SpectrogramPanel,
    ) -> None:
        panel_stack = spectre_server.core.plotting.PanelStack(non_interactive=True)
        panel_stack.add_panel(panel)
        batches_dir = spectre_config_paths.get_batches_dir_path(2025, 2, 13)
        path = panel_stack.save(TAG, batches_dir)
        assert path.endswith(".png")
        assert os.path.exists(path)

    def test_save_no_panels_raises(
        self,
        spectre_config_paths: spectre_server.core.config.Paths,
    ) -> None:
        panel_stack = spectre_server.core.plotting.PanelStack(non_interactive=True)
        batches_dir = spectre_config_paths.get_batches_dir_path(2025, 2, 13)
        with pytest.raises(ValueError):
            panel_stack.save(TAG, batches_dir)

    def test_save_with_dBb(
        self,
        spectre_config_paths: spectre_server.core.config.Paths,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        panel_stack = spectre_server.core.plotting.PanelStack(non_interactive=True)
        panel_stack.add_panel(
            spectre_server.core.plotting.SpectrogramPanel(spectrogram, dBb=True)
        )
        batches_dir = spectre_config_paths.get_batches_dir_path(2025, 2, 13)
        path = panel_stack.save(TAG, batches_dir)
        assert os.path.exists(path)

    def test_save_with_log_norm(
        self,
        spectre_config_paths: spectre_server.core.config.Paths,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        panel_stack = spectre_server.core.plotting.PanelStack(non_interactive=True)
        panel_stack.add_panel(
            spectre_server.core.plotting.SpectrogramPanel(spectrogram, log_norm=True)
        )
        batches_dir = spectre_config_paths.get_batches_dir_path(2025, 2, 13)
        path = panel_stack.save(TAG, batches_dir)
        assert os.path.exists(path)

    def test_save_elapsed_time(
        self,
        spectre_config_paths: spectre_server.core.config.Paths,
        panel: spectre_server.core.plotting.SpectrogramPanel,
    ) -> None:
        panel_stack = spectre_server.core.plotting.PanelStack(
            non_interactive=True, elapsed_time=True
        )
        panel_stack.add_panel(panel)
        batches_dir = spectre_config_paths.get_batches_dir_path(2025, 2, 13)
        path = panel_stack.save(TAG, batches_dir)
        assert os.path.exists(path)

    def test_save_mhz(
        self,
        spectre_config_paths: spectre_server.core.config.Paths,
        panel: spectre_server.core.plotting.SpectrogramPanel,
    ) -> None:
        panel_stack = spectre_server.core.plotting.PanelStack(
            non_interactive=True, mhz=True
        )
        panel_stack.add_panel(panel)
        batches_dir = spectre_config_paths.get_batches_dir_path(2025, 2, 13)
        path = panel_stack.save(TAG, batches_dir)
        assert os.path.exists(path)

    def test_save_multiple_panels(
        self,
        spectre_config_paths: spectre_server.core.config.Paths,
        spectrogram: spectre_server.core.spectrograms.Spectrogram,
    ) -> None:
        panel_stack = spectre_server.core.plotting.PanelStack(non_interactive=True)
        panel_stack.add_panel(
            spectre_server.core.plotting.SpectrogramPanel(spectrogram)
        )
        panel_stack.add_panel(
            spectre_server.core.plotting.SpectrogramPanel(spectrogram, dBb=True)
        )
        batches_dir = spectre_config_paths.get_batches_dir_path(2025, 2, 13)
        path = panel_stack.save(TAG, batches_dir)
        assert os.path.exists(path)
