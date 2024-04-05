from spectre.receivers.Receiver import Receiver
from argparse import ArgumentParser
from cfg import CONFIG

## called as a subprocess for spectre start capture

if __name__ == "__main__":

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
        receiver.start_capture(tag, CONFIG.path_to_capture_configs)

    except Exception as e:
        with open(CONFIG.path_to_capture_log, 'w') as capture_log:
            capture_log.write(f"0: {e}")
        
        capture_log.close()




