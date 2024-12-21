import numpy as np
import random
import pandas as pd

class StockTradingRLAgent:
    def __init__(self, state_size, action_size, learning_rate=0.001, gamma=0.95, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = []
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.model = self._build_model()

    def _build_model(self):
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Dense
        from tensorflow.keras.optimizers import Adam

        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state, verbose=0)
        return np.argmax(act_values[0])

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, min(len(self.memory), batch_size))
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target += self.gamma * np.amax(self.model.predict(next_state, verbose=0)[0])
            target_f = self.model.predict(state, verbose=0)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

# PLACEHOLDER
def get_llm_prediction(news_headline, stock_data):
    return random.choice(['rise', 'fall', 'neutral'])

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def get_state(data, headlines, t, n):
    d = t - n + 1
    block = data[d:t + 1] if d >= 0 else -d * [data[0]] + data[0:t + 1]
    res = [sigmoid(block[i + 1] - block[i]) for i in range(n - 1)]

    llm_sentiment = get_llm_prediction(headlines[t], block)
    sentiment_mapping = {'rise': 1, 'fall': -1, 'neutral': 0}
    res.append(sentiment_mapping[llm_sentiment])

    return np.array([res])


def train_agent(data, headlines, window_size, episodes, batch_size):
    state_size = window_size
    action_size = 3
    agent = StockTradingRLAgent(state_size, action_size)

    for e in range(episodes):
        print(f"Episode {e+1}/{episodes}")
        total_profit = 0
        state = get_state(data, headlines, 0, window_size + 1)
        for t in range(len(data) - 1):
            action = agent.act(state)

            next_state = get_state(data, headlines, t + 1, window_size + 1)
            reward = 0
            if action == 1:
                reward = data[t + 1] - data[t]
            elif action == 2:
                reward = data[t] - data[t + 1]

            total_profit += reward
            done = t == len(data) - 2
            agent.remember(state, action, reward, next_state, done)
            state = next_state

            if done:
                print(f"Episode {e+1}: Total Profit: {total_profit:.2f}")

        agent.replay(batch_size)


data = np.random.rand(100) * 100
headlines = ["Headline {}".format(i) for i in range(100)]

window_size = 10
episodes = 50
batch_size = 32

train_agent(data, headlines, window_size, episodes, batch_size)