# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os

SPECTRE_DIR_PATH = os.environ.get("SPECTRE_DIR_PATH")
if SPECTRE_DIR_PATH is None:
    raise ValueError("The environment variable SPECTRE_DIR_PATH has not been set.")

CHUNKS_DIR_PATH = os.environ.get("SPECTRE_CHUNKS_DIR_PATH", 
                                 os.path.join(SPECTRE_DIR_PATH, 'chunks'))
os.makedirs(CHUNKS_DIR_PATH, exist_ok=True)

LOGS_DIR_PATH = os.environ.get("SPECTRE_LOGS_DIR_PATH",
                               os.path.join(SPECTRE_DIR_PATH, 'logs'))
os.makedirs(LOGS_DIR_PATH, exist_ok=True)

JSON_CONFIGS_DIR_PATH = os.environ.get("SPECTRE_JSON_CONFIGS_DIR_PATH",
                                       os.path.join(SPECTRE_DIR_PATH, "json_configs"))
os.makedirs(JSON_CONFIGS_DIR_PATH, exist_ok=True)

DEFAULT_TIME_FORMAT = "%H:%M:%S"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_DATETIME_FORMAT = f"{DEFAULT_DATE_FORMAT}T{DEFAULT_TIME_FORMAT}"

INSTRUMENT_CODES = [
    "ALASKA-ANCHORAGE",
    "ALASKA-COHOE",
    "ALASKA-HAARP",
    "ALGERIA-CRAAG",
    "ALMATY",
    "AUSTRIA-Krumbach",
    "AUSTRIA-MICHELBACH",
    "AUSTRIA-OE3FLB",
    "AUSTRIA-UNIGRAZ",
    "Australia-ASSA",
    "BIR",
    "Croatia-Visnjan",
    "DENMARK",
    "EGYPT-Alexandria",
    "EGYPT-SpaceAgency",
    "FINLAND-Siuntio",
    "Finland-Kempele",
    "GERMANY-DLR",
    "GLASGOW",
    "GREENLAND",
    "HUMAIN",
    "HURBANOVO",
    "INDIA-GAURI",
    "INDIA-OOTY",
    "INDIA-UDAIPUR",
    "JAPAN-IBARAKI",
    "KASI",
    "MEXART",
    "MEXICO-FCFM-UANL",
    "MEXICO-LANCE-A",
    "MEXICO-LANCE-B",
    "MONGOLIA-UB",
    "MRO",
    "MRT3",
    "Malaysia-Banting",
    "NORWAY-EGERSUND",
    "NORWAY-NY-AALESUND",
    "NORWAY-RANDABERG",
    "POLAND-Grotniki",
    "ROMANIA",
    "ROSWELL-NM",
    "SPAIN-PERALEJOS",
    "SSRT",
    "SWISS-HB9SCT",
    "SWISS-HEITERSWIL",
    "SWISS-IRSOL",
    "SWISS-Landschlacht",
    "SWISS-MUHEN",
    "TRIEST",
    "TURKEY",
    "UNAM",
    "URUGUAY",
    "USA-BOSTON",
]

def _get_date_based_dir_path(base_dir: str, year: int = None, 
                             month: int = None, day: int = None) -> str:
    if day and not (year and month):
        raise ValueError("A day requires both a month and a year.")
    if month and not year:
        raise ValueError("A month requires a year.")
    
    date_dir_components = []
    if year:
        date_dir_components.append(f"{year:04}")
    if month:
        date_dir_components.append(f"{month:02}")
    if day:
        date_dir_components.append(f"{day:02}")
    
    return os.path.join(base_dir, *date_dir_components)


def get_chunks_dir_path(year: int = None, month: int = None, day: int = None) -> str:
    return _get_date_based_dir_path(CHUNKS_DIR_PATH, year, month, day)


def get_logs_dir_path(year: int = None, month: int = None, day: int = None) -> str:
    return _get_date_based_dir_path(LOGS_DIR_PATH, year, month, day)