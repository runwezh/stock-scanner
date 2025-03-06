from fastapi import FastAPI, Request, Response, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Generator
from services.stock_analyzer_service import StockAnalyzerService
# 导入新的异步服务
from services.us_stock_service_async import USStockServiceAsync
from services.fund_service_async import FundServiceAsync
import asyncio
import threading
import os
import traceback
import httpx
from logger import get_logger
from utils.api_utils import APIUtils
# 加载环境变量
from dotenv import load_dotenv
import uvicorn

load_dotenv()

# 获取日志器
logger = get_logger()

app = FastAPI(
    title="Stock Scanner API",
    description="异步股票分析API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源，生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],    
    allow_headers=["*"],
)

# 设置静态文件
frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend', 'dist')
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

# 初始化异步服务
# StockAnalyzerService 不需要全局初始化，在 /analyze 接口中按需创建
us_stock_service = USStockServiceAsync()
fund_service = FundServiceAsync()

# 定义请求和响应模型
class AnalyzeRequest(BaseModel):
    stock_codes: List[str]
    market_type: str = "A"
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    api_model: Optional[str] = None
    api_timeout: Optional[str] = None

class TestAPIRequest(BaseModel):
    api_url: str
    api_key: str
    api_model: Optional[str] = None
    api_timeout: Optional[int] = 10

@app.get("/")
async def index(request: Request):
    # 检查是否使用前端构建版本
    if os.path.exists(frontend_dist):
        index_file = os.path.join(frontend_dist, 'index.html')
        return FileResponse(index_file)
    else:
        # 不再使用模板渲染，而是重定向到API文档页面
        logger.warning("前端构建目录不存在，重定向到API文档页面")
        return RedirectResponse(url="/docs")

@app.get("/config")
async def get_config():
    """返回系统配置信息"""
    config = {
        'announcement': os.getenv('ANNOUNCEMENT_TEXT') or '',
        'default_api_url': os.getenv('API_URL', ''),
        'default_api_model': os.getenv('API_MODEL', 'gpt-3.5-turbo'),
        'default_api_timeout': os.getenv('API_TIMEOUT', '60')
    }
    return config

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    try:
        logger.info("开始处理分析请求")
        stock_codes = request.stock_codes
        market_type = request.market_type
        
        logger.debug(f"接收到分析请求: stock_codes={stock_codes}, market_type={market_type}")
        
        # 获取自定义API配置
        custom_api_url = request.api_url
        custom_api_key = request.api_key
        custom_api_model = request.api_model
        custom_api_timeout = request.api_timeout
        
        logger.debug(f"自定义API配置: URL={custom_api_url}, 模型={custom_api_model}, API Key={'已提供' if custom_api_key else '未提供'}, Timeout={custom_api_timeout}")
        
        # 创建新的分析器实例，使用自定义配置
        custom_analyzer = StockAnalyzerService(
            custom_api_url=custom_api_url,
            custom_api_key=custom_api_key,
            custom_api_model=custom_api_model,
            custom_api_timeout=custom_api_timeout
        )
        
        if not stock_codes:
            logger.warning("未提供股票代码")
            raise HTTPException(status_code=400, detail="请输入代码")
        
        # 定义流式生成器
        async def generate_stream():
            if len(stock_codes) == 1:
                # 单个股票分析流式处理
                stock_code = stock_codes[0].strip()
                logger.info(f"开始单股流式分析: {stock_code}")
                
                init_message = f'{{"stream_type": "single", "stock_code": "{stock_code}"}}\n'
                yield init_message
                
                logger.debug(f"开始处理股票 {stock_code} 的流式响应")
                chunk_count = 0
                
                # 使用异步生成器
                async for chunk in custom_analyzer.analyze_stock(stock_code, market_type, stream=True):
                    chunk_count += 1
                    yield chunk + '\n'
                
                logger.info(f"股票 {stock_code} 流式分析完成，共发送 {chunk_count} 个块")
            else:
                # 批量分析流式处理
                logger.info(f"开始批量流式分析: {stock_codes}")
                
                init_message = f'{{"stream_type": "batch", "stock_codes": {stock_codes}}}\n'
                yield init_message
                
                logger.debug(f"开始处理批量股票的流式响应")
                chunk_count = 0
                
                # 使用异步生成器
                async for chunk in custom_analyzer.scan_stocks(
                    [code.strip() for code in stock_codes], 
                    min_score=0, 
                    market_type=market_type,
                    stream=True
                ):
                    chunk_count += 1
                    yield chunk + '\n'
                
                logger.info(f"批量流式分析完成，共发送 {chunk_count} 个块")
        
        logger.info("成功创建流式响应生成器")
        return StreamingResponse(generate_stream(), media_type='application/json')
            
    except Exception as e:
        error_msg = f"分析时出错: {str(e)}"
        logger.error(error_msg)
        logger.exception(e)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/search_us_stocks")
