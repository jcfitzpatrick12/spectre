# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import spectre_core.logs

spectre_core.logs.configure_root_logger(spectre_core.logs.ProcessType.USER)

import flask

from .config import SPECTRE_BIND_HOST, SPECTRE_BIND_PORT
from .routes.configs import configs_blueprint
from .routes.recordings import recordings_blueprint
from .routes.batches import batches_blueprint
from .routes.receivers import receivers_blueprint
from .routes.logs import logs_blueprint


def make_app() -> flask.Flask:
    app = flask.Flask(__name__)
    app.register_blueprint(configs_blueprint)
    app.register_blueprint(recordings_blueprint)
    app.register_blueprint(batches_blueprint)
    app.register_blueprint(logs_blueprint)
    app.register_blueprint(receivers_blueprint)

    return app


if __name__ == "__main__":
    app = make_app()
    app.run(host=SPECTRE_BIND_HOST, port=SPECTRE_BIND_PORT, debug=True)
