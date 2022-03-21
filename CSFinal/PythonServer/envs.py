import random
import numpy as np
from messagehandler import Communicator
import cv2
import time


class Space:
    space = [(1, 1, 0), (0, 1, 0), (0, 0, 0), (1, 0, 0), (0, 0, 1), (0, 1, 1)]
    n = len(space)

    def __init__(self):
        pass

    def contains(self, x):
        return x in self.space

    def sample(self):
        return random.sample(self.space, 1)[0]


class GameEnv:
    DEFAULT_MESSAGE_FORMAT = [('touched', 4, int), ('height', 4, int), ('width', 4, int), ('image', -1, np.float32)]

    def __init__(self, communicator, message_format=None):
        self.action_space = Space()
        self.communicator = communicator
        communicator.get_data()
        self.message_format = message_format if message_format else self.DEFAULT_MESSAGE_FORMAT
        self.ACTION_SPACE_SIZE = self.action_space.n
        self.ep = 0
        self.total_time = 7
        self.episode_start = time.perf_counter()
        self.epoch = 0

    def get_epoch_as_bytes(self, byteorder='little'):
        return self.epoch.to_bytes(4, byteorder=byteorder)

    def smart_decode(self, message):
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

    def decode_data(self, message):
        touch = int.from_bytes(message[:4], 'little')
        dims = int.from_bytes(message[4:8], 'little'), int.from_bytes(message[8:12], 'little'), 3
        array_received = np.frombuffer(message[12:], dtype=np.float32)
        array_received = array_received.reshape(dims)
        array_received = np.rot90(array_received)
        return array_received, touch

    def step(self, action):
        action = self.action_space.space[action]

        self.communicator.send_data(self.get_epoch_as_bytes() + self.encode_action(action))
        observation, touch = self.decode_data(self.communicator.get_data())
        done = False
        if touch == 1:
            done = True
            self.ep = 0
            reward = 0
        elif time.perf_counter() - self.episode_start > self.total_time:
            done = True
            self.ep = 0
            reward = -1
        else:
            reward = -1
        self.ep += 1
        return observation, reward, done

    @staticmethod
    def encode_action(action):
        message_type = b'i'
        msg = message_type
        for item in action:
            msg += str(item).encode()
        return msg

    def reset(self):
        self.communicator.send_data(self.get_epoch_as_bytes() + b'r')
        print('sent reset')
        self.episode_start = time.perf_counter()
        observation, _ = self.decode_data(self.communicator.get_data())
        print('Got first state')
        time.sleep(.12)
        self.epoch += 1
        return observation

    def close(self):
        self.communicator.send_data(b'c')

    def render(self, mode=None, close=False):
        if not mode:
            return


class Processor:
    def __init__(self):
        pass

    def process_step(self, observation, reward, done, info):
        return observation, reward, done, info


if __name__ == '__main__':
    c = Communicator()
    g = GameEnv(c)
    print(g.step((0, 0, 1)))
