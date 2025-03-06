# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later


from spectre_core.logs import log_call
from spectre_core import jobs

def _calculate_total_runtime(seconds: int = 0, 
                             minutes: int = 0, 
                             hours: int = 0
) -> float:
    total_duration = seconds + (minutes * 60) + (hours * 3600) # [s]
    if total_duration <= 0:
        raise ValueError(f"Total duration must be strictly positive.")
    return total_duration

@log_call
def capture(tag: str, 
            seconds: int = 0, 
            minutes: int = 0, 
            hours: int = 0, 
            force_restart: bool = False
) -> str:
    """Start capturing data from an SDR in real time.

    :param tag: The capture config tag.
    :param seconds: The seconds component of the total runtime, defaults to 0
    :param minutes: The minutes component of the total runtime, defaults to 0
    :param hours: The hours component of the total runtime, defaults to 0
    :param force_restart: If any worker encounters an error at runtime, force all
    the workers to restart their processes. Defaults to False
    :return: A string indicating the job has completed.
    """
    workers = [ jobs.do_capture(tag) ]
    total_runtime = _calculate_total_runtime(seconds, minutes, hours)
    jobs.start_job(
        workers, total_runtime, force_restart
    )
    return "Capture complete."
                       

@log_call
def session(tag: str, 
            seconds: int = 0, 
            minutes: int = 0, 
            hours: int = 0, 
            force_restart: bool = False
) -> str:
    """Start a `spectre` session.
    
    Start capturing data from an SDR, and post-process the data in real time into spectrograms.

    :param tag: The capture config tag.
    :param seconds: The seconds component of the total runtime, defaults to 0
    :param minutes: The minutes component of the total runtime, defaults to 0
    :param hours: The hours component of the total runtime, defaults to 0
    :param force_restart: If any worker encounters an error at runtime, force all
    the workers to restart their processes. Defaults to False
    """
    workers = [ jobs.do_post_processing(tag), jobs.do_capture(tag) ]
    total_runtime = _calculate_total_runtime(seconds, minutes, hours)
    jobs.start_job(
        workers, total_runtime, force_restart
    )
    return "Session complete."
    