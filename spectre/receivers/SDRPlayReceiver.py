# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre.receivers.SPECTREReceiver import SPECTREReceiver
from spectre.receivers import validators

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

        validators.closed_confine_samp_rate(capture_config['samp_rate'], 
                                            self.get_specification("samp_rate_lower_bound"), 
                                            self.get_specification("samp_rate_upper_bound"))


        validators.closed_confine_bandwidth(capture_config['bandwidth'], 
                                            self.get_specification("bandwidth_lower_bound"), 
                                            self.get_specification("bandwidth_upper_bound"))

        validators.closed_upper_bound_IF_gain(capture_config['IF_gain'], 
                                              self.get_specification("IF_gain_upper_bound"))
        
        validators.closed_upper_bound_RF_gain(capture_config['RF_gain'], 
                                              self.get_specification("RF_gain_upper_bound"))
