import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import os
from typing import Dict, List, Optional, Tuple, Any
from logger import get_logger

# 获取日志器
logger = get_logger()

class StockDataProvider:
    """
    异步股票数据提供服务
    负责获取股票、基金等金融产品的历史数据
    """
    
    def __init__(self):
        """初始化数据提供者服务"""
        logger.debug("初始化StockDataProvider")
    
    async def get_stock_data(self, stock_code: str, market_type: str = 'A', 
                            start_date: Optional[str] = None, 
                            end_date: Optional[str] = None) -> pd.DataFrame:
        """
        异步获取股票或基金数据
        
        Args:
            stock_code: 股票代码
            market_type: 市场类型，默认为'A'股
            start_date: 开始日期，格式YYYYMMDD，默认为一年前
            end_date: 结束日期，格式YYYYMMDD，默认为今天
            
        Returns:
            包含历史数据的DataFrame
        """
        # 使用线程池执行同步的akshare调用
        return await asyncio.to_thread(
            self._get_stock_data_sync, 
            stock_code, 
            market_type, 
            start_date, 
            end_date
        )
    
    def _get_stock_data_sync(self, stock_code: str, market_type: str = 'A', 
                           start_date: Optional[str] = None, 
                           end_date: Optional[str] = None) -> pd.DataFrame:
        """
        同步获取股票数据的实现
        将被异步方法调用
        """
        import akshare as ak
        
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
            
        try:
            # 验证股票代码格式
            if market_type == 'A':
                # 上海证券交易所股票代码以6开头
                # 深圳证券交易所股票代码以0或3开头
                # 科创板股票代码以688开头
                # 北京证券交易所股票代码以8开头
                valid_prefixes = ['0', '3', '6', '688', '8']
                valid_format = False
                
                for prefix in valid_prefixes:
                    if stock_code.startswith(prefix):
                        valid_format = True
                        break
                
                if not valid_format:
                    error_msg = f"无效的A股股票代码格式: {stock_code}。A股代码应以0、3、6、688或8开头"
                    logger.error(f"[股票代码格式错误] {error_msg}")
                    raise ValueError(error_msg)

                logger.debug(f"获取A股数据: {stock_code}")
                df = ak.stock_zh_a_hist(
                    symbol=stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )
                
            elif market_type in ['HK']:
                logger.debug(f"获取港股数据: {stock_code}")
                df = ak.stock_hk_daily(
                    symbol=stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )
                
            elif market_type in ['US']:
                logger.debug(f"获取美股数据: {stock_code}")
                df = ak.stock_us_daily(
                    symbol=stock_code,
                    adjust="qfq"
                )
                # 过滤日期
                df = df[(df.index >= start_date) & (df.index <= end_date)]
                
            elif market_type in ['ETF', 'LOF']:
                logger.debug(f"获取{market_type}基金数据: {stock_code}")
                df = ak.fund_etf_hist_sina(
                    symbol=stock_code,
                    start_date=start_date.replace('-', ''),
                    end_date=end_date.replace('-', '')
                )
                
            else:
                error_msg = f"不支持的市场类型: {market_type}"
                logger.error(f"[市场类型错误] {error_msg}")
                raise ValueError(error_msg)
                
            # 标准化列名
            if market_type == 'A':
                # 根据实际数据结构调整列名映射
                # 实际数据列：['日期', '股票代码', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
                df.columns = ['Date', 'Code', 'Open', 'Close', 'High', 'Low', 'Volume', 'Amount', 'Amplitude', 'Change_pct', 'Change', 'Turnover']
            elif market_type in ['HK', 'US']:
                # 根据实际情况调整
                df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Amount']
            elif market_type in ['ETF', 'LOF']:
                # 基金数据可能有不同的列
                df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Amount']
                
            # 确保日期列是日期类型
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
                
            # 确保按日期升序排序
            df.sort_index(inplace=True)
                
            logger.info(f"成功获取{market_type}数据 {stock_code}, 数据点数: {len(df)}")
            return df
            
        except Exception as e:
            error_msg = f"获取{market_type}数据失败 {stock_code}: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            raise Exception(error_msg)
            
    async def get_multiple_stocks_data(self, stock_codes: List[str], 
                                     market_type: str = 'A',
                                     start_date: Optional[str] = None, 
                                     end_date: Optional[str] = None,
                                     max_concurrency: int = 5) -> Dict[str, pd.DataFrame]:
        """
        异步批量获取多只股票数据
        
        Args:
            stock_codes: 股票代码列表
            market_type: 市场类型，默认为'A'股
            start_date: 开始日期，格式YYYYMMDD
            end_date: 结束日期，格式YYYYMMDD
            max_concurrency: 最大并发数，默认为5
            
        Returns:
            字典，键为股票代码，值为对应的DataFrame
        """
        # 使用信号量控制并发数
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def get_with_semaphore(code):
            async with semaphore:
                try:
                    return code, await self.get_stock_data(code, market_type, start_date, end_date)
                except Exception as e:
                    logger.error(f"获取股票 {code} 数据时出错: {str(e)}")
                    return code, None
        
        # 创建异步任务
        tasks = [get_with_semaphore(code) for code in stock_codes]
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks)
        
        # 构建结果字典，过滤掉失败的请求
        return {code: df for code, df in results if df is not None} 