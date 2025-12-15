# MLB Hub

一个为美职棒大联盟（MLB）提供一站式信息中心的Web应用，集成了实时比分、数据统计、新闻和视频集锦。

### ✨ 功能

-   实时比分与赛程
    
-   搜索球员与球队
    
-   查看联盟数据领先者和官方排名
    
-   聚合来自主流体育媒体的新闻
    
-   来自YouTube的最新视频集锦
    

### 🛠️ 技术栈

-   **后端**: Python, Flask
    
-   **前端**: Vue.js 3, Vue Router, Axios
    

----------

## 🚀 本地运行指南

### 环境要求

-   Node.js (v16+)
    
-   Python (v3.8+)
    
-   API密钥，需从以下服务获取：
    
    -   [OpenWeatherMap](https://www.google.com/url?sa=E&q=https%3A%2F%2Fopenweathermap.org%2Fapi)
        
    -   [News API](https://www.google.com/url?sa=E&q=https%3A%2F%2Fnewsapi.org%2F)
        
    -   [Google Cloud (用于 YouTube Data API)](https://www.google.com/url?sa=E&q=https%3A%2F%2Fconsole.cloud.google.com%2Fapis%2Flibrary%2Fyoutube.googleapis.com)
        

### 安装与配置

**1. 配置后端**

codeBash

```
# 进入 backend 目录
cd backend

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Windows 用户请使用 `venv\Scripts\activate`

# 安装依赖
pip install -r requirements.txt

# 从示例文件创建 .env 文件
cp .env.example .env

# 在 .env 文件中填入你的 API 密钥
OPENWEATHER_API_KEY="YOUR_KEY_HERE"
NEWSAPI_KEY="YOUR_KEY_HERE"
YOUTUBE_API_KEY="YOUR_KEY_HERE"

# 启动后端服务 (运行于 http://localhost:5000)
python run.py
```

**2. 配置前端**

codeBash

```
# 在新终端中，进入 frontend 目录
cd frontend

# 安装依赖
npm install

# 启动前端开发服务 (运行于 http://localhost:8080)
npm run serve
```

现在，在浏览器中打开 http://localhost:8080 即可访问。

----------

## ☁️ 部署指南

本项目包含独立的前端和后端，需要分别进行部署。

### 后端部署

Python Flask 后端可以部署到任何支持 Python 应用的服务上 (例如 **Render, Heroku, Vercel**)。

1.  **安装生产环境 WSGI 服务器：**
    
    codeBash
    
    ```
    pip install gunicorn
    pip freeze > requirements.txt
    ```
    
2.  **设置启动命令：** 在你的托管服务平台设置中，将启动命令设置为：
    
    codeCode
    
    ```
    gunicorn run:app
    ```
    
3.  **配置环境变量：** 在服务平台的仪表盘中，添加以下环境变量，并填入你的密钥：
    
    -   OPENWEATHER_API_KEY
        
    -   NEWSAPI_KEY
        
    -   YOUTUBE_API_KEY
        

### 前端部署

Vue.js 前端是一个静态网站，可以部署到任何静态网站托管服务 (例如 **Vercel, Netlify, GitHub Pages**)。

1.  **重要：更新 API 地址**
    
    在构建应用之前，你**必须**修改 frontend/src/services/ApiService.js 文件中的后端 API 地址。将 baseURL 的值更改为你已部署的后端服务的公开 URL。
    
    codeJavaScript
    
    ```
    // frontend/src/services/ApiService.js
    
    const apiClient = axios.create({
      // 修改此行
      baseURL: 'https://your-deployed-backend-url.com/api', 
      headers: {
        'Content-Type': 'application/json'
      }
    });
    ```
    
2.  **构建应用**
    
    在 frontend 目录下运行以下命令：
    
    codeBash
    
    ```
    npm run build
    ```
    
    这将在 frontend 目录下生成一个 dist 文件夹，其中包含了所有用于生产环境的静态文件。
    
3.  **部署**
    
    将生成的 frontend/dist 文件夹部署到你选择的托管服务。大多数现代托管服务 (如 Vercel 或 Netlify) 都可以直接关联你的 Git 仓库，并自动完成构建和部署流程。

