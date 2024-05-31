import numpy as np

from spectre.spectrogram.Spectrogram import Spectrogram

class AnalyticalSpectrogramFactory:
    def __init__(self,):
        self.builder_methods = {
            "cosine_signal_test_1": self.cosine_signal_test_1
        }
        self.known_cases = list(self.builder_methods.keys())

    def get_spectrogram(self, analytical_case: str, **kwargs) -> Spectrogram:
        builder_method = self.builder_methods.get(analytical_case)
        if builder_method is None:
            raise ValueError(f"Invalid analytical case. Expected one of {self.known_cases}, but received {analytical_case}.")
        S = builder_method(**kwargs)
        return S
    
    def cosine_signal_test_1(self, 
                             shape=None,
                             window_size = None,
                             samp_rate = None,
                             frequency = None,
                             amplitude = None,
                             hop = None,
                             ):
        if shape is None:
            raise ValueError(f"Please specify the spectrogram shape, by passing in the \"shape\" keyword argument with a tuple.")
        
        if window_size is None:
            raise ValueError(f"Please specify the number of samples in each window, by passing in the \"window_size\" keyword argument with an integer.")

        if samp_rate is None:
            raise ValueError(f"Please specify the sample rate, by passing in the \"samp_rate\" keyword argument with an integer.")
        
        if frequency is None:
            raise ValueError(f"Please specify the frequency of the underlying signal by passing in the \"frequency\" keyword argument with an integer.")
        
        if amplitude is None:
            raise ValueError(f"Please specify the amplitude of the underlying signal, by passing in the \"amplitude\" keyword argument with a numeric type.")
        
        if hop is None:
            raise ValueError(f"Please specify the integer hop, by passing in the \"hop\" keyword argument with an integer.")
        
        shape_type = type(shape)
        if shape_type != tuple:
            raise TypeError(f"\"shape\" must be set as a tuple. Received {shape_type}")

        # a defines the ratio of the sampling rate to the frequency of the synthetic signal
        a = int(samp_rate / frequency)
        # p is the "number of sampled periods"
        # which can be found equal to the ratio of window_size to a
        p = int(window_size / a)
        # infer the number of frequency samples
        num_frequency_samples = shape[0]
        num_time_samples = shape[1]

        spectral_slice = np.zeros(num_frequency_samples)
        derived_spectral_amplitude = amplitude * window_size / 2
        spectral_slice[p] = derived_spectral_amplitude
        spectral_slice[window_size - p] = derived_spectral_amplitude
        # analytical solution is derived for 0 <= k <= N-1 indexing
        # so, we need to fftshift the array to align the slices to the naturally
        # ordered frequency array (-ve -> +ve for increasing indices from 0 -> N-1)
        spectral_slice = np.fft.fftshift(spectral_slice)

        # build teh analytical spectrogram
        analytical_dynamic_spectra = np.ones(shape)
        analytical_dynamic_spectra = analytical_dynamic_spectra*spectral_slice[:, np.newaxis]   

        time_seconds = np.array([tau*hop*(1/samp_rate) for tau in range(num_time_samples)])

        if num_frequency_samples % 2 != 0:
            raise ValueError("The number of frequency samples must be even (identically, the window size must be even).")
        
        freq_bound = int(num_frequency_samples/2)
        freq_MHz = np.array([(m*samp_rate/num_frequency_samples)*1e-6 for m in range(-freq_bound, freq_bound)])

        S = Spectrogram(analytical_dynamic_spectra,
                                   time_seconds,
                                   freq_MHz,
                                   'analytically-derived-spectrogram',
                                   units = "amplitude",)
        
        return S
