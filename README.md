
# eBay Second-hand Item Price Prediction System

This project implements a dynamic price prediction system for second-hand items using deep reinforcement learning based on eBay API data.

## Project Structure

- `/config`: Configuration files for the project
- `/data`: Data directories for storing raw and processed data
  - `/data/raw`: Raw data collected from eBay API
  - `/data/processed`: Processed and cleaned data
  - `/data/features`: Extracted features for model training
  - `/data/models`: Trained DRL models
  - `/data/cache`: Cached data for performance optimization
- `/docs`: Documentation including system design
- `/logs`: Application logs
- `/src`: Source code
  - `/src/api`: API-related modules including eBay API client
  - `/src/data`: Data collection and processing modules
  - `/src/model`: DRL model and market environment
  - `/src/utils`: Utility scripts and helpers

## Setup Instructions

1. Replace the placeholder API credentials in `config/config.json` with actual eBay API credentials.
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Start data collection:
   ```
   python src/data/data_collector.py
   ```

## Core Components

- **EbayAPIClient**: Handles API requests to eBay
- **DataCollector**: Manages data collection processes
- **DataPreprocessor**: Cleans and prepares data
- **FeatureExtractor**: Extracts features for the model
- **DRLModel**: Implements the deep reinforcement learning model
- **MarketEnvironment**: Simulates the market environment for DRL training

## Data Processing Flow

1. Collect raw data from eBay API
2. Clean and preprocess the data
3. Extract features for model training
4. Train the DRL model on the processed data
5. Generate price predictions for new items
