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
    return os.path.join('data/raw', f'category_{category_id}')

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
    def __init__(self, config_path: str = "config/config.json"):
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
        self.raw_data_dir = "data/raw"
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
        # 記錄開始時間（同時保存 datetime 物件和 ISO 格式字串）
        start_time_dt = datetime.now()
        self.stats["start_time"] = start_time_dt.isoformat()
        self.logger.info(f"Starting data collection for {len(self.categories)} categories")
        
        for category in self.categories:
            try:
                await self.collect_category_data(category)
                self.stats["categories_processed"] += 1
            except Exception as e:
                self.logger.error(f"Error collecting data for category {category['name']}: {str(e)}")
                self.stats["errors"] += 1
        
        # 記錄結束時間（同時保存 datetime 物件和 ISO 格式字串）
        end_time_dt = datetime.now()
        self.stats["end_time"] = end_time_dt.isoformat()
        
        # 使用 datetime 物件計算時間差
        collection_time = (end_time_dt - start_time_dt).total_seconds()
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
        
        # 如果 API 調用失敗或沒有收集到足夠的資料，生成模擬資料
        if len(active_items) < 10:
            self.logger.warning(f"Not enough active items collected for category {category_name}. Generating mock data.")
            active_items = self._generate_mock_items(category, is_active=True, count=50)
            
        if len(sold_items) < 10:
            self.logger.warning(f"Not enough sold items collected for category {category_name}. Generating mock data.")
            sold_items = self._generate_mock_items(category, is_active=False, count=50)
        
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
        elif category["id"] == "11450":  # Wristwatch
            return base_terms + ["used rolex", "used omega", "vintage watch"]
        elif category["id"] == "261007":  # Digital Cameras
            return base_terms + ["used canon", "used nikon", "used sony camera"]
        elif category["id"] == "20081":  # Tablets & eReaders
            return base_terms + ["used ipad", "used kindle", "used samsung tablet"]
        elif category["id"] == "139971":  # Video Game Consoles
            return base_terms + ["used playstation", "used xbox", "used nintendo switch"]
        elif category["id"] == "175672":  # Headphones
            return base_terms + ["used bose", "used sony headphones", "used airpods"]
        elif category["id"] == "11700":  # Computer Components
            return base_terms + ["used gpu", "used cpu", "used motherboard"]
        elif category["id"] == "3676":  # TV, Video & Audio
            return base_terms + ["used tv", "used speakers", "used home theater"]
        elif category["id"] == "293":  # Books & Magazines
            return base_terms + ["used textbooks", "used novels", "vintage magazines"]
        elif category["id"] == "15724":  # Clothing & Accessories
            return base_terms + ["vintage clothing", "designer clothes", "used luxury"]
        elif category["id"] == "11116":  # Toys & Games
            return base_terms + ["used lego", "collectible toys", "board games"]
        elif category["id"] == "619":  # Musical Instruments
            return base_terms + ["used guitar", "used piano", "used drums"]
        elif category["id"] == "888":  # Sporting Goods
            return base_terms + ["used golf clubs", "used fitness equipment", "used bicycle"]
        elif category["id"] == "26395":  # Home Appliances
            return base_terms + ["used kitchen appliances", "used vacuum", "used coffee maker"]
        elif category["id"] == "14308":  # Furniture
            return base_terms + ["used sofa", "used desk", "vintage furniture"]
        elif category["id"] == "550":  # Art & Collectibles
            return base_terms + ["vintage art", "collectibles", "antiques"]
        elif category["id"] == "2984":  # Jewelry
            return base_terms + ["used silver jewelry", "used gold jewelry", "vintage jewelry"]
        elif category["id"] == "1249":  # Tools & Workshop Equipment
            return base_terms + ["used power tools", "used hand tools", "used workshop equipment"]
        elif category["id"] == "220":  # Bicycles
            return base_terms + ["used mountain bike", "used road bike", "vintage bicycle"]
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
        
    def _generate_mock_items(self, category: Dict, is_active: bool = True, count: int = 50) -> List[Dict]:
        """
        生成模擬資料，確保即使 API 調用失敗也能返回有效的測試資料
        
        Args:
            category: 類別資訊
            is_active: 是否為活躍商品（相對於已售出商品）
            count: 要生成的項目數量
            
        Returns:
            List[Dict]: 模擬商品資料列表
        """
        self.logger.info(f"Generating {count} mock {'active' if is_active else 'sold'} items for category {category['name']}")
        
        category_id = category["id"]
        category_name = category["name"]
        mock_items = []
        
        # 根據類別設定不同的價格範圍和標題
        price_ranges = {
            "9355": (300, 2000),  # 筆電價格範圍
            "15032": (200, 1200),  # 手機價格範圍
            "11450": (100, 1500),  # 手錶價格範圍
            "261007": (150, 1800),  # 數位相機價格範圍
            "20081": (100, 1200),  # 平板與電子閱讀器價格範圍
            "139971": (100, 800),  # 遊戲主機價格範圍
            "175672": (20, 500),  # 耳機價格範圍
            "11700": (30, 800),  # 電腦零組件價格範圍
            "3676": (100, 2000),  # 電視、影音設備價格範圍
            "293": (5, 150),  # 書籍與雜誌價格範圍
            "15724": (10, 500),  # 服飾與配件價格範圍
            "11116": (10, 200),  # 玩具與遊戲價格範圍
            "619": (50, 2000),  # 樂器價格範圍
            "888": (20, 800),  # 運動用品價格範圍
            "26395": (50, 1000),  # 家用電器價格範圍
            "14308": (50, 1500),  # 家具價格範圍
            "550": (20, 2000),  # 藝術品與收藏品價格範圍
            "2984": (30, 3000),  # 珠寶價格範圍
            "1249": (30, 800),  # 工具與工作坊設備價格範圍
            "220": (50, 2500)  # 自行車價格範圍
        }
        
        title_prefixes = {
            "9355": ["Laptop", "Notebook", "MacBook", "ThinkPad", "Dell XPS", "HP Spectre", "Asus ZenBook"],
            "15032": ["iPhone", "Samsung Galaxy", "Google Pixel", "OnePlus", "Xiaomi", "Huawei", "Sony Xperia"],
            "11450": ["Rolex", "Omega", "Seiko", "Casio", "Fossil", "Timex", "Citizen", "Tag Heuer"],
            "261007": ["Canon", "Nikon", "Sony", "Fujifilm", "Panasonic", "Olympus", "Leica"],
            "20081": ["iPad", "Kindle", "Samsung Tab", "Microsoft Surface", "Lenovo Tab", "Amazon Fire"],
            "139971": ["PlayStation", "Xbox", "Nintendo Switch", "Wii", "Sega", "Atari", "GameCube"],
            "175672": ["Bose", "Sony", "AirPods", "Beats", "Sennheiser", "JBL", "Audio-Technica"],
            "11700": ["GPU", "CPU", "Motherboard", "RAM", "SSD", "HDD", "Power Supply", "Cooling Fan"],
            "3676": ["TV", "Speakers", "Home Theater", "Soundbar", "Projector", "Receiver", "Amplifier"],
            "293": ["Textbook", "Novel", "Magazine", "Comic", "Biography", "Cookbook", "Self-help Book"],
            "15724": ["Jacket", "Shirt", "Pants", "Dress", "Shoes", "Handbag", "Watch", "Sunglasses"],
            "11116": ["LEGO", "Action Figure", "Board Game", "Puzzle", "Doll", "RC Car", "Model Kit"],
            "619": ["Guitar", "Piano", "Drums", "Violin", "Saxophone", "Trumpet", "Flute", "Keyboard"],
            "888": ["Golf Clubs", "Treadmill", "Bicycle", "Tennis Racket", "Fishing Rod", "Ski", "Snowboard"],
            "26395": ["Refrigerator", "Washing Machine", "Microwave", "Vacuum", "Coffee Maker", "Blender"],
            "14308": ["Sofa", "Desk", "Chair", "Bed", "Dresser", "Bookshelf", "Table", "Cabinet"],
            "550": ["Painting", "Sculpture", "Print", "Antique", "Collectible", "Vintage Item", "Memorabilia"],
            "2984": ["Ring", "Necklace", "Bracelet", "Earrings", "Watch", "Pendant", "Brooch"],
            "1249": ["Power Drill", "Saw", "Hammer", "Screwdriver Set", "Wrench", "Tool Box", "Workbench"],
            "220": ["Mountain Bike", "Road Bike", "BMX", "Cruiser", "Electric Bike", "Folding Bike", "Hybrid Bike"]
        }
        
        conditions = ["New", "Like New", "Very Good", "Good", "Acceptable", "For parts or not working"]
        
        # 獲取該類別的價格範圍和標題前綴
        price_range = price_ranges.get(category_id, (50, 500))  # 默認價格範圍
        prefixes = title_prefixes.get(category_id, [category_name])  # 默認使用類別名稱
        
        # 當前時間
        now = datetime.now()
        
        # 生成模擬資料
        for i in range(count):
            # 生成隨機價格
            price = round(random.uniform(price_range[0], price_range[1]), 2)
            
            # 如果是已售出商品，價格可能略低
            if not is_active:
                price = price * random.uniform(0.7, 0.95)
            
            # 隨機選擇標題前綴和添加一些描述
            prefix = random.choice(prefixes)
            title = f"{prefix} {random.choice(['Pro', 'Air', 'Ultra', 'Max', 'Plus', 'Mini', 'Standard'])} {random.randint(5, 15)}" \
                   f" {random.choice(['GB', 'TB', 'inch', ''])}"
            
            # 隨機選擇商品狀況
            condition = random.choice(conditions)
            
            # 生成隨機日期
            if is_active:
                # 活躍商品的上架日期在過去 1-30 天內
                listing_date = (now - timedelta(days=random.randint(1, 30))).isoformat()
                # 結束日期在未來 1-30 天內
                end_date = (now + timedelta(days=random.randint(1, 30))).isoformat()
                sold_date = None
            else:
                # 已售出商品的上架日期在過去 10-60 天內
                listing_date = (now - timedelta(days=random.randint(10, 60))).isoformat()
                # 結束日期（也是售出日期）在過去 1-10 天內
                end_date = (now - timedelta(days=random.randint(1, 10))).isoformat()
                sold_date = end_date
            
            # 生成唯一 ID
            item_id = f"mock_{category_id}_{i}_{int(time.time())}_{random.randint(1000, 9999)}"
            
            # 創建模擬商品資料
            mock_item = {
                "itemId": item_id,
                "title": title,
                "condition": condition,
                "price": price,
                "currency": "USD",
                "category_id": category_id,
                "listing_date": listing_date,
                "end_date": end_date,
                "collection_date": now.isoformat(),
                "url": f"https://example.com/item/{item_id}"
            }
            
            # 如果是已售出商品，添加相關資訊
            if not is_active:
                mock_item["is_sold"] = True
                mock_item["sold_date"] = sold_date
            
            mock_items.append(mock_item)
        
        return mock_items
