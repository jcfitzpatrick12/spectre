# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for the e-CALLISTO-specific batch, validators and merged models."""

import pytest
import pydantic

import spectre_server.core.batches
import spectre_server.core.receivers
from spectre_server.core.models._validators import validate_focus_code


class TestECallistoBatch:
    def test_declared_extensions(self) -> None:
        """Only fits + fc32 are declared (no bin file)."""
        extension = spectre_server.core.batches.ECallistoBatchExtension
        assert extension.FITS == "fits"
        assert extension.FC32 == "fc32"
        assert not hasattr(extension, "BIN")


class TestValidateFocusCode:
    @pytest.mark.parametrize("value", ["00", "01", "02", "10", "42", "99"])
    def test_accepts_two_digit_strings(self, value: str) -> None:
        validate_focus_code(value)

    @pytest.mark.parametrize(
        "value",
        ["", "0", "1", "100", "AB", " 1", "1 ", "-1", "+1", "1.0", "abc"],
    )
    def test_rejects_malformed(self, value: str) -> None:
        with pytest.raises(ValueError):
            validate_focus_code(value)

    @pytest.mark.parametrize("value", [0, 1, 12, None, 1.5, [], {}])
    def test_rejects_non_string(self, value) -> None:
        with pytest.raises(ValueError):
            validate_focus_code(value)


_VALID_ECALLISTO_FIELDS = {
    "instrument": "TEST",
    "object": "Sun",
    "origin": "TEST",
    "telescope": "TEST",
    "obs_lac": "N",
    "obs_loc": "W",
    "obs_lat": 50.0,
    "obs_lon": 0.0,
    "obs_alt": 0.0,
}


class TestRX888MK2ECallistoValidator:
    @pytest.fixture
    def receiver(self) -> spectre_server.core.receivers.Base:
        recv = spectre_server.core.receivers.get_receiver("rx888mk2")
        recv.mode = "ecallisto"
        return recv

    def test_defaults_validate(
        self, receiver: spectre_server.core.receivers.Base
    ) -> None:
        receiver.model_validate({})

    @pytest.mark.parametrize(
        "overrides",
        [
            {"obs_lac": "E"},
            {"obs_loc": "N"},
            {"obs_lat": -10.0},
            {"obs_lat": 100.0},
            {"obs_lon": -1.0},
            {"obs_lon": 200.0},
            {"instrument": ""},
            {"object": ""},
            {"origin": ""},
            {"telescope": ""},
        ],
    )
    def test_rejects_invalid_overrides(
        self,
        receiver: spectre_server.core.receivers.Base,
        overrides: dict,
    ) -> None:
        with pytest.raises(pydantic.ValidationError):
            receiver.model_validate({**_VALID_ECALLISTO_FIELDS, **overrides})


class TestSignalGeneratorECallistoValidator:
    @pytest.fixture
    def receiver(self) -> spectre_server.core.receivers.Base:
        recv = spectre_server.core.receivers.get_receiver("signal_generator")
        recv.mode = "ecallisto"
        return recv

    def test_defaults_validate(
        self, receiver: spectre_server.core.receivers.Base
    ) -> None:
        receiver.model_validate({})

    @pytest.mark.parametrize(
        "overrides",
        [
            {"obs_lac": "E"},
            {"obs_loc": "N"},
            {"instrument": ""},
            {"window_type": "hann"},
        ],
    )
    def test_rejects_invalid_overrides(
        self,
        receiver: spectre_server.core.receivers.Base,
        overrides: dict,
    ) -> None:
        with pytest.raises(pydantic.ValidationError):
            receiver.model_validate({**_VALID_ECALLISTO_FIELDS, **overrides})
