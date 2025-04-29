# 股票分析系统 (Stock Analysis System)

## 简介

基于 https://github.com/DR-lin-eng/stock-scanner 二次修改，感谢原作者  

## 功能变更

1. 增加html页面，支持浏览器在线使用  
2. 增加港股、美股支持  
3. 完善Dockerfile、GitHub Actions 支持docker一键部署使用  
4. 支持x86_64 和 ARM64架构镜像  
5. 支持流式输出，支持前端传入Key(仅作为本地用户使用，日志等内容不会输出) 感谢@Cassianvale  
6. 重构为Vue3+Vite+TS+Naive UI，支持响应式布局  
7. 支持GitHub Actions 一键部署  
8. 支持Nginx反向代理，可通过80/443端口访问

## Docker镜像一键部署

```
# 拉取最新版本
docker pull cassianvale/stock-scanner:latest

# 启动主应用容器
docker run -d \
  --name stock-scanner-app \
  --network stock-scanner-network \
  -p 8888:8888 \
  -v "$(pwd)/logs:/app/logs" \
  -v "$(pwd)/data:/app/data" \
  -e API_KEY="你的API密钥" \
  -e API_URL="你的API地址" \
  -e API_MODEL="你的API模型" \
  -e API_TIMEOUT="60" \
  -e LOGIN_PASSWORD="你的登录密码" \
  -e ANNOUNCEMENT_TEXT="你的公告内容" \
  --restart unless-stopped \
  cassianvale/stock-scanner:latest
  
# 运行Nginx容器
docker run -d \
  --name stock-scanner-nginx \
  --network stock-scanner-network \
  -p 80:80 \
  -p 443:443 \
  -v "$(pwd)/nginx/nginx.conf:/etc/nginx/conf.d/default.conf" \
  -v "$(pwd)/nginx/logs:/var/log/nginx" \
  -v "$(pwd)/nginx/ssl:/etc/nginx/ssl" \
  --restart unless-stopped \
  nginx:stable-alpine

针对API_URL处理兼容更多的api地址，规则与Cherry Studio一致， /结尾忽略v1版本，#结尾强制使用输入地址。
API_URL 处理逻辑说明：
1. 当 API_URL 以 / 结尾时直接追加 chat/completions，保留原有版本号：
  示例：
   输入: https://ark.cn-beijing.volces.com/api/v3/
   输出: https://ark.cn-beijing.volces.com/api/v3/chat/completions
2. 当 API_URL 以 # 结尾时强制使用当前链接：
  示例：
   输入: https://ark.cn-beijing.volces.com/api/v3/chat/completions#
   输出: https://ark.cn-beijing.volces.com/api/v3/chat/completions
3. 当 API_URL 不以 / 结尾时使用默认版本号 v1：
  示例：
   输入: https://ark.cn-beijing.volces.com/api
   输出: https://ark.cn-beijing.volces.com/api/v1/chat/completions


```

默认8888端口，部署完成后访问  http://你的域名或ip:8888 即可使用  

## 使用Nginx反向代理

项目已集成Nginx服务，可以通过80端口(HTTP)和443端口(HTTPS)访问应用  
使用docker-compose启动：  

```shell
# 克隆仓库
git clone https://github.com/cassianvale/stock-scanner.git
cd stock-scanner

# 创建.env文件并填写必要的环境变量
cat > .env << EOL
API_KEY=你的API密钥
API_URL=你的API地址
API_MODEL=你的API模型
API_TIMEOUT=超时时间(默认60秒)
LOGIN_PASSWORD=登录密码(可选)
ANNOUNCEMENT_TEXT=公告文本
EOL

# 创建SSL证书目录
mkdir -p nginx/ssl

# 生成自签名SSL证书（仅用于测试环境）
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

# 启动服务
docker-compose up -d
```

### 使用自己的SSL证书

如果您有自己的SSL证书，可以替换自签名证书：

1. 将您的证书文件放在 `nginx/ssl/` 目录下
2. 确保证书文件命名为 `fullchain.pem`，私钥文件命名为 `privkey.pem`
3. 重启服务: `docker-compose restart nginx`

