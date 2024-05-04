from argparse import ArgumentParser
import os

from spectre.watchdog.Watcher import Watcher
from cfg import CONFIG
from spectre.json_config.CaptureConfig import CaptureConfig
from host.utils import capture_session

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--tag", required=True, type=str, help="")
    args = parser.parse_args()
    tag = args.tag

    if not os.path.exists(CONFIG.chunks_dir):
        os.mkdir(CONFIG.chunks_dir)

    try:
        # load the particular extension to watch from the capture config from the capture config
        capture_config_instance = CaptureConfig(tag, CONFIG.json_configs_dir)
        capture_config = capture_config_instance.load_as_dict()
        watch_extension = capture_config.get('watch_extension')

        watcher = Watcher(tag, watch_extension, CONFIG.chunks_dir, CONFIG.json_configs_dir)
        watcher.start()

    except Exception as e:
        capture_session.log_subprocess(os.getpid(), str(e))
