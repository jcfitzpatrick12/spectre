# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import signal
import typing
import pydantic

import gnuradio.gr


import spectre_server.core.config
import spectre_server.core.fields


class BaseModel(pydantic.BaseModel):
    """Base model to be inherited by all flowgraph models."""

    model_config = pydantic.ConfigDict(validate_assignment=True)
    max_noutput_items: spectre_server.core.fields.Field.max_noutput_items = 100000


M = typing.TypeVar("M", bound="BaseModel")


class Base(gnuradio.gr.top_block, typing.Generic[M]):
    def __init__(
        self,
        tag: str,
        model: M,
        batches_dir_path: typing.Optional[str] = None,
    ):
        """An abstract interface for a configurable GNU Radio flowgraph.

        :param tag: The data tag.
        :param model: The model containing configurable parameters.
        :param batches_dir_path: Directory to store data produced at runtime.
        """
        super().__init__()
        self.__model = model
        self._batches_dir_path = (
            batches_dir_path or spectre_server.core.config.paths.get_batches_dir_path()
        )
        self.configure(tag, self.__model)

    def configure(self, tag: str, model: M) -> None:
        """Configure the flowgraph for the block.

        :param tag: The data tag.
        :param model: Contains parameters to configure the flowgraph.
        """
        # TODO: Using the `@abc.abstractmethod` decorator causes static type checking to complain that subclasses are abstract, even
        # when they implement this method. I think inheriting from `gnuradio.gr.top_block` is throwing things off.
        raise NotImplementedError("Flowgraphs must implement the `configure` method.")

    def activate(self) -> None:
        """Activate the GNU Radio flowgraph."""

        def sig_handler(sig=None, frame=None):
            self.stop()
            self.wait()
            sys.exit(0)

        signal.signal(signal.SIGINT, sig_handler)
        signal.signal(signal.SIGTERM, sig_handler)

        self.run(self.__model.max_noutput_items)
