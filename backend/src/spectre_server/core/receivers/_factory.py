# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing

import spectre_server.core.exceptions
import spectre_server.core.batches

from ._register import receivers
from ._base import Base
from ._config import read_config
from ._signal_generator import SignalGenerator
from ._custom import Custom
from ._rsp1a import RSP1A
from ._rspduo import RSPduo
from ._rspdx import RSPdx
from ._usrp import USRP
from ._b200mini import B200mini
from ._hackrf import HackRF
from ._hackrfone import HackRFOne
from ._rtlsdr import RTLSDR


@typing.overload
def get_receiver(
    receiver_name: typing.Literal["custom"], mode: typing.Optional[str] = None
) -> Custom: ...
@typing.overload
def get_receiver(
    receiver_name: typing.Literal["signal_generator"], mode: typing.Optional[str] = None
) -> SignalGenerator: ...
@typing.overload
def get_receiver(
    receiver_name: typing.Literal["rsp1a"], mode: typing.Optional[str] = None
) -> RSP1A: ...
@typing.overload
def get_receiver(
    receiver_name: typing.Literal["rspduo"], mode: typing.Optional[str] = None
) -> RSPduo: ...
@typing.overload
def get_receiver(
    receiver_name: typing.Literal["rspdx"], mode: typing.Optional[str] = None
) -> RSPdx: ...
@typing.overload
def get_receiver(
    receiver_name: typing.Literal["usrp"], mode: typing.Optional[str] = None
) -> USRP: ...
@typing.overload
def get_receiver(
    receiver_name: typing.Literal["b200mini"], mode: typing.Optional[str] = None
) -> B200mini: ...
@typing.overload
def get_receiver(
    receiver_name: typing.Literal["hackrf"], mode: typing.Optional[str] = None
) -> HackRF: ...
@typing.overload
def get_receiver(
    receiver_name: typing.Literal["hackrfone"], mode: typing.Optional[str] = None
) -> HackRFOne: ...
@typing.overload
def get_receiver(
    receiver_name: typing.Literal["rtlsdr"], mode: typing.Optional[str] = None
) -> RTLSDR: ...
@typing.overload
def get_receiver(receiver_name: str, mode: typing.Optional[str] = None) -> Base: ...


def get_receiver(receiver_name: str, mode: typing.Optional[str] = None) -> Base:
    """Get a registered receiver.

    :param receiver_name: The name of the receiver.
    :param mode: The initial operating mode for the receiver, defaults to None
    :raises ReceiverNotFoundError: If the receiver name is not registered.
    :return: An instance of the receiver class registered under `receiver_name`.
    """
    receiver_cls = receivers.get(receiver_name)
    if receiver_cls is None:
        valid_receivers = list(receivers.keys())
        raise spectre_server.core.exceptions.ReceiverNotFoundError(
            f"Could not find the receiver '{receiver_name}', "
            f"expected one of {valid_receivers}"
        )
    return receiver_cls(receiver_name, mode=mode)


def get_batch_cls(
    tag: str, configs_dir_path: typing.Optional[str] = None
) -> typing.Type[spectre_server.core.batches.Base]:
    """Get the right API used to read batch files under the input tag, accounting for
    batch files containing third-party spectrogram data.

    :param tag: The batch file tag.
    """
    config = read_config(tag, configs_dir_path)
    receiver = get_receiver(config.receiver_name, config.receiver_mode)
    return receiver.batch_cls