相关参考：[免费泛域名 SSL 证书申请及自动续期（使用 1Panel 面板）](https://bronya-zaychik.cn/archives/GenSSL.html)

## Github Actions 部署

| 环境变量 | 说明 |
| --- | --- |
| DOCKERHUB_USERNAME | Docker Hub用户名 |
| DOCKERHUB_TOKEN | Docker Hub访问令牌 |
| SERVER_HOST | 部署服务器地址 |
| SERVER_USERNAME | 服务器用户名 |
| SSH_PRIVATE_KEY | SSH私钥 |
| DEPLOY_PATH | 部署路径 |
| SLACK_WEBHOOK | Slack通知Webhook（可选） |


## 项目简介 (Project Overview)

这是一个专业的A股股票分析系统，提供全面的技术指标分析和投资建议。系统包括三个主要组件：
- 单股票分析GUI
- 批量股票扫描器
- 高级技术指标分析引擎

This is a professional A-share stock analysis system that provides comprehensive technical indicator analysis and investment recommendations. The system includes three main components:
- Single Stock Analysis GUI
- Batch Stock Scanner
- Advanced Technical Indicator Analysis Engine

## 功能特点 (Key Features)

### 单股票分析 (Single Stock Analysis)
- 实时计算多种技术指标
- 生成详细的股票分析报告
- 提供投资建议
- 支持单股和批量分析

### 全市场扫描 (Market-Wide Scanning)
- 扫描全部A股股票
- 根据多维度技术指标进行评分
- 筛选高潜力股票
- 按价格区间生成分析报告

## 技术指标 (Technical Indicators)
- 移动平均线 (Moving Average)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- 布林带 (Bollinger Bands)
- 能量潮指标 (OBV)
- 随机指标 (Stochastic Oscillator)
- 平均真实波动范围 (ATR)

## 技术栈详解 (Technology Stack)

### 后端技术栈 (Backend Stack)

#### 核心编程语言与框架 (Core Language & Frameworks)
- Python 3.10 - 主要开发语言
- FastAPI (0.115.11) - 现代、高性能的Web框架
- Uvicorn (0.34.0) - 快速ASGI服务器

#### 数据处理与科学计算 (Data Processing & Scientific Computing)
- NumPy (1.25.2) - 科学计算基础库
- Pandas (2.0.3) - 数据分析和处理框架
- SciPy (1.11.3) - 科学计算工具箱
- AkShare (1.16.83) - 金融数据获取库

#### 异步处理 (Asynchronous Processing)
- httpx (0.28.1) - 现代异步HTTP客户端
- AsyncGenerator - 异步生成器实现流式处理

#### 数据可视化 (Data Visualization)
- Matplotlib (3.7.3) - 绘图库
- Seaborn (0.13.0) - 基于Matplotlib的统计数据可视化

#### 数据解析与处理 (Data Parsing & Processing)
- BeautifulSoup4 (4.12.3) - HTML解析
- lxml (4.9.4) - XML/HTML处理
- html5lib (1.1) - HTML解析器
- jsonpath (0.82.2) - JSON数据处理
- openpyxl (3.1.5) - Excel文件处理

#### 安全与认证 (Security & Authentication)
- python-jose (3.4.0) - JWT令牌处理
- passlib (1.7.4) - 密码哈希和验证

#### 配置与日志 (Configuration & Logging)
- python-dotenv (1.0.1) - 环境变量管理
- loguru (0.7.2) - 高级日志记录

### 前端技术栈 (Frontend Stack)

#### 核心框架和语言 (Core Frameworks & Languages)
- Vue.js 3.5.13 - 渐进式JavaScript框架
- TypeScript - 类型安全的JavaScript超集
- Vite 6.2.0 - 现代前端构建工具

#### UI组件与路由 (UI Components & Routing)
- Naive UI (2.41.0) - Vue 3组件库
- Vue Router (4.5.0) - 官方路由管理器

#### 工具库 (Utility Libraries)
- Axios (1.8.1) - HTTP客户端
- Marked (15.0.7) - Markdown解析和渲染
- VueUse (12.8.2) - Vue组合式API工具集

### 部署与运维技术 (Deployment & DevOps)

#### 容器化 (Containerization)
- Docker - 应用容器化
- Docker Compose - 多容器应用编排

#### Web服务器 (Web Server)
- Nginx - 反向代理，SSL终端，静态资源缓存

#### CI/CD (Continuous Integration/Deployment)
- GitHub Actions - 自动化构建和部署

### 系统架构 (System Architecture)

#### 微服务架构 (Microservices Architecture)
- 前后端分离设计
- 服务层设计模式，各服务相对独立

#### 异步处理流程 (Asynchronous Processing)
- 流式响应 (Streaming Response)
- 异步数据获取和处理

#### 安全机制 (Security Mechanisms)
- JWT认证
- HTTPS/SSL加密
- CORS防护

### 特色功能 (Special Features)

#### AI分析集成 (AI Analysis Integration)
- 通过外部API (如OpenAI) 进行股票数据分析
- 流式数据传输，支持实时响应

#### 多市场支持 (Multi-Market Support)
- A股市场
- 美股市场
- 港股市场
- ETF/LOF基金

## 系统依赖 (System Dependencies)
- Python 3.8+
- PyQt6
- Pandas
- NumPy
- AkShare
- Markdown2

## 快速开始 (Quick Start)

### 安装依赖 (Install Dependencies)
```bash
pip install -r requirements.txt
```

### 运行应用 (Run Application)
#### 单股票分析GUI
```bash
python gui2.py
```

#### 全市场股票扫描
```bash
python 全部股票分析推荐1.py
```

## 配置 (Configuration)
- 在 `.env` 文件中配置 Gemini API 密钥
- 可在 `stock_analyzer.py` 中调整技术指标参数

## 输出 (Outputs)
分析结果将保存在 `scanner` 目录下：
- `price_XX_YY.txt`：按价格区间的详细分析
- `summary.txt`：市场扫描汇总报告

## 注意事项 (Notes)
- 股票分析仅供参考，不构成投资建议
- 使用前请确保网络连接正常
- 建议在实盘前充分测试

## 贡献 (Contributing)
欢迎提交 issues 和 pull requests！

## 许可证 (License)
[待添加具体许可证信息]

## 免责声明 (Disclaimer)
本系统仅用于学习和研究目的，投资有风险，入市需谨慎。