import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import random
from collections import deque, namedtuple
from typing import Dict, List, Tuple, Any, Optional
import os
import json
import time
from datetime import datetime

from src.utils.logger import Logger
from src.model.market_environment import MarketEnvironment

# 定義經驗回放的數據結構
Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state', 'done'])

class ReplayBuffer:
    """
    經驗回放緩衝區，用於存儲和採樣訓練數據
    """
    def __init__(self, capacity: int = 10000):
        """
        初始化經驗回放緩衝區
        
        Args:
            capacity (int): 緩衝區容量
        """
        self.buffer = deque(maxlen=capacity)
    
    def add(self, state: Dict, action: int, reward: float, next_state: Dict, done: bool) -> None:
        """
        添加經驗到緩衝區
        
        Args:
            state (Dict): 當前狀態
            action (int): 執行的動作
            reward (float): 獲得的獎勵
            next_state (Dict): 下一個狀態
            done (bool): 是否結束
        """
        experience = Experience(state, action, reward, next_state, done)
        self.buffer.append(experience)
    
    def sample(self, batch_size: int) -> List[Experience]:
        """
        從緩衝區中隨機採樣經驗
        
        Args:
            batch_size (int): 批次大小
            
        Returns:
            List[Experience]: 經驗樣本列表
        """
        return random.sample(self.buffer, min(len(self.buffer), batch_size))
    
    def __len__(self) -> int:
        """
        獲取緩衝區中的經驗數量
        
        Returns:
            int: 經驗數量
        """
        return len(self.buffer)

