
import time
import json
import os
import requests
from functools import wraps

# Load config
CONFIG_PATH = "/data/chats/p6wyr/workspace/config/config.json"

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}

def rate_limiter(max_calls, time_frame):
    """
    Decorator to implement rate limiting for API calls
    
    Args:
        max_calls (int): Maximum number of calls allowed
        time_frame (int): Time frame in seconds
    """
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            # Remove calls older than the time frame
            while calls and current_time - calls[0] > time_frame:
                calls.pop(0)
            
            # If we've reached the maximum calls, wait
            if len(calls) >= max_calls:
                sleep_time = calls[0] + time_frame - current_time
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    current_time = time.time()
                calls.pop(0)
            
            # Make the call and record the time
            calls.append(current_time)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def handle_api_errors(func):
    """
    Decorator to handle common API errors
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_count = 0
        retry_delay = 1  # seconds
        
        while retry_count < max_retries:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                retry_count += 1
                if retry_count >= max_retries:
                    from utils.logger import Logger
                    logger = Logger().get_logger()
                    logger.error(f"API request failed after {max_retries} attempts: {str(e)}")
                    raise
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
    
    return wrapper

class APIResponse:
    """
    Standardized API response object
    """
    def __init__(self, success=True, data=None, error=None, status_code=200):
        self.success = success
        self.data = data
        self.error = error
        self.status_code = status_code
    
    def to_dict(self):
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "status_code": self.status_code
        }
    
    def __str__(self):
        return json.dumps(self.to_dict())
