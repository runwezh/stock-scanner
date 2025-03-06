import pandas as pd
import numpy as np
import os
import json
import asyncio
import httpx
from typing import Dict, List, Optional, Any, Generator, AsyncGenerator
from dotenv import load_dotenv
from logger import get_logger
from utils.api_utils import APIUtils

# 获取日志器
logger = get_logger()

class AIAnalyzer:
    """
    异步AI分析服务
    负责调用AI API对股票数据进行分析
    """
    
    def __init__(self, custom_api_url=None, custom_api_key=None, custom_api_model=None, custom_api_timeout=None):
        """
        初始化AI分析服务
        
        Args:
            custom_api_url: 自定义API URL
            custom_api_key: 自定义API密钥
            custom_api_model: 自定义API模型
            custom_api_timeout: 自定义API超时时间
        """
        # 加载环境变量
        load_dotenv()
        
        # 设置API配置
        self.API_URL = custom_api_url or os.getenv('API_URL')
        self.API_KEY = custom_api_key or os.getenv('API_KEY')
        self.API_MODEL = custom_api_model or os.getenv('API_MODEL', 'gpt-3.5-turbo')
        self.API_TIMEOUT = int(custom_api_timeout or os.getenv('API_TIMEOUT', 60))
        
        logger.debug(f"初始化AIAnalyzer: API_URL={self.API_URL}, API_MODEL={self.API_MODEL}, API_KEY={'已提供' if self.API_KEY else '未提供'}, API_TIMEOUT={self.API_TIMEOUT}")
    
    async def get_ai_analysis(self, df: pd.DataFrame, stock_code: str, market_type: str = 'A', stream: bool = False) -> AsyncGenerator[str, None]:
        """
        对股票数据进行AI分析
        
        Args:
            df: 包含技术指标的DataFrame
            stock_code: 股票代码
            market_type: 市场类型，默认为'A'股
            stream: 是否使用流式响应
            
        Returns:
            异步生成器，生成分析结果字符串
        """
        try:
            logger.info(f"开始AI分析 {stock_code}, 流式模式: {stream}")
            
            # AI 分析内容
            # 最近14天的股票数据记录
            recent_data = df.tail(14).to_dict('records')
            
            # 包含trend, volatility, volume_trend, rsi_level的字典
            technical_summary = {
                'trend': 'upward' if df.iloc[-1]['MA5'] > df.iloc[-1]['MA20'] else 'downward',
                'volatility': f"{df.iloc[-1]['Volatility']:.2f}%",
                'volume_trend': 'increasing' if df.iloc[-1]['Volume_Ratio'] > 1 else 'decreasing',
                'rsi_level': df.iloc[-1]['RSI']
            }
            
            # 根据市场类型调整分析提示
            if market_type in ['ETF', 'LOF']:
                prompt = f"""
                分析基金 {stock_code}：

                技术指标概要：
                {technical_summary}
                
                近14日交易数据：
                {recent_data}
                
                请分析该基金的技术面状况，包括：
                1. 趋势分析：判断基金当前的趋势方向
                2. 动量分析：基于RSI和交易量评估基金动量
                3. 支撑与阻力位：确定关键价格位
                4. 技术面总结
                5. 投资建议

                将分析结果格式化为JSON，像这样：
                {{
                    "trend_analysis": "趋势分析结果...",
                    "momentum_analysis": "动量分析结果...",
                    "support_resistance": "支撑阻力位分析...",
                    "technical_summary": "技术面总结...",
                    "investment_advice": "投资建议..."
                }}
                """
            else:
                prompt = f"""
                分析股票 {stock_code}：

                技术指标概要：
                {technical_summary}
                
                近14日交易数据：
                {recent_data}
                
                请分析该股票的技术面状况，包括：
                1. 趋势分析：当前趋势方向及强度
                2. 动量分析：基于MACD、RSI等指标
                3. 支撑与阻力位：关键价格位分析
                4. 成交量分析：交易量的变化及意义
                5. 波动性评估：ATR和波动率分析
                6. 技术面总结
                7. 投资建议：根据技术分析给出操作建议

                将分析结果格式化为JSON，像这样：
                {{
                    "trend_analysis": "趋势分析结果...",
                    "momentum_analysis": "动量分析结果...",
                    "support_resistance": "支撑阻力位分析...",
                    "volume_analysis": "成交量分析...",
                    "volatility_assessment": "波动性评估...",
                    "technical_summary": "技术面总结...",
                    "investment_advice": "投资建议..."
                }}
                """
            
            # 格式化API URL
            api_url = APIUtils.format_api_url(self.API_URL)
            
            # 准备请求数据
            request_data = {
                "model": self.API_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "stream": stream
            }
            
            # 准备请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.API_KEY}"
            }
            
            # 异步请求API
            async with httpx.AsyncClient(timeout=self.API_TIMEOUT) as client:
                # 记录请求
                logger.debug(f"发送AI请求: URL={api_url}, MODEL={self.API_MODEL}, STREAM={stream}")
                
                if stream:
                    # 流式响应处理
                    async with client.stream("POST", api_url, json=request_data, headers=headers) as response:
                        if response.status_code != 200:
                            error_text = await response.aread()
                            error_data = json.loads(error_text)
                            error_message = error_data.get('error', {}).get('message', '未知错误')
                            logger.error(f"AI API请求失败: {response.status_code} - {error_message}")
                            yield json.dumps({"error": f"API请求失败: {error_message}"})
                            return
                            
                        # 处理流式响应
                        buffer = ""
                        collected_messages = []
                        
                        async for chunk in response.aiter_text():
                            if chunk:
                                chunk_str = chunk.strip()
                                if chunk_str.startswith("data: "):
                                    chunk_str = chunk_str[6:]  # 去除"data: "前缀
                                    
                                if chunk_str == "[DONE]":
                                    continue
                                    
                                try:
                                    # 解析数据块
                                    chunk_data = json.loads(chunk_str)
                                    delta = chunk_data.get("choices", [{}])[0].get("delta", {})
                                    content = delta.get("content", "")
                                    
                                    if content:
                                        buffer += content
                                        # 尝试提取完整的JSON
                                        if buffer.strip().startswith("{") and buffer.strip().endswith("}"):
                                            try:
                                                result_json = json.loads(buffer)
                                                yield json.dumps({
                                                    "stock_code": stock_code,
                                                    "analysis": result_json
                                                })
                                                buffer = ""  # 重置缓冲区
                                            except json.JSONDecodeError:
                                                # JSON不完整，继续收集
                                                pass
                                        
                                        # 达到一定长度就输出
                                        if len(buffer) > 100:
                                            yield json.dumps({
                                                "stock_code": stock_code,
                                                "ai_analysis_chunk": buffer
                                            })
                                            collected_messages.append(buffer)
                                            buffer = ""
                                except json.JSONDecodeError:
                                    # 忽略无法解析的块
                                    continue
                        
                        # 处理最后的缓冲区
                        if buffer:
                            yield json.dumps({
                                "stock_code": stock_code,
                                "ai_analysis_chunk": buffer
                            })
                            collected_messages.append(buffer)
                        
                        # 尝试从整个内容中提取JSON
                        full_content = "".join(collected_messages)
                        
                        # 如果没有成功解析JSON，返回原始内容
                        if not full_content.strip().startswith("{"):
                            yield json.dumps({
                                "stock_code": stock_code,
                                "raw_analysis": full_content
                            })
                else:
                    # 非流式响应处理
                    response = await client.post(api_url, json=request_data, headers=headers)
                    
                    if response.status_code != 200:
                        error_data = response.json()
                        error_message = error_data.get('error', {}).get('message', '未知错误')
                        logger.error(f"AI API请求失败: {response.status_code} - {error_message}")
                        yield json.dumps({"error": f"API请求失败: {error_message}"})
                        return
                    
                    response_data = response.json()
                    analysis_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    try:
                        # 尝试解析JSON
                        analysis_json = json.loads(analysis_text)
                        yield json.dumps({
                            "stock_code": stock_code,
                            "analysis": analysis_json
                        })
                    except json.JSONDecodeError:
                        # 返回原始文本
                        yield json.dumps({
                            "stock_code": stock_code,
                            "raw_analysis": analysis_text
                        })
                        
            logger.info(f"完成对 {stock_code} 的AI分析")
                
        except Exception as e:
            logger.error(f"AI分析 {stock_code} 时出错: {str(e)}")
            logger.exception(e)
            yield json.dumps({"error": f"分析出错: {str(e)}"})
    
    def _truncate_json_for_logging(self, json_obj, max_length=500):
        """
        截断JSON对象以便记录日志
        
        Args:
            json_obj: JSON对象
            max_length: 最大长度
            
        Returns:
            截断后的字符串
        """
        json_str = json.dumps(json_obj, ensure_ascii=False)
        if len(json_str) <= max_length:
            return json_str
        return json_str[:max_length] + "..." 