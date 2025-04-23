import os
import json
import pandas as pd
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple
import time
import random
from tqdm import tqdm

from src.api.ebay_api_client import EbayAPIClient
from src.utils.logger import Logger

# Helper functions (simplified versions) to avoid extra imports
def generate_item_id(item_data):
    """Generate a unique ID for an item based on its properties"""
    import hashlib
    item_str = f"{item_data.get('title', '')}-{item_data.get('condition', '')}"
    return hashlib.md5(item_str.encode('utf-8')).hexdigest()

def get_category_folder(category_id):
    """Get the folder path for a specific category"""
    return os.path.join('/data/chats/p6wyr/workspace/data/raw', f'category_{category_id}')

def save_json(data, file_path):
    """Save data as JSON"""
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def save_items_to_csv(items, file_path):
    """Save a list of items to CSV"""
    df = pd.DataFrame(items)
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    df.to_csv(file_path, index=False)

class DataCollector:
    """
    Data collection module for retrieving second-hand item data from eBay
    """
    def __init__(self, config_path: str = "/data/chats/p6wyr/workspace/config/config.json"):
        """
        Initialize the data collector
        
        Args:
            config_path (str): Path to configuration file
        """
        self.logger = Logger().get_logger()
        self.logger.info("Initializing DataCollector module")
        
        # Load configuration
        self.config_path = config_path
        self._load_config()
        
        # Initialize eBay API client
        self.ebay_client = EbayAPIClient(config_path=config_path)
        
        # Set up data directories
        self.raw_data_dir = "/data/chats/p6wyr/workspace/data/raw"
        os.makedirs(self.raw_data_dir, exist_ok=True)
        
        # Track collection statistics
        self.stats = {
            "items_collected": 0,
            "categories_processed": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None
        }
    
    def _load_config(self) -> None:
        """
        Load configuration from file
        """
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            
            # Extract relevant configuration
            self.categories = self.config.get("data", {}).get("categories", [])
            self.sample_size_per_category = self.config.get("data", {}).get("sample_size_per_category", 100)
            self.history_window = self.config.get("data", {}).get("history_window", 30)
            self.update_frequency = self.config.get("data", {}).get("update_frequency", 24)
            
            self.logger.info(f"Configuration loaded: {len(self.categories)} categories")
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            # Use default values
            self.categories = [
                {"id": "9355", "name": "Laptops & Netbooks"},
                {"id": "15032", "name": "Cell Phones & Smartphones"}
            ]
            self.sample_size_per_category = 100
            self.history_window = 30
            self.update_frequency = 24
    
    async def collect_data(self) -> Dict:
        """
        Collect data for all configured categories
        
        Returns:
            Dict: Collection statistics
        """
        self.stats["start_time"] = datetime.now()
        self.logger.info(f"Starting data collection for {len(self.categories)} categories")
        
        for category in self.categories:
            try:
                await self.collect_category_data(category)
                self.stats["categories_processed"] += 1
            except Exception as e:
                self.logger.error(f"Error collecting data for category {category['name']}: {str(e)}")
                self.stats["errors"] += 1
        
        self.stats["end_time"] = datetime.now()
        collection_time = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        self.logger.info(f"Data collection completed: {self.stats['items_collected']} items collected "
                         f"from {self.stats['categories_processed']} categories in {collection_time:.2f} seconds")
        
        # Save collection stats
        stats_file = os.path.join(self.raw_data_dir, f"collection_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        save_json(self.stats, stats_file)
        
        return self.stats
    
    async def collect_category_data(self, category: Dict) -> None:
        """
        Collect data for a specific category
        
        Args:
            category (Dict): Category information with id and name
        """
        category_id = category["id"]
        category_name = category["name"]
        self.logger.info(f"Collecting data for category: {category_name} (ID: {category_id})")
        
        # Create category folder
        category_folder = get_category_folder(category_id)
        os.makedirs(category_folder, exist_ok=True)
        
        # Define search terms for this category
        search_terms = self._get_search_terms_for_category(category)
        
        # Collect active listings
        active_items = await self._collect_active_items(category, search_terms)
        
        # Collect sold items for price history
        sold_items = await self._collect_sold_items(category, search_terms)
        
        # Save category data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        active_file = os.path.join(category_folder, f"active_items_{timestamp}.csv")
        sold_file = os.path.join(category_folder, f"sold_items_{timestamp}.csv")
        
        save_items_to_csv(active_items, active_file)
        save_items_to_csv(sold_items, sold_file)
        
        # Create a metadata file to track the collection
        metadata = {
            "category_id": category_id,
            "category_name": category_name,
            "timestamp": datetime.now().isoformat(),
            "active_items_count": len(active_items),
            "sold_items_count": len(sold_items),
            "active_items_file": active_file,
            "sold_items_file": sold_file
        }
        
        metadata_file = os.path.join(category_folder, f"metadata_{timestamp}.json")
        save_json(metadata, metadata_file)
        
        # Update stats
        self.stats["items_collected"] += len(active_items) + len(sold_items)
    
    def _get_search_terms_for_category(self, category: Dict) -> List[str]:
        """Get appropriate search terms for a category"""
        category_name = category["name"]
        base_terms = [category_name, f"used {category_name}"]
        
        # Add category-specific terms
        if category["id"] == "9355":  # Laptops
            return base_terms + ["refurbished laptop", "macbook", "thinkpad"]
        elif category["id"] == "15032":  # Cell Phones
            return base_terms + ["used iphone", "used samsung galaxy"]
        else:
            return base_terms
    
    async def _collect_active_items(self, category: Dict, search_terms: List[str]) -> List[Dict]:
        """Collect active listings for a category using multiple search terms"""
        category_id = category["id"]
        collected_items = []
        
        for search_term in search_terms:
            try:
                # Make the API request
                response = await self.ebay_client.search_items(
                    keywords=search_term,
                    category_id=category_id,
                    limit=min(50, self.sample_size_per_category // len(search_terms))
                )
                
                if not response.success:
                    continue
                
                # Extract items from response
                items = response.data.get("itemSummaries", [])
                
                # Process each item
                for item in items:
                    try:
                        # Generate a consistent item ID
                        item_id = item.get("itemId") or generate_item_id(item)
                        
                        # Get more detailed information about the item
                        details_response = await self.ebay_client.get_item_details(item_id, use_cache=True)
                        
                        if details_response.success:
                            item_details = details_response.data
                            
                            # Process and add the item
                            processed_item = self._process_item_data(item, item_details)
                            collected_items.append(processed_item)
                            
                            # Small delay to avoid overwhelming the API
                            await asyncio.sleep(0.1)
                    except Exception as e:
                        self.logger.error(f"Error processing item: {str(e)}")
                
                # Add a delay between search terms
                await asyncio.sleep(1.0)
                
            except Exception as e:
                self.logger.error(f"Error collecting items: {str(e)}")
        
        # Deduplicate items
        unique_items = []
        seen_ids = set()
        for item in collected_items:
            if item["itemId"] not in seen_ids:
                unique_items.append(item)
                seen_ids.add(item["itemId"])
        
        return unique_items
    
    async def _collect_sold_items(self, category: Dict, search_terms: List[str]) -> List[Dict]:
        """Collect sold items data for price history"""
        category_id = category["id"]
        sold_items = []
        
        for search_term in search_terms[:2]:
            try:
                # Make the API request for sold items
                response = await self.ebay_client.get_sold_items(
                    keywords=search_term,
                    category_id=category_id,
                    days_back=self.history_window,
                    limit=min(50, self.sample_size_per_category // len(search_terms))
                )
                
                if not response.success:
                    continue
                
                # The structure of the sold items response is different
                items = []
                try:
                    search_result = response.data.get("findCompletedItemsResponse", [{}])[0]
                    result_items = search_result.get("searchResult", [{}])[0].get("item", [])
                    items.extend(result_items)
                except (KeyError, IndexError) as e:
                    self.logger.warning(f"Error parsing sold items response: {str(e)}")
                
                # Process sold items
                for item in items:
                    try:
                        processed_item = self._process_sold_item_data(item)
                        sold_items.append(processed_item)
                    except Exception as e:
                        self.logger.error(f"Error processing sold item: {str(e)}")
                
                # Add a delay between search terms
                await asyncio.sleep(1.0)
                
            except Exception as e:
                self.logger.error(f"Error collecting sold items: {str(e)}")
        
        # Deduplicate sold items
        unique_sold_items = []
        seen_ids = set()
        for item in sold_items:
            if item["itemId"] not in seen_ids:
                unique_sold_items.append(item)
                seen_ids.add(item["itemId"])
        
        return unique_sold_items
    
    def _process_item_data(self, item_summary: Dict, item_details: Dict) -> Dict:
        """Process and normalize item data from API responses"""
        # Basic processing - simplified for brevity
        return {
            "itemId": item_summary.get("itemId", ""),
            "title": item_summary.get("title", ""),
            "condition": item_summary.get("condition", ""),
            "price": self._extract_price(item_summary.get("price", {})),
            "currency": self._extract_currency(item_summary.get("price", {})),
            "category_id": item_details.get("categoryId", ""),
            "listing_date": item_summary.get("itemCreationDate", ""),
            "end_date": item_summary.get("itemEndDate", ""),
            "collection_date": datetime.now().isoformat(),
            "url": item_summary.get("itemWebUrl", "")
        }
    
    def _process_sold_item_data(self, item: Dict) -> Dict:
        """Process sold item data which has a different structure"""
        listing_info = item.get("listingInfo", {})
        selling_status = item.get("sellingStatus", [{}])[0]
        
        return {
            "itemId": item.get("itemId", ""),
            "title": item.get("title", [""])[0] if isinstance(item.get("title"), list) else item.get("title", ""),
            "condition": item.get("condition", {}).get("conditionDisplayName", ""),
            "price": float(selling_status.get("currentPrice", [{}])[0].get("__value__", 0)),
            "currency": selling_status.get("currentPrice", [{}])[0].get("@currencyId", "USD"),
            "category_id": item.get("primaryCategory", [{}])[0].get("categoryId", ""),
            "listing_date": listing_info.get("startTime", ""),
            "end_date": listing_info.get("endTime", ""),
            "collection_date": datetime.now().isoformat(),
            "is_sold": True,
            "sold_date": listing_info.get("endTime", "")
        }
    
    def _extract_price(self, price_data: Dict) -> float:
        """Extract price value from price object"""
        if isinstance(price_data, dict):
            value = price_data.get("value")
            if value is not None:
                try:
                    return float(value)
                except (ValueError, TypeError):
                    pass
        return 0.0
    
    def _extract_currency(self, price_data: Dict) -> str:
        """Extract currency from price object"""
        if isinstance(price_data, dict):
            return price_data.get("currency", "USD")
        return "USD"
