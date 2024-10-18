# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC, abstractmethod
from typing import Callable, Any

from spectre.file_handlers.json.handlers import CaptureConfigHandler
from spectre.receivers import validators
from spectre.exceptions import InvalidModeError, InvalidReceiver


class BaseReceiver(ABC):
    def __init__(self, name: str, mode: str = None):
        self.name = name

        self.capture_methods: dict[str, Callable] = None
        self._set_capture_methods()

        self.templates: dict[str, dict[str, Any]] = None
        self._set_templates()

        self.validators: dict[str, Callable] = None
        self._set_validators()

        self.valid_modes: list[str] = None
        self._set_valid_modes()

        self.specifications: dict[str, Any] = None
        self._set_specifications()

        if not mode is None:
            self.set_mode(mode)


    @abstractmethod
    def _set_capture_methods(self) -> None:
        pass


    @abstractmethod
    def _set_validators(self) -> None:
        pass


    @abstractmethod
    def _set_templates(self) -> None:
        pass


    @abstractmethod
    def _set_specifications(self) -> None:
        pass


    def get_specifications(self) -> dict[dict, Any]:
        return self.specifications
    
    
    def get_specification(self, specification_key: str) -> Any:
        try:
            return self.specifications.get(specification_key)
        except KeyError:
            raise KeyError(f"Invalid specification key '{specification_key}'. Valid modes are: {self.specifications.keys()}")

    
    # ensure that all receiver maps define the same modes for the receiver
    def _set_valid_modes(self) -> None:
        capture_method_modes = list(self.capture_methods.keys())
        validator_modes = list(self.validators.keys())
        template_modes = list(self.templates.keys())

        if capture_method_modes == validator_modes == template_modes:
            self.valid_modes = capture_method_modes
        else:
            raise KeyError(f"Mode key mismatch for the receiver {self.name}. Could not define valid modes")


    def set_mode(self, mode: str) -> None:
        if not mode in self.valid_modes:
            raise InvalidModeError(f"{mode} is not a defined mode for the receiver {self.name}. Expected one of {self.valid_modes}")
        self.mode = mode


    def mode_set(self):
        return (self.mode is not None)
    
    
    def get_capture_method(self) -> Callable:
        return self.capture_methods.get(self.mode)


    def get_validator(self) -> Callable:
        return self.validators.get(self.mode)


    def get_template(self) -> dict[str, Any]:
        return self.templates.get(self.mode)


    def validate(self, capture_config: dict) -> None:
        validator = self.get_validator()
        validator(capture_config)
        return


    def start_capture(self, tags: list[str]) -> None:
        capture_configs = [self.load_capture_config(tag) for tag in tags]
        capture_method = self.get_capture_method()
        capture_method(capture_configs)
        return


    def save_params_as_capture_config(self, tag: str, params: list[str], doublecheck_overwrite: bool = True) -> None:
        capture_config_handler = CaptureConfigHandler(tag)
        template = self.get_template()
        capture_config = capture_config_handler.type_cast_params(params, template) # type cast the params list according to the active template
        self.save_capture_config(tag, capture_config, doublecheck_overwrite=doublecheck_overwrite)


    def save_capture_config(self, tag: str, capture_config: dict, doublecheck_overwrite: bool = True) -> None:
        capture_config_handler = CaptureConfigHandler(tag)
        # basic validation against the template
        capture_config_handler.validate_against_template(capture_config, 
                                                         self.get_template(), 
                                                         ignore_keys=["receiver", "mode", "tag"])
        # validate against receiver-specific constraints in the current mode
        self.validate(capture_config)
        # update the extra metadata
        capture_config.update({"receiver": self.name, "mode": self.mode, "tag": tag})
        # and finally, save the validated capture config to a JSON
        capture_config_handler.save(capture_config, doublecheck_overwrite = doublecheck_overwrite)
        return


    def load_capture_config(self, tag: str) -> dict:
        capture_config_handler = CaptureConfigHandler(tag)
        capture_config = capture_config_handler.read()

        if capture_config["receiver"] != self.name:
            raise InvalidReceiver(f"Capture config receiver mismatch for tag {tag}. Expected {self.name}, got {capture_config['receiver']}")
        
        if capture_config["mode"] != self.mode:
            raise InvalidModeError(f"Mode mismatch for the tag {tag}. Expected {self.mode}, got {capture_config['mode']}")

        self.validate(capture_config)
        return capture_config


    def template_to_command(self, tag: str, as_string: bool = False) -> str:
        command_as_list = ["spectre", "create", "capture-config", 
                           "--tag", tag, 
                           "--receiver", self.name, 
                           "--mode", self.mode]
        template = self.get_template()
        for key, value in template.items():
            command_as_list.extend(["-p", f"{key}={value.__name__}"])

        return " ".join(command_as_list) if as_string else command_as_list


