# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


import flask
import os

from ..services import batches as services
from ._utils import validate_date, is_true
from ._format_responses import jsendify_response, serve_from_directory


batches_blueprint = flask.Blueprint(
    "batches", __name__, url_prefix="/spectre-data/batches"
)


def get_batch_file_endpoint(
    batch_file_path: str,
) -> str:
    """Return the URL endpoint corresponding to the input batch file path,"""
    return flask.url_for(
        "batches.get_batch_file",
        file_name=os.path.basename(batch_file_path),
    )


def get_batch_file_endpoints(batch_file_paths: list[str]) -> list[str]:
    """Return the URL endpoints corresponding to the input batch file paths."""
    return [get_batch_file_endpoint(batch_file) for batch_file in batch_file_paths]


@batches_blueprint.route("/<string:file_name>", methods=["GET"])
def get_batch_file(file_name: str) -> flask.Response:
    return serve_from_directory(services.get_batch_file(file_name))


@batches_blueprint.route("/<string:file_name>", methods=["DELETE"])
@jsendify_response
def delete_batch_file(file_name: str) -> str:
    dry_run = flask.request.args.get("dry_run", type=is_true, default=False)
    batch_file_path = services.delete_batch_file(file_name, dry_run=dry_run)
    return get_batch_file_endpoint(batch_file_path)


@batches_blueprint.route("/", methods=["GET"])
@jsendify_response
def get_batch_files() -> dict[str, list[str] | dict]:
    year = flask.request.args.get("year", type=int)
    month = flask.request.args.get("month", type=int)
    day = flask.request.args.get("day", type=int)
    tags = flask.request.args.getlist("tag")
    extensions = flask.request.args.getlist("extension")
    page = flask.request.args.get("page", type=int, default=1)
    per_page = flask.request.args.get("per_page", type=int, default=9)
    sort_order = flask.request.args.get("sort", type=str, default="desc").lower()

    validate_date(year, month, day)

    # Get all matching batch files
    all_batch_files = services.get_batch_files(
        tags, extensions, year=year, month=month, day=day, sort_order=sort_order
    )

    # Calculate pagination
    total_items = len(all_batch_files)
    total_pages = max(1, (total_items + per_page - 1) // per_page)

    # Ensure page is within valid range
    page = max(1, min(page, total_pages))

    # Calculate slice indices
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    # Get paginated batch files
    paginated_files = all_batch_files[start_idx:end_idx]

    return {
        "items": get_batch_file_endpoints(paginated_files),
        "pagination": {
            "current_page": page,
            "per_page": per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "sort": sort_order,
        },
    }


@batches_blueprint.route("/", methods=["DELETE"])
@jsendify_response
def delete_batch_files() -> list[str]:
    year = flask.request.args.get("year", type=int)
    month = flask.request.args.get("month", type=int)
    day = flask.request.args.get("day", type=int)
    extensions = flask.request.args.getlist("extension")
    tags = flask.request.args.getlist("tag")
    dry_run = flask.request.args.get("dry_run", type=is_true, default=False)
    validate_date(year, month, day)
    batch_files = services.delete_batch_files(
        tags, extensions, year=year, month=month, day=day, dry_run=dry_run
    )
    return get_batch_file_endpoints(batch_files)


@batches_blueprint.route(
    "/<string:file_name>/analytical-test-results",
    methods=["GET"],
)
@jsendify_response
def get_analytical_test_results(
    file_name: str,
) -> dict[str, bool | dict[float, bool]]:
    absolute_tolerance = flask.request.args.get(
        "absolute_tolerance", type=float, default=1e-5
    )
    return services.get_analytical_test_results(file_name, absolute_tolerance)


@batches_blueprint.route("/tags", methods=["GET"])
@jsendify_response
def get_tags() -> list[str]:
    year = flask.request.args.get("year", type=int)
    month = flask.request.args.get("month", type=int)
    day = flask.request.args.get("day", type=int)
    validate_date(year, month, day)
    return services.get_tags(year, month, day)


@batches_blueprint.route("/plots", methods=["PUT"])
@jsendify_response
def create_plot() -> str:
    json = flask.request.get_json()
    # Data from multiple batch files can be compared, by passing extra `tags` through the request body.
    tags = json.get("tags")
    figsize_x = json.get("figsize_x")
    figsize_y = json.get("figsize_y")
    obs_date = json.get("obs_date")
    start_time = json.get("start_time")
    end_time = json.get("end_time")
    lower_freq = json.get("lower_freq")
    upper_freq = json.get("upper_freq")
    log_norm = json.get("log_norm")
    dBb = json.get("dBb")
    vmin = json.get("vmin")
    vmax = json.get("vmax")

    # Handle the edge cases for figsize being specified.
    figsize_x_specified = figsize_x is not None
    figsize_y_specified = figsize_y is not None
    if figsize_x_specified ^ figsize_y_specified:
        raise ValueError(
            "Either both of `figsize_x` and `figsize_y` must be specified, or neither."
        )
    elif figsize_x_specified and figsize_y_specified:
        figsize = (figsize_x, figsize_y)
    else:
        # If nothing is specified, set an arbitrary default value.
        figsize = (15, 8)

    # Create the plot and return the name of the batch file containing the plot.
    batch_file = services.create_plot(
        tags,
        figsize,
        obs_date,
        start_time,
        end_time,
        lower_freq=lower_freq,
        upper_freq=upper_freq,
        log_norm=log_norm,
        dBb=dBb,
        vmin=vmin,
        vmax=vmax,
    )
    return get_batch_file_endpoint(batch_file)
