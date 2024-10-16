import logging

from spectre.chunks import Chunks
from spectre.logging import configure_root_logger
from spectre.receivers.factory import get_receiver

configure_root_logger("USER", logging.INFO)
test = get_receiver("test")