# optional parent class which provides default templates and validators
class SPECTREReceiver(BaseReceiver):
    def __init__(self, receiver_name: str, mode: str = None):
        self.__set_default_templates()
        super().__init__(receiver_name, mode = mode)
        return
    
    def __set_default_templates(self) -> None:
        self.default_templates = {
            "fixed": {
                "center_freq": float, # [Hz]
                "bandwidth": float, # [Hz]
                "samp_rate": int, # [Hz]
                "IF_gain": int, # [dB]
                "RF_gain": int, # [dB]
                "chunk_size": int, #  [s]
                "joining_time": int, # [s]
                "time_resolution": float, # [s]
                "frequency_resolution": float, # [Hz]
                "window_type": str, # window type for STFFT
                "window_kwargs": dict, # keyword arguments for window function, must be in order as in scipy documentation.
                "window_size": int, # number of samples in STFFT window
                "STFFT_kwargs": dict, # keyword arguments for the scipy STFFT class
                "chunk_key": str, # tag will map to the chunk with this key
                "event_handler_key": str, # tag will map to event handler with this key during post processing
            },
            "sweep": {
                "min_freq": float, # [Hz]
                "max_freq": float, # [Hz]
                "samples_per_step": int, 
                "freq_step": float, # [Hz]
                "bandwidth": float, # [Hz]
                "samp_rate": int, # [Hz]
                "IF_gain": int, # [dB]
                "RF_gain": int, # [dB]
                "chunk_size": int, #  [s]
                "joining_time": int, # [s]
                "time_resolution": float, # [s]
                "frequency_resolution": float, # [Hz]
                "window_type": str, # window type for STFFT
                "window_kwargs": dict, # keyword arguments for window function, must be in order as in scipy documentation.
                "window_size": int, # number of samples in STFFT window
                "STFFT_kwargs": dict, # keyword arguments for the scipy STFFT class
                "chunk_key": str, # tag will map to the chunk with this key
                "event_handler_key": str, # tag will map to event handler with this key during post processing
            }
        }
        return
    

    def _get_default_template(self, default_template_key: str) -> dict:
        default_template = self.default_templates.get(default_template_key)
        if default_template is None:
            raise KeyError(f"No default template found with key {default_template_key}")
        return default_template
    

    def _default_sweep_validator(self, capture_config: dict) -> None:
        min_freq = capture_config["min_freq"]
        max_freq = capture_config["max_freq"]
        samples_per_step = capture_config["samples_per_step"]
        freq_step = capture_config["freq_step"]
        bandwidth = capture_config["bandwidth"]
        samp_rate = capture_config["samp_rate"]
        IF_gain = capture_config["IF_gain"]
        RF_gain = capture_config["RF_gain"]
        chunk_size = capture_config["chunk_size"]
        time_resolution = capture_config["time_resolution"]
        window_type = capture_config["window_type"]
        window_kwargs = capture_config["window_kwargs"]
        window_size = capture_config["window_size"]
        STFFT_kwargs = capture_config["STFFT_kwargs"]
        chunk_key = capture_config["chunk_key"]
        event_handler_key = capture_config[ "event_handler_key"]

        validators.validate_center_freq_strictly_positive(min_freq)
        validators.validate_center_freq_strictly_positive(max_freq)
        validators.validate_samp_rate_strictly_positive(samp_rate)
        validators.validate_bandwidth_strictly_positive(bandwidth)
        validators.validate_nyquist_criterion(samp_rate, 
                                              bandwidth)
        validators.validate_chunk_size_strictly_positive(chunk_size)
        validators.validate_time_resolution(time_resolution, 
                                             chunk_size) 
        validators.validate_window(window_type, 
                                   window_kwargs, 
                                   window_size,
                                   chunk_size,
                                   samp_rate)
        validators.validate_STFFT_kwargs(STFFT_kwargs)
        validators.validate_chunk_key(chunk_key, "sweep")
        validators.validate_event_handler_key(event_handler_key, "sweep")
        validators.validate_gain_is_negative(IF_gain)
        validators.validate_gain_is_negative(RF_gain)
        validators.validate_num_steps_per_sweep(min_freq, 
                                                max_freq, 
                                                samp_rate, 
                                                freq_step)
        validators.validate_sweep_interval(min_freq, 
                                           max_freq, 
                                           samp_rate, 
                                           freq_step,
                                           samples_per_step,
                                           chunk_size)
        validators.validate_non_overlapping_steps(freq_step, 
                                                  samp_rate)
        validators.validate_num_samples_per_step(samples_per_step, 
                                                 window_size)

        # if the api latency is defined, raise a warning if the step interval is of the same order
        api_latency = self.specifications.get("api_latency")
        if api_latency:
            validators.validate_step_interval(samples_per_step, 
                                              samp_rate, 
                                              api_latency)
        return
    

    def _default_fixed_validator(self, capture_config: dict) -> None:
        center_freq = capture_config["center_freq"]
        bandwidth = capture_config["bandwidth"]
        samp_rate = capture_config["samp_rate"]
        IF_gain = capture_config["IF_gain"]
        RF_gain = capture_config["RF_gain"]
        chunk_size = capture_config["chunk_size"]
        time_resolution = capture_config["time_resolution"]
        window_type = capture_config["window_type"]
        window_kwargs = capture_config["window_kwargs"]
        window_size = capture_config["window_size"]
        STFFT_kwargs = capture_config["STFFT_kwargs"]
        chunk_key = capture_config["chunk_key"]
        event_handler_key = capture_config["event_handler_key"]

        validators.validate_center_freq_strictly_positive(center_freq)
        validators.validate_samp_rate_strictly_positive(samp_rate)
        validators.validate_bandwidth_strictly_positive(bandwidth)
        validators.validate_nyquist_criterion(samp_rate, bandwidth)
        validators.validate_chunk_size_strictly_positive(chunk_size)
        validators.validate_time_resolution(time_resolution, chunk_size) 
        validators.validate_window(window_type, 
                                          window_kwargs, 
                                          window_size,
                                          chunk_size,
                                          samp_rate)
        validators.validate_STFFT_kwargs(STFFT_kwargs)
        validators.validate_chunk_key(chunk_key, "default")
        validators.validate_event_handler_key(event_handler_key, "default")
        validators.validate_gain_is_negative(IF_gain)
        validators.validate_gain_is_negative(RF_gain)
        return
    

