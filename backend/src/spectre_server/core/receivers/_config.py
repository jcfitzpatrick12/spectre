# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses
import os
import typing
import json

import spectre_server.core.io
import spectre_server.core.config


def _validate_tag(tag: str) -> None:
    if "_" in tag:
        raise ValueError("An underscore is not allowed in a config tag.")


def _validate_keys(content: dict[str, str]) -> None:
    required_keys = {
        _CaptureConfigKey.RECEIVER_NAME,
        _CaptureConfigKey.RECEIVER_MODE,
        _CaptureConfigKey.PARAMETERS,
    }
    missing_keys = required_keys - content.keys()
    if missing_keys:
        raise ValueError(f"Missing required keys in config content: {missing_keys}")


@dataclasses.dataclass(frozen=True)
class _CaptureConfigKey:
    """Defined JSON keys for configs.

    :ivar RECEIVER_NAME: The name of the receiver.
    :ivar RECEIVER_MODE: The operating mode for the receiver.
    :ivar PARAMETERS: User-configured parameters.
    """

    RECEIVER_NAME = "receiver_name"
    RECEIVER_MODE = "receiver_mode"
    PARAMETERS = "parameters"


class Config:
    def __init__(self, tag: str, content: dict[str, typing.Any]) -> None:
        """A container for config data.

        :param tag: The tag of the config.
        :param content: The config data.
        """
        _validate_keys(content)
        _validate_tag(tag)
        self._tag = tag
        self._content = content

    @property
    def tag(self) -> str:
        """A config tag."""
        return self._tag

    @property
    def receiver_name(self) -> str:
        """The name of the receiver."""
        return self._content[_CaptureConfigKey.RECEIVER_NAME]

    @property
    def receiver_mode(self) -> str:
        """The operating mode for the receiver."""
        return self._content[_CaptureConfigKey.RECEIVER_MODE]

    @property
    def parameters(self) -> dict[str, typing.Any]:
        """Configurable parameters."""
        return self._content[_CaptureConfigKey.PARAMETERS]

    @property
    def content(self) -> dict[str, typing.Any]:
        return self._content


def get_config_file_path(
    tag: str, configs_dir_path: typing.Optional[str] = None
) -> str:
    """Build a config file path.

    :param tag: The config tag.
    :param configs_dir_path: Optionally override the directory containing the configs, defaults to None
    """
    configs_dir_path = (
        configs_dir_path or spectre_server.core.config.paths.get_configs_dir_path()
    )
    return os.path.join(configs_dir_path, f"{tag}.json")


def read_config(tag: str, configs_dir_path: typing.Optional[str] = None) -> Config:
    """Read any config data from the filesystem for any receiver, without validation.

    :param tag: The config tag.
    :param configs_dir_path: Optionally override the directory containing the configs, defaults to None
    :return: A container storing the config data.
    """
    config_file_path = get_config_file_path(tag, configs_dir_path)
    if not os.path.exists(config_file_path):
        raise FileNotFoundError(f"A config with tag '{tag}' does not exist.")
    return Config(
        tag,
        spectre_server.core.io.read_file(
            config_file_path, spectre_server.core.io.FileFormat.JSON
        ),
    )


def parse_config_file_name(file_name: str) -> tuple[str, str]:
    """Parse a config file name into its tag and extension."""
    return os.path.splitext(file_name)


def write_config(
    tag: str,
    receiver_name: str,
    receiver_mode: str,
    parameters: dict[str, typing.Any],
    configs_dir_path: typing.Optional[str] = None,
) -> None:
    """Write parameters to a config on the filesystem.

    :param tag: The config tag.
    :param receiver_name: The name of the receiver.
    :param receiver_mode: The name of the operating mode.
    :param parameters: The parameters to save.
    :param configs_dir_path: Optionally override the directory containing the configs, defaults to None
    """
    _validate_tag(tag)
    configs_dir_path = (
        configs_dir_path or spectre_server.core.config.paths.get_configs_dir_path()
    )
    content = {
        _CaptureConfigKey.RECEIVER_NAME: receiver_name,
        _CaptureConfigKey.RECEIVER_MODE: receiver_mode,
        _CaptureConfigKey.PARAMETERS: parameters,
    }
    file_path = os.path.join(configs_dir_path, f"{tag}.json")
    with open(file_path, "w") as f:
        json.dump(content, f, indent=4)
