import os
import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any

from src.utils.logger import Logger
from src.utils.api_utils import rate_limiter, handle_api_errors, APIResponse, load_config

class EbayAPIClient:
    """
    Client for interacting with eBay API for data collection
    """
    def __init__(self, config_path: str = "/data/chats/p6wyr/workspace/config/config.json"):
        """
        Initialize the eBay API client with configuration
        
        Args:
            config_path (str): Path to the configuration file
        """
        self.logger = Logger().get_logger()
        self.logger.info("Initializing eBay API client")
        
        # Load configuration
        self.config = self._load_config(config_path)
        self.api_config = self.config.get("api", {}).get("ebay", {})
        
        # API credentials
        self.app_id = self.api_config.get("app_id", "")
        self.cert_id = self.api_config.get("cert_id", "")
        self.dev_id = self.api_config.get("dev_id", "")
        self.client_secret = self.api_config.get("client_secret", "")
        self.ru_name = self.api_config.get("ru_name", "")
        
        # API settings
        self.sandbox_mode = self.api_config.get("sandbox_mode", True)
        self.rate_limits = self.api_config.get("rate_limits", {
            "calls_per_second": 5,
            "calls_per_day": 5000
        })
        
        # Set base URLs based on sandbox mode
        if self.sandbox_mode:
            self.base_url = "https://api.sandbox.ebay.com"
            self.auth_url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
        else:
            self.base_url = "https://api.ebay.com"
            self.auth_url = "https://api.ebay.com/identity/v1/oauth2/token"
            
        # Initialize access token
        self.access_token = None
        self.token_expiry = None
        
        # Cache directory for API responses
        self.cache_dir = "/data/chats/p6wyr/workspace/data/cache/api_responses"
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from file
        
        Args:
            config_path (str): Path to the configuration file
            
        Returns:
            Dict: Configuration settings
        """
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            self.logger.warning(f"Configuration file not found at {config_path}, using defaults")
            return {}

    @handle_api_errors
    async def authenticate(self) -> bool:
        """
        Authenticate with eBay API and get access token
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        # Check if we already have a valid token
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return True
            
        self.logger.info("Authenticating with eBay API")
        
        # Prepare authentication request
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {self._get_basic_auth_header()}'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'scope': 'https://api.ebay.com/oauth/api_scope'
        }
        
        try:
            response = requests.post(self.auth_url, headers=headers, data=data)
            response.raise_for_status()
            
            # Parse token response
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 7200)  # Default 2 hours
            
            # Set token expiry time
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 300)  # 5 min buffer
            
            self.logger.info(f"Successfully authenticated with eBay API, token valid until {self.token_expiry}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            return False
    
    def _get_basic_auth_header(self) -> str:
        """
        Generate the Base64 encoded Basic auth header
        
        Returns:
            str: Base64 encoded auth string
        """
        import base64
        credentials = f"{self.app_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return encoded_credentials
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get headers with authorization token
        
        Returns:
            Dict[str, str]: Headers for API requests
        """
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'  # Default to US marketplace
        }
    
    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """
        Generate a cache key for the API request
        
        Args:
            endpoint (str): API endpoint
            params (Dict): Request parameters
            
        Returns:
            str: Cache key
        """
        param_str = json.dumps(params, sort_keys=True)
        return f"{endpoint}_{hash(param_str)}"
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """
        Get cached API response
        
        Args:
            cache_key (str): Cache key
            
        Returns:
            Optional[Dict]: Cached response or None
        """
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                # Check if cache is still valid
                if datetime.now().timestamp() < cached_data.get('expiry', 0):
                    self.logger.info(f"Using cached response for {cache_key}")
                    return cached_data.get('data')
            except Exception as e:
                self.logger.warning(f"Error reading cache: {str(e)}")
        
        return None
    
    def _cache_response(self, cache_key: str, data: Dict, cache_ttl: int = 3600) -> None:
        """
        Cache API response
        
        Args:
            cache_key (str): Cache key
            data (Dict): Response data
            cache_ttl (int): Cache TTL in seconds
        """
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        try:
            cached_data = {
                'data': data,
                'expiry': datetime.now().timestamp() + cache_ttl
            }
            with open(cache_file, 'w') as f:
                json.dump(cached_data, f)
            self.logger.info(f"Cached response for {cache_key}")
        except Exception as e:
            self.logger.warning(f"Error caching response: {str(e)}")
    
    @rate_limiter(max_calls=5, time_frame=1)  # 5 calls per second
    @handle_api_errors
    async def make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                          data: Optional[Dict] = None, use_cache: bool = True,
                          cache_ttl: int = 3600) -> APIResponse:
        """
        Make an API request to eBay
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            params (Optional[Dict]): Query parameters
            data (Optional[Dict]): Request body for POST requests
            use_cache (bool): Whether to use cache
            cache_ttl (int): Cache TTL in seconds
            
        Returns:
            APIResponse: Response object
        """
        # Ensure authentication
        if not self.access_token or not self.token_expiry or datetime.now() > self.token_expiry:
            if not await self.authenticate():
                return APIResponse(
                    success=False, 
                    error="Authentication failed", 
                    status_code=401
                )
        
        # Check cache if enabled
        if use_cache and method.upper() == 'GET':
            cache_key = self._get_cache_key(endpoint, params or {})
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                return APIResponse(success=True, data=cached_response, status_code=200)
        
        # Prepare request
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_auth_headers()
        
        try:
            # Make request
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                json=data
            )
            response.raise_for_status()
            
            # Parse response
            response_data = response.json()
            
            # Cache response if needed
            if use_cache and method.upper() == 'GET':
                cache_key = self._get_cache_key(endpoint, params or {})
                self._cache_response(cache_key, response_data, cache_ttl)
            
            return APIResponse(
                success=True,
                data=response_data,
                status_code=response.status_code
            )
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error: {str(e)}"
            try:
                error_data = e.response.json()
                if 'errors' in error_data:
                    error_msg = f"{error_msg} - {error_data['errors']}"
            except:
                pass
            
            return APIResponse(
                success=False,
                error=error_msg,
                status_code=e.response.status_code if e.response else 500
            )
            
        except Exception as e:
            return APIResponse(
                success=False,
                error=f"Request failed: {str(e)}",
                status_code=500
            )
    
    async def search_items(self, keywords: str, category_id: Optional[str] = None, 
                          item_condition: Optional[List[str]] = None, 
                          price_range: Optional[Dict[str, float]] = None,
                          sort_order: str = "endingSoonest",
                          limit: int = 100) -> APIResponse:
        """
        Search for items on eBay
        
        Args:
            keywords (str): Search keywords
            category_id (Optional[str]): Category ID
            item_condition (Optional[List[str]]): List of condition IDs
            price_range (Optional[Dict[str, float]]): Price range with min and max keys
            sort_order (str): Sort order (endingSoonest, newlyListed, etc.)
            limit (int): Maximum number of items to return
            
        Returns:
            APIResponse: Response with search results
        """
        self.logger.info(f"Searching for '{keywords}' in category {category_id}")
        
        # Build query parameters
        params = {
            'q': keywords,
            'limit': min(limit, 200),  # API maximum is 200
            'sort': sort_order,
            'filter': []
        }
        
        # Add category filter if provided
        if category_id:
            params['category_ids'] = category_id
        
        # Add condition filter if provided
        if item_condition:
            condition_filter = {
                'itemFilter': {
                    'name': 'Condition',
                    'value': item_condition
                }
            }
            params['filter'].append(condition_filter)
        
        # Add price range filter if provided
        if price_range:
            if 'min' in price_range:
                min_price_filter = {
                    'itemFilter': {
                        'name': 'MinPrice',
                        'value': price_range['min'],
                        'paramName': 'Currency',
                        'paramValue': 'USD'
                    }
                }
                params['filter'].append(min_price_filter)
                
            if 'max' in price_range:
                max_price_filter = {
                    'itemFilter': {
                        'name': 'MaxPrice',
                        'value': price_range['max'],
                        'paramName': 'Currency',
                        'paramValue': 'USD'
                    }
                }
                params['filter'].append(max_price_filter)
        
        # Convert filters to string format
        if params['filter']:
            params['filter'] = json.dumps(params['filter'])
        else:
            del params['filter']
        
        # Make API request
        return await self.make_request(
            method='GET',
            endpoint='buy/browse/v1/item_summary/search',
            params=params,
            use_cache=True,
            cache_ttl=3600  # Cache for 1 hour
        )

    async def get_item_details(self, item_id: str, use_cache: bool = True) -> APIResponse:
        """
        Get detailed information about a specific item
        
        Args:
            item_id (str): eBay item ID
            use_cache (bool): Whether to use cache
            
        Returns:
            APIResponse: Response with item details
        """
        self.logger.info(f"Getting details for item {item_id}")
        
        return await self.make_request(
            method='GET',
            endpoint=f'buy/browse/v1/item/{item_id}',
            use_cache=use_cache,
            cache_ttl=3600  # Cache for 1 hour
        )

    async def get_item_analytics(self, item_ids: List[str]) -> APIResponse:
        """
        Get analytics for multiple items
        
        Args:
            item_ids (List[str]): List of eBay item IDs
            
        Returns:
            APIResponse: Response with item analytics
        """
        self.logger.info(f"Getting analytics for {len(item_ids)} items")
        
        # eBay Analytics API has a limit on the number of items
        if len(item_ids) > 20:
            self.logger.warning(f"Too many item IDs provided ({len(item_ids)}), using first 20 only")
            item_ids = item_ids[:20]
        
        return await self.make_request(
            method='POST',
            endpoint='commerce/analytics/v1/item_analytics',
            data={'itemIds': item_ids},
            use_cache=False  # Analytics data should be fresh
        )

    async def get_sold_items(self, keywords: str, category_id: Optional[str] = None,
                            days_back: int = 30, limit: int = 100) -> APIResponse:
        """
        Search for completed/sold items
        
        Args:
            keywords (str): Search keywords
            category_id (Optional[str]): Category ID
            days_back (int): Number of days to look back
            limit (int): Maximum number of items to return
            
        Returns:
            APIResponse: Response with completed/sold items
        """
        self.logger.info(f"Searching for sold items: '{keywords}' in category {category_id}")
        
        # This endpoint requires the Finding API, which has a different structure
        # We'll adapt our client to handle this special case
        
        params = {
            'keywords': keywords,
            'itemFilter': [
                {'name': 'SoldItemsOnly', 'value': 'true'},
                {'name': 'ListingType', 'value': 'FixedPrice'}
            ],
            'sortOrder': 'EndTimeSoonest',
            'paginationInput': {
                'entriesPerPage': min(limit, 100),
                'pageNumber': 1
            }
        }
        
        if category_id:
            params['categoryId'] = category_id
        
        # The Finding API has a different endpoint structure
        endpoint = 'finding/v1/services'
        
        return await self.make_request(
            method='GET',
            endpoint=endpoint,
            params={
                'OPERATION-NAME': 'findCompletedItems',
                'SERVICE-VERSION': '1.13.0',
                'SECURITY-APPNAME': self.app_id,
                'RESPONSE-DATA-FORMAT': 'JSON',
                'REST-PAYLOAD': 'true',
                'keywords': keywords,
                'categoryId': category_id,
                'itemFilter(0).name': 'SoldItemsOnly',
                'itemFilter(0).value': 'true',
                'sortOrder': 'EndTimeSoonest',
                'paginationInput.entriesPerPage': min(limit, 100),
            },
            use_cache=True,
            cache_ttl=3600 * 6  # Cache for 6 hours
        )

    async def get_categories(self, parent_id: Optional[str] = None) -> APIResponse:
        """
        Get eBay categories
        
        Args:
            parent_id (Optional[str]): Parent category ID for subcategories
            
        Returns:
            APIResponse: Response with categories
        """
        self.logger.info(f"Getting categories with parent ID: {parent_id}")
        
        params = {}
        if parent_id:
            params['category_id'] = parent_id
        
        return await self.make_request(
            method='GET',
            endpoint='commerce/taxonomy/v1/category_tree/0',  # 0 is for US marketplace
            params=params,
            use_cache=True,
            cache_ttl=86400 * 7  # Cache for 7 days as categories don't change often
        )

    async def get_category_aspects(self, category_id: str) -> APIResponse:
        """
        Get category aspects (item specifics)
        
        Args:
            category_id (str): Category ID
            
        Returns:
            APIResponse: Response with category aspects
        """
        self.logger.info(f"Getting aspects for category {category_id}")
        
        return await self.make_request(
            method='GET',
            endpoint=f'commerce/taxonomy/v1/category_tree/0/get_item_aspects_for_category',
            params={'category_id': category_id},
            use_cache=True,
            cache_ttl=86400 * 7  # Cache for 7 days
        )