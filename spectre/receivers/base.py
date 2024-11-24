# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC, abstractmethod
from typing import Callable, Any, Optional

from spectre.receivers import validators
from spectre.file_handlers.configs import (
    CaptureConfig,
    validate_against_type_template,
    type_cast_params
)
from spectre.exceptions import (
    TemplateNotFoundError,
    ModeNotFoundError,
    SpecificationNotFoundError
)


class BaseReceiver(ABC):
    def __init__(self, name: str, mode: Optional[str] = None):
        self._name = name

        self._capture_methods: dict[str, Callable] = None
        self._set_capture_methods()

        self._type_templates: dict[str, dict[str, Any]] = None
        self._set_type_templates()

        self._validators: dict[str, Callable] = None
        self._set_validators()

        self._specifications: dict[str, Any] = None
        self._set_specifications()

        self.mode = mode



    @abstractmethod
    def _set_capture_methods(self) -> None:
        pass


    @abstractmethod
    def _set_validators(self) -> None:
        pass

    @abstractmethod
    def _set_type_templates(self) -> None:
        pass


    @abstractmethod
    def _set_specifications(self) -> None:
        pass

    
    @property
    def name(self) -> str:
        return self._name
    

    @property
    def capture_methods(self) -> dict[str, Callable]:
        return self._capture_methods
    

    @property
    def validators(self) -> dict[str, Callable]:
        return self._validators


    @property
    def type_templates(self) -> dict[str, dict[str, Any]]:
        return self._type_templates


    @property
    def specifications(self) -> dict[dict, Any]:
        return self._specifications


    @property
    def valid_modes(self) -> None:
        capture_method_modes = list(self.capture_methods.keys())
        validator_modes = list(self.validators.keys())
        type_template_modes = list(self.type_templates.keys())

        if capture_method_modes == validator_modes == type_template_modes:
            return capture_method_modes
        else:
            raise ValueError(f"Mode mismatch for the receiver {self.name}. Could not define valid modes")

    @property
    def mode(self) -> str:
        return self._mode
    

    @mode.setter
    def mode(self, value: Optional[str]) -> None:
        if (value is not None) and value not in self.valid_modes:
            raise ModeNotFoundError((f"{value} is not a defined mode for the receiver {self.name}. "
                                     f"Expected one of {self.valid_modes}"))
        self._mode = value


    @property
    def mode_is_set(self) -> bool:
        return (self._mode is not None)


    @property
    def capture_method(self) -> Callable:
        return self.capture_methods[self.mode]


    @property
    def validator(self) -> Callable:
        return self.validators[self.mode]


    @property
    def type_template(self) -> dict[str, Any]:
        return self._type_templates[self.mode]
    

    def get_specification(self, 
                          specification_key: str) -> Any:
        specification = self.specifications.get(specification_key)
        if specification is None:
            expected_specifications = list(self.specifications.keys())
            raise SpecificationNotFoundError(f"Invalid specification '{specification_key}'. Expected one of {expected_specifications}")
        return specification


    def validate_capture_config(self, 
                                capture_config: CaptureConfig) -> None:
        # validate against the active type template
        validate_against_type_template(capture_config, 
                                       self.type_template, 
                                       ignore_keys=["receiver", "mode", "tag"])
        # validate against receiver-specific constraints
        self.validator(capture_config)



    def start_capture(self, 
                      tag: str) -> None:
        capture_config = self.load_capture_config(tag)
        self.capture_method(capture_config)


    def save_params(self, 
                    params: list[str],  
                    tag: str, 
                    doublecheck_overwrite: bool = True) -> None:
        d = type_cast_params(params, 
                             self.type_template)
        
        validate_against_type_template(d,
                                       self.type_template)
        
        self.save_capture_config(d, 
                                 tag, 
                                 doublecheck_overwrite=doublecheck_overwrite)


    def save_capture_config(self, 
                            d: dict[str, Any],
                            tag: str, 
                            doublecheck_overwrite: bool = True) -> None:
        
        self.validate_capture_config(d)

        d.update({"receiver": self.name, 
                  "mode": self.mode, 
                  "tag": tag})
        
        capture_config = CaptureConfig(tag)
        capture_config.save(d, 
                            doublecheck_overwrite = doublecheck_overwrite)


    def load_capture_config(self, 
                            tag: str) -> CaptureConfig:
        
        capture_config = CaptureConfig(tag)

        if capture_config["receiver"] != self.name:
            raise ValueError(f"Capture config receiver mismatch for tag {tag}. Expected {self.name}, got {capture_config['receiver']}")
        
        if capture_config["mode"] != self.mode:
            raise ValueError(f"Mode mismatch for the tag {tag}. Expected {self.mode}, got {capture_config['mode']}")
        
        self.validate_capture_config(capture_config)
        return capture_config


    def get_create_capture_config_cmd(self, 
                                      tag: str, 
                                      as_string: bool = False) -> str:
        """Get a command which can be used to create a capture config with the SPECTRE CLI."""
        command_as_list = ["spectre", "create", "capture-config", 
                           "--tag", tag, 
                           "--receiver", self.name, 
                           "--mode", self.mode]
        for key, value in self.type_template.items():
            command_as_list.extend(["-p", f"{key}={value.__name__}"])

        return " ".join(command_as_list) if as_string else command_as_list