# parent class for shared methods and attributes of SDRPlay receivers
class SDRPlayReceiver(SPECTREReceiver):
    def __init__(self, receiver_name: str, mode: str = None):
        super().__init__(receiver_name, mode = mode)

    def _sdrplay_validator(self, capture_config: dict) -> None:
        # RSPduo specific validations in single tuner mode
        center_freq_lower_bound = self.get_specification("center_freq_lower_bound")
        center_freq_upper_bound = self.get_specification("center_freq_upper_bound")
        center_freq = capture_config.get("center_freq")
        min_freq = capture_config.get("min_freq")
        max_freq = capture_config.get("max_freq")
        if center_freq:
            validators.closed_confine_center_freq(center_freq, 
                                                  center_freq_lower_bound, 
                                                  center_freq_upper_bound)
        if min_freq:
            validators.closed_confine_center_freq(min_freq, 
                                                  center_freq_lower_bound, 
                                                  center_freq_upper_bound)
        if max_freq:
            validators.closed_confine_center_freq(max_freq, 
                                                  center_freq_lower_bound, 
                                                  center_freq_upper_bound)

        validators.closed_confine_samp_rate(capture_config["samp_rate"], 
                                            self.get_specification("samp_rate_lower_bound"), 
                                            self.get_specification("samp_rate_upper_bound"))


        validators.closed_confine_bandwidth(capture_config["bandwidth"], 
                                            self.get_specification("bandwidth_lower_bound"), 
                                            self.get_specification("bandwidth_upper_bound"))

        validators.closed_upper_bound_IF_gain(capture_config["IF_gain"], 
                                              self.get_specification("IF_gain_upper_bound"))
        
        validators.closed_upper_bound_RF_gain(capture_config["RF_gain"], 
                                              self.get_specification("RF_gain_upper_bound"))
