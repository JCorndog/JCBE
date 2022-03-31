from collections import deque
import os
import random
import subprocess
import time

from keras import layers
from keras.callbacks import TensorBoard
from keras.models import Model, load_model
from keras.optimizer_v2.adam import Adam
import numpy as np
import tensorflow as tf

from envs import GameEnv
from messagehandler import Communicator
from utils import get_args, load_config, load_model_details, set_shutdown_actions

args = get_args()
# print(tf.__version__)

cfg = load_config(args.cfg_file)

print(cfg)

REPLAY_MEMORY_SIZE = cfg['REPLAY_MEMORY_SIZE']
MIN_REPLAY_MEMORY_SIZE = cfg['MIN_REPLAY_MEMORY_SIZE']
MODEL_NAME = cfg['MODEL_NAME']

MINIBACH_SIZE = cfg['MINIBACH_SIZE']
DISCOUNT = cfg['DISCOUNT']
UPDATE_TARGET_EVERY = cfg['UPDATE_TARGET_EVERY']
MIN_REWARD = cfg['MIN_REWARD']
EPISODES = cfg['EPISODES']
EPISODE_LENGTH = cfg['EPISODE_LENGTH']

epsilon = cfg['epsilon']  # not a constant, going to be decayed
EPSILON_DECAY = cfg['EPSILON_DECAY']
MIN_EPSILON = cfg['MIN_EPSILON']

AGGREGATE_STATS_EVERY = cfg['AGGREGATE_STATS_EVERY']
SAVE_EVERY = cfg['SAVE_EVERY']

LOAD_MODEL, start_episode, epsilon = load_model_details(MODEL_NAME, epsilon)

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.experimental.set_virtual_device_configuration(gpus[0], [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=int(1024 * 6 / args.num_sess))])
    except RuntimeError as e:
        print(e)


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

        self.tensorboard = ModifiedTensorBoard(log_dir=f'logs/{MODEL_NAME}/{int(time.time())}')

        self.target_update_counter = 0

    def create_model(self):
        if LOAD_MODEL:
            model = load_model(LOAD_MODEL)
            print('Model Loaded')
        else:
            image_input = layers.Input(shape=(44, 44, 3))
            movement_input = layers.Input(shape=(12,))

            conv0 = layers.Conv2D(filters=6, kernel_size=(5, 5), activation='relu')(image_input)
            relu0 = layers.Activation('relu')(conv0)
            pool0 = layers.MaxPooling2D()(relu0)
            drop0 = layers.Dropout(0.2)(pool0)

            conv1 = layers.Conv2D(filters=16, kernel_size=(5, 5), activation='relu')(drop0)
            relu1 = layers.Activation('relu')(conv1)
            pool1 = layers.MaxPooling2D()(relu1)
            drop1 = layers.Dropout(0.2)(pool1)
            flat = layers.Flatten()(drop1)
            dense0 = layers.Dense(units=250, activation='relu')(flat)
            dense1 = layers.Dense(units=100, activation='relu')(dense0)
            dense2 = layers.Dense(units=50, activation='relu')(dense1)

            concat = layers.Concatenate()([dense2, movement_input])
            dense3 = layers.Dense(units=30, activation='relu')(concat)
            dense4 = layers.Dense(units=20, activation='relu')(dense3)
            output = layers.Dense(units=6, activation='linear')(dense4)

            model = Model(inputs=[image_input, movement_input], outputs=[output])
            model.compile(loss='mse', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])
        return model

    def update_replay_memory(self, transition):
        self.replay_memory.append(transition)

    def get_qs(self, state):
        # print(type(state),state.shape)
        return self.model.predict([np.array([state[0]]), np.array([state[1]])])[0]

    def train(self, terminal_state, step):
        if len(self.replay_memory) < MIN_REPLAY_MEMORY_SIZE:
            time.sleep(.118)  # mimic time taken to train model
            return

        minibatch = random.sample(self.replay_memory, MINIBACH_SIZE)

        current_states = [np.array([transition[0][0] for transition in minibatch]), np.array([transition[0][1] for transition in minibatch])]
        current_qs_list = self.model.predict(current_states)

        new_current_states = [np.array([transition[3][0] for transition in minibatch]), np.array([transition[3][1] for transition in minibatch])]
        future_qs_list = self.target_model.predict(new_current_states)
        X_img = []
        X_movement = []
        y = []

        for index, (current_state, action, reward, new_current_states, done) in enumerate(minibatch):
            if not done:
                max_future_q = np.max(future_qs_list[index])
                new_q = reward + DISCOUNT * max_future_q
            else:
                new_q = reward

            current_qs = current_qs_list[index]

            current_qs[action] = new_q

            X_img.append(current_state[0])
            X_movement.append(current_state[1])
            y.append(current_qs)

        self.model.fit([np.array(X_img), np.array(X_movement)], np.array(y), batch_size=MINIBACH_SIZE, verbose=0, shuffle=False, callbacks=[self.tensorboard] if terminal_state else None)

        if terminal_state:
            self.target_update_counter += 1

        if self.target_update_counter > UPDATE_TARGET_EVERY:
            self.target_model.set_weights(self.model.get_weights())
            self.target_update_counter = 0


