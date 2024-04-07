from spectre.receivers.Receiver import Receiver
from argparse import ArgumentParser
from cfg import CONFIG
from host.utils import capture_session
import os

def main():
    parser = ArgumentParser()
    parser.add_argument("--receiver", type=str, help="")
    parser.add_argument("--mode", type=str, help="")
    parser.add_argument("--tag", type=str, help="")

    args = parser.parse_args()

    receiver_name = args.receiver
    mode = args.mode
    tag = args.tag

    try:
        receiver = Receiver(receiver_name)
        receiver.set_mode(mode)
        receiver.start_capture(tag, CONFIG.json_configs_dir)

    except Exception as e:
        capture_session.log_subprocess(os.getpid(), str(e))

if __name__ == "__main__":
    main()






