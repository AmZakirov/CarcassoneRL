import random
import numpy as np
from collections import deque
from keras.models import Sequential 
from keras.layers import Dense
from keras.optimizers import Adam


class DQNAgent:
    
    def __init__(self, state_size, action_size, to_load=False):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=4000)
        self.gamma = 0.5
        self.epsilon = 0
        self.epsilon_decay = 0.1
        self.epsilon_max = 0.9
        self.learning_rate = 1
        self.model = self._build_model()
        if to_load:
            self.model.load_weights('Models/finalweights.hdf5')

    def _build_model(self):
        model = Sequential() 
        model.add(Dense(32, activation="relu",
                        input_dim=self.state_size))
        # model.add(Dense(16, activation="relu"))
        # model.add(Dense(8, activation="relu"))
        # model.add(Dense(16, activation="relu"))
        model.add(Dense(8, activation="relu"))
        model.add(Dense(self.action_size, activation="linear"))
        model.compile(loss="mse", optimizer=Adam(lr=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done): 
        self.memory.append((state, action, reward, next_state, done))

    def train(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        # minibatch = self.memory[-batch_size:]
        for state, action, delta, next_state, done in minibatch:
            if done:
                target = delta 
            else:
                target = (delta + self.gamma * np.amax(self.model.predict(next_state, verbose=0)[0]))
            target_f = self.model.predict(state, verbose=0)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
            
        if self.epsilon <= self.epsilon_max:
            self.epsilon += self.epsilon_decay
            

    def act(self, state):
        if np.random.rand() >= self.epsilon:
            return random.randrange(self.action_size) 
        act_values = self.model.predict(state, verbose=0)
        decision = np.argmax(act_values[0])
        return decision
    
    def act_loaded(self, state):
        if np.random.rand() >= self.epsilon_max:
            return random.randrange(self.action_size) 
        act_values = self.model.predict(state, verbose=0)
        decision = np.argmax(act_values[0])
        return decision

    def save(self, name): 
        self.model.save_weights(name)