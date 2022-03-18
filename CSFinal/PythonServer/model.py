import random
import time
from collections import deque
import os

import tensorflow as tf
from keras import layers
from keras.callbacks import TensorBoard
from keras.models import Sequential
from keras.optimizer_v2.adam import Adam
import numpy as np

from envs import GameEnv
from messagehandler import Communicator
import time
print(tf.__version__)

REPLAY_MEMORY_SIZE = 10_000
MIN_REPLAY_MEMORY_SIZE = 500
MODEL_NAME = 'first'
MINIBACH_SIZE = 64
DISCOUNT = 0.99
UPDATE_TARGET_EVERY = 5
MIN_REWARD = -200
EPISODES = 20

epsilon = 1  # not a constant, going to be decayed
EPSILON_DECAY = 0.99975
MIN_EPSILON = 0.001

AGGREGATE_STATS_EVERY = 50


# from https://pythonprogramming.net/deep-q-learning-dqn-reinforcement-learning-python-tutorial/
class ModifiedTensorBoard(TensorBoard):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = 1
        self.writer = tf.summary.create_file_writer(self.log_dir)
        self._log_write_dir = self.log_dir

    def set_model(self, model):
        self.model = model

        self._train_dir = os.path.join(self._log_write_dir, 'train')
        self._train_step = self.model._train_counter

        self._val_dir = os.path.join(self._log_write_dir, 'validation')
        self._val_step = self.model._test_counter

        self._should_write_train_graph = False

    def on_epoch_end(self, epoch, logs=None):
        self.update_stats(**logs)

    def on_batch_end(self, batch, logs=None):
        pass

    def on_train_end(self, _):
        pass

    def update_stats(self, **stats):
        with self.writer.as_default():
            for key, value in stats.items():
                tf.summary.scalar(key, value, step=self.step)
                self.writer.flush()


class DQNAgent:
    def __init__(self):
        self.model = self.create_model()
        self.model.summary()

        self.target_model = self.create_model()
        self.target_model.set_weights(self.model.get_weights())

        self.replay_memory = deque(maxlen=REPLAY_MEMORY_SIZE)

        self.tensorboard = ModifiedTensorBoard(log_dir=f'logs/{MODEL_NAME}-{int(time.time())}')

        self.target_update_counter = 0

    def create_model(self):
        model = Sequential()
        model.add(layers.Conv2D(filters=6, kernel_size=(5, 5), activation='relu', input_shape=(44, 44, 3)))
        model.add(layers.Activation('relu'))
        model.add(layers.MaxPooling2D())
        model.add(layers.Dropout(0.1))

        model.add(layers.Conv2D(filters=16, kernel_size=(5, 5), activation='relu'))
        model.add(layers.Activation('relu'))
        model.add(layers.MaxPooling2D())
        model.add(layers.Dropout(0.1))

        model.add(layers.Flatten())
        model.add(layers.Dense(units=50, activation='relu'))
        model.add(layers.Dense(units=20, activation='relu'))
        model.add(layers.Dense(units=6, activation='softmax'))

        model.compile(loss='mse', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])
        return model

    def update_replay_memory(self, transition):
        self.replay_memory.append(transition)

    def get_qs(self, state):
        print(type(state),state.shape)
        return self.model.predict(np.array([state]))[0]

    def train(self, terminal_state, step):
        if len(self.replay_memory) < MIN_REPLAY_MEMORY_SIZE:
            return

        minibatch = random.sample(self.replay_memory, MINIBACH_SIZE)

        current_states = np.array([transition[0] for transition in minibatch])
        current_qs_list = self.model.predict(current_states)

        new_current_states = np.array([transition[3] for transition in minibatch])
        future_qs_list = self.target_model.predict(new_current_states)
        X = []
        y = []

        for index, (current_state, action, reward, new_current_states, done) in enumerate(minibatch):
            if not done:
                max_future_q = np.max(future_qs_list[index])
                new_q = reward + DISCOUNT * max_future_q
            else:
                new_q = reward

            current_qs = current_qs_list[index]

            current_qs[action] = new_q

            X.append(current_state)
            y.append(current_qs)

        self.model.fit(np.array(X), np.array(y), batch_size=MINIBACH_SIZE, verbose=0, shuffle=False, callbacks=[self.tensorboard] if terminal_state else None)

        if terminal_state:
            self.target_update_counter += 1

        if self.target_update_counter > UPDATE_TARGET_EVERY:
            self.target_model.set_weights(self.model.get_weights())
            self.target_update_counter = 0


def main():
    global epsilon
    ep_rewards = [-200]
    com = Communicator()
    env = GameEnv(com)
    random.seed(1)
    np.random.seed(1)
    tf.random.set_seed(1)

    if not os.path.isdir('models'):
        os.makedirs('models')

    agent = DQNAgent()

    for episode in range(1, EPISODES + 1):
        agent.tensorboard.step = episode

        episode_reward = 0
        step = 1
        current_state = env.reset()
        s = time.perf_counter()
        done = False
        while not done:

            # This part stays mostly the same, the change is to query a model for Q values
            if np.random.random() > epsilon:
                # Get action from Q table
                action = np.argmax(agent.get_qs(current_state))
            else:
                # Get random action
                action = np.random.randint(0, env.ACTION_SPACE_SIZE)

            new_state, reward, done = env.step(action)

            # Transform new continous state to new discrete state and count reward
            episode_reward += reward

            # Every step we update replay memory and train main network
            agent.update_replay_memory((current_state, action, reward, new_state, done))
            agent.train(done, step)

            current_state = new_state
            n = time.perf_counter()
            print(n-s)
            s = n
            step += 1

        # Append episode reward to a list and log stats (every given number of episodes)
        ep_rewards.append(episode_reward)
        if not episode % AGGREGATE_STATS_EVERY or episode == 1:
            average_reward = sum(ep_rewards[-AGGREGATE_STATS_EVERY:]) / len(ep_rewards[-AGGREGATE_STATS_EVERY:])
            min_reward = min(ep_rewards[-AGGREGATE_STATS_EVERY:])
            max_reward = max(ep_rewards[-AGGREGATE_STATS_EVERY:])
            agent.tensorboard.update_stats(reward_avg=average_reward, reward_min=min_reward, reward_max=max_reward, epsilon=epsilon)

            # Save model, but only when min reward is greater or equal a set value
            if min_reward >= MIN_REWARD:
                agent.model.save(f'models/{MODEL_NAME}__{max_reward:_>7.2f}max_{average_reward:_>7.2f}avg_{min_reward:_>7.2f}min__{int(time.time())}.model')

        # Decay epsilon
        if epsilon > MIN_EPSILON:
            epsilon *= EPSILON_DECAY
            epsilon = max(MIN_EPSILON, epsilon)


if __name__ == '__main__':
    main()
