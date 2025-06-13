import numpy as np
import pandas as pd
import random
import time
from typing import Dict, List, Tuple, Any, Optional
import os
import json
from datetime import datetime, timedelta

from src.utils.logger import Logger

class MarketEnvironment:
    """
    市場環境模擬器，用於模擬二手商品市場的動態
    作為強化學習的環境，提供狀態、動作和獎勵
    """
    def __init__(self, config_path: str = "config/config.json"):
        """
        初始化市場環境
        
        Args:
            config_path (str): 配置文件路徑
        """
        self.logger = Logger().get_logger()
        self.logger.info("初始化市場環境模擬器")
        
        # 加載配置
        self.config_path = config_path
        self._load_config()
        
        # 環境狀態
        self.current_state = None
        self.current_item = None
        self.episode_step = 0
        self.max_steps = self.config.get("market", {}).get("max_steps", 30)
        
        # 市場參數
        self.market_params = self.config.get("market", {})
        self.price_sensitivity = self.market_params.get("price_sensitivity", 0.7)
        self.time_sensitivity = self.market_params.get("time_sensitivity", 0.3)
        self.market_volatility = self.market_params.get("market_volatility", 0.1)
        
        # 動作空間定義
        self.price_adjustment_range = self.market_params.get("price_adjustment_range", [-0.3, 0.3])
        self.price_adjustment_steps = self.market_params.get("price_adjustment_steps", 10)
        self.action_space_size = self.price_adjustment_steps
        
        # 計算價格調整步長
        self.price_step = (self.price_adjustment_range[1] - self.price_adjustment_range[0]) / (self.price_adjustment_steps - 1)
        
        # 獎勵參數
        self.reward_weights = {
            "profit": self.market_params.get("profit_weight", 0.7),
            "time": self.market_params.get("time_weight", 0.3)
        }
        
        # 市場數據
        self.market_data = {}
        self.category_stats = {}
        
        # 加載市場數據
        self._load_market_data()
    
    def _load_config(self) -> None:
        """
        從配置文件加載配置
        """
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            self.logger.info("成功加載配置文件")
        except Exception as e:
            self.logger.error(f"加載配置文件失敗: {str(e)}")
            # 使用默認配置
            self.config = {
                "market": {
                    "max_steps": 30,
                    "price_sensitivity": 0.7,
                    "time_sensitivity": 0.3,
                    "market_volatility": 0.1,
                    "price_adjustment_range": [-0.3, 0.3],
                    "price_adjustment_steps": 10,
                    "profit_weight": 0.7,
                    "time_weight": 0.3
                }
            }
    
    def _load_market_data(self) -> None:
        """
        加載市場數據，包括各類別的價格統計信息和銷售時間分佈
        """
        try:
            # 加載類別統計數據
            stats_path = os.path.join("data", "features", "category_stats.json")
            if os.path.exists(stats_path):
                with open(stats_path, 'r') as f:
                    self.category_stats = json.load(f)
                self.logger.info(f"成功加載類別統計數據: {len(self.category_stats)} 個類別")
            else:
                self.logger.warning("類別統計數據文件不存在，將使用模擬數據")
                self._generate_mock_category_stats()
        except Exception as e:
            self.logger.error(f"加載市場數據失敗: {str(e)}")
            self._generate_mock_category_stats()
    
    def _generate_mock_category_stats(self) -> None:
        """
        生成模擬的類別統計數據
        """
        self.logger.info("生成模擬的類別統計數據")
        categories = [
            # 原有類別
            {"id": "9355", "name": "Laptops & Netbooks"},
            {"id": "15032", "name": "Cell Phones & Smartphones"},
            {"id": "11450", "name": "Wristwatch"},
            {"id": "261007", "name": "Digital Cameras"},
            # 新增類別
            {"id": "20081", "name": "Tablets & eReaders"},
            {"id": "139971", "name": "Video Game Consoles"},
            {"id": "175672", "name": "Headphones"},
            {"id": "11700", "name": "Computer Components"},
            {"id": "3676", "name": "TV, Video & Audio"},
            {"id": "293", "name": "Books & Magazines"},
            {"id": "15724", "name": "Clothing & Accessories"},
            {"id": "11116", "name": "Toys & Games"},
            {"id": "619", "name": "Musical Instruments"},
            {"id": "888", "name": "Sporting Goods"},
            {"id": "26395", "name": "Home Appliances"},
            {"id": "14308", "name": "Furniture"},
            {"id": "550", "name": "Art & Collectibles"},
            {"id": "2984", "name": "Jewelry"},
            {"id": "1249", "name": "Tools & Workshop Equipment"},
            {"id": "220", "name": "Bicycles"}
        ]
        
        self.category_stats = {}
        for category in categories:
            category_id = category["id"]
            # 原有類別
            if category_id == "9355":  # 筆電
                self.category_stats[category_id] = {
                    "price_mean": 800.0,
                    "price_std": 300.0,
                    "price_min": 200.0,
                    "price_max": 2000.0,
                    "avg_days_to_sell": 12.5,
                    "std_days_to_sell": 5.2
                }
            elif category_id == "15032":  # 手機
                self.category_stats[category_id] = {
                    "price_mean": 400.0,
                    "price_std": 150.0,
                    "price_min": 100.0,
                    "price_max": 1200.0,
                    "avg_days_to_sell": 8.3,
                    "std_days_to_sell": 3.7
                }
            elif category_id == "11450":  # 手錶
                self.category_stats[category_id] = {
                    "price_mean": 300.0,
                    "price_std": 200.0,
                    "price_min": 50.0,
                    "price_max": 1500.0,
                    "avg_days_to_sell": 10.2,
                    "std_days_to_sell": 4.5
                }
            elif category_id == "261007":  # 數位相機
                self.category_stats[category_id] = {
                    "price_mean": 500.0,
                    "price_std": 250.0,
                    "price_min": 150.0,
                    "price_max": 1800.0,
                    "avg_days_to_sell": 14.8,
                    "std_days_to_sell": 6.3
                }
            # 新增類別
            elif category_id == "20081":  # 平板與電子閱讀器
                self.category_stats[category_id] = {
                    "price_mean": 350.0,
                    "price_std": 200.0,
                    "price_min": 100.0,
                    "price_max": 1200.0,
                    "avg_days_to_sell": 10.5,
                    "std_days_to_sell": 4.8
                }
            elif category_id == "139971":  # 遊戲主機
                self.category_stats[category_id] = {
                    "price_mean": 300.0,
                    "price_std": 150.0,
                    "price_min": 100.0,
                    "price_max": 800.0,
                    "avg_days_to_sell": 7.5,
                    "std_days_to_sell": 3.2
                }
            elif category_id == "175672":  # 耳機
                self.category_stats[category_id] = {
                    "price_mean": 120.0,
                    "price_std": 80.0,
                    "price_min": 20.0,
                    "price_max": 500.0,
                    "avg_days_to_sell": 6.8,
                    "std_days_to_sell": 2.9
                }
            elif category_id == "11700":  # 電腦零組件
                self.category_stats[category_id] = {
                    "price_mean": 180.0,
                    "price_std": 120.0,
                    "price_min": 30.0,
                    "price_max": 800.0,
                    "avg_days_to_sell": 9.2,
                    "std_days_to_sell": 4.1
                }
            elif category_id == "3676":  # 電視、影音設備
                self.category_stats[category_id] = {
                    "price_mean": 450.0,
                    "price_std": 300.0,
                    "price_min": 100.0,
                    "price_max": 2000.0,
                    "avg_days_to_sell": 15.3,
                    "std_days_to_sell": 6.7
                }
            elif category_id == "293":  # 書籍與雜誌
                self.category_stats[category_id] = {
                    "price_mean": 25.0,
                    "price_std": 20.0,
                    "price_min": 5.0,
                    "price_max": 150.0,
                    "avg_days_to_sell": 18.5,
                    "std_days_to_sell": 8.2
                }
            elif category_id == "15724":  # 服飾與配件
                self.category_stats[category_id] = {
                    "price_mean": 60.0,
                    "price_std": 50.0,
                    "price_min": 10.0,
                    "price_max": 500.0,
                    "avg_days_to_sell": 14.2,
                    "std_days_to_sell": 6.5
                }
            elif category_id == "11116":  # 玩具與遊戲
                self.category_stats[category_id] = {
                    "price_mean": 40.0,
                    "price_std": 30.0,
                    "price_min": 10.0,
                    "price_max": 200.0,
                    "avg_days_to_sell": 11.8,
                    "std_days_to_sell": 5.3
                }
            elif category_id == "619":  # 樂器
                self.category_stats[category_id] = {
                    "price_mean": 350.0,
                    "price_std": 300.0,
                    "price_min": 50.0,
                    "price_max": 2000.0,
                    "avg_days_to_sell": 20.5,
                    "std_days_to_sell": 9.8
                }
            elif category_id == "888":  # 運動用品
                self.category_stats[category_id] = {
                    "price_mean": 120.0,
                    "price_std": 100.0,
                    "price_min": 20.0,
                    "price_max": 800.0,
                    "avg_days_to_sell": 13.7,
                    "std_days_to_sell": 6.1
                }
            elif category_id == "26395":  # 家用電器
                self.category_stats[category_id] = {
                    "price_mean": 200.0,
                    "price_std": 150.0,
                    "price_min": 50.0,
                    "price_max": 1000.0,
                    "avg_days_to_sell": 16.2,
                    "std_days_to_sell": 7.4
                }
            elif category_id == "14308":  # 家具
                self.category_stats[category_id] = {
                    "price_mean": 250.0,
                    "price_std": 200.0,
                    "price_min": 50.0,
                    "price_max": 1500.0,
                    "avg_days_to_sell": 22.3,
                    "std_days_to_sell": 10.5
                }
            elif category_id == "550":  # 藝術品與收藏品
                self.category_stats[category_id] = {
                    "price_mean": 180.0,
                    "price_std": 200.0,
                    "price_min": 20.0,
                    "price_max": 2000.0,
                    "avg_days_to_sell": 25.8,
                    "std_days_to_sell": 12.3
                }
            elif category_id == "2984":  # 珠寶
                self.category_stats[category_id] = {
                    "price_mean": 220.0,
                    "price_std": 250.0,
                    "price_min": 30.0,
                    "price_max": 3000.0,
                    "avg_days_to_sell": 19.6,
                    "std_days_to_sell": 8.9
                }
            elif category_id == "1249":  # 工具與工作坊設備
                self.category_stats[category_id] = {
                    "price_mean": 150.0,
                    "price_std": 120.0,
                    "price_min": 30.0,
                    "price_max": 800.0,
                    "avg_days_to_sell": 17.4,
                    "std_days_to_sell": 7.8
                }
            elif category_id == "220":  # 自行車
                self.category_stats[category_id] = {
                    "price_mean": 280.0,
                    "price_std": 220.0,
                    "price_min": 50.0,
                    "price_max": 2500.0,
                    "avg_days_to_sell": 15.9,
                    "std_days_to_sell": 7.2
                }
    
    def reset(self, item_data: Dict = None) -> Dict:
        """
        重置環境，開始新的價格預測場景
        
        Args:
            item_data (Dict, optional): 商品數據，如果為None則隨機生成
            
        Returns:
            Dict: 初始狀態
        """
        self.episode_step = 0
        
        # 如果沒有提供商品數據，則隨機生成
        if item_data is None:
            self.current_item = self._generate_random_item()
        else:
            self.current_item = item_data
        
        # 初始化狀態
        self.current_state = self._create_state()
        
        return self.current_state
    
    def step(self, action: int) -> Tuple[Dict, float, bool, Dict]:
        """
        執行一個動作，更新環境狀態
        
        Args:
            action (int): 動作索引，對應價格調整比例
            
        Returns:
            Tuple[Dict, float, bool, Dict]: 新狀態、獎勵、是否結束、額外信息
        """
        # 增加步數
        self.episode_step += 1
        
        # 將動作索引轉換為價格調整比例
        price_adjustment = self._action_to_adjustment(action)
        
        # 應用價格調整
        original_price = self.current_item["price"]
        new_price = original_price * (1 + price_adjustment)
        self.current_item["price"] = new_price
        
        # 計算銷售概率和預期銷售時間
        sale_probability, expected_days = self._calculate_market_response()
        
        # 計算獎勵
        reward = self._calculate_reward(original_price, new_price, sale_probability, expected_days)
        
        # 更新狀態
        self.current_state = self._create_state()
        
        # 檢查是否結束
        done = self.episode_step >= self.max_steps
        
        # 額外信息
        info = {
            "original_price": original_price,
            "new_price": new_price,
            "price_adjustment": price_adjustment,
            "sale_probability": sale_probability,
            "expected_days": expected_days,
            "step": self.episode_step
        }
        
        return self.current_state, reward, done, info
    
    def _action_to_adjustment(self, action: int) -> float:
        """
        將動作索引轉換為價格調整比例
        
        Args:
            action (int): 動作索引
            
        Returns:
            float: 價格調整比例
        """
        # 確保動作在有效範圍內
        action = max(0, min(action, self.action_space_size - 1))
        
        # 計算對應的價格調整比例
        adjustment = self.price_adjustment_range[0] + action * self.price_step
        
        return adjustment
    
    def _calculate_market_response(self) -> Tuple[float, float]:
        """
        計算市場對當前價格的反應，包括銷售概率和預期銷售時間
        
        Returns:
            Tuple[float, float]: 銷售概率和預期銷售天數
        """
        category_id = self.current_item.get("category_id", "9355")  # 默認使用筆電類別
        category_stats = self.category_stats.get(category_id, {})
        
        # 獲取類別的價格統計信息
        price_mean = category_stats.get("price_mean", 500.0)
        price_std = category_stats.get("price_std", 200.0)
        avg_days_to_sell = category_stats.get("avg_days_to_sell", 10.0)
        std_days_to_sell = category_stats.get("std_days_to_sell", 5.0)
        
        # 計算價格偏差（標準化）
        current_price = self.current_item["price"]
        price_deviation = (current_price - price_mean) / price_std if price_std > 0 else 0
        
        # 計算銷售概率（價格越低，銷售概率越高）
        # 使用 sigmoid 函數將價格偏差映射到 (0,1) 範圍
        sale_probability = 1 / (1 + np.exp(self.price_sensitivity * price_deviation))
        
        # 添加一些隨機性
        sale_probability = min(1.0, max(0.01, sale_probability + random.uniform(-0.1, 0.1) * self.market_volatility))
        
        # 計算預期銷售時間（價格越高，銷售時間越長）
        expected_days = avg_days_to_sell * (1 + self.time_sensitivity * price_deviation)
        expected_days = max(1.0, expected_days + random.uniform(-1.0, 1.0) * std_days_to_sell * self.market_volatility)
        
        return sale_probability, expected_days
    
    def _calculate_reward(self, original_price: float, new_price: float, 
                          sale_probability: float, expected_days: float) -> float:
        """
        計算獎勵，綜合考慮利潤和銷售時間
        
        Args:
            original_price (float): 原始價格
            new_price (float): 新價格
            sale_probability (float): 銷售概率
            expected_days (float): 預期銷售天數
            
        Returns:
            float: 獎勵值
        """
        # 估計成本（假設為原始價格的70%）
        estimated_cost = original_price * 0.7
        
        # 計算利潤
        profit = new_price - estimated_cost
        
        # 標準化利潤（相對於原始價格）
        normalized_profit = profit / original_price if original_price > 0 else 0
        
        # 計算時間懲罰（銷售時間越長，懲罰越大）
        # 使用類別平均銷售時間作為基準
        category_id = self.current_item.get("category_id", "9355")
        avg_days = self.category_stats.get(category_id, {}).get("avg_days_to_sell", 10.0)
        time_penalty = expected_days / avg_days if avg_days > 0 else expected_days / 10.0
        
        # 綜合獎勵 = 利潤獎勵 * 銷售概率 - 時間懲罰
        profit_reward = normalized_profit * sale_probability * self.reward_weights["profit"]
        time_reward = -time_penalty * self.reward_weights["time"]
        
        total_reward = profit_reward + time_reward
        
        return total_reward
    
    def _create_state(self) -> Dict:
        """
        創建當前環境狀態的表示
        
        Returns:
            Dict: 狀態表示
        """
        # 獲取商品特徵
        item_features = self._extract_item_features()
        
        # 獲取市場特徵
        market_features = self._extract_market_features()
        
        # 獲取時間特徵
        time_features = self._extract_time_features()
        
        # 合併所有特徵
        state = {
            **item_features,
            **market_features,
            **time_features,
            "step": self.episode_step / self.max_steps  # 標準化步數
        }
        
        return state
    
    def _extract_item_features(self) -> Dict:
        """
        提取商品特徵
        
        Returns:
            Dict: 商品特徵
        """
        item = self.current_item
        category_id = item.get("category_id", "9355")
        category_stats = self.category_stats.get(category_id, {})
        
        # 獲取類別的價格統計信息
        price_mean = category_stats.get("price_mean", 500.0)
        price_std = category_stats.get("price_std", 200.0)
        
        # 標準化價格
        normalized_price = (item["price"] - price_mean) / price_std if price_std > 0 else 0
        
        # 提取商品特徵
        features = {
            "normalized_price": normalized_price,
            "condition_score": self._condition_to_score(item.get("condition", "Used")),
        }
        
        # 添加類別特徵（one-hot編碼）- 所有20種類別
        # 原有類別
        features["is_laptop"] = 1.0 if category_id == "9355" else 0.0
        features["is_phone"] = 1.0 if category_id == "15032" else 0.0
        features["is_watch"] = 1.0 if category_id == "11450" else 0.0
        features["is_camera"] = 1.0 if category_id == "261007" else 0.0
        
        # 新增類別
        features["is_tablet"] = 1.0 if category_id == "20081" else 0.0
        features["is_game_console"] = 1.0 if category_id == "139971" else 0.0
        features["is_headphone"] = 1.0 if category_id == "175672" else 0.0
        features["is_computer_component"] = 1.0 if category_id == "11700" else 0.0
        features["is_tv_audio"] = 1.0 if category_id == "3676" else 0.0
        features["is_book"] = 1.0 if category_id == "293" else 0.0
        features["is_clothing"] = 1.0 if category_id == "15724" else 0.0
        features["is_toy"] = 1.0 if category_id == "11116" else 0.0
        features["is_instrument"] = 1.0 if category_id == "619" else 0.0
        features["is_sport"] = 1.0 if category_id == "888" else 0.0
        features["is_appliance"] = 1.0 if category_id == "26395" else 0.0
        features["is_furniture"] = 1.0 if category_id == "14308" else 0.0
        features["is_art"] = 1.0 if category_id == "550" else 0.0
        features["is_jewelry"] = 1.0 if category_id == "2984" else 0.0
        features["is_tool"] = 1.0 if category_id == "1249" else 0.0
        features["is_bicycle"] = 1.0 if category_id == "220" else 0.0
        
        return features
    
    def _extract_market_features(self) -> Dict:
        """
        提取市場特徵
        
        Returns:
            Dict: 市場特徵
        """
        category_id = self.current_item.get("category_id", "9355")
        category_stats = self.category_stats.get(category_id, {})
        
        # 市場特徵
        features = {
            "market_volatility": self.market_volatility,
            "avg_days_to_sell": category_stats.get("avg_days_to_sell", 10.0) / 30.0,  # 標準化到 [0,1]
            "price_std": category_stats.get("price_std", 200.0) / 1000.0  # 標準化到 [0,1]
        }
        
        return features
    
    def _extract_time_features(self) -> Dict:
        """
        提取時間特徵
        
        Returns:
            Dict: 時間特徵
        """
        # 獲取當前時間
        now = datetime.now()
        
        # 提取時間特徵
        features = {
            "day_of_week": now.weekday() / 6.0,  # 標準化到 [0,1]
            "month": (now.month - 1) / 11.0,  # 標準化到 [0,1]
            "is_weekend": 1.0 if now.weekday() >= 5 else 0.0
        }
        
        return features
    
    def _condition_to_score(self, condition: str) -> float:
        """
        將商品狀況轉換為數值分數
        
        Args:
            condition (str): 商品狀況描述
            
        Returns:
            float: 狀況分數 [0,1]
        """
        condition = condition.lower()
        
        if "new" in condition:
            return 1.0
        elif "like new" in condition:
            return 0.9
        elif "very good" in condition:
            return 0.8
        elif "good" in condition:
            return 0.6
        elif "acceptable" in condition:
            return 0.4
        elif "for parts" in condition or "not working" in condition:
            return 0.1
        else:
            return 0.5  # 默認中等狀況
    
    def _generate_random_item(self) -> Dict:
        """
        生成隨機商品數據用於測試
        
        Returns:
            Dict: 隨機商品數據
        """
        # 隨機選擇類別 (所有20種類別)
        categories = [
            # 原有類別
            "9355", "15032", "11450", "261007",  # 筆電、手機、手錶和數位相機
            # 新增類別
            "20081", "139971", "175672", "11700", "3676", "293", 
            "15724", "11116", "619", "888", "26395", "14308", 
            "550", "2984", "1249", "220"
        ]
        category_id = random.choice(categories)
        
        # 根據類別設定價格範圍
        if category_id == "9355":  # 筆電
            price_range = (300, 2000)
            title_prefixes = ["Laptop", "Notebook", "MacBook", "ThinkPad", "Dell XPS"]
        elif category_id == "15032":  # 手機
            price_range = (200, 1200)
            title_prefixes = ["iPhone", "Samsung Galaxy", "Google Pixel", "OnePlus"]
        elif category_id == "11450":  # 手錶
            price_range = (50, 1500)
            title_prefixes = ["Rolex", "Omega", "Seiko", "Casio", "Apple Watch", "Garmin"]
        elif category_id == "261007":  # 數位相機
            price_range = (150, 1800)
            title_prefixes = ["Canon", "Nikon", "Sony", "Fujifilm", "Panasonic", "Olympus"]
        elif category_id == "20081":  # 平板與電子閱讀器
            price_range = (100, 1200)
            title_prefixes = ["iPad", "Samsung Tab", "Kindle", "Kobo", "Huawei MatePad"]
        elif category_id == "139971":  # 遊戲主機
            price_range = (100, 800)
            title_prefixes = ["PlayStation", "Xbox", "Nintendo Switch", "Steam Deck", "Sega"]
        elif category_id == "175672":  # 耳機
            price_range = (20, 500)
            title_prefixes = ["Sony", "Bose", "Sennheiser", "AirPods", "Beats", "JBL"]
        elif category_id == "11700":  # 電腦零組件
            price_range = (30, 800)
            title_prefixes = ["Intel", "AMD", "NVIDIA", "Corsair", "Kingston", "Western Digital"]
        elif category_id == "3676":  # 電視、影音設備
            price_range = (100, 2000)
            title_prefixes = ["Samsung TV", "LG TV", "Sony TV", "TCL", "Vizio", "Bose Speaker"]
        elif category_id == "293":  # 書籍與雜誌
            price_range = (5, 150)
            title_prefixes = ["Book", "Novel", "Textbook", "Magazine", "Comic", "Encyclopedia"]
        elif category_id == "15724":  # 服飾與配件
            price_range = (10, 500)
            title_prefixes = ["Nike", "Adidas", "Gucci", "H&M", "Zara", "Uniqlo"]
        elif category_id == "11116":  # 玩具與遊戲
            price_range = (10, 200)
            title_prefixes = ["LEGO", "Barbie", "Hot Wheels", "Nerf", "Monopoly", "Puzzle"]
        elif category_id == "619":  # 樂器
            price_range = (50, 2000)
            title_prefixes = ["Guitar", "Piano", "Violin", "Drum", "Saxophone", "Flute"]
        elif category_id == "888":  # 運動用品
            price_range = (20, 800)
            title_prefixes = ["Tennis Racket", "Golf Club", "Basketball", "Yoga Mat", "Dumbbell", "Treadmill"]
        elif category_id == "26395":  # 家用電器
            price_range = (50, 1000)
            title_prefixes = ["Refrigerator", "Washing Machine", "Microwave", "Vacuum", "Blender", "Coffee Maker"]
        elif category_id == "14308":  # 家具
            price_range = (50, 1500)
            title_prefixes = ["Sofa", "Bed", "Table", "Chair", "Desk", "Bookshelf"]
        elif category_id == "550":  # 藝術品與收藏品
            price_range = (20, 2000)
            title_prefixes = ["Painting", "Sculpture", "Antique", "Collectible", "Poster", "Vintage"]
        elif category_id == "2984":  # 珠寶
            price_range = (30, 3000)
            title_prefixes = ["Ring", "Necklace", "Bracelet", "Earrings", "Watch", "Pendant"]
        elif category_id == "1249":  # 工具與工作坊設備
            price_range = (30, 800)
            title_prefixes = ["Drill", "Saw", "Hammer", "Screwdriver", "Wrench", "Toolbox"]
        elif category_id == "220":  # 自行車
            price_range = (50, 2500)
            title_prefixes = ["Mountain Bike", "Road Bike", "BMX", "Electric Bike", "Folding Bike", "Hybrid Bike"]
        
        # 隨機選擇狀況
        conditions = ["New", "Like New", "Very Good", "Good", "Acceptable", "For parts or not working"]
        condition = random.choice(conditions)
        
        # 生成隨機價格
        price = random.uniform(price_range[0], price_range[1])
        
        # 生成標題
        prefix = random.choice(title_prefixes)
        title = f"{prefix} {random.choice(['Pro', 'Air', 'Ultra', 'Max', 'Plus', 'Mini'])} {random.randint(5, 15)}"
        
        # 創建商品數據
        item = {
            "itemId": f"mock_{int(time.time())}_{random.randint(1000, 9999)}",
            "title": title,
            "condition": condition,
            "price": price,
            "category_id": category_id,
            "listing_date": datetime.now().isoformat(),
            "collection_date": datetime.now().isoformat()
        }
        
        return item
    
    def get_action_space_size(self) -> int:
        """
        獲取動作空間大小
        
        Returns:
            int: 動作空間大小
        """
        return self.action_space_size
    
    def get_state_space_size(self) -> int:
        """
        獲取狀態空間大小（特徵數量）
        
        Returns:
            int: 狀態空間大小
        """
        # 創建一個示例狀態來計算特徵數量
        example_state = self._create_state()
        return len(example_state)
    
    def get_state_feature_names(self) -> List[str]:
        """
        獲取狀態特徵名稱列表
        
        Returns:
            List[str]: 特徵名稱列表
        """
        example_state = self._create_state()
        return list(example_state.keys())
    
    def get_action_meanings(self) -> List[str]:
        """
        獲取動作的含義描述
        
        Returns:
            List[str]: 動作含義列表
        """
        meanings = []
        for i in range(self.action_space_size):
            adjustment = self._action_to_adjustment(i)
            percentage = adjustment * 100
            meanings.append(f"調整價格 {percentage:+.1f}%")
        return meanings