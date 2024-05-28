from spectre.receivers.BaseCaptureConfigMount import BaseCaptureConfigMount
from spectre.receivers.mount_register import register_capture_config_mount
from spectre.utils import validator_helpers
from spectre.utils import dict_helpers


@register_capture_config_mount("Test")
class CaptureConfigMount(BaseCaptureConfigMount):
    def __init__(self,):
        super().__init__()
        pass

    def set_templates(self) -> None:
        self.templates = {
            "cosine_signal_test_1": {
                'samp_rate': int, # gr (sampling rate)
                'frequency': float, # gr (frequency of the cosine signal)
                'amplitude': float, # gr (ampltude of the cosine signal)
                'chunk_size': int, # gr (size of each batched file) [s]
                'window_type': str, # post_proc (window type)
                'window_kwargs': dict, # post_proc (keyword arguments for window function) must be in order as in scipy documentation.
                'Nx': int, # post_proc (number of samples for window)
                'STFFT_kwargs': dict, # post_proc (keyword arguments for STFFT)
                'chunk_key': str, # tag will map to the chunk with this key
                'event_handler_key': str, # tag will map to event handler with this key during post processing
                'watch_extension': str, # postprocessing will call proc defined in event handler for files appearing with this extension
                'integration_time': float # spectrograms will be averaged over a time integration_time
            },
            
            "key_value_test": {
                'int_key': int,
                'str_key': str,
                'dict_key': dict,
                'float_key': float,
                'bool_key': bool, 
            }
        }


    def set_validators(self) -> None:
        self.validators = {
            "cosine_signal_test_1": self.cosine_signal_test_1_validator,
            "key_value_test": self.key_value_test_validator,
        }


    def cosine_signal_test_1_validator(self, capture_config: dict) -> None:
        # unpack the capture config
        samp_rate = capture_config.get("samp_rate")
        frequency = capture_config.get("frequency")
        amplitude = capture_config.get("amplitude")
        chunk_size = capture_config.get("chunk_size")
        window_type = capture_config.get("window_type")
        Nx = capture_config.get("Nx")
        STFFT_kwargs = capture_config.get("STFFT_kwargs")
        chunk_key = capture_config.get("chunk_key")
        event_handler_key = capture_config.get("event_handler_key")
        watch_extension = capture_config.get("watch_extension")
        integration_time = capture_config.get("integration_time")


        if integration_time != 0:
            raise ValueError(f"Integration time must be zero. Received {integration_time}")


        if watch_extension != ".bin":
            raise ValueError(f"watch_extension must be \".bin\". Received {watch_extension}")


        if chunk_key != "default":
            raise ValueError(f"chunk_key must be \"default\". Received {chunk_key}")

        
        if event_handler_key != "default":
            raise ValueError(f"event_handler_key must be \"default\". Received {event_handler_key}")


        # checking that the chunk_size is greater than the period of the underlying signal
        T = 1 / frequency
        # chunk_size must be more than one period  
        if chunk_size < T:
            raise ValueError("chunk_size must be equal than or greater to the period of the underlying signal.")
        

        # check that the sample rate is an integer multiple of the underlying signal frequency
        if samp_rate % frequency != 0:
            raise ValueError("samp_rate must be some integer multiple of frequency.")

        # checking that the sample rate is above the Nyquist rate
        # a is also the number of samples taken over one cycle of the underlying signal
        a = int(samp_rate/frequency)
        if a < 2:
            raise ValueError(f"The ratio samp_rate/frequency must be a natural number greater than two.  Received {a}")
        
        # ensuring the window type is rectangular
        if window_type != "boxcar":
            raise ValueError(f"Window type must be \"box\". Received {window_type}")
        
        # ensuring that the hop is specified as a keyword argument
        if set(STFFT_kwargs.keys()) != {"hop"}:
            raise KeyError(f"Only allowed kwarg is STFFT_kwargs is \"hop\". Received {STFFT_kwargs.keys()}")
        
        # checking that hop is of integer type
        hop = STFFT_kwargs.get("hop")
        if type(hop) != int:
            raise TypeError(f"hop must an integer. Received {hop}")
        
        # checking that hop is an integer multiple of the ratio (samp_rate/frequency)
        if hop % a != 0:
            raise ValueError(f"hop must be an integer multiple of samp_rate/frequency. Received {hop}")

        # checking that we are "hopping" over at least one period of the underlying signal
        b = int(hop / a)
        if b < 1:
            raise ValueError("The ratio hop/Np, where Np is the number of samples in one cycle according to the sample rate, must be a positive natural number")
        
        # analytical requirement
        # if p is the number of sampled cycles, we can find that p = Nx / a
        # the number of sampled cycles must be a positive natural number.
        p = Nx / a
        if Nx % a != 0:
            raise ValueError(f"The number of sampled cycles must be a positive natural number. Computed that p={p}")

        p = int(p)
        if p < 1:
            raise ValueError(f"The number of sampled cycles must be a positive natural number. Computed that p={p}")
        
        if p % 2 != 0 :
            raise ValueError(f"The number of sampled cycles must be an even positive natural number. Computed that p={p}")

        # the window size must be greater than the hop
        if Nx < hop:
            raise ValueError("Window size (# samples in the window), must be greater than the hop.")
        
        return
    

    def key_value_test_validator(self, capture_config: dict) -> None:
        print("Performing key value test.")
        template = self.templates.get('key_value_test')
        if template is None:
            raise ValueError("Could not find template for the key value test.")
        
        dict_helpers.validate_keys(capture_config, template)
        print("Keys verified.")

        dict_helpers.validate_types(capture_config, template)
        print("Values verified.")

        print("Validated capture config is consistent with the template")
        return


    