import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
from typing import Dict, List, Any

class FeatureExtractor:
    """
    負責特徵工程的類別，提供特徵轉換與萃取等功能。
    """
    def __init__(self, config=None):
        self.config = config
        self.features_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "features")
        os.makedirs(self.features_dir, exist_ok=True)
        
    def extract_features(self, df):
        """
        從輸入的 DataFrame 萃取特徵。
        """
        # 範例：新增欄位作為特徵
        df = df.copy()
        if 'price' in df.columns:
            df['log_price'] = df['price'].apply(lambda x: np.log1p(x) if x > 0 else 0)
        return df

    def transform(self, df):
        """
        對資料進行轉換（如標準化、正規化等）。
        """
        # 範例：將所有數值欄位標準化
        df = df.copy()
        num_cols = df.select_dtypes(include=['float64', 'int64']).columns
        for col in num_cols:
            mean = df[col].mean()
            std = df[col].std()
            if std > 0:
                df[col] = (df[col] - mean) / std
        return df
        
    def extract_all_features(self, preprocessed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理所有類別的特徵萃取，並返回統計資訊。
        
        Args:
            preprocessed_data: 預處理後的資料字典，包含各類別的資料
            
        Returns:
            Dict: 包含特徵萃取結果與統計資訊的字典
        """
        results = {
            "features_extracted": 0,
            "categories_processed": 0,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "category_stats": {}
        }
        
        # 處理每個類別的資料
        for category_id, category_data in preprocessed_data.items():
            try:
                # 取得類別資料
                active_items = category_data.get("active_items", [])
                sold_items = category_data.get("sold_items", [])
                
                # 轉換為 DataFrame
                active_df = pd.DataFrame(active_items) if active_items else pd.DataFrame()
                sold_df = pd.DataFrame(sold_items) if sold_items else pd.DataFrame()
                
                # 萃取特徵
                if not active_df.empty:
                    active_features_df = self.extract_features(active_df)
                    active_features_df = self.transform(active_features_df)
                    
                    # 儲存特徵
                    category_dir = os.path.join(self.features_dir, f"category_{category_id}")
                    os.makedirs(category_dir, exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    features_file = os.path.join(category_dir, f"active_features_{timestamp}.csv")
                    active_features_df.to_csv(features_file, index=False)
                    
                    results["features_extracted"] += len(active_features_df)
                
                # 處理已售出商品的特徵
                if not sold_df.empty:
                    sold_features_df = self.extract_features(sold_df)
                    sold_features_df = self.transform(sold_features_df)
                    
                    # 儲存特徵
                    category_dir = os.path.join(self.features_dir, f"category_{category_id}")
                    os.makedirs(category_dir, exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    features_file = os.path.join(category_dir, f"sold_features_{timestamp}.csv")
                    sold_features_df.to_csv(features_file, index=False)
                    
                    results["features_extracted"] += len(sold_features_df)
                
                # 計算並儲存類別統計資訊
                category_stats = self._calculate_category_stats(active_df, sold_df)
                results["category_stats"][category_id] = category_stats
                
                results["categories_processed"] += 1
                
            except Exception as e:
                print(f"Error processing features for category {category_id}: {str(e)}")
        
        # 記錄結束時間
        results["end_time"] = datetime.now().isoformat()
        
        # 將 NumPy 類型轉換為 Python 原生類型，以便 JSON 序列化
        def convert_numpy_types(obj):
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
                return int(obj)
            elif isinstance(obj, (np.float64, np.float32, np.float16)):
                return float(obj)
            else:
                return obj
                
        # 儲存特徵萃取結果
        stats_file = os.path.join(self.features_dir, f"feature_extraction_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(stats_file, 'w') as f:
            json.dump(convert_numpy_types(results), f, indent=4)
        
        # 確保返回值也經過 NumPy 類型轉換
        return convert_numpy_types(results)
    
    def _calculate_category_stats(self, active_df: pd.DataFrame, sold_df: pd.DataFrame) -> Dict[str, Any]:
        """
        計算類別的統計資訊
        
        Args:
            active_df: 活躍商品的 DataFrame
            sold_df: 已售出商品的 DataFrame
            
        Returns:
            Dict: 統計資訊字典
        """
        stats = {}
        
        # 計算價格統計資訊
        if not active_df.empty and 'price' in active_df.columns:
            stats["active_price_mean"] = active_df["price"].mean()
            stats["active_price_std"] = active_df["price"].std()
            stats["active_price_min"] = active_df["price"].min()
            stats["active_price_max"] = active_df["price"].max()
            stats["active_count"] = len(active_df)
        
        if not sold_df.empty and 'price' in sold_df.columns:
            stats["sold_price_mean"] = sold_df["price"].mean()
            stats["sold_price_std"] = sold_df["price"].std()
            stats["sold_price_min"] = sold_df["price"].min()
            stats["sold_price_max"] = sold_df["price"].max()
            stats["sold_count"] = len(sold_df)
        
        # 如果兩者都有資料，計算價格差異
        if not active_df.empty and not sold_df.empty and 'price' in active_df.columns and 'price' in sold_df.columns:
            stats["price_diff_mean"] = active_df["price"].mean() - sold_df["price"].mean()
            stats["price_ratio"] = active_df["price"].mean() / sold_df["price"].mean() if sold_df["price"].mean() > 0 else 0
        
        return stats