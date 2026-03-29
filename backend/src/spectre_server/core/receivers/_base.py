# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typing
import logging
import pydantic

import watchdog.observers
import watchdog.events

import spectre_server.core.exceptions
import spectre_server.core.batches
import spectre_server.core.events
import spectre_server.core.config
import spectre_server.core.flowgraphs
import spectre_server.core.logs

from ._config import Config, read_config, write_config

_LOGGER = logging.getLogger(__name__)

T = typing.TypeVar("T")


class ReceiverComponents(typing.Generic[T]):
    def __init__(self) -> None:
        """Manage receiver components per operating mode."""
        self._components: dict[str, T] = {}

    @property
    def modes(self) -> list[str]:
        """Get all the added operating modes."""
        return list(self._components.keys())

    def add(self, mode: str, component: T) -> None:
        """Add a component for a particular operating mode.

        :param mode: The operating mode for the receiver.
        :param component: The component associated with this mode.
        """
        self._components[mode] = component

    def get(self, mode: str) -> T:
        """Retrieve the component for a particular operating mode.

        :param mode: The operating mode for the receiver.
        :return: The component associated with this mode.
        :raises ModeNotFoundError: If the mode is not found.
        """
        if mode not in self._components:
            raise spectre_server.core.exceptions.ModeNotFoundError(
                f"Mode `{mode}` not found. Expected one of {self.modes}"
            )
        return self._components[mode]


class Models(ReceiverComponents[typing.Type[pydantic.BaseModel]]):
    """Store the model class per operating mode."""


class Flowgraphs(ReceiverComponents[typing.Type[spectre_server.core.flowgraphs.Base]]):
    """Store the flowgraph class per operating mode."""


class EventHandlers(ReceiverComponents[typing.Type[spectre_server.core.events.Base]]):
    """Store the event handler class per operating mode."""


class Batches(ReceiverComponents[typing.Type[spectre_server.core.batches.Base]]):
    """Store the batch class per operating mode."""


