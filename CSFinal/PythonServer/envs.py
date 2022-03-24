import random
import time
from typing import Dict, List, Tuple

import numpy as np

from messagehandler import Communicator


class Space:
    space: List[Tuple[int, int, int]] = [(1, 1, 0), (0, 1, 0), (0, 0, 0), (1, 0, 0), (0, 0, 1), (0, 1, 1)]
    n = len(space)

    def __init__(self) -> None:
        pass

    def contains(self, x: Tuple[int, int, int]) -> bool:
        return x in self.space

    def sample(self) -> Tuple[int, int, int]:
        return random.sample(self.space, 1)[0]


class GameEnv:
    DEFAULT_MESSAGE_FORMAT = [('touched', 4, int), ('height', 4, int), ('width', 4, int), ('image', -1, np.float32)]
    TOUCH_REWARD = 25
    MOVE_PENALTY = 1

    def __init__(self, communicator: Communicator, message_format=None) -> None:
        self.action_space = Space()
        self.communicator = communicator
        communicator.get_data()
        self.message_format = message_format if message_format else self.DEFAULT_MESSAGE_FORMAT
        self.ACTION_SPACE_SIZE = self.action_space.n
        self.ep = 0
        self.total_time = 3
        self.episode_start = time.perf_counter()
        self.epoch = 0
        self.distance = None

    def get_epoch_as_bytes(self, byteorder: str = 'little') -> bytes:
        return self.epoch.to_bytes(4, byteorder=byteorder)

    def smart_decode(self, message: bytes) -> Dict:
        pos = 0
        data = {}
        for name, num_bytes, tipe in self.message_format:
            if num_bytes > 0:
                submessage = message[pos:pos + num_bytes]
            else:
                submessage = message[pos:]
            if tipe == int:
                data[name] = int.from_bytes(submessage, 'little')
            elif tipe == np.float32:
                array_received = np.frombuffer(submessage, dtype=np.float32)
                array_received = array_received.reshape((data['height'], data['width']))
                data[name] = np.rot90(array_received)
            pos += num_bytes

        return data

    @staticmethod
    def decode_data(message: bytes) -> Tuple[np.ndarray, int, float]:
        touch = int.from_bytes(message[:4], 'little')
        distance = np.frombuffer(message[4:8], dtype=np.float32)[0]
        dims = int.from_bytes(message[8:12], 'little'), int.from_bytes(message[12:16], 'little'), 3
        array_received = np.frombuffer(message[16:], dtype=np.float32)
        array_received = array_received.reshape(dims)
        array_received = np.rot90(array_received)
        return array_received, touch, distance

    def step(self, action: int, random_move: bool) -> Tuple[np.ndarray, int, bool]:
        selected_action = self.action_space.space[action]
        random_move = b'1' if random_move else b'0'
        self.communicator.send_data(self.get_epoch_as_bytes() + self.encode_action(selected_action)+random_move)
        observation, touch, distance = self.decode_data(self.communicator.get_data())

        done = False
        if touch == 1:
            done = True
            self.ep = 0
            reward = self.TOUCH_REWARD
        elif time.perf_counter() - self.episode_start > self.total_time:
            done = True
            self.ep = 0
            reward = -self.MOVE_PENALTY
        elif distance < self.distance:
            reward = -self.MOVE_PENALTY / 3
        else:
            reward = -self.MOVE_PENALTY
        self.ep += 1
        self.distance = distance
        return observation, reward, done

    @staticmethod
    def encode_action(action: Tuple[int, int, int]) -> bytes:
        message_type = b'i'
        msg = message_type
        for item in action:
            msg += str(item).encode()
        return msg

    def reset(self) -> np.ndarray:
        print(self.distance)
        self.communicator.send_data(self.get_epoch_as_bytes() + b'r')
        print('sent reset')
        self.episode_start = time.perf_counter()
        observation, _, self.distance = self.decode_data(self.communicator.get_data())
        print('Got first state')
        time.sleep(.12)
        self.epoch += 1
        return observation

    def close(self) -> None:
        self.communicator.send_data(b'c')

    def render(self, mode=None, close: bool = False) -> None:
        if not mode:
            return


if __name__ == '__main__':
    c = Communicator()
    g = GameEnv(c)
    print(g.step((0, 0, 1)))
