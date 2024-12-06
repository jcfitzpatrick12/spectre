# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
from spectre_core.spectrograms.analytical import TestResults

from spectre_cli.commands import safe_request
from spectre_cli.commands import (
    TAG_HELP,
    ABSOLUTE_TOLERANCE_HELP,
    PER_SPECTRUM_HELP
)

test_app = typer.Typer()


def _pretty_print_test_results(file_name: str, 
                               test_results: TestResults, 
                               per_spectrum: bool
) -> None:
    """Print test results with appropriate formatting and colours."""
    
    def print_colored(label: str, value: bool) -> None:
        typer.secho(f"{label}: {'PASS' if value else 'FAIL'}", fg="green" if value else "red")

    def print_spectrum_results():
        typer.secho("\nPer spectrum results:" if per_spectrum else "\nSummary:")
        if per_spectrum:
            for time, is_valid in test_results.spectrum_validated.items():
                typer.secho(f"  Time {float(time):.3f} [s]: {'PASS' if is_valid else 'FAIL'}", fg="green" if is_valid else "red")
        else:
            typer.secho(f"  Validated spectrums: {test_results.num_validated_spectrums}", fg="green")
            typer.secho(f"  Invalid spectrums: {test_results.num_invalid_spectrums}", fg="red")

    typer.secho(f"\nTest results for {file_name}:", bold=True)
    print_colored("Times validated", test_results.times_validated)
    print_colored("Frequencies validated", test_results.frequencies_validated)
    print_spectrum_results()


@test_app.command()
def analytical(
    tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
    absolute_tolerance: float = typer.Option(1e-3, "--atol", "--absolute-tolerance", help=ABSOLUTE_TOLERANCE_HELP),
    per_spectrum: bool = typer.Option(False, "--per-spectrum", help=PER_SPECTRUM_HELP),
) -> None:
    
    json = {
        "tag": tag,
        "absolute_tolerance": absolute_tolerance,
    }
    jsend_dict = safe_request("test/analytical",
                              "GET",
                              json = json)
    results_per_chunk = jsend_dict["data"]

    for file_name, test_results in results_per_chunk.items():
        test_results = TestResults(test_results["times_validated"],
                                   test_results["frequencies_validated"],
                                   test_results["spectrum_validated"])

        _pretty_print_test_results(file_name,
                                   test_results,
                                   per_spectrum)
        
    raise typer.Exit()