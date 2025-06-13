#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基於深度強化學習的二手商品動態價格預測系統執行腳本

此腳本提供了一個完整的界面來執行eBay二手商品價格預測系統的各個組件，
包括數據收集、預處理、特徵提取、模型訓練和前端展示。
"""

import os
import sys
import json
import asyncio
import argparse
import subprocess
import webbrowser
from datetime import datetime
from typing import Dict, List, Optional, Any

# 導入項目組件
from src.api.ebay_api_client import EbayAPIClient
from src.data.data_collector import DataCollector
from src.data.data_preprocessor import DataPreprocessor
from src.data.feature_extractor import FeatureExtractor
from src.model.drl_model import DQNAgent
from src.model.market_environment import MarketEnvironment
from src.utils.logger import Logger

# 嘗試導入主驅動類
try:
    from main_driver import EbayPricePredictionPipeline
except ImportError:
    print("警告: 無法導入主驅動類，某些功能可能無法使用")

# 配置日誌
logger = Logger().get_logger()

# 定義顏色代碼，用於終端輸出
COLORS = {
    "HEADER": "\033[95m",
    "BLUE": "\033[94m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "ENDC": "\033[0m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m"
}

def print_colored(text: str, color: str = "BLUE", bold: bool = False) -> None:
    """
    打印帶顏色的文本到終端
    """
    color_code = COLORS.get(color, COLORS["BLUE"])
    bold_code = COLORS["BOLD"] if bold else ""
    print(f"{color_code}{bold_code}{text}{COLORS['ENDC']}")

def print_section(title: str) -> None:
    """
    打印帶格式的章節標題
    """
    print("\n" + "=" * 80)
    print_colored(f" {title} ", "HEADER", bold=True)
    print("=" * 80)

def print_step(step: str) -> None:
    """
    打印執行步驟
    """
    print_colored(f"\n>> {step}", "GREEN")

def check_environment() -> bool:
    """
    檢查運行環境是否滿足要求
    """
    print_step("檢查運行環境...")
    
    # 檢查Python版本
    python_version = sys.version.split()[0]
    print(f"Python版本: {python_version}")
    
    # 檢查必要的目錄
    required_dirs = [
        "data", "data/raw", "data/preprocessed", "data/features", 
        "data/models", "config", "src"
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
    
    if missing_dirs:
        print_colored(f"警告: 以下目錄不存在: {', '.join(missing_dirs)}", "YELLOW")
        create = input("是否創建這些目錄? (y/n): ").lower() == 'y'
        if create:
            for directory in missing_dirs:
                os.makedirs(directory, exist_ok=True)
            print_colored("已創建所有必要目錄", "GREEN")
        else:
            print_colored("未創建缺失的目錄，某些功能可能無法正常工作", "YELLOW")
    
    # 檢查配置文件
    config_path = "config/config.json"
    if not os.path.exists(config_path):
        print_colored(f"錯誤: 配置文件 {config_path} 不存在", "RED")
        return False
    
    # 檢查依賴項
    try:
        import torch
        import pandas
        import numpy
        import requests
        print_colored("所有核心依賴項已安裝", "GREEN")
    except ImportError as e:
        print_colored(f"錯誤: 缺少依賴項 - {str(e)}", "RED")
        print("請運行: pip install -r requirements.txt")
        return False
    
    return True

async def run_data_collection(args) -> None:
    """
    執行數據收集過程
    """
    print_section("數據收集")
    
    # 加載配置
    with open(args.config, 'r') as f:
        config = json.load(f)
    
    # 初始化數據收集器
    collector = DataCollector(config_path=args.config)
    
    # 如果指定了類別，則使用指定的類別
    categories = None
    if args.categories:
        try:
            with open(args.categories, 'r') as f:
                categories = json.load(f)
            print(f"已加載 {len(categories)} 個類別從 {args.categories}")
        except Exception as e:
            print_colored(f"錯誤: 無法加載類別文件 - {str(e)}", "RED")
            return
    
    # 執行數據收集
    print_step("開始收集數據...")
    try:
        stats = await collector.collect_data()
        print_colored(f"數據收集完成! 統計信息: {json.dumps(stats, indent=2)}", "GREEN")
    except Exception as e:
        print_colored(f"錯誤: 數據收集失敗 - {str(e)}", "RED")

def run_data_preprocessing(args) -> None:
    """
    執行數據預處理過程
    """
    print_section("數據預處理")
    
    # 初始化預處理器
    preprocessor = DataPreprocessor(config_path=args.config)
    
    # 執行預處理
    print_step("開始預處理數據...")
    try:
        stats = preprocessor.process_all_data()
        print_colored(f"數據預處理完成! 統計信息: {json.dumps(stats, indent=2)}", "GREEN")
    except Exception as e:
        print_colored(f"錯誤: 數據預處理失敗 - {str(e)}", "RED")

def run_feature_extraction(args) -> None:
    """
    執行特徵提取過程
    """
    print_section("特徵提取")
    
    # 初始化預處理器和特徵提取器
    preprocessor = DataPreprocessor(config_path=args.config)
    extractor = FeatureExtractor(config=args.config)
    
    # 獲取預處理數據
    print_step("加載預處理數據...")
    preprocessed_data = preprocessor.get_preprocessed_data()
    if not preprocessed_data:
        print_colored("錯誤: 沒有可用的預處理數據", "RED")
        return
    
    # 執行特徵提取
    print_step("開始提取特徵...")
    try:
        stats = extractor.extract_all_features(preprocessed_data)
        print_colored(f"特徵提取完成! 統計信息: {json.dumps(stats, indent=2)}", "GREEN")
    except Exception as e:
        print_colored(f"錯誤: 特徵提取失敗 - {str(e)}", "RED")

def run_model_training(args) -> None:
    """
    執行模型訓練過程
    """
    print_section("模型訓練")
    
    # 加載配置
    with open(args.config, 'r') as f:
        config = json.load(f)
    
    # 初始化市場環境
    print_step("初始化市場環境...")
    try:
        env = MarketEnvironment(config_path=args.config)
        print_colored("市場環境初始化成功", "GREEN")
    except Exception as e:
        print_colored(f"錯誤: 市場環境初始化失敗 - {str(e)}", "RED")
        return
    
    # 初始化DQN代理
    print_step("初始化DQN代理...")
    try:
        # 從環境中獲取狀態大小和動作空間大小
        # 使用環境的get_state_space_size方法獲取正確的狀態空間大小
        state_size = env.get_state_space_size()  # 動態獲取環境狀態空間大小
        action_size = env.action_space_size  # 從環境中獲取動作空間大小
        
        agent = DQNAgent(state_size=state_size, action_size=action_size, config_path=args.config)
        print_colored("DQN代理初始化成功", "GREEN")
    except Exception as e:
        print_colored(f"錯誤: DQN代理初始化失敗 - {str(e)}", "RED")
        return
    
    # 訓練模型
    print_step("開始訓練模型...")
    try:
        episodes = args.episodes or config.get("training", {}).get("episodes", 1000)
        print(f"訓練回合數: {episodes}")
        
        training_stats = agent.train(episodes=episodes)
        print_colored("模型訓練完成!", "GREEN")
        print(f"訓練統計信息: {json.dumps(training_stats, indent=2)}")
        
        # 保存模型
        if args.save_model:
            model_path = args.save_model
            agent.save_model(model_path)
            print_colored(f"模型已保存到: {model_path}", "GREEN")
    except Exception as e:
        print_colored(f"錯誤: 模型訓練失敗 - {str(e)}", "RED")

def run_model_evaluation(args) -> None:
    """
    執行模型評估過程
    """
    print_section("模型評估")
    
    # 加載配置
    with open(args.config, 'r') as f:
        config = json.load(f)
    
    # 檢查模型路徑
    if not args.model_path:
        print_colored("錯誤: 未指定模型路徑", "RED")
        return
    
    if not os.path.exists(args.model_path):
        print_colored(f"錯誤: 模型文件 {args.model_path} 不存在", "RED")
        return
    
    # 初始化市場環境
    print_step("初始化市場環境...")
    try:
        env = MarketEnvironment(config_path=args.config, evaluation=True)
        print_colored("市場環境初始化成功", "GREEN")
    except Exception as e:
        print_colored(f"錯誤: 市場環境初始化失敗 - {str(e)}", "RED")
        return
    
    # 初始化DQN代理並加載模型
    print_step("加載預訓練模型...")
    try:
        # 從環境中獲取狀態大小和動作空間大小
        state_size = env.get_state_space_size()  # 動態獲取環境狀態空間大小
        action_size = env.action_space_size  # 從環境中獲取動作空間大小
        
        agent = DQNAgent(state_size=state_size, action_size=action_size, config_path=args.config)
        agent.load_model(args.model_path)
        print_colored(f"模型加載成功: {args.model_path}", "GREEN")
    except Exception as e:
        print_colored(f"錯誤: 模型加載失敗 - {str(e)}", "RED")
        return
    
    # 評估模型
    print_step("開始評估模型...")
    try:
        episodes = args.episodes or config.get("evaluation", {}).get("episodes", 100)
        print(f"評估回合數: {episodes}")
        
        eval_stats = agent.evaluate(episodes=episodes)
        print_colored("模型評估完成!", "GREEN")
        print(f"評估統計信息: {json.dumps(eval_stats, indent=2)}")
    except Exception as e:
        print_colored(f"錯誤: 模型評估失敗 - {str(e)}", "RED")

def run_frontend(args) -> None:
    """
    啟動前端服務
    """
    print_section("啟動前端服務")
    
    frontend_dir = "react_template"
    if not os.path.exists(frontend_dir):
        print_colored(f"錯誤: 前端目錄 {frontend_dir} 不存在", "RED")
        return
    
    # 檢查是否安裝了npm
    try:
        # 使用 shell=True 來確保在 Windows 環境下能正確找到 npm 命令
        # 這樣可以解決 PATH 環境變量問題
        result = subprocess.run("npm --version", shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise subprocess.SubprocessError("npm 命令執行失敗")
        print_colored(f"檢測到 npm 版本: {result.stdout.strip()}", "GREEN")
    except (subprocess.SubprocessError, FileNotFoundError):
        print_colored("錯誤: 未安裝npm，無法啟動前端服務", "RED")
        print("請安裝Node.js和npm: https://nodejs.org/")
        return
    
    # 切換到前端目錄
    os.chdir(frontend_dir)
    
    # 安裝依賴
    print_step("安裝前端依賴...")
    try:
        # 使用 shell=True 來確保在 Windows 環境下能正確執行 npm 命令
        subprocess.run("npm install", shell=True, check=True)
        print_colored("前端依賴安裝成功", "GREEN")
    except subprocess.SubprocessError as e:
        print_colored(f"錯誤: 安裝前端依賴失敗 - {str(e)}", "RED")
        return
    
    # 啟動開發服務器
    print_step("啟動前端開發服務器...")
    print_colored("前端服務將在 http://localhost:5173 啟動", "BLUE")
    print_colored("按 Ctrl+C 停止服務", "YELLOW")
    
    # 打開瀏覽器
    if not args.no_browser:
        webbrowser.open("http://localhost:5173")
    
    # 啟動服務
    try:
        # 使用 shell=True 來確保在 Windows 環境下能正確執行 npm 命令
        subprocess.run("npm run dev", shell=True, check=True)
    except KeyboardInterrupt:
        print_colored("\n前端服務已停止", "YELLOW")
    except subprocess.SubprocessError as e:
        print_colored(f"錯誤: 啟動前端服務失敗 - {str(e)}", "RED")

async def run_complete_pipeline(args) -> None:
    """
    執行完整的數據處理和模型訓練流程
    """
    print_section("執行完整流程")
    
    # 檢查是否可以導入主驅動類
    if 'EbayPricePredictionPipeline' not in globals():
        print_colored("錯誤: 無法導入主驅動類，無法執行完整流程", "RED")
        return
    
    # 初始化流水線
    print_step("初始化流水線...")
    try:
        pipeline = EbayPricePredictionPipeline(config_path=args.config)
        print_colored("流水線初始化成功", "GREEN")
    except Exception as e:
        print_colored(f"錯誤: 流水線初始化失敗 - {str(e)}", "RED")
        return
    
    # 執行完整流程
    print_step("開始執行完整流程...")
    try:
        # 加載類別（如果指定）
        categories = None
        if args.categories:
            with open(args.categories, 'r') as f:
                categories = json.load(f)
            print(f"已加載 {len(categories)} 個類別從 {args.categories}")
        
        # 執行流水線
        stats = await pipeline.run_complete_pipeline(categories=categories)
        
        print_colored("完整流程執行成功!", "GREEN")
        print(f"流程統計信息: {json.dumps(stats, indent=2)}")
    except Exception as e:
        print_colored(f"錯誤: 執行完整流程失敗 - {str(e)}", "RED")

def parse_arguments():
    """
    解析命令行參數
    """
    parser = argparse.ArgumentParser(description="eBay二手商品價格預測系統執行腳本")
    
    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="要執行的命令")
    
    # 通用參數
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--config", default="config/config.json", help="配置文件路徑")
    
    # 數據收集命令
    collect_parser = subparsers.add_parser("collect", parents=[parent_parser], help="收集數據")
    collect_parser.add_argument("--categories", help="類別配置文件路徑")
    
    # 數據預處理命令
    preprocess_parser = subparsers.add_parser("preprocess", parents=[parent_parser], help="預處理數據")
    
    # 特徵提取命令
    extract_parser = subparsers.add_parser("extract", parents=[parent_parser], help="提取特徵")
    
    # 模型訓練命令
    train_parser = subparsers.add_parser("train", parents=[parent_parser], help="訓練模型")
    train_parser.add_argument("--episodes", type=int, help="訓練回合數")
    train_parser.add_argument("--save-model", help="保存模型的路徑")
    
    # 模型評估命令
    eval_parser = subparsers.add_parser("evaluate", parents=[parent_parser], help="評估模型")
    eval_parser.add_argument("--model-path", required=True, help="模型文件路徑")
    eval_parser.add_argument("--episodes", type=int, help="評估回合數")
    
    # 前端命令
    frontend_parser = subparsers.add_parser("frontend", parents=[parent_parser], help="啟動前端服務")
    frontend_parser.add_argument("--no-browser", action="store_true", help="不自動打開瀏覽器")
    
    # 完整流程命令
    pipeline_parser = subparsers.add_parser("pipeline", parents=[parent_parser], help="執行完整流程")
    pipeline_parser.add_argument("--categories", help="類別配置文件路徑")
    
    # 全部命令（按順序執行所有步驟）
    all_parser = subparsers.add_parser("all", parents=[parent_parser], help="執行所有步驟")
    all_parser.add_argument("--categories", help="類別配置文件路徑")
    all_parser.add_argument("--episodes", type=int, help="訓練回合數")
    all_parser.add_argument("--save-model", default="data/models/dqn_model.pth", help="保存模型的路徑")
    all_parser.add_argument("--no-browser", action="store_true", help="不自動打開瀏覽器")
    
    return parser.parse_args()

async def main():
    """
    主函數
    """
    # 打印歡迎信息
    print("\n" + "*" * 80)
    print_colored("eBay二手商品價格預測系統", "HEADER", bold=True)
    print("*" * 80)
    print("基於深度強化學習的二手商品動態價格預測系統")
    print("版本: 1.0.0")
    print("*" * 80 + "\n")
    
    # 解析命令行參數
    args = parse_arguments()
    
    # 如果沒有指定命令，顯示幫助信息
    if not args.command:
        print("請指定要執行的命令。使用 --help 查看可用命令。")
        return
    
    # 檢查環境
    if not check_environment():
        print_colored("環境檢查失敗，請修復上述問題後重試", "RED")
        return
    
    # 根據命令執行相應的功能
    if args.command == "collect":
        await run_data_collection(args)
    elif args.command == "preprocess":
        run_data_preprocessing(args)
    elif args.command == "extract":
        run_feature_extraction(args)
    elif args.command == "train":
        run_model_training(args)
    elif args.command == "evaluate":
        run_model_evaluation(args)
    elif args.command == "frontend":
        run_frontend(args)
    elif args.command == "pipeline":
        await run_complete_pipeline(args)
    elif args.command == "all":
        # 執行所有步驟
        print_colored("執行所有步驟...", "BLUE", bold=True)
        
        # 數據收集
        await run_data_collection(args)
        
        # 數據預處理
        run_data_preprocessing(args)
        
        # 特徵提取
        run_feature_extraction(args)
        
        # 模型訓練
        run_model_training(args)
        
        # 啟動前端
        run_frontend(args)

if __name__ == "__main__":
    # 運行主函數
    asyncio.run(main())