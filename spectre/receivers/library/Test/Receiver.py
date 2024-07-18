from spectre.receivers.receiver_register import register_receiver
from spectre.receivers.SPECTREReceiver import SPECTREReceiver
from spectre.receivers.library.Test.gr import cosine_signal_test_1
from spectre.utils import validator_helpers

@register_receiver("Test")
class Receiver(SPECTREReceiver):
    def __init__(self, receiver_name: str, mode: str):
        super().__init__(receiver_name, mode)


    def _set_capture_methods(self) -> None:
        self.capture_methods = {
            "cosine-signal-test-1": self.__cosine_signal_test_1
        }
        return
    

    def _set_validators(self) -> None:
        self.validators = {
            "cosine-signal-test-1": self.__cosine_signal_test_1_validator
        }
        return
    

    def _set_templates(self) -> None:
        self.templates = {
            "cosine-signal-test-1": {
                'samp_rate': int, # gr (sampling rate)
                'frequency': float, # gr (frequency of the cosine signal)
                'amplitude': float, # gr (ampltude of the cosine signal)
                'chunk_size': int, # gr (size of each batched file) [s]
                'window_type': str, # post_proc (window type)
                'window_kwargs': dict, # post_proc (keyword arguments for window function) must be in order as in scipy documentation.
                'window_size': int, # post_proc (number of samples for window)
                'STFFT_kwargs': dict, # post_proc (keyword arguments for STFFT)
                'chunk_key': str, # tag will map to the chunk with this key
                'event_handler_key': str, # tag will map to event handler with this key during post processing
                'integration_time': float # spectrograms will be averaged over a time integration_time
            },
        }
        return


    def __cosine_signal_test_1(self, capture_configs: list) -> None:
        capture_config = capture_configs[0]
        cosine_signal_test_1.main(capture_config)
        return
    

    def __cosine_signal_test_1_validator(self, capture_config: dict) -> None:
        # unpack the capture config
        samp_rate = capture_config.get("samp_rate")
        frequency = capture_config.get("frequency")
        amplitude = capture_config.get("amplitude")
        chunk_size = capture_config.get("chunk_size")
        window_type = capture_config.get("window_type")
        window_size = capture_config.get("window_size")
        STFFT_kwargs = capture_config.get("STFFT_kwargs")
        chunk_key = capture_config.get("chunk_key")
        event_handler_key = capture_config.get("event_handler_key")
        integration_time = capture_config.get("integration_time")

        validator_helpers.validate_samp_rate_strictly_positive(samp_rate)
        validator_helpers.validate_chunk_size_strictly_positive(chunk_size)
        validator_helpers.validate_integration_time(integration_time, chunk_size) 
        validator_helpers.validate_window(window_type, 
                                          {}, 
                                          window_size,
                                          chunk_size,
                                          samp_rate)
        validator_helpers.validate_STFFT_kwargs(STFFT_kwargs)
        validator_helpers.validate_chunk_key(chunk_key, "default")
        validator_helpers.validate_event_handler_key(event_handler_key, "default")

        if integration_time != 0:
            raise ValueError(f"Integration time must be zero. Received: {integration_time}")
        
        # check that the sample rate is an integer multiple of the underlying signal frequency
        if samp_rate % frequency != 0:
            raise ValueError("samp_rate must be some integer multiple of frequency.")

        a = samp_rate/frequency
        if a < 2:
            raise ValueError(f"The ratio samp_rate/frequency must be a natural number greater than two.  Received: {a}")
        
        # ensuring the window type is rectangular
        if window_type != "boxcar":
            raise ValueError(f"Window type must be \"boxcar\". Received: {window_type}")

        # ensuring that the hop is specified as a keyword argument
        if set(STFFT_kwargs.keys()) != {"hop"}:
            raise KeyError(f"Only allowed kwarg is STFFT_kwargs is \"hop\". Received: {STFFT_kwargs.keys()}")
        
        # checking that hop is of integer type
        hop = STFFT_kwargs.get("hop")
        if type(hop) != int:
            raise TypeError(f"hop must an integer. Received: {hop}")
        
        # analytical requirement
        # if p is the number of sampled cycles, we can find that p = window_size / a
        # the number of sampled cycles must be a positive natural number.
        p = window_size / a
        if window_size % a != 0:
            raise ValueError(f"The number of sampled cycles must be a positive natural number. Computed that p={p}")
    
    
        if amplitude <= 0:
            raise ValueError(f"amplitude must be strictly positive. Received: {amplitude}")
        return
    