# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os

SPECTRE_PARENT_DIR_PATH = os.environ.get("SPECTRE_DIR_PATH")
if SPECTRE_PARENT_DIR_PATH is None:
    raise ValueError("The environment variable SPECTRE_DIR_PATH has not been set.")

CHUNKS_DIR_PATH = os.environ.get("SPECTRE_CHUNKS_DIR", os.path.join(SPECTRE_PARENT_DIR_PATH, 'chunks'))
os.makedirs(CHUNKS_DIR_PATH, exist_ok=True)

LOGS_DIR_PATH = os.path.join(SPECTRE_PARENT_DIR_PATH, 'logs')
os.makedirs(CHUNKS_DIR_PATH, exist_ok=True)

JSON_CONFIGS_DIR_PATH = os.path.join(SPECTRE_PARENT_DIR_PATH, "cfg", "json_configs")
os.makedirs(CHUNKS_DIR_PATH, exist_ok=True)

DEFAULT_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

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