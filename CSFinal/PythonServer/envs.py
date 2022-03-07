import random
import numpy as np
from messagehandler import Communicator


class Space:
    space = {(1, 1, 0), (0, 1, 0), (0, 0, 0), (1, 0, 0), (0, 0, 1), (0, 1, 1)}

    def __init__(self):
        pass

    def contains(self, x):
        return x in self.space

    def sample(self):
        return random.sample(self.space, 1)[0]


class GameEnv:
    def __init__(self, communicator):
        self.action_space = Space()
        self.communicator = communicator

    def decode_data(self, message):
        touch = int.from_bytes(message[:4], 'little')
        dims = int.from_bytes(message[4:8], 'little'), int.from_bytes(message[8:12], 'little'), 3
        array_received = np.frombuffer(message[12:], dtype=np.float32)
        array_received = array_received.reshape(dims)
        array_received = np.rot90(array_received)
        return array_received, touch

    def step(self, action):
        err_msg = "%r (%s) invalid action" % (action, type(action))
        assert self.action_space.contains(action), err_msg
        print(self.encode_action(action))



        self.communicator.send_data(self.encode_action(action))
        observation, reward = self.decode_data(self.communicator.get_data())
        # incomming_msg = self.communicator.get_data()
        done = False
        if reward == 1:
            done = True

        return observation, reward, done, {}

    @staticmethod
    def encode_action(action):
        message_type = b'i'
        msg = message_type
        for item in action:
            msg += str(item).encode()
        return msg

    def reset(self):
        self.communicator.send_data(b'r')
        observation, _ = self.decode_data(self.communicator.get_data())
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
