import os
import json
from typing import Dict, Any, Optional

class DataPreprocessor:
    """
    負責資料預處理的類別，提供資料清理與轉換等功能。
    """
    def __init__(self, config_path=None):
        self.config_path = config_path
        self.preprocessed_data = {}
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "preprocessed")
        os.makedirs(self.data_dir, exist_ok=True)

    def process_all_data(self):
        """
        執行所有資料的預處理流程，這裡僅為範例回傳一個簡單結果。
        同時儲存預處理後的資料，以便後續特徵萃取使用。
        """
        # 實際實作時應該處理資料並回傳統計資訊
        # 這裡建立一個簡單的預處理資料結構作為範例
        self.preprocessed_data = {
            "category_1": {
                "active_items": [
                    {"id": "item1", "price": 100, "condition": "new"},
                    {"id": "item2", "price": 150, "condition": "used"}
                ],
                "sold_items": [
                    {"id": "item3", "price": 90, "condition": "used"},
                    {"id": "item4", "price": 120, "condition": "new"}
                ]
            },
            "category_2": {
                "active_items": [
                    {"id": "item5", "price": 200, "condition": "new"}
                ],
                "sold_items": [
                    {"id": "item6", "price": 180, "condition": "used"}
                ]
            }
        }
        
        # 儲存預處理後的資料
        self._save_preprocessed_data()
        
        return {"status": "success", "message": "Data preprocessing completed", "categories": len(self.preprocessed_data)}
    
    def get_preprocessed_data(self) -> Dict[str, Any]:
        """
        獲取預處理後的資料。如果資料尚未處理，則嘗試從檔案載入。
        
        Returns:
            Dict: 預處理後的資料字典
        """
        if not self.preprocessed_data:
            self._load_preprocessed_data()
            
        return self.preprocessed_data
    
    def _save_preprocessed_data(self) -> None:
        """
        儲存預處理後的資料到檔案
        """
        try:
            file_path = os.path.join(self.data_dir, "preprocessed_data.json")
            with open(file_path, 'w') as f:
                json.dump(self.preprocessed_data, f, indent=4)
        except Exception as e:
            print(f"Error saving preprocessed data: {str(e)}")
    
    def _load_preprocessed_data(self) -> None:
        """
        從檔案載入預處理後的資料
        """
        try:
            file_path = os.path.join(self.data_dir, "preprocessed_data.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    self.preprocessed_data = json.load(f)
        except Exception as e:
            print(f"Error loading preprocessed data: {str(e)}")
            self.preprocessed_data = {}