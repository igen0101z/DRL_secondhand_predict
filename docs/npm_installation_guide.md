# Node.js 和 npm 安裝指南

## 問題描述

在運行項目時出現以下錯誤：

```
錯誤: 未安裝npm，無法啟動前端服務
請安裝Node.js和npm: https://nodejs.org/
```

## 安裝步驟

### Windows 系統

1. 訪問 Node.js 官方網站：https://nodejs.org/
2. 下載並安裝 LTS (長期支持) 版本
3. 安裝過程中保持默認選項即可，這將同時安裝 Node.js 和 npm
4. 安裝完成後，打開命令提示符或 PowerShell，輸入以下命令驗證安裝：
   ```
   node -v
   npm -v
   ```

### macOS 系統

1. 訪問 Node.js 官方網站：https://nodejs.org/
2. 下載並安裝 LTS 版本
3. 或者使用 Homebrew 安裝：
   ```
   brew install node
   ```
4. 安裝完成後，打開終端，輸入以下命令驗證安裝：
   ```
   node -v
   npm -v
   ```

### Linux 系統

#### 使用包管理器

**Ubuntu/Debian:**
```
sudo apt update
sudo apt install nodejs npm
```

**CentOS/RHEL/Fedora:**
```
sudo dnf install nodejs
```

#### 使用 NVM (推薦)

1. 安裝 NVM (Node Version Manager)：
   ```
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
   ```
   或
   ```
   wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
   ```

2. 重新加載配置：
   ```
   source ~/.bashrc
   ```

3. 安裝 Node.js：
   ```
   nvm install --lts
   ```

4. 驗證安裝：
   ```
   node -v
   npm -v
   ```

## 安裝後操作

安裝完成後，返回項目目錄並重新運行前端服務：

```
python run_project.py --frontend
```

## 常見問題

1. **權限問題**：如果遇到權限錯誤，可能需要使用管理員權限運行安裝命令。

2. **PATH 問題**：如果安裝後命令無法識別，可能需要將 Node.js 和 npm 添加到系統 PATH 中。

3. **版本兼容性**：如果項目需要特定版本的 Node.js，可以使用 NVM 安裝和管理多個版本。

## 其他資源

- [Node.js 官方文檔](https://nodejs.org/en/docs/)
- [npm 文檔](https://docs.npmjs.com/)
- [NVM GitHub 倉庫](https://github.com/nvm-sh/nvm)