# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from ._register import register_receiver
from ._base import Base
from ._names import ReceiverName


@register_receiver(ReceiverName.CUSTOM)
class Custom(Base):
    """A customisable receiver with no pre-defined operating modes.

    Use `add_mode` to add new operating modes.
    """
