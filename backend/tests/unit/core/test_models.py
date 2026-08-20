# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import spectre_server.core.models


class TestValidators:
    @pytest.mark.parametrize(
        ("floor_start_times", "batch_size", "time_range"),
        [
            # Time range cannot be less than the batch size.
            (True, 3, 2),
            # Time range cannot be zero.
            (True, 3, 0),
        ],
    )
    def test_validate_floor_start_times_raises(
        self, floor_start_times: bool, batch_size: float, time_range: float
    ) -> None:
        """Check the validator correctly raises when floor_start_times doesn't make sense."""
        with pytest.raises(ValueError, match="To floor start times"):
            spectre_server.core.models.validate_floor_start_times(
                floor_start_times, batch_size, time_range
            )

    @pytest.mark.parametrize(
        ("floor_start_times", "batch_size", "time_range"),
        [
            # If we're not flooring the start times, any combination is ok.
            (False, 3, 2),
            # Time range can be more than batch size.
            (True, 3, 4),
            # Standard combination for an e-Callisto node.
            (True, 1, 900),
        ],
    )
    def test_validate_floor_start_times_ok(
        self, floor_start_times: bool, batch_size: float, time_range: float
    ) -> None:
        """Check the validator passes when flooring the start times does make sense."""
        spectre_server.core.models.validate_floor_start_times(
            floor_start_times, batch_size, time_range
        )
