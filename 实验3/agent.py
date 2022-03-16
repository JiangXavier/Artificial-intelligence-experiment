import numpy as np
import math

class QLearning(object):
    def __init__(self, state_dim, action_dim, cfg):
        self.action_dim = action_dim  # dimension of acgtion
        self.lr = cfg.lr  # learning rate
        self.gamma = cfg.gamma # 衰减系数
        self.epsilon = 0
        self.sample_count = 0
        self.Q_table = np.zeros((state_dim, action_dim))  # Q表格
        self.epsilon_end = 0.1
        self.epsilon_start = 0.9
        self.epsilon_decay = 2000

    def choose_action(self, state):
        ####################### 智能体的决策函数，需要完成Q表格方法（需要完成）#######################
        self.sample_count += 1
        self.epsilon = self.epsilon_end + (self.epsilon_start - self.epsilon_end) * math.exp(
            -1.0 * self.sample_count / self.epsilon_decay)
        if np.random.uniform(0, 1) > self.epsilon:  # 随机选取0-1之间的值，如果大于epsilon就按照贪心策略选取action，否则随机选取
            action = self.predict(state)  # 根据当前观测预测下一步选择哪个action
        else:
            action = np.random.choice(self.action_dim)  # 有一定概率随机探索选取一个动作
        return action

    def predict(self,state):
         Q_list = self.Q_table[state, :]  # 当前观测（状态）那一行，所有列
         Q_max = np.max(Q_list)  # 选择当前观测（状态）下对应Q值最大的那个动作
         action_list = np.where(Q_list == Q_max)[0]  # 找到Q_max在Q_list里对应的所有index
         action = np.random.choice(action_list)  # Q_max可能对应多个action，可以随机抽取一个
         return action

    def update(self, state, action, reward, next_state, done):
        ############################ Q表格的更新方法（需要完成）##################################
        Q_predict = self.Q_table[state, action]##估计值
        if done:
            Q_target = reward  # 没有下一个状态了
        else:
            Q_target = reward + self.gamma * np.max(self.Q_table[next_state, :])  # Q-table-learning 现实值
        self.Q_table[state, action] += self.lr * (Q_target - Q_predict)


    def save(self, path):
        np.save(path + "Q_table.npy", self.Q_table)

    def load(self, path):
        self.Q_table = np.load(path + "Q_table.npy")
