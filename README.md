# eBay二手商品動態價格預測系統

本專案以深度強化學習（DRL）為核心，實現eBay二手商品價格預測與自動化決策，涵蓋數據收集、預處理、特徵工程、模型訓練、評估及前端展示。

## 專案結構

```
├── code.ipynb                # 互動式開發與分析筆記本（XML-based cell格式）
├── main_driver.py            # 主流程驅動類 EbayPricePredictionPipeline
├── run_project.py            # 一鍵式執行腳本（支援命令列多階段流程）
├── requirements.txt          # Python依賴
├── config/                   # 配置檔（如API金鑰、參數）
├── data/                     # 數據資料夾（raw, preprocessed, features, models等）
├── src/                      # 專案核心程式碼
│   ├── api/                  # eBay API 客戶端
│   ├── data/                 # 數據收集、預處理、特徵工程
│   ├── model/                # DRL模型與環境
│   └── utils/                # 日誌、工具
├── react_template/           # 前端展示（Vite + React + Tailwind）
└── docs/                     # 系統設計、流程、圖表
```

## 安裝與執行

1. **安裝Python依賴**
   ```bash
   pip install -r requirements.txt
   ```
2. **配置API金鑰與參數**
   - 編輯 `config/config.json` 填入eBay API金鑰與相關參數。
3. **數據處理與模型訓練**
   - 以命令列方式分步或一鍵執行：
     ```bash
     python run_project.py all
     # 或分步
     python run_project.py collect
     python run_project.py preprocess
     python run_project.py extract
     python run_project.py train
     python run_project.py evaluate --model-path <模型路徑>
     ```
4. **啟動前端服務**
   ```bash
   python run_project.py frontend
   # 或手動
   cd react_template
   npm install
   npm run dev
   ```

## 主要技術棧
- Python 3.8+
- PyTorch, NumPy, Pandas, scikit-learn
- Flask, Requests
- Vite, React, Tailwind CSS (前端)

## 資料流程
1. **數據收集**：自eBay API自動抓取商品資訊
2. **預處理**：缺失值處理、資料清洗
3. **特徵工程**：自動化特徵萃取
4. **模型訓練**：DQN等強化學習模型
5. **評估與推論**：模型效能評估與預測
6. **前端展示**：互動式價格決策模擬與視覺化

## 參考文件
- `docs/` 內含系統設計、流程圖、API說明等
- `code.ipynb` 互動式開發紀錄（XML-based cell格式）

---
如有問題請參閱README或聯絡專案作者。