async def search_us_stocks(keyword: str = ""):
    try:
        if not keyword:
            raise HTTPException(status_code=400, detail="请输入搜索关键词")
        
        # 直接使用异步服务的异步方法
        results = await us_stock_service.search_us_stocks(keyword)
        return {"results": results}
        
    except Exception as e:
        logger.error(f"搜索美股代码时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search_funds")
async def search_funds(keyword: str = "", market_type: str = ""):
    try:
        if not keyword:
            raise HTTPException(status_code=400, detail="请输入搜索关键词")
        
        # 直接使用异步服务的异步方法
        results = await fund_service.search_funds(keyword, market_type)
        return {"results": results}
        
    except Exception as e:
        logger.error(f"搜索基金代码时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test_api_connection")
async def test_api_connection(request: TestAPIRequest):
    """测试API连接"""
    try:
        logger.info("开始测试API连接")
        api_url = request.api_url
        api_key = request.api_key
        api_model = request.api_model
        api_timeout = request.api_timeout
        
        logger.debug(f"测试API连接: URL={api_url}, 模型={api_model}, API Key={'已提供' if api_key else '未提供'}, Timeout={api_timeout}")
        
        if not api_url:
            logger.warning("未提供API URL")
            raise HTTPException(status_code=400, detail="请提供API URL")
            
        if not api_key:
            logger.warning("未提供API Key")
            raise HTTPException(status_code=400, detail="请提供API Key")
            
        # 构建API URL
        test_url = APIUtils.format_api_url(api_url)
        logger.debug(f"完整API测试URL: {test_url}")
        
        # 使用异步HTTP客户端发送测试请求
        async with httpx.AsyncClient(timeout=float(api_timeout)) as client:
            response = await client.post(
                test_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": api_model or "gpt-3.5-turbo",
                    "messages": [
                        {"role": "user", "content": "Hello, this is a test message. Please respond with 'API connection successful'."}
                    ],
                    "max_tokens": 20
                }
            )
        
        # 检查响应
        if response.status_code == 200:
            logger.info(f"API 连接测试成功: {response.status_code}")
            return {"success": True, "message": "API 连接测试成功"}
        else:
            error_data = response.json()
            error_message = error_data.get('error', {}).get('message', '未知错误')
            logger.warning(f"API连接测试失败: {response.status_code} - {error_message}")
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": f"API 连接测试失败: {error_message}", "status_code": response.status_code}
            )
            
    except httpx.RequestError as e:
        logger.error(f"API 连接请求错误: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": f"请求错误: {str(e)}"}
        )
    except Exception as e:
        logger.error(f"测试 API 连接时出错: {str(e)}")
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"API 测试连接时出错: {str(e)}"}
        )

# 新增 API 端点：获取美股详情
@app.get("/us_stock_detail/{symbol}")
async def get_us_stock_detail(symbol: str):
    try:
        if not symbol:
            raise HTTPException(status_code=400, detail="请提供股票代码")
        
        # 使用异步服务获取详情
        detail = await us_stock_service.get_us_stock_detail(symbol)
        return detail
        
    except Exception as e:
        logger.error(f"获取美股详情时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 新增 API 端点：获取基金详情
@app.get("/fund_detail/{symbol}")
async def get_fund_detail(symbol: str, market_type: str = "ETF"):
    try:
        if not symbol:
            raise HTTPException(status_code=400, detail="请提供基金代码")
        
        # 使用异步服务获取详情
        detail = await fund_service.get_fund_detail(symbol, market_type)
        return detail
        
    except Exception as e:
        logger.error(f"获取基金详情时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    logger.info("股票分析系统启动")
    uvicorn.run("web_server:app", host="127.0.0.1", port=8888, reload=True)