class QNetwork(nn.Module):
    """
    深度Q網絡，用於近似Q函數
    """
    def __init__(self, state_size: int, action_size: int, hidden_size: int = 128):
        """
        初始化Q網絡
        
        Args:
            state_size (int): 狀態特徵維度
            action_size (int): 動作空間大小
            hidden_size (int): 隱藏層大小
        """
        super(QNetwork, self).__init__()
        
        # 定義網絡結構
        self.fc1 = nn.Linear(state_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, action_size)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向傳播
        
        Args:
            x (torch.Tensor): 輸入狀態張量
            
        Returns:
            torch.Tensor: 各動作的Q值
        """
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

class DQNAgent:
    """
    深度Q網絡代理，用於學習最優價格調整策略
    """
    def __init__(self, state_size: int, action_size: int, config_path: str = "config/config.json"):
        """
        初始化DQN代理
        
        Args:
            state_size (int): 狀態特徵維度
            action_size (int): 動作空間大小
            config_path (str): 配置文件路徑
        """
        self.logger = Logger().get_logger()
        self.logger.info("初始化DQN代理")
        
        # 加載配置
        self.config_path = config_path
        self._load_config()
        
        # 設置設備（CPU或GPU）
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.logger.info(f"使用設備: {self.device}")
        
        # 狀態和動作空間
        self.state_size = state_size
        self.action_size = action_size
        
        # 創建Q網絡和目標網絡
        self.qnetwork_local = QNetwork(state_size, action_size, 
                                      self.drl_params.get("hidden_size", 128)).to(self.device)
        self.qnetwork_target = QNetwork(state_size, action_size, 
                                       self.drl_params.get("hidden_size", 128)).to(self.device)
        
        # 設置優化器
        self.optimizer = optim.Adam(self.qnetwork_local.parameters(), 
                                   lr=self.drl_params.get("learning_rate", 1e-3))
        
        # 創建經驗回放緩衝區
        self.memory = ReplayBuffer(self.drl_params.get("buffer_size", 10000))
        
        # 訓練參數
        self.batch_size = self.drl_params.get("batch_size", 64)
        self.gamma = self.drl_params.get("gamma", 0.99)  # 折扣因子
        self.tau = self.drl_params.get("tau", 1e-3)  # 用於軟更新目標網絡的參數
        self.update_every = self.drl_params.get("update_every", 4)  # 每隔多少步更新網絡
        
        # 探索參數
        self.epsilon = self.drl_params.get("epsilon_start", 1.0)
        self.epsilon_min = self.drl_params.get("epsilon_min", 0.01)
        self.epsilon_decay = self.drl_params.get("epsilon_decay", 0.995)
        
        # 訓練步數計數器
        self.t_step = 0
        
        # 模型保存路徑
        self.model_dir = "models"
        os.makedirs(self.model_dir, exist_ok=True)
    
    def _load_config(self) -> None:
        """
        從配置文件加載配置
        """
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            self.drl_params = self.config.get("drl", {})
            self.logger.info("成功加載DRL配置")
        except Exception as e:
            self.logger.error(f"加載配置文件失敗: {str(e)}")
            # 使用默認配置
            self.drl_params = {
                "hidden_size": 128,
                "buffer_size": 10000,
                "batch_size": 64,
                "gamma": 0.99,
                "tau": 1e-3,
                "learning_rate": 1e-3,
                "update_every": 4,
                "epsilon_start": 1.0,
                "epsilon_min": 0.01,
                "epsilon_decay": 0.995
            }
    
    def step(self, state: Dict, action: int, reward: float, next_state: Dict, done: bool) -> None:
        """
        更新經驗回放緩衝區並學習
        
        Args:
            state (Dict): 當前狀態
            action (int): 執行的動作
            reward (float): 獲得的獎勵
            next_state (Dict): 下一個狀態
            done (bool): 是否結束
        """
        # 添加經驗到回放緩衝區
        self.memory.add(state, action, reward, next_state, done)
        
        # 每隔update_every步學習一次
        self.t_step = (self.t_step + 1) % self.update_every
        if self.t_step == 0 and len(self.memory) > self.batch_size:
            experiences = self.memory.sample(self.batch_size)
            self._learn(experiences)
    
    def act(self, state: Dict, eval_mode: bool = False) -> int:
        """
        根據當前策略選擇動作
        
        Args:
            state (Dict): 當前狀態
            eval_mode (bool): 是否為評估模式（不使用探索）
            
        Returns:
            int: 選擇的動作
        """
        # 將狀態字典轉換為張量
        state_tensor = self._dict_to_tensor(state)
        
        # 設置為評估模式
        self.qnetwork_local.eval()
        
        with torch.no_grad():
            action_values = self.qnetwork_local(state_tensor)
        
        # 設置回訓練模式
        self.qnetwork_local.train()
        
        # 在評估模式下，直接選擇最佳動作
        if eval_mode:
            return torch.argmax(action_values).item()
        
        # 在訓練模式下，使用ε-greedy策略
        if random.random() > self.epsilon:
            return torch.argmax(action_values).item()
        else:
            return random.choice(range(self.action_size))
    
    def _learn(self, experiences: List[Experience]) -> None:
        """
        從經驗批次中學習
        
        Args:
            experiences (List[Experience]): 經驗樣本列表
        """
        # 解包經驗
        states = [e.state for e in experiences]
        actions = torch.tensor([e.action for e in experiences], dtype=torch.long).to(self.device)
        rewards = torch.tensor([e.reward for e in experiences], dtype=torch.float).to(self.device)
        next_states = [e.next_state for e in experiences]
        dones = torch.tensor([e.done for e in experiences], dtype=torch.float).to(self.device)
        
        # 將狀態字典列表轉換為張量
        states_tensor = torch.stack([self._dict_to_tensor(s) for s in states])
        next_states_tensor = torch.stack([self._dict_to_tensor(s) for s in next_states])
        
        # 獲取當前Q值估計
        q_values = self.qnetwork_local(states_tensor).gather(1, actions.unsqueeze(1))
        
        # 獲取下一個狀態的最大Q值
        q_targets_next = self.qnetwork_target(next_states_tensor).detach().max(1)[0].unsqueeze(1)
        
        # 計算目標Q值
        q_targets = rewards.unsqueeze(1) + (self.gamma * q_targets_next * (1 - dones.unsqueeze(1)))
        
        # 計算損失
        loss = F.mse_loss(q_values, q_targets)
        
        # 最小化損失
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # 軟更新目標網絡
        self._soft_update()
        
        # 更新探索率
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def _soft_update(self) -> None:
        """
        軟更新目標網絡參數：θ_target = τ*θ_local + (1-τ)*θ_target
        """
        for target_param, local_param in zip(self.qnetwork_target.parameters(), self.qnetwork_local.parameters()):
            target_param.data.copy_(self.tau * local_param.data + (1.0 - self.tau) * target_param.data)
    
    def _dict_to_tensor(self, state_dict: Dict) -> torch.Tensor:
        """
        將狀態字典轉換為張量
        
        Args:
            state_dict (Dict): 狀態字典
            
        Returns:
            torch.Tensor: 狀態張量
        """
        # 提取狀態字典中的值並轉換為列表
        state_values = list(state_dict.values())
        
        # 轉換為張量
        return torch.tensor(state_values, dtype=torch.float).to(self.device)
    
    def save(self, filename: str = None) -> str:
        """
        保存模型
        
        Args:
            filename (str, optional): 文件名，如果為None則使用時間戳
            
        Returns:
            str: 保存的文件路徑
        """
        if filename is None:
            filename = f"dqn_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pth"
        
        filepath = os.path.join(self.model_dir, filename)
        
        torch.save({
            'qnetwork_local_state_dict': self.qnetwork_local.state_dict(),
            'qnetwork_target_state_dict': self.qnetwork_target.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'state_size': self.state_size,
            'action_size': self.action_size,
            'hidden_size': self.drl_params.get("hidden_size", 128)
        }, filepath)
        
        self.logger.info(f"模型已保存到: {filepath}")
        return filepath
    
    def load(self, filepath: str) -> None:
        """
        加載模型
        
        Args:
            filepath (str): 模型文件路徑
        """
        if not os.path.exists(filepath):
            self.logger.error(f"模型文件不存在: {filepath}")
            return
        
        checkpoint = torch.load(filepath, map_location=self.device)
        
        # 檢查模型結構是否匹配
        if checkpoint['state_size'] != self.state_size or checkpoint['action_size'] != self.action_size:
            self.logger.warning(f"模型結構不匹配: 期望 ({self.state_size}, {self.action_size}),"  
                              f"實際 ({checkpoint['state_size']}, {checkpoint['action_size']})")
            return
        
        # 加載模型參數
        self.qnetwork_local.load_state_dict(checkpoint['qnetwork_local_state_dict'])
        self.qnetwork_target.load_state_dict(checkpoint['qnetwork_target_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        
        self.logger.info(f"成功加載模型: {filepath}")
    
    def train(self, episodes: int = 1000, max_steps: int = None, save_freq: int = 100, render: bool = False) -> Dict:
        """
        訓練DQN代理
        
        Args:
            episodes (int): 訓練的回合數
            max_steps (int, optional): 每個回合的最大步數，如果為None則使用環境的默認值
            save_freq (int): 保存模型的頻率（每多少個回合保存一次）
            render (bool): 是否渲染環境
            
        Returns:
            Dict: 訓練統計信息
        """
        self.logger.info(f"開始訓練DQN代理，共 {episodes} 個回合")
        
        # 初始化市場環境
        from src.model.market_environment import MarketEnvironment
        env = MarketEnvironment(config_path=self.config_path)
        
        # 訓練統計
        scores = []
        epsilon_history = []
        training_stats = {
            "episodes": episodes,
            "final_epsilon": None,
            "avg_score": None,
            "max_score": None,
            "min_score": None,
            "training_time": None
        }
        
        start_time = time.time()
        
        # 訓練循環
        for episode in range(1, episodes + 1):
            # 重置環境
            state = env.reset()
            score = 0
            done = False
            step = 0
            
            # 記錄當前的探索率
            epsilon_history.append(self.epsilon)
            
            # 回合循環
            while not done:
                # 選擇動作
                action = self.act(state)
                
                # 執行動作
                next_state, reward, done, info = env.step(action)
                
                # 更新代理
                self.step(state, action, reward, next_state, done)
                
                # 更新狀態和累積獎勵
                state = next_state
                score += reward
                step += 1
                
                # 如果設置了最大步數且達到最大步數，則結束回合
                if max_steps is not None and step >= max_steps:
                    done = True
                
                # 渲染環境（如果需要）
                if render:
                    print(f"Step {step}: Action={action}, Reward={reward:.4f}, Done={done}")
                    print(f"Price: {info['original_price']:.2f} -> {info['new_price']:.2f} ({info['price_adjustment']*100:+.1f}%)")
                    print(f"Sale Probability: {info['sale_probability']:.2f}, Expected Days: {info['expected_days']:.1f}")
                    print("---")
            
            # 記錄回合得分
            scores.append(score)
            
            # 打印訓練進度
            if episode % 10 == 0:
                avg_score = np.mean(scores[-10:])
                self.logger.info(f"回合 {episode}/{episodes} | 平均得分: {avg_score:.2f} | 探索率: {self.epsilon:.4f}")
            
            # 定期保存模型
            if episode % save_freq == 0:
                self.save(f"dqn_model_episode_{episode}.pth")
        
        # 保存最終模型
        final_model_path = self.save("dqn_model_final.pth")
        
        # 計算訓練時間
        training_time = time.time() - start_time
        
        # 更新訓練統計
        training_stats["final_epsilon"] = self.epsilon
        training_stats["avg_score"] = float(np.mean(scores))
        training_stats["max_score"] = float(np.max(scores))
        training_stats["min_score"] = float(np.min(scores))
        training_stats["training_time"] = training_time
        training_stats["model_path"] = final_model_path
        
        self.logger.info(f"訓練完成，最終平均得分: {np.mean(scores[-100:]):.2f}")
        
        return training_stats
    
    def evaluate(self, episodes: int = 100, max_steps: int = None, render: bool = False) -> Dict:
        """
        評估DQN代理
        
        Args:
            episodes (int): 評估的回合數
            max_steps (int, optional): 每個回合的最大步數，如果為None則使用環境的默認值
            render (bool): 是否渲染環境
            
        Returns:
            Dict: 評估統計信息
        """
        self.logger.info(f"開始評估DQN代理，共 {episodes} 個回合")
        
        # 初始化市場環境（評估模式）
        from src.model.market_environment import MarketEnvironment
        env = MarketEnvironment(config_path=self.config_path, evaluation=True)
        
        # 評估統計
        scores = []
        eval_stats = {
            "episodes": episodes,
            "avg_score": None,
            "max_score": None,
            "min_score": None,
            "evaluation_time": None
        }
        
        start_time = time.time()
        
        # 評估循環
        for episode in range(1, episodes + 1):
            # 重置環境
            state = env.reset()
            score = 0
            done = False
            step = 0
            
            # 回合循環
            while not done:
                # 選擇動作（評估模式，不使用探索）
                action = self.act(state, eval_mode=True)
                
                # 執行動作
                next_state, reward, done, info = env.step(action)
                
                # 更新狀態和累積獎勵
                state = next_state
                score += reward
                step += 1
                
                # 如果設置了最大步數且達到最大步數，則結束回合
                if max_steps is not None and step >= max_steps:
                    done = True
                
                # 渲染環境（如果需要）
                if render:
                    print(f"Step {step}: Action={action}, Reward={reward:.4f}, Done={done}")
                    print(f"Price: {info['original_price']:.2f} -> {info['new_price']:.2f} ({info['price_adjustment']*100:+.1f}%)")
                    print(f"Sale Probability: {info['sale_probability']:.2f}, Expected Days: {info['expected_days']:.1f}")
                    print("---")
            
            # 記錄回合得分
            scores.append(score)
            
            # 打印評估進度
            if episode % 10 == 0:
                avg_score = np.mean(scores)
                self.logger.info(f"回合 {episode}/{episodes} | 平均得分: {avg_score:.2f}")
        
        # 計算評估時間
        evaluation_time = time.time() - start_time
        
        # 更新評估統計
        eval_stats["avg_score"] = float(np.mean(scores))
        eval_stats["max_score"] = float(np.max(scores))
        eval_stats["min_score"] = float(np.min(scores))
        eval_stats["evaluation_time"] = evaluation_time
        
        self.logger.info(f"評估完成，平均得分: {np.mean(scores):.2f}")
        
        return eval_stats
    
    def save_model(self, filepath: str) -> None:
        """
        保存模型到指定路徑
        
        Args:
            filepath (str): 模型文件路徑
        """
        # 確保目錄存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 保存模型
        torch.save({
            'qnetwork_local_state_dict': self.qnetwork_local.state_dict(),
            'qnetwork_target_state_dict': self.qnetwork_target.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'state_size': self.state_size,
            'action_size': self.action_size,
            'hidden_size': self.drl_params.get("hidden_size", 128)
        }, filepath)
        
        self.logger.info(f"模型已保存到: {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """
        從指定路徑加載模型
        
        Args:
            filepath (str): 模型文件路徑
        """
        self.load(filepath)

def train_dqn(env: MarketEnvironment, num_episodes: int = 1000, max_steps: int = None, 
             save_freq: int = 100, render: bool = False) -> DQNAgent:
    """
    訓練DQN代理
    
    Args:
        env (MarketEnvironment): 市場環境
        num_episodes (int): 訓練的回合數
        max_steps (int, optional): 每個回合的最大步數，如果為None則使用環境的默認值
        save_freq (int): 保存模型的頻率（每多少個回合保存一次）
        render (bool): 是否渲染環境
        
    Returns:
        DQNAgent: 訓練好的DQN代理
    """
    logger = Logger().get_logger()
    logger.info(f"開始訓練DQN代理，共 {num_episodes} 個回合")
    
    # 獲取狀態和動作空間大小
    state_size = env.get_state_space_size()
    action_size = env.get_action_space_size()
    
    # 創建DQN代理
    agent = DQNAgent(state_size, action_size)
    
    # 訓練統計
    scores = []
    epsilon_history = []
    
    # 訓練循環
    for episode in range(1, num_episodes + 1):
        # 重置環境
        state = env.reset()
        score = 0
        done = False
        step = 0
        
        # 記錄當前的探索率
        epsilon_history.append(agent.epsilon)
        
        # 回合循環
        while not done:
            # 選擇動作
            action = agent.act(state)
            
            # 執行動作
            next_state, reward, done, info = env.step(action)
            
            # 更新代理
            agent.step(state, action, reward, next_state, done)
            
            # 更新狀態和累積獎勵
            state = next_state
            score += reward
            step += 1
            
            # 如果設置了最大步數且達到最大步數，則結束回合
            if max_steps is not None and step >= max_steps:
                done = True
            
            # 渲染環境（如果需要）
            if render:
                print(f"Step {step}: Action={action}, Reward={reward:.4f}, Done={done}")
                print(f"Price: {info['original_price']:.2f} -> {info['new_price']:.2f} ({info['price_adjustment']*100:+.1f}%)")
                print(f"Sale Probability: {info['sale_probability']:.2f}, Expected Days: {info['expected_days']:.1f}")
                print("---")
        
        # 記錄回合得分
        scores.append(score)
        
        # 打印訓練進度
        if episode % 10 == 0:
            avg_score = np.mean(scores[-10:])
            logger.info(f"回合 {episode}/{num_episodes} | 平均得分: {avg_score:.2f} | 探索率: {agent.epsilon:.4f}")
        
        # 定期保存模型
        if episode % save_freq == 0:
            agent.save(f"dqn_model_episode_{episode}.pth")
    
    # 保存最終模型
    agent.save("dqn_model_final.pth")
    
    # 打印訓練統計
    logger.info(f"訓練完成，最終平均得分: {np.mean(scores[-100:]):.2f}")
    
    return agent

def evaluate_dqn(env: MarketEnvironment, agent: DQNAgent, num_episodes: int = 100, render: bool = True) -> Dict:
    """
    評估DQN代理的性能
    
    Args:
        env (MarketEnvironment): 市場環境
        agent (DQNAgent): DQN代理
        num_episodes (int): 評估的回合數
        render (bool): 是否渲染環境
        
    Returns:
        Dict: 評估結果統計
    """
    logger = Logger().get_logger()
    logger.info(f"開始評估DQN代理，共 {num_episodes} 個回合")
    
    # 評估統計
    scores = []
    sale_probs = []
    expected_days_list = []
    price_adjustments = []
    
    # 評估循環
    for episode in range(1, num_episodes + 1):
        # 重置環境
        state = env.reset()
        score = 0
        done = False
        episode_sale_probs = []
        episode_expected_days = []
        episode_price_adjustments = []
        
        # 回合循環
        while not done:
            # 選擇動作（評估模式，不使用探索）
            action = agent.act(state, eval_mode=True)
            
            # 執行動作
            next_state, reward, done, info = env.step(action)
            
            # 更新狀態和累積獎勵
            state = next_state
            score += reward
            
            # 記錄統計數據
            episode_sale_probs.append(info['sale_probability'])
            episode_expected_days.append(info['expected_days'])
            episode_price_adjustments.append(info['price_adjustment'])
            
            # 渲染環境（如果需要）
            if render and episode <= 5:  # 只渲染前5個回合
                print(f"Step {info['step']}: Action={action}, Reward={reward:.4f}, Done={done}")
                print(f"Price: {info['original_price']:.2f} -> {info['new_price']:.2f} ({info['price_adjustment']*100:+.1f}%)")
                print(f"Sale Probability: {info['sale_probability']:.2f}, Expected Days: {info['expected_days']:.1f}")
                print("---")
        
        # 記錄回合統計
        scores.append(score)
        sale_probs.append(np.mean(episode_sale_probs))
        expected_days_list.append(np.mean(episode_expected_days))
        price_adjustments.append(np.mean(episode_price_adjustments))
        
        # 打印評估進度
        if episode % 10 == 0:
            logger.info(f"評估回合 {episode}/{num_episodes} | 得分: {score:.2f}")
    
    # 計算評估統計
    results = {
        "avg_score": float(np.mean(scores)),
        "std_score": float(np.std(scores)),
        "avg_sale_probability": float(np.mean(sale_probs)),
        "avg_expected_days": float(np.mean(expected_days_list)),
        "avg_price_adjustment": float(np.mean(price_adjustments)),
        "min_score": float(np.min(scores)),
        "max_score": float(np.max(scores))
    }
    
    # 打印評估結果
    logger.info(f"評估完成，平均得分: {results['avg_score']:.2f} ± {results['std_score']:.2f}")
    logger.info(f"平均銷售概率: {results['avg_sale_probability']:.2f}")
    logger.info(f"平均預期銷售天數: {results['avg_expected_days']:.2f}")
    logger.info(f"平均價格調整: {results['avg_price_adjustment']*100:+.2f}%")
    
    return results