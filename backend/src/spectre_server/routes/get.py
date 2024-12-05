# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import Blueprint, request

from spectre_server.services import get
from spectre_server.routes import jsendify_response


get_blueprint = Blueprint("get", __name__)


@get_blueprint.route("/callisto-instrument-codes", methods=["GET"])
@jsendify_response
def callisto_instrument_codes():
    return get.callisto_instrument_codes()


@get_blueprint.route("/log-file-names", methods=["GET"])
@jsendify_response
def log_file_names():
    payload = request.get_json()
    process_type = payload.get("process_type")
    year = payload.get("year")
    month = payload.get("month")
    day = payload.get("day")
    return get.log_file_names(process_type,
                              year,
                              month,
                              day)


@get_blueprint.route("/chunk-files", methods=["GET"])
@jsendify_response
def chunk_files():
    payload = request.get_json()
    tag = payload.get("tag")
    year = payload.get("year")
    month = payload.get("month")
    day = payload.get("day")
    extensions = payload.get("extensions")
    return get.chunk_file_names(tag,
                                year,
                                month,
                                day,
                                extensions)


@get_blueprint.route("/receivers", methods=["GET"])
@jsendify_response
def receivers():
    return get.receiver_names()


@get_blueprint.route("/modes", methods=["GET"])
@jsendify_response
def modes():
    payload = request.get_json()
    receiver_name = payload.get("receiver_name")
    return get.receiver_modes(receiver_name)


@get_blueprint.route("/specifications", methods=["GET"])
@jsendify_response
def specifications():
    payload = request.get_json()
    receiver_name = payload.get("receiver_name")
    return get.receiver_specifications(receiver_name)


@get_blueprint.route("/fits-configs", methods=["GET"])
@jsendify_response
def fits_configs():
    return get.fits_config_file_names()


@get_blueprint.route("/capture-configs", methods=["GET"])
@jsendify_response
def capture_configs():
    return get.capture_config_file_names()


@get_blueprint.route("/tags", methods=["GET"])
@jsendify_response
def tags():
    payload = request.get_json()
    year = payload.get("year")
    month = payload.get("month")
    day = payload.get("day")
    return get.tags(year,
                    month,
                    day)


@get_blueprint.route("/log", methods=["GET"])
@jsendify_response
def log():
    payload = request.get_json()
    pid = payload.get("pid")
    file_name = payload.get("file_name")
    return get.log_file_contents(pid,
                                 file_name)

@get_blueprint.route("/fits-config-type-template", methods=["GET"])
@jsendify_response
def fits_config_type_template():
    return get.fits_config_type_template()


@get_blueprint.route("/capture-config-type-template", methods=["GET"])
@jsendify_response
def capture_config_type_template():
    payload = request.get_json()
    receiver_name = payload.get("receiver_name")
    mode = payload.get("mode")
    return get.capture_config_type_template(receiver_name,
                                            mode)

@get_blueprint.route("/fits-config", methods=["GET"])
@jsendify_response
def fits_config():
    payload = request.get_json()
    tag = payload.get("tag")
    return get.fits_config_contents(tag)


@get_blueprint.route("/capture-config", methods=["GET"])
@jsendify_response
def capture_config():
    payload = request.get_json()
    tag = payload.get("tag")
    return get.capture_config_contents(tag)