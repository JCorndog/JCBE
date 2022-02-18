import random
import rl.core
from messagehandler import Communicator


class Space():
    space = {(1, 0, 1), (1, 1, 0), (0, 1, 0), (0, 0, 0), (1, 0, 0), (0, 0, 1), (1, 1, 1), (0, 1, 1)}

    def __init__(self):
        pass

    def contains(self, x):
        return x in self.space

    def sample(self):
        return random.sample(self.space, 1)[0]


class GameEnv():
    def __init__(self):
        self.action_space = Space()
        self.communicator = Communicator

    def step(self, action):
        err_msg = "%r (%s) invalid action" % (action, type(action))
        assert self.action_space.contains(action), err_msg
        print(self.encode_action(action))
        # self.communicator.send_data(self.encode_action(action))
        # incomming_msg = self.communicator.get_data()

        observation = [1]
        reward = 1
        done = False

        return observation, reward, done, {}

    def encode_action(self, action):
        message_type = b'i'
        msg = message_type
        for item in action:
            msg += chr(item).encode()
        return msg

    def reset(self):
        self.communicator.send_data(b'r')

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
    g = GameEnv()
    print(g.step((0,0,1)))