def main():
    global epsilon
    ep_rewards = [-80]
    agent = DQNAgent()
    game_proc = subprocess.Popen(['..\\builds\\all_ports\\CSFinal.exe', str(args.port)])  # launch game with correct port num
    set_shutdown_actions([lambda: game_proc.kill()])
    com = Communicator(args.port)
    env = GameEnv(com, total_time=EPISODE_LENGTH)
    random.seed(2)
    np.random.seed(2)
    tf.random.set_seed(2)

    if not os.path.isdir('models'):
        os.makedirs('models')

    for episode in range(start_episode, EPISODES + 1):
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
                random_move = False
            else:
                # Get random action
                random_move = True
                action = np.random.randint(0, env.ACTION_SPACE_SIZE)

            new_state, reward, done = env.step(action, random_move)
            # Transform new continous state to new discrete state and count reward
            episode_reward += reward

            # Every step we update replay memory and train main network
            agent.update_replay_memory((current_state, action, reward, new_state, done))
            agent.train(done, step)

            current_state = new_state
            n = time.perf_counter()
            # print(n-s)
            s = n
            step += 1
            if step % 10 == 0:
                print(step)
                # print(sum(times)/len(times))
        print(f'Episode: {episode}\nSteps: {step}\nEp Reward: {episode_reward}\nEpsilon:{epsilon:0.4f}\n')
        # Append episode reward to a list and log stats (every given number of episodes)
        ep_rewards.append(episode_reward)
        if not episode % AGGREGATE_STATS_EVERY or episode == 1:
            average_reward = sum(ep_rewards[-AGGREGATE_STATS_EVERY:]) / len(ep_rewards[-AGGREGATE_STATS_EVERY:])
            min_reward = min(ep_rewards[-AGGREGATE_STATS_EVERY:])
            max_reward = max(ep_rewards[-AGGREGATE_STATS_EVERY:])
            agent.tensorboard.update_stats(reward_avg=average_reward, reward_min=min_reward, reward_max=max_reward, epsilon=epsilon)

            # Save model, but only when min reward is greater or equal a set value
            if min_reward >= MIN_REWARD and episode % SAVE_EVERY == 0:
                agent.model.save(f'models/{MODEL_NAME}/episode_{episode}__epsilon_{epsilon}__time_{int(time.time())}__{max_reward:_>7.2f}max_{average_reward:_>7.2f}avg_{min_reward:_>7.2f}min.model')

        # Decay epsilon
        if epsilon > MIN_EPSILON:
            epsilon *= EPSILON_DECAY
            epsilon = max(MIN_EPSILON, epsilon)
    game_proc.kill()

if __name__ == '__main__':
    main()
