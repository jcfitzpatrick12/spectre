# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""Pairwise structural-compatibility checks between Spectre-emitted e-CALLISTO FITS
files and a pair of ground-truth station fixtures.

We do NOT expect bit-for-bit equality with the reference files (those are produced by
the legacy ``e-Callisto_Py_RX-888_MK_II`` pipeline, with station-specific values and
post-hoc tags like ``FOCUSCOD``). Instead, we assert:

* Spectre's primary HDU has exactly the keys / value formats that real e-CALLISTO viewers
  read (DATE-OBS slash-separated, CONTENT prefixed with the slash date, ``BITPIX=8``,
  hemisphere codes, ...).
* The reference fixtures contain those same keys, sanity-checking the schema.
* ``FOCUSCOD`` is absent from Spectre output (it is appended by the CLI rename step, not
  the backend).
"""

import gzip
import os
import re
import shutil

import pytest
import astropy.io.fits

import spectre_server.core.batches
import spectre_server.core.config
import spectre_server.core.receivers


_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
_FIXTURE_NAMES = (
    "GLASGOW_20260614_034500_01.fit.gz",
    "SPAIN-SIGUENZA_20260617_061500_02.fit.gz",
)

_DATE_SLASH_RE = re.compile(r"^\d{4}/\d{2}/\d{2}$")
_TIME_RE = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d+$")
_CONTENT_RE = re.compile(
    r"^\d{4}/\d{2}/\d{2}\s+Radio flux density, e-CALLISTO \(.+\)$"
)


# ---------- Reference fixture sanity ---------------------------------------------------

@pytest.fixture(params=_FIXTURE_NAMES)
def reference_primary_header(request, tmp_path) -> astropy.io.fits.Header:
    """Decompress one ground-truth fixture and yield its primary header."""
    fixture_src = os.path.join(_DATA_DIR, request.param)
    fixture_dst = tmp_path / request.param[:-3]
    with gzip.open(fixture_src, "rb") as f_in, open(fixture_dst, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    with astropy.io.fits.open(fixture_dst) as hdul:
        yield hdul[0].header.copy()


class TestReferenceFixtureSchema:
    """Sanity-check that the ground-truth fixtures contain the schema we replicate."""

    REQUIRED_KEYS = (
        "SIMPLE", "BITPIX", "NAXIS", "NAXIS1", "NAXIS2", "EXTEND",
        "DATE", "CONTENT", "ORIGIN", "TELESCOP", "INSTRUME", "OBJECT",
        "DATE-OBS", "TIME-OBS", "DATE-END", "TIME-END",
        "BZERO", "BSCALE", "BUNIT",
        "DATAMIN", "DATAMAX",
        "CRVAL1", "CRPIX1", "CTYPE1", "CDELT1",
        "CRVAL2", "CRPIX2", "CTYPE2", "CDELT2",
        "OBS_LAT", "OBS_LAC", "OBS_LON", "OBS_LOC", "OBS_ALT",
        "FRQFILE", "PWM_VAL",
    )

    def test_required_keys_present(
        self, reference_primary_header: astropy.io.fits.Header
    ) -> None:
        for key in self.REQUIRED_KEYS:
            assert key in reference_primary_header, key

    def test_bitpix_is_eight(
        self, reference_primary_header: astropy.io.fits.Header
    ) -> None:
        assert reference_primary_header["BITPIX"] == 8

    def test_date_obs_uses_slashes(
        self, reference_primary_header: astropy.io.fits.Header
    ) -> None:
        assert _DATE_SLASH_RE.match(reference_primary_header["DATE-OBS"])

    def test_content_format(
        self, reference_primary_header: astropy.io.fits.Header
    ) -> None:
        assert _CONTENT_RE.match(reference_primary_header["CONTENT"])


# ---------- Spectre output produced via the analytical signal generator ----------------

_TAG = "ecallisto-compat"
_PARAMETERS = {
    "batch_size": 1,
    "amplitude": 3.0,
    "frequency": 16000.0,
    "window_hop": 256,
    "window_size": 256,
    "window_type": "boxcar",
    "sample_rate": 128000,
    "time_resolution": 0,
    "frequency_resolution": 0,
    "instrument": "TEST",
    "object": "Sun",
    "origin": "TEST",
    "telescope": "TEST",
    "obs_lat": 50.0,
    "obs_lon": 0.0,
    "obs_alt": 0.0,
    "obs_lac": "N",
    "obs_loc": "W",
}


@pytest.fixture
def spectre_primary_header(
    spectre_config_paths: spectre_server.core.config.Paths,
) -> astropy.io.fits.Header:
    receiver = spectre_server.core.receivers.get_receiver("signal_generator")
    receiver.mode = "ecallisto"
    receiver.write_config(
        _TAG, _PARAMETERS, configs_dir_path=spectre_config_paths.get_configs_dir_path()
    )
    config = receiver.read_config(
        _TAG, configs_dir_path=spectre_config_paths.get_configs_dir_path()
    )
    spectre_server.core.receivers.record_spectrograms(
        [config],
        5,
        spectre_data_dir_path=spectre_config_paths.get_spectre_data_dir_path(),
    )

    for batch in spectre_server.core.batches.Batches(
        _TAG,
        receiver.batch_cls,
        spectre_config_paths.get_batches_dir_path(),
    ):
        if batch.spectrogram_file.exists:
            with astropy.io.fits.open(batch.spectrogram_file.file_path) as hdul:
                return hdul[0].header.copy()

    pytest.fail("Spectre produced no FITS spectrogram in ecallisto mode.")


class TestSpectreECallistoFits:
    def test_bitpix_is_eight(
        self, spectre_primary_header: astropy.io.fits.Header
    ) -> None:
        assert spectre_primary_header["BITPIX"] == 8

    def test_date_obs_uses_slashes(
        self, spectre_primary_header: astropy.io.fits.Header
    ) -> None:
        assert _DATE_SLASH_RE.match(spectre_primary_header["DATE-OBS"])

    def test_time_obs_has_fractional_seconds(
        self, spectre_primary_header: astropy.io.fits.Header
    ) -> None:
        assert _TIME_RE.match(spectre_primary_header["TIME-OBS"])

    def test_content_format(
        self, spectre_primary_header: astropy.io.fits.Header
    ) -> None:
        assert _CONTENT_RE.match(spectre_primary_header["CONTENT"])
        assert "TEST" in spectre_primary_header["CONTENT"]

    def test_hemisphere_codes(
        self, spectre_primary_header: astropy.io.fits.Header
    ) -> None:
        assert spectre_primary_header["OBS_LAC"] == "N"
        assert spectre_primary_header["OBS_LOC"] == "W"

    def test_bunit_is_digits(
        self, spectre_primary_header: astropy.io.fits.Header
    ) -> None:
        assert spectre_primary_header["BUNIT"] == "digits"

    def test_focuscod_absent(
        self, spectre_primary_header: astropy.io.fits.Header
    ) -> None:
        """FOCUSCOD is appended by the CLI rename step, not the backend."""
        assert "FOCUSCOD" not in spectre_primary_header

    def test_neutral_callisto_headers(
        self, spectre_primary_header: astropy.io.fits.Header
    ) -> None:
        assert spectre_primary_header["FRQFILE"] == ""
        assert spectre_primary_header["PWM_VAL"] == 0

    def test_observatory_coordinates_numeric(
        self, spectre_primary_header: astropy.io.fits.Header
    ) -> None:
        """Ground truth emits OBS_LAT/LON/ALT as numbers, not quoted strings."""
        for key in ("OBS_LAT", "OBS_LON", "OBS_ALT"):
            assert isinstance(spectre_primary_header[key], (int, float)), key
