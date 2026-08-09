# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os

import flask

from .config import SPECTRE_BIND_HOST, SPECTRE_BIND_PORT
from .routes.configs import configs_blueprint
from .routes.recordings import recordings_blueprint
from .routes.batches import batches_blueprint
from .routes.receivers import receivers_blueprint
from .routes.logs import logs_blueprint

from .core.logs import (
    configure_root_logger,
    get_server_log_file_path,
)
from .core.jobs import RecordingManager
from .core.config import TimeFormat, utc_now


def _configure_server_logger() -> None:
    start_time = utc_now().strftime(TimeFormat.DATETIME)
    file_path = get_server_log_file_path(start_time, os.getpid())
    configure_root_logger(file_path)


def make_app() -> flask.Flask:
    _configure_server_logger()
    app = flask.Flask(__name__)
    app.register_blueprint(configs_blueprint)
    app.register_blueprint(recordings_blueprint)
    app.register_blueprint(batches_blueprint)
    app.register_blueprint(logs_blueprint)
    app.register_blueprint(receivers_blueprint)

    return app


if __name__ == "__main__":
    RecordingManager().mark_in_flight_failed(utc_now())
    app = make_app()
    app.run(host=SPECTRE_BIND_HOST, port=SPECTRE_BIND_PORT, debug=True)