# optional parent class which provides default templates and validators
class SPECTREReceiver(BaseReceiver):
    def __init__(self, *args, **kwargs):
        self.__set_default_type_templates()
        super().__init__(*args, **kwargs)
    

    @property
    def default_type_templates(self) -> dict[str, dict[str, Any]]:
        return self._default_type_templates
    

    def __set_default_type_templates(self) -> None:
        self._default_type_templates = {
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
    

    def _get_default_type_template(self, 
                                   mode: str) -> dict:
        default_type_template = self.default_type_templates[mode]
        if default_type_template is None:
            raise TemplateNotFoundError(f"No default template found for the mode {mode}")
        return default_type_template
    

    def _default_sweep_validator(self, 
                                 capture_config: CaptureConfig) -> None:
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

        validators.center_freq_strictly_positive(min_freq)
        validators.center_freq_strictly_positive(max_freq)
        validators.samp_rate_strictly_positive(samp_rate)
        validators.bandwidth_strictly_positive(bandwidth)
        validators.nyquist_criterion(samp_rate, 
                                              bandwidth)
        validators.chunk_size_strictly_positive(chunk_size)
        validators.time_resolution(time_resolution, 
                                             chunk_size) 
        validators.window(window_type, 
                          window_kwargs, 
                          window_size,
                          chunk_size,
                          samp_rate)
        validators.STFFT_kwargs(STFFT_kwargs)
        validators.chunk_key(chunk_key, "sweep")
        validators.event_handler_key(event_handler_key, "sweep")
        validators.gain_is_negative(IF_gain)
        validators.gain_is_negative(RF_gain)
        validators.num_steps_per_sweep(min_freq, 
                                       max_freq, 
                                       samp_rate, 
                                       freq_step)
        validators.sweep_interval(min_freq, 
                                  max_freq, 
                                  samp_rate, 
                                  freq_step,
                                  samples_per_step,
                                  chunk_size)
        validators.non_overlapping_steps(freq_step, 
                                         samp_rate)
        validators.num_samples_per_step(samples_per_step, 
                                        window_size)

        # if the api latency is defined, raise a warning if the step interval is of the same order
        api_latency = self.specifications.get("api_latency")
        if api_latency:
            validators.step_interval(samples_per_step, 
                                     samp_rate, 
                                     api_latency)
    

    def _default_fixed_validator(self, 
                                 capture_config: CaptureConfig) -> None:
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

        validators.center_freq_strictly_positive(center_freq)
        validators.samp_rate_strictly_positive(samp_rate)
        validators.bandwidth_strictly_positive(bandwidth)
        validators.nyquist_criterion(samp_rate, bandwidth)
        validators.chunk_size_strictly_positive(chunk_size)
        validators.time_resolution(time_resolution, chunk_size) 
        validators.window(window_type, 
                          window_kwargs, 
                          window_size,
                          chunk_size,
                          samp_rate)
        validators.STFFT_kwargs(STFFT_kwargs)
        validators.chunk_key(chunk_key, 
                             "fixed")
        validators.event_handler_key(event_handler_key, 
                                     "fixed")
        validators.gain_is_negative(IF_gain)
        validators.gain_is_negative(RF_gain)
    

# parent class for shared methods and attributes of SDRPlay receivers
class SDRPlayReceiver(SPECTREReceiver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _sdrplay_validator(self, 
                           capture_config: CaptureConfig) -> None:
        # RSPduo specific validations in single tuner mode
        center_freq_lower_bound = self.get_specification("center_freq_lower_bound")
        center_freq_upper_bound = self.get_specification("center_freq_upper_bound")
        center_freq = capture_config.get("center_freq")
        min_freq = capture_config.get("min_freq")
        max_freq = capture_config.get("max_freq")

        if center_freq:
            print("Outside")
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
