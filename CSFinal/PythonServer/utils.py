import os
from typing import Dict, Tuple, Optional, List
import argparse
import yaml
import re
import signal


def set_shutdown_actions(funcs: List) -> None:
    def handler(signum, frame):
        for func in funcs:
            func()

    signal.signal(signal.SIGINT, handler)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg_file', type=str, help='Path to the config file', required=True)
    parser.add_argument('--port', type=int, help='Connection port', default=5555)
    parser.add_argument('--num_sess', type=int, help='Connection port', default=1)
    args = parser.parse_args()
    return args


def get_most_recent_dir(path: str) -> str:
    all_subdirs = [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    latest_subdir = max(all_subdirs, key=os.path.getmtime)
    return latest_subdir


def load_config(path: str) -> Dict:
    with open(path, 'r') as infile:
        cfg = yaml.load(infile, yaml.Loader)
    return cfg


def load_model_details(MODEL_NAME: str, epsilon_default: float = 1) -> Tuple[Optional[bool], int, float]:
    if os.path.isdir(os.path.join('models', MODEL_NAME)):
        load_dir = get_most_recent_dir(os.path.join('models', MODEL_NAME))
        LOAD_MODEL = load_dir
        start_episode = int(re.findall('episode_(.*?)__', os.path.split(load_dir)[1])[0])
        epsilon = float(re.findall('epsilon_(.*?)__', os.path.split(load_dir)[1])[0])
        print(LOAD_MODEL, epsilon, start_episode)
    else:
        LOAD_MODEL = None
        start_episode = 1
        epsilon = epsilon_default
    return LOAD_MODEL, start_episode, epsilon
