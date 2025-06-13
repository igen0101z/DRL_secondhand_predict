import os
import asyncio
import argparse
import json
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional, Any

from src.api.ebay_api_client import EbayAPIClient
from src.data.data_collector import DataCollector
from src.data.data_preprocessor import DataPreprocessor
from src.data.feature_extractor import FeatureExtractor
from src.utils.logger import Logger

class EbayPricePredictionPipeline:
    """
    Main driver class that integrates all components of the eBay second-hand item price prediction system
    """
    def __init__(self, config_path: str = "config/config.json"):
        """Initialize the pipeline with configuration"""
        self.logger = Logger().get_logger()
        self.logger.info("Initializing eBay Price Prediction Pipeline")
        # Load configuration
        self.config_path = config_path
        self._load_config()
        # Initialize components
        self.ebay_client = None  # Initialize later to avoid unnecessary token fetching
        self.data_collector = None
        self.data_preprocessor = DataPreprocessor(config_path=config_path)
        self.feature_extractor = FeatureExtractor(config=config_path)
    
    def _load_config(self) -> None:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            self.logger.info(f"Configuration loaded successfully from {self.config_path}")
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            raise
    
    async def initialize_api_client(self) -> None:
        """Initialize the eBay API client"""
        self.logger.info("Initializing eBay API client")
        self.ebay_client = EbayAPIClient(config_path=self.config_path)
        success = await self.ebay_client.authenticate()
        
        if success:
            self.logger.info("eBay API client successfully authenticated")
        else:
            self.logger.error("Failed to authenticate eBay API client")
            raise RuntimeError("API authentication failed")
    
    async def run_data_collection(self, categories: Optional[List[Dict]] = None) -> Dict:
        """Run the data collection process"""
        self.logger.info("Starting data collection process")
        
        # Initialize data collector
        self.data_collector = DataCollector(config_path=self.config_path)
        
        # If specific categories provided, override the defaults
        if categories:
            self.data_collector.categories = categories
            self.logger.info(f"Using {len(categories)} provided categories for collection")
        
        # Run collection process
        stats = await self.data_collector.collect_data()
        return stats
    
    def run_data_preprocessing(self) -> Dict:
        """Run the data preprocessing step"""
        self.logger.info("Starting data preprocessing")
        stats = self.data_preprocessor.process_all_data()
        return stats
    
    def run_feature_extraction(self) -> Dict:
        """Run the feature extraction process"""
        self.logger.info("Starting feature extraction")
        # 獲取預處理後的資料
        preprocessed_data = self.data_preprocessor.get_preprocessed_data()
        if not preprocessed_data:
            self.logger.error("No preprocessed data available for feature extraction")
            return {"error": "No preprocessed data available"}
        
        # 傳遞預處理後的資料給特徵萃取器
        stats = self.feature_extractor.extract_all_features(preprocessed_data)
        return stats
    
    async def run_complete_pipeline(self, categories: Optional[List[Dict]] = None) -> Dict:
        """Run the complete data pipeline: collection, preprocessing, and feature extraction"""
        pipeline_stats = {
            "start_time": datetime.now().isoformat(),
            "collection": None,
            "preprocessing": None,
            "feature_extraction": None,
            "end_time": None
        }
        
        try:
            # Initialize API client
            await self.initialize_api_client()
            
            # Run data collection
            collection_stats = await self.run_data_collection(categories)
            pipeline_stats["collection"] = collection_stats
            
            # Run data preprocessing
            preprocessing_stats = self.run_data_preprocessing()
            pipeline_stats["preprocessing"] = preprocessing_stats
            
            # Run feature extraction
            extraction_stats = self.run_feature_extraction()
            pipeline_stats["feature_extraction"] = extraction_stats
            
            # Complete pipeline
            pipeline_stats["end_time"] = datetime.now().isoformat()
            
            return pipeline_stats
            
        except Exception as e:
            self.logger.error(f"Error in pipeline execution: {str(e)}")
            pipeline_stats["error"] = str(e)
            pipeline_stats["end_time"] = datetime.now().isoformat()
            return pipeline_stats

async def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description='eBay Second-hand Item Price Prediction System')
    parser.add_argument('--config', type=str, default="config/config.json", 
                        help='Path to configuration file')
    parser.add_argument('--mode', type=str, choices=['collect', 'preprocess', 'extract', 'full'], 
                        default='full', help='Operation mode')
    parser.add_argument('--category', type=str, help='Specific category ID to process')
    
    # For Jupyter notebook environment, use default arguments
    args = parser.parse_args([])
    
    # Initialize logger
    logger = Logger().get_logger()
    logger.info(f"Starting application in {args.mode} mode")
    
    # Initialize pipeline
    pipeline = EbayPricePredictionPipeline(config_path=args.config)
    
    # Prepare categories if specific one provided
    categories = None
    if args.category:
        # Look up category name from config
        category_name = "Unknown"
        for cat in pipeline.config.get("data", {}).get("categories", []):
            if cat["id"] == args.category:
                category_name = cat["name"]
                break
        
        categories = [{"id": args.category, "name": category_name}]
    
    # Execute requested operation
    if args.mode == 'collect':
        await pipeline.initialize_api_client()
        stats = await pipeline.run_data_collection(categories)
    
    elif args.mode == 'preprocess':
        stats = pipeline.run_data_preprocessing()
    
    elif args.mode == 'extract':
        stats = pipeline.run_feature_extraction()
    
    elif args.mode == 'full':
        stats = await pipeline.run_complete_pipeline(categories)
    
    return stats

if __name__ == "__main__":
    print("Starting eBay Price Prediction Pipeline")
    import asyncio
    pipeline_stats = asyncio.run(main())
    if pipeline_stats is not None:
        print(f"Pipeline completed with {pipeline_stats.get('collection', {}).get('items_collected', 0)} items collected")
    else:
        print("Pipeline completed, but未取得 pipeline_stats，請檢查錯誤日誌。")
