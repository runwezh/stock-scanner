import pandas as pd
import numpy as np
import asyncio
import json
from typing import Dict, List, Optional, Tuple, Any, AsyncGenerator
from logger import get_logger
from services.stock_data_provider import StockDataProvider
from services.technical_indicator import TechnicalIndicator
from services.stock_scorer import StockScorer
from services.ai_analyzer import AIAnalyzer

# 获取日志器
logger = get_logger()

class StockAnalyzerService:
    """
    股票分析服务
    作为门面类协调数据提供、指标计算、评分和AI分析等组件
    """
    
    def __init__(self, custom_api_url=None, custom_api_key=None, custom_api_model=None, custom_api_timeout=None):
        """
        初始化股票分析服务
        
        Args:
            custom_api_url: 自定义API URL
            custom_api_key: 自定义API密钥
            custom_api_model: 自定义API模型
            custom_api_timeout: 自定义API超时时间
        """
        # 初始化各个组件
        self.data_provider = StockDataProvider()
        self.indicator = TechnicalIndicator()
        self.scorer = StockScorer()
        self.ai_analyzer = AIAnalyzer(
            custom_api_url=custom_api_url,
            custom_api_key=custom_api_key,
            custom_api_model=custom_api_model,
            custom_api_timeout=custom_api_timeout
        )
        
        logger.info("初始化StockAnalyzerService完成")
    
    async def analyze_stock(self, stock_code: str, market_type: str = 'A', stream: bool = False) -> AsyncGenerator[str, None]:
        """
        分析单只股票
        
        Args:
            stock_code: 股票代码
            market_type: 市场类型，默认为'A'股
            stream: 是否使用流式响应
            
        Returns:
            异步生成器，生成分析结果的JSON字符串
        """
        try:
            logger.info(f"开始分析股票: {stock_code}, 市场: {market_type}")
            
            # 获取股票数据
            df = await self.data_provider.get_stock_data(stock_code, market_type)
            
            # 计算技术指标
            df_with_indicators = self.indicator.calculate_indicators(df)
            
            # 计算评分
            score = self.scorer.calculate_score(df_with_indicators)
            recommendation = self.scorer.get_recommendation(score)
            
            # 生成基本分析结果
            basic_result = {
                "stock_code": stock_code,
                "score": score,
                "recommendation": recommendation,
                "data_point_count": len(df),
                "market_type": market_type
            }
            
            # 输出基本分析结果
            logger.info(f"基本分析结果: {json.dumps(basic_result)}")
            yield json.dumps(basic_result)
            
            # 使用AI进行深入分析
            async for analysis_chunk in self.ai_analyzer.get_ai_analysis(df_with_indicators, stock_code, market_type, stream):
                yield analysis_chunk
                
            logger.info(f"完成股票分析: {stock_code}")
            
        except Exception as e:
            error_msg = f"分析股票 {stock_code} 时出错: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            yield json.dumps({"error": error_msg})
    
    async def scan_stocks(self, stock_codes: List[str], market_type: str = 'A', min_score: int = 0, stream: bool = False) -> AsyncGenerator[str, None]:
        """
        批量扫描股票
        
        Args:
            stock_codes: 股票代码列表
            market_type: 市场类型
            min_score: 最低评分阈值
            stream: 是否使用流式响应
            
        Returns:
            异步生成器，生成扫描结果的JSON字符串
        """
        try:
            logger.info(f"开始批量扫描 {len(stock_codes)} 只股票, 市场: {market_type}")
            
            # 输出初始状态
            yield json.dumps({
                "status": "scanning",
                "total_stocks": len(stock_codes),
                "market_type": market_type,
                "min_score": min_score
            })
            
            # 批量获取股票数据
            stock_data_dict = await self.data_provider.get_multiple_stocks_data(stock_codes, market_type)
            
            # 计算技术指标
            stock_with_indicators = {}
            for code, df in stock_data_dict.items():
                try:
                    stock_with_indicators[code] = self.indicator.calculate_indicators(df)
                except Exception as e:
                    logger.error(f"计算 {code} 技术指标时出错: {str(e)}")
            
            # 评分股票
            results = self.scorer.batch_score_stocks(stock_with_indicators)
            
            # 过滤低于最低评分的股票
            filtered_results = [r for r in results if r[1] >= min_score]
            
            # 输出评分结果
            yield json.dumps({
                "scan_results": [
                    {
                        "stock_code": code,
                        "score": score,
                        "recommendation": rec
                    } for code, score, rec in filtered_results
                ],
                "total_matched": len(filtered_results),
                "total_scanned": len(results)
            })
            
            # 如果需要进一步分析，对评分较高的股票进行AI分析
            if stream and filtered_results:
                top_stocks = filtered_results[:3]  # 只分析前3只评分最高的股票
                
                for stock_code, score, _ in top_stocks:
                    df = stock_with_indicators.get(stock_code)
                    if df is not None:
                        # 输出正在分析的股票信息
                        yield json.dumps({
                            "analyzing": stock_code,
                            "score": score
                        })
                        
                        # AI分析
                        async for analysis_chunk in self.ai_analyzer.get_ai_analysis(df, stock_code, market_type, stream):
                            yield analysis_chunk
            
            # 输出扫描完成信息
            yield json.dumps({
                "status": "completed",
                "total_scanned": len(results),
                "total_matched": len(filtered_results)
            })
            
            logger.info(f"完成批量扫描 {len(stock_codes)} 只股票, 符合条件: {len(filtered_results)}")
            
        except Exception as e:
            error_msg = f"批量扫描股票时出错: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            yield json.dumps({"error": error_msg}) 