class Base:
    def __init__(
        self,
        name: str,
        mode: typing.Optional[str] = None,
        models: typing.Optional[Models] = None,
        flowgraphs: typing.Optional[Flowgraphs] = None,
        event_handlers: typing.Optional[EventHandlers] = None,
        batches: typing.Optional[Batches] = None,
    ) -> None:
        """An abstraction layer for software-defined radio receivers.

        :param name: The name of the receiver.
        :param mode: Optionally set the operating mode for the receiver, defaults to None
        :param models: Optionally provide model classes per operating mode, defaults to None
        :param flowgraphs: Optionally provide flowgraph classes per operating mode, defaults to None
        :param event_handlers: Optionally provide event handler classes per operating mode, defaults to None
        :param batches: Optionally provide batch classes per operating mode, defaults to None
        """
        self.__name = name
        self.__mode = mode
        self.__models = models or Models()
        self.__flowgraphs = flowgraphs or Flowgraphs()
        self.__event_handlers = event_handlers or EventHandlers()
        self.__batches = batches or Batches()

    @property
    def name(self) -> str:
        """The name of the receiver."""
        return self.__name

    @property
    def mode(self) -> typing.Optional[str]:
        """The operating mode, or `None` if it's not set."""
        return self.__mode

    @mode.setter
    def mode(self, value: typing.Optional[str]) -> None:
        """Set the operating mode.

        :param value: The new operating mode of the receiver. Use `None` to unset the mode.
        """
        _LOGGER.info(f"Setting the mode to '{value}'")
        if not value is None and value not in self.modes:
            raise spectre_server.core.exceptions.ModeNotFoundError(
                f"Mode `{value}` not found. Expected one of {self.modes}"
            )
        self.__mode = value

    @property
    def modes(self) -> list[str]:
        """The available operating modes for the receiver.

        :raises ValueError: If the modes are inconsistent.
        """
        if (
            not self.__flowgraphs.modes
            == self.__event_handlers.modes
            == self.__batches.modes
        ):
            raise ValueError(f"Inconsistent modes for the receiver '{self.name}'")
        return self.__flowgraphs.modes

    @property
    def active_mode(self) -> str:
        """The active operating mode, raising an error if not set.

        :raises ValueError: If no mode is currently set.
        :return: The active operating mode.
        """
        if self.__mode is None:
            raise ValueError(
                f"An active mode is not set for the receiver '{self.name}'. "
                f"Currently, the mode is {self.__mode}"
            )
        return self.__mode

    @property
    def model_cls(self) -> typing.Type[pydantic.BaseModel]:
        """The model for the active operating mode."""
        return self.__models.get(self.active_mode)

    @property
    def model_schema(self) -> dict[str, typing.Any]:
        """The JSON schema representation of the model for the active operating mode."""
        return self.model_cls.model_json_schema()

    @property
    def flowgraph_cls(
        self,
    ) -> typing.Type[spectre_server.core.flowgraphs.Base]:
        """The flowgraph for the active operating mode."""
        return self.__flowgraphs.get(self.active_mode)

    @property
    def event_handler_cls(
        self,
    ) -> typing.Type[spectre_server.core.events.Base]:
        """The event handler for the active operating mode."""
        return self.__event_handlers.get(self.active_mode)

    @property
    def batch_cls(self) -> typing.Type[spectre_server.core.batches.Base]:
        """The batch for the active operating mode."""
        return self.__batches.get(self.active_mode)

    def model_validate(
        self, parameters: dict[str, typing.Any], skip: bool = False
    ) -> pydantic.BaseModel:
        """Create a model for the active operating mode using the input parameters.

        :param parameters: The parameters used to create the model.
        :param skip: If True, skip validating the parameters.
        :return: The validated model.
        """
        _LOGGER.info("Validating parameters...")
        return self.model_cls.model_validate(parameters, context={"skip": skip})

    def read_config(
        self,
        tag: str,
        skip_validation: bool = False,
        configs_dir_path: typing.Optional[str] = None,
    ) -> Config:
        """Read a config for this receiver.

        :param tag: The tag of the config.
        :param skip_validation: If True, skip validating the parameters.
        :param configs_dir_path: Optionally override the directory which stores the configs, defaults to None
        :return: A structure storing the file contents.
        :raises ValueError: If the config does not belong to this receiver.
        """
        configs_dir_path = (
            configs_dir_path or spectre_server.core.config.paths.get_configs_dir_path()
        )
        config = read_config(tag, configs_dir_path)
        if not config.receiver_name == self.name:
            raise ValueError(
                f"Config with tag {tag}, does not belong to this receiver. Expected '{self.name}', got {config.receiver_name}."
            )
        _ = self.model_validate(config.parameters, skip=skip_validation)
        return config

    def write_config(
        self,
        tag: str,
        parameters: dict[str, typing.Any],
        skip_validation: bool = False,
        configs_dir_path: typing.Optional[str] = None,
    ) -> None:
        """Write parameters to a config.

        :param tag: The tag of the config.
        :param parameters: The parameters to save.
        :param skip_validation: If True, skip validating the parameters.
        :param configs_dir_path: Optionally override the directory which stores the configs, defaults to None
        """
        write_config(
            tag,
            self.name,
            self.active_mode,
            self.model_validate(parameters, skip=skip_validation).model_dump(),
            configs_dir_path,
        )

    @spectre_server.core.logs.log_call
    def activate_flowgraph(
        self,
        tag: str,
        parameters: dict[str, typing.Any],
        skip_validation: bool = False,
        batches_dir_path: typing.Optional[str] = None,
    ) -> None:
        """Activate a flowgraph.

        :param config: The config used to configure the flowgraph.
        :param skip_validation: If True, skip validating the parameters.
        :param batches_dir_path: Optionally override the directory which stores the runtime data, defaults to None
        """
        _LOGGER.info("Starting the flowgraph...")
        self.flowgraph_cls(
            tag,
            self.model_validate(parameters, skip=skip_validation),
            batches_dir_path=batches_dir_path,
        ).activate()

    @spectre_server.core.logs.log_call
    def activate_post_processing(
        self,
        tag: str,
        parameters: dict[str, typing.Any],
        skip_validation: bool = False,
        batches_dir_path: typing.Optional[str] = None,
    ) -> None:
        """Activate post processing.

        :param config: The config used to configure post processing.
        :param skip_validation: If True, skip validating the parameters.
        :param batches_dir_path: Optionally override the directory which stores the runtime data, defaults to None
        """

        batches_dir_path = (
            batches_dir_path or spectre_server.core.config.paths.get_batches_dir_path()
        )
        observer = watchdog.observers.Observer()
        observer.schedule(
            self.event_handler_cls(
                tag,
                self.model_validate(parameters, skip=skip_validation),
                self.batch_cls,
            ),
            batches_dir_path,
            recursive=True,
            event_filter=[watchdog.events.FileCreatedEvent],
        )

        try:
            _LOGGER.info("Starting the post processing...")
            observer.start()
            observer.join()
        except KeyboardInterrupt:
            _LOGGER.warning(
                (
                    "Keyboard interrupt detected. Signalling "
                    "the post processing to stop"
                )
            )
            observer.stop()
            _LOGGER.warning(("Post processing has been successfully stopped"))

    def add_mode(
        self,
        mode: str,
        model: typing.Type[pydantic.BaseModel],
        flowgraph: typing.Type[spectre_server.core.flowgraphs.Base],
        event_handler: typing.Type[spectre_server.core.events.Base],
        batch: typing.Type[spectre_server.core.batches.Base],
    ) -> None:
        """Add an operating mode.

        :param mode: The name of the operating mode.
        :param model: The model defining configurable parameters for the operating mode.
        :param flowgraph: The flowgraph class for this operating mode, which will record
        the signal.
        :param event_handler: The event handler class for this operating mode, which will
        post process data recorded by the flowgraph.
        :param batch: The batch class used to read data produced at runtime by this operating mode.
        """
        self.__models.add(mode, model)
        self.__flowgraphs.add(mode, flowgraph)
        self.__event_handlers.add(mode, event_handler)
        self.__batches.add(mode, batch)
