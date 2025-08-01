# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typer import Typer, Option, Exit, secho

from ._utils import safe_request

test_typer = Typer(help="Run tests.")


def _pretty_print_test_results(
    file_name: str,
    times_validated: bool,
    frequencies_validated: bool,
    spectrum_validated: dict[float, bool],
    per_spectrum: bool,
) -> None:
    """Print test results with appropriate formatting and colours."""

    def print_colored(label: str, value: bool) -> None:
        secho(f"{label}: {'PASS' if value else 'FAIL'}", fg="green" if value else "red")

    def print_spectrum_results():
        secho("\nPer spectrum results:" if per_spectrum else "\nSummary:")
        if per_spectrum:
            for time, is_valid in spectrum_validated.items():
                secho(
                    f"  Time {float(time):.3f} [s]: {'PASS' if is_valid else 'FAIL'}",
                    fg="green" if is_valid else "red",
                )
        else:
            num_validated_spectrums = sum(
                is_validated for is_validated in spectrum_validated.values()
            )
            secho(f"  Validated spectrums: {num_validated_spectrums}", fg="green")

            num_invalid_spectrums = len(spectrum_validated) - num_validated_spectrums
            secho(f"  Invalid spectrums: {num_invalid_spectrums}", fg="red")

    secho(f"\nTest results for {file_name}:", bold=True)
    print_colored("Times validated", times_validated)
    print_colored("Frequencies validated", frequencies_validated)
    print_spectrum_results()


@test_typer.command(
    help=(
        "Validate spectrograms produced by the signal generator against "
        "analytically derived solutions."
    )
)
def analytical(
    file_name: str = Option(..., "-f", help="The name of the spectrogram file."),
    absolute_tolerance: float = Option(
        1e-3,
        "--atol",
        "--absolute-tolerance",
        help="The absolute tolerance to which we consider agreement with the "
        "analytical solution for each spectral component. See the 'atol' "
        "keyword argument for `np.isclose`.",
    ),
    per_spectrum: bool = Option(
        False, "--per-spectrum", help="Show validated status per spectrum."
    ),
) -> None:

    params = {
        "absolute_tolerance": absolute_tolerance,
    }
    jsend_dict = safe_request(
        f"spectre-data/batches/{file_name}/analytical-test-results",
        "GET",
        params=params,
    )
    test_results = jsend_dict["data"]
    _pretty_print_test_results(
        file_name,
        test_results["times_validated"],
        test_results["frequencies_validated"],
        test_results["spectrum_validated"],
        per_spectrum,
    )

    raise Exit()
