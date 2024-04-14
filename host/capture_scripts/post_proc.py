from argparse import ArgumentParser
import os

from spectre.watchdog.Watcher import Watcher
from spectre.watchdog.DefaultEventHandler import DefaultEventHandler
from host.cfg import CONFIG
from host.utils import capture_session

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--tag", required=True, type=str, help="Tag associated with the chunks to be processed")
    args = parser.parse_args()

    WATCH_DIR = CONFIG.chunks_dir
    os.makedirs(WATCH_DIR, exist_ok=True)

    try:
        watcher = Watcher(WATCH_DIR, args.tag, ".bin")
        default_event_handler = DefaultEventHandler(watcher, args.tag, ".bin", WATCH_DIR, CONFIG.json_configs_dir)
        watcher.run(default_event_handler)
    except Exception as e:
        capture_session.log_subprocess(os.getpid(), str(e))
