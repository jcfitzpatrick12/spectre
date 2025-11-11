# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing
import os
import logging

import spectre_core.receivers
import spectre_core.logs
import spectre_core.config
import spectre_core.batches


_LOGGER = logging.getLogger(__name__)


@spectre_core.logs.log_call
def get_config(
    file_name: str,
) -> str:
    """Get the file path of a config which exists in the file system.

    :param file_name: Look for a config with this file name.
    :return: The file path of the config if it exists in the file system, as an absolute path within the container's file system.
    """
    tag, _ = spectre_core.receivers.parse_config_file_name(file_name)
    return spectre_core.receivers.get_config_file_path(tag)


@spectre_core.logs.log_call
def get_config_raw(file_name: str) -> dict[str, typing.Any]:
    """Read a config file.

    :param file_name: The file name of the config.
    :return: The contents of the config, as a serialisable dictionary.
    """
    tag, _ = spectre_core.receivers.parse_config_file_name(file_name)
    config = spectre_core.receivers.read_config(tag)
    return config.content


@spectre_core.logs.log_call
def get_configs() -> list[str]:
    """Get the absolute file paths of all configs which exist in the file system."""
    config_dir = spectre_core.config.paths.get_configs_dir_path()
    return [entry.path for entry in os.scandir(config_dir) if entry.is_file()]


def _has_batches(tag: str) -> bool:
    batches = spectre_core.batches.Batches(
        tag, spectre_core.receivers.get_batch_cls(tag)
    )
    return len(batches) > 0


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
                f"Files exist under the tag {tag}. Any updates to the corresponding config may lead to undefined behaviour. "
                f"For any changes, it is recommended to create a new config, or to first delete existing batch files "
                f"if they are no longer required. This warning can be overridden."
            )
            _LOGGER.error(error_message)
            raise FileExistsError(error_message)


def _parse_string_parameter(string_parameter: str) -> list[str]:
    """Parse string of the form `a=b` into a list of the form `[a, b]`.

    :param string_parameter: A string representation of a capture config parameter.
    :raises ValueError: If the input parameter is not of the form `a=b`.
    :return: The parsed components of the input string parameter, using the `=` character as a separator.
    The return list will always contain two elements.
    """
    if not string_parameter or "=" not in string_parameter:
        raise ValueError(f"Invalid format: '{string_parameter}'. Expected 'KEY=VALUE'.")
    if string_parameter.startswith("=") or string_parameter.endswith("="):
        raise ValueError(f"Invalid format: '{string_parameter}'. Expected 'KEY=VALUE'.")
    # remove leading and trailing whitespace.
    string_parameter = string_parameter.strip()
    return string_parameter.split("=", 1)


def _parse_string_parameters(string_parameters: list[str]) -> dict[str, str]:
    """Parses a list of strings of the form `a=b` into a dictionary mapping each `a` to each `b`.

    :param string_parameters: A list of strings, where each element is of the form `a=b`.
    :return: A dictionary mapping each `a` to each `b`, after parsing each element.
    """
    d = {}
    for string_parameter in string_parameters:
        k, v = _parse_string_parameter(string_parameter)
        d[k] = v
    return d


@spectre_core.logs.log_call
def create_config(
    file_name: str,
    receiver_name: str,
    receiver_mode: str,
    string_parameters: typing.Optional[list[str]] = None,
    force: bool = False,
    validate: bool = True,
) -> str:
    """Create a config.

    :param file_name: The file name of the config.
    :param receiver_name: The name of the receiver.
    :param receiver_mode: The operating mode of the receiver.
    :param string_parameters: The parameters to store as key-value pairs. Specifically,
    A list of strings of the form `a=b`, where each element is interpreted as a parameter
    with name `a` and value `b`, defaults to None. A None value will be interpreted as an empty list.
    :param force: If True, force the update even if batches exist with the input tag. Defaults to False
    :param validate: If True, validate config parameters. Defaults to True.
    :return: The file path of the newly created config, as an absolute path in the container's file system.
    :raises FileExistsError: If the config already exists, files exist under the config tag and force is False.
    """
    if string_parameters is None:
        string_parameters = []

    receiver = spectre_core.receivers.get_receiver(receiver_name, mode=receiver_mode)

    tag, _ = spectre_core.receivers.parse_config_file_name(file_name)

    if os.path.exists(spectre_core.receivers.get_config_file_path(tag)):
        _caution_update(tag, force)

    receiver.write_config(
        tag,
        _parse_string_parameters(string_parameters),
        skip_validation=not validate or force,
    )

    return spectre_core.receivers.get_config_file_path(tag)


@spectre_core.logs.log_call
def update_config(
    file_name: str,
    string_parameters: list[str],
    force: bool = False,
    validate: bool = True,
) -> str:
    """Update a config.

    Any parameters passed in via `string_parameters` will overwrite existing parameters.

    :param file_name: The file name of the config.
    :param string_parameters: The parameters to update as key-value pairs. Specifically,
    A list of strings of the form `a=b`, where each element is interpreted as a parameter
    with name `a` and value `b`.
    :param force: If True, force the update even if batches exist with the input tag. Defaults to False
    :param validate: If True, apply the capture template and validate config parameters. Defaults to True.
    :return: The file path of the successfully updated config, as an absolute path in the container's file system.
    :raises FileNotFoundError: If the config does not exist.
    """
    tag, _ = spectre_core.receivers.parse_config_file_name(file_name)
    if not os.path.exists(spectre_core.receivers.get_config_file_path(tag)):
        raise FileNotFoundError(f"{file_name} does not exist.")

    _caution_update(tag, force)
    config = spectre_core.receivers.read_config(tag)
    parameters = {**config.parameters, **_parse_string_parameters(string_parameters)}

    receiver = spectre_core.receivers.get_receiver(
        config.receiver_name, mode=config.receiver_mode
    )
    receiver.write_config(
        tag,
        parameters,
        skip_validation=not validate or force,
    )
    return spectre_core.receivers.get_config_file_path(tag)


@spectre_core.logs.log_call
def delete_config(file_name: str, dry_run: bool = False) -> str:
    """Delete a config.

    :param file_name: The file name of the config.
    :param dry_run: If True, display which files would be deleted without actually deleting them. Defaults to False
    :return: The file path of the deleted config, as an absolute path within the container's file system.
    """
    tag, _ = spectre_core.receivers.parse_config_file_name(file_name)
    if _has_batches(tag):
        error_message = (
            f"Files exist under the tag {tag}, and deleting the corresponding config "
            f"would lead to undefined behaviour."
        )
        _LOGGER.error(error_message)
        raise FileExistsError(error_message)

    config_file_path = spectre_core.receivers.get_config_file_path(tag)
    if not dry_run:
        if not os.path.exists(config_file_path):
            raise FileNotFoundError(f"{file_name} does not exist.")
        os.remove(config_file_path)
    return config_file_path
