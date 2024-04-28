from host.cfg import CONFIG
from spectre.chunks.Chunks import Chunks
from spectre.spectrogram import factory
from spectre.spectrogram.Panels import Panels

class ChunksHandler:
    def __init__(self, tag):
        self.tag = tag
        self.chunks = Chunks(tag, CONFIG.chunks_dir, CONFIG.json_configs_dir)
        self.set_default_spectrogram()

    def update_tag(self, tag):
        self.tag = tag
        self.chunks = Chunks(tag, CONFIG.chunks_dir, CONFIG.json_configs_dir)
        self.set_default_spectrogram()

    def get_spectrogram(self, entry_values):
        start_time = entry_values['start_time'].get()
        end_time = entry_values['end_time'].get()
        lower_freq = float(entry_values['lower_freq'].get())
        upper_freq = float(entry_values['upper_freq'].get())
        avg_over_int_time = int(entry_values['avg_over_int_time'].get())
        avg_over_int_freq = int(entry_values['avg_over_int_freq'].get())
        S = self.chunks.build_spectrogram_from_range(start_time, end_time)
        S = factory.frequency_chop(S, lower_freq, upper_freq)
        S = factory.frequency_average(S, avg_over_int_freq)
        S = factory.time_average(S, avg_over_int_time)
        return S


    def set_default_spectrogram(self):
        chunks_list = list(self.chunks.dict.values())
        for chunk in reversed(chunks_list):
            if chunk.fits.exists():
                self.default_S = chunk.fits.load_spectrogram()
                return
        raise ValueError(f"No fits files exist for tag {self.tag}")


    def get_field_defaults(self):
        return {
            'tag': self.tag,
            'start_time': self.default_S.datetimes[0].strftime(CONFIG.default_time_format),
            'end_time': self.default_S.datetimes[-1].strftime(CONFIG.default_time_format),
            'lower_freq': round(self.default_S.freq_MHz[0], 2),
            'upper_freq': round(self.default_S.freq_MHz[-1], 2),
            'avg_over_int_time': 1,
            'avg_over_int_freq': 1
        }

    def get_field_labels(self):
        return {
            'tag': 'Tag: ',
            'start_time': "Start time: ",
            'end_time': "End time: ",
            'lower_freq': "Lower frequency [MHz]: ",
            'upper_freq': "Higher frequency [MHz]: ",
            'avg_over_int_time': "Average over (time): ",
            'avg_over_int_freq': "Average over (frequency): ",
        }

    def get_panel_types(self):
        return Panels(self.default_S).panel_type_dict.keys()