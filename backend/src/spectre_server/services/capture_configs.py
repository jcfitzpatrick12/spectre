# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger

_LOGGER = getLogger(__name__)

from typing import Optional, Any
from os import scandir
from os.path import splitext

from spectre_core.config import get_configs_dir_path
from spectre_core.batches import Batches, get_batch_cls_from_tag
from spectre_core.receivers import get_receiver, ReceiverName
from spectre_core.logs import log_call
from spectre_core.capture_configs import (
    CaptureConfig,
    parse_string_parameters,
    make_parameters,
)


def _get_capture_config(file_name: str) -> CaptureConfig:
    """Get a capture config instance from its file name."""
    tag, _ = splitext(file_name)
    return CaptureConfig(tag)


@log_call
def get_capture_config(
    file_name: str,
) -> str:
    """Get the file path of a capture config which exists in the file system.

    :param file_name: Look for a capture config with this file name.
    :return: The file path of the capture config if it exists in the file system, as an absolute path within the container's file system.
    """
    capture_config = _get_capture_config(file_name)
    return capture_config.file_path


@log_call
def read_capture_config(file_name: str) -> dict[str, Any]:
    """Read the contents of a capture config.

    :param file_name: The file name of the capture config.
    :return: The contents of the capture config, as a serialisable dictionary.
    """
    capture_config = _get_capture_config(file_name)
    return capture_config.read()


@log_call
def get_capture_configs() -> list[str]:
    """Get the absolute file paths of all capture configs which exist in the file system."""
    config_dir = get_configs_dir_path()
    return [entry.path for entry in scandir(config_dir)]


def _has_batches(tag: str) -> bool:
    """Returns True if any batch files exist under the input tag."""
    batch_cls = get_batch_cls_from_tag(tag)
    batches = Batches(tag, batch_cls)
    return len(batches.batch_list) > 0


def _caution_update(tag: str, force: bool) -> None:
    """Caution users if batch files exist with the input tag.

    :param tag: The batch file tag.
    :param force: If True, warn the user, suppress the explicit error and continue with the update.
    :raises FileExistsError: Raised if `force` is False, and batches exist with the input tag.
    """
    if _has_batches(tag):
        if force:
            _LOGGER.warning(f"Batches exist under the tag {tag}, forcing update")
            return
        else:
            error_message = (
                f"Batches exist under the tag {tag}. Any updates to the capture config may lead to undefined behaviour. "
                f"For any changes, it is recommended to create a new capture config, or to first delete existing batch files "
                f"if they are no longer required. This warning can be overridden."
            )
            _LOGGER.error(error_message)
            raise FileExistsError(error_message)


@log_call
def create_capture_config(
    file_name: str,
    receiver_name: str,
    receiver_mode: str,
    string_parameters: Optional[list[str]] = None,
    force: bool = False,
    validate: bool = True,
) -> str:
    """Create a capture config.

    :param file_name: The file name of the capture config.
    :param receiver_name: The name of the receiver.
    :param receiver_mode: The operating mode of the receiver.
    :param string_parameters: The parameters to store as key-value pairs. Specifically,
    A list of strings of the form `a=b`, where each element is interpreted as a parameter
    with name `a` and value `b`, defaults to None. A None value will be interpreted as an empty list.
    :param force: If True, force the update even if batches exist with the input tag. Defaults to False
    :param validate: If True, validate capture config parameters. Defaults to True.
    :return: The file path of the newly created capture config, as an absolute path in the container's file system.
    """
    if string_parameters is None:
        string_parameters = []

    name = ReceiverName(receiver_name)
    receiver = get_receiver(name, mode=receiver_mode)

    parameters = make_parameters(parse_string_parameters(string_parameters))

    tag, extension = splitext(file_name)

    if extension != ".json":
        raise ValueError("Capture config file names must be of the form <tag>.json")

    capture_config = _get_capture_config(file_name)
    # If the capture config already exists, check if batches exist under the tag.
    if capture_config.exists:
        _caution_update(tag, force)

    receiver.save_parameters(tag, parameters, validate=validate, force=True)

    # create an instance of the newly created capture config
    capture_config = _get_capture_config(file_name)

    _LOGGER.info(
        f"The capture-config for tag '{tag}' has been created: {capture_config.file_name}"
    )

    return capture_config.file_path


@log_call
def update_capture_config(
    file_name: str,
    string_parameters: list[str],
    force: bool = False,
    validate: bool = True,
) -> str:
    """Update a capture config.

    Any parameters passed in via `string_parameters` will overwrite existing parameters.

    :param file_name: The file name of the capture config.
    :param string_parameters: The parameters to update as key-value pairs. Specifically,
    A list of strings of the form `a=b`, where each element is interpreted as a parameter
    with name `a` and value `b`.
    :param force: If True, force the update even if batches exist with the input tag. Defaults to False
    :param validate: If True, apply the capture template and validate capture config parameters. Defaults to True.
    :return: The file path of the successfully updated capture config, as an absolute path in the container's file system.
    """
    tag, _ = splitext(file_name)
    _caution_update(tag, force)

    new_parameters = make_parameters(parse_string_parameters(string_parameters))

    capture_config = _get_capture_config(file_name)

    for existing_parameter in capture_config.parameters:
        if existing_parameter.name in new_parameters.name_list:
            continue
        new_parameters.add_parameter(existing_parameter.name, existing_parameter.value)

    name = ReceiverName(capture_config.receiver_name)
    receiver = get_receiver(name, capture_config.receiver_mode)
    receiver.save_parameters(tag, new_parameters, validate=validate, force=True)

    _LOGGER.info(
        f"Capture config for tag: {tag} has been successfully updated: {capture_config.file_name}"
    )

    return capture_config.file_path


@log_call
def delete_capture_config(file_name: str, dry_run: bool = False) -> str:
    """Delete a capture config.

    :param file_name: The file name of the capture config.
    :param dry_run: If True, display which files would be deleted without actually deleting them. Defaults to False
    :return: The file path of the successfully deleted capture config, as an absolute path within the container's file system.
    """
    tag, _ = splitext(file_name)
    if _has_batches(tag):
        error_message = (
            f"Batches exist under the tag {tag}, and deleting the corresponding capture config "
            f"would lead to undefined behaviour."
        )
        _LOGGER.error(error_message)
        raise FileExistsError(error_message)

    capture_config = _get_capture_config(file_name)
    if not dry_run:
        capture_config.delete()
    _LOGGER.info(f"File deleted: {capture_config.file_name}")
    return capture_config.file_path
