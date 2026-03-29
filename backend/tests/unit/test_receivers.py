# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing
import os

import pytest
import pydantic

import spectre_server.core.receivers
import spectre_server.core.exceptions
import spectre_server.core.config

ACTIVE_MODE = "cosine_wave"
INVALID_STRING_FIELD = "foobarbaz"


@pytest.fixture
def custom_receiver() -> spectre_server.core.receivers.Base:
    return spectre_server.core.receivers.get_receiver(
        spectre_server.core.receivers.ReceiverName.CUSTOM
    )


@pytest.fixture()
def inactive_signal_generator() -> spectre_server.core.receivers.Base:
    return spectre_server.core.receivers.get_receiver(
        spectre_server.core.receivers.ReceiverName.SIGNAL_GENERATOR
    )


@pytest.fixture()
def signal_generator() -> spectre_server.core.receivers.Base:
    return spectre_server.core.receivers.get_receiver(
        spectre_server.core.receivers.ReceiverName.SIGNAL_GENERATOR, ACTIVE_MODE
    )


class TestReceiver:
    def test_no_active_mode(
        self, inactive_signal_generator: spectre_server.core.receivers.Base
    ) -> None:
        """Check that a receiver with no mode set, is inactive."""
        assert inactive_signal_generator.mode is None
        with pytest.raises(ValueError):
            inactive_signal_generator.active_mode

    def test_modes_consistent(
        self, signal_generator: spectre_server.core.receivers.Base
    ) -> None:
        """Check that the active mode is consistent with the mode."""
        assert signal_generator.active_mode == signal_generator.mode

    def test_active_mode(
        self, signal_generator: spectre_server.core.receivers.Base
    ) -> None:
        """Check that a receiver with mode set, is active."""
        assert signal_generator.active_mode == ACTIVE_MODE

    def test_set_mode(
        self, inactive_signal_generator: spectre_server.core.receivers.Base
    ) -> None:
        """Check that a mode can be set and unset."""
        receiver = inactive_signal_generator
        receiver.mode = ACTIVE_MODE
        assert receiver.mode == ACTIVE_MODE
        receiver.mode = None
        assert receiver.mode is None

    def test_set_invalid_mode(
        self, custom_receiver: spectre_server.core.receivers.Base
    ) -> None:
        """Check that you cannot set an invalid mode."""
        with pytest.raises(spectre_server.core.exceptions.ModeNotFoundError):
            # Use an arbitrary invalid mode name
            custom_receiver.mode = "foobar"

    def test_name(self, signal_generator: spectre_server.core.receivers.Base) -> None:
        """Check that the receiver name is set correctly."""
        assert (
            signal_generator.name
            == spectre_server.core.receivers.ReceiverName.SIGNAL_GENERATOR
        )

    def test_check_modes(
        self, signal_generator: spectre_server.core.receivers.Base
    ) -> None:
        """Check that the `modes` provides a correct list of available modes."""
        assert signal_generator.modes == ["cosine_wave", "constant_staircase"]

    def test_check_modes_empty(
        self, custom_receiver: spectre_server.core.receivers.Base
    ) -> None:
        """Check that an empty receiver has no operating modes."""
        assert len(custom_receiver.modes) == 0
        assert not custom_receiver.modes

    def test_config_io(
        self,
        signal_generator: spectre_server.core.receivers.Base,
        spectre_config_paths: spectre_server.core.config.Paths,
    ) -> None:
        """Check that we can read and write parameters from a config."""

        # Write a config to file, using defaults for most parameters except the sample rate.
        tag = "foobar"
        parameters = {"sample_rate": 256000}
        signal_generator.write_config(
            tag,
            parameters,
            configs_dir_path=spectre_config_paths.get_configs_dir_path(),
        )

        # Check a file got created at the expected path.
        expected_absolute_path = os.path.join(
            spectre_config_paths.get_configs_dir_path(), f"{tag}.json"
        )
        assert os.path.exists(expected_absolute_path)

        # Read it back and inspect the contents.
        config = signal_generator.read_config(
            tag, configs_dir_path=spectre_config_paths.get_configs_dir_path()
        )

        assert config.receiver_mode == "cosine_wave"
        assert config.receiver_name == "signal_generator"
        assert "sample_rate" in config.parameters
        assert config.parameters["sample_rate"] == 256000


class TestReceivers:
    @pytest.mark.parametrize(
        ("receiver_name"),
        [
            spectre_server.core.receivers.ReceiverName.RSP1A,
            spectre_server.core.receivers.ReceiverName.RSPDUO,
            spectre_server.core.receivers.ReceiverName.RSPDX,
            spectre_server.core.receivers.ReceiverName.USRP,
            spectre_server.core.receivers.ReceiverName.B200MINI,
            spectre_server.core.receivers.ReceiverName.HACKRF,
            spectre_server.core.receivers.ReceiverName.HACKRFONE,
            spectre_server.core.receivers.ReceiverName.RTLSDR,
        ],
    )
    def test_construction(self, receiver_name: str) -> None:
        """Check that each receiver can be constructed."""
        _ = spectre_server.core.receivers.get_receiver(receiver_name)

    @pytest.mark.parametrize(
        ("receiver_name"),
        [
            spectre_server.core.receivers.ReceiverName.RSP1A,
            spectre_server.core.receivers.ReceiverName.RSP1B,
            spectre_server.core.receivers.ReceiverName.RSPDUO,
            spectre_server.core.receivers.ReceiverName.RSPDX,
            spectre_server.core.receivers.ReceiverName.USRP,
            spectre_server.core.receivers.ReceiverName.B200MINI,
            spectre_server.core.receivers.ReceiverName.HACKRF,
            spectre_server.core.receivers.ReceiverName.HACKRFONE,
            spectre_server.core.receivers.ReceiverName.RTLSDR,
        ],
    )
    def test_write_default_config(
        self, spectre_config_paths: spectre_server.core.config.Paths, receiver_name: str
    ) -> None:
        """Check that the default configs satisfy each model."""
        receiver = spectre_server.core.receivers.get_receiver(receiver_name)
        for mode in receiver.modes:
            receiver.mode = mode

            # Dynamically create the tag based on the receiver and mode.
            mode = mode.replace("_", "-")
            tag = f"{receiver_name}-{mode}"

            receiver.write_config(
                tag, {}, configs_dir_path=spectre_config_paths.get_configs_dir_path()
            )
            assert os.path.exists(
                spectre_server.core.receivers.get_config_file_path(
                    tag, spectre_config_paths.get_configs_dir_path()
                )
            )

    @pytest.mark.parametrize(
        ("receiver_name", "field_name", "field_values"),
        [
            (
                spectre_server.core.receivers.ReceiverName.B200MINI,
                "wire_format",
                ["sc8", "sc12", "sc16"],
            ),
            (
                spectre_server.core.receivers.ReceiverName.B200MINI,
                "output_type",
                ["fc32", "sc16"],
            ),
            (
                spectre_server.core.receivers.ReceiverName.USRP,
                "wire_format",
                ["sc8", "sc12", "sc16"],
            ),
            (
                spectre_server.core.receivers.ReceiverName.USRP,
                "output_type",
                ["fc32", "sc16"],
            ),
        ],
    )
    def test_valid_single_field_all_modes(
        self, receiver_name: str, field_name: str, field_values: list[typing.Any]
    ) -> None:
        """Check a receiver accepts a valid single field, for all modes."""
        receiver = spectre_server.core.receivers.get_receiver(receiver_name)
        for mode in receiver.modes:
            receiver.mode = mode
            for field_value in field_values:
                receiver.model_validate({field_name: field_value})

    @pytest.mark.parametrize(
        ("receiver_name", "field_name", "field_values"),
        [
            (
                spectre_server.core.receivers.ReceiverName.B200MINI,
                "wire_format",
                [INVALID_STRING_FIELD],
            ),
            (
                spectre_server.core.receivers.ReceiverName.B200MINI,
                "output_type",
                [INVALID_STRING_FIELD],
            ),
            (
                spectre_server.core.receivers.ReceiverName.USRP,
                "wire_format",
                [INVALID_STRING_FIELD],
            ),
            (
                spectre_server.core.receivers.ReceiverName.USRP,
                "output_type",
                [INVALID_STRING_FIELD],
            ),
        ],
    )
    def test_invalid_single_field_all_modes(
        self, receiver_name: str, field_name: str, field_values: list[typing.Any]
    ) -> None:
        """Check a receiver rejects an invalid single field, for all modes."""
        receiver = spectre_server.core.receivers.get_receiver(receiver_name)
        for mode in receiver.modes:
            receiver.mode = mode
            for field_value in field_values:
                with pytest.raises(pydantic.ValidationError):
                    receiver.model_validate({field_name: field_value})
