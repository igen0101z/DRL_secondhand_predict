
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import hashlib

def generate_item_id(item_data):
    """
    Generate a unique ID for an item based on its properties
    """
    # Create a string with important item attributes
    item_str = f"{item_data.get('title', '')}-{item_data.get('condition', '')}-{item_data.get('brand', '')}"
    # Generate a hash
    return hashlib.md5(item_str.encode('utf-8')).hexdigest()

def timestamp_to_features(timestamp):
    """
    Convert a timestamp to temporal features
    """
    dt = datetime.fromtimestamp(timestamp)
    return {
        'hour': dt.hour / 24.0,  # Normalize to [0,1]
        'day_of_week': dt.weekday() / 6.0,  # Normalize to [0,1]
        'day_of_month': (dt.day - 1) / 30.0,  # Normalize to [0,1]
        'month': (dt.month - 1) / 11.0,  # Normalize to [0,1]
        'is_weekend': 1.0 if dt.weekday() >= 5 else 0.0
    }

def normalize_price(price, category_stats):
    """
    Normalize price based on category statistics
    """
    mean = category_stats.get('price_mean', price)
    std = category_stats.get('price_std', 1.0)
    if std == 0:
        std = 1.0
    return (price - mean) / std

def convert_to_timeseries_format(data, time_column='timestamp', value_column='price'):
    """
    Convert data to time series format suitable for model training
    """
    df = pd.DataFrame(data)
    df = df.sort_values(by=time_column)
    return df

def create_sliding_windows(data, window_size=30, step_size=1):
    """
    Create sliding windows from time series data
    """
    windows = []
    for i in range(0, len(data) - window_size + 1, step_size):
        windows.append(data[i:i + window_size])
    return windows

def save_json(data, file_path):
    """
    Save data as JSON
    """
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def load_json(file_path):
    """
    Load data from JSON
    """
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r') as f:
        return json.load(f)

def get_category_folder(category_id):
    """
    Get the folder path for a specific category
    """
    return os.path.join('/data/chats/p6wyr/workspace/data/raw', f'category_{category_id}')

def save_items_to_csv(items, file_path):
    """
    Save a list of items to CSV
    """
    df = pd.DataFrame(items)
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    df.to_csv(file_path, index=False)

def save_item_history(item_id, history_data, category_id=None):
    """
    Save item price history
    """
    folder = '/data/chats/p6wyr/workspace/data/raw/price_history'
    if category_id:
        folder = os.path.join(folder, f'category_{category_id}')
    
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f'{item_id}_history.json')
    
    save_json(history_data, file_path)
