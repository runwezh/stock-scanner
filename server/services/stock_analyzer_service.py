import json
import asyncio # Added for asyncio.sleep
from datetime import datetime
from typing import List, AsyncGenerator
from server.utils.logger import get_logger
from server.services.stock_data_provider import StockDataProvider
from server.services.technical_indicator import TechnicalIndicator
from server.services.stock_scorer import StockScorer
from server.services.ai_analyzer import AIAnalyzer

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
    
    @staticmethod
    def format_hk_code(code: str) -> str:
        """
        格式化港股股票代码：去除前缀，仅保留数字并补齐5位
        例如：'hk700' -> '00700', '0700' -> '00700', '388' -> '00388'
        """
        import re
        m = re.search(r'(\d{3,5})$', code)
        if m:
            return m.group(1).zfill(5)
        return code
    
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
        stock_name_to_pass = stock_code # Default to code
        sector_to_pass = None # Default to None

        try:
            # 港股代码格式化逻辑已移至 web 层，这里不再处理
            logger.info(f"开始分析股票: {stock_code}, 市场: {market_type}")
            
            # 获取股票数据
            df = await self.data_provider.get_stock_data(stock_code, market_type)
            
            # 尝试尽早获取股票名称和行业信息
            stock_name_to_pass = getattr(df, 'stock_name', stock_code)
            sector_to_pass = getattr(df, 'sector', None)
            logger.debug(f"Extracted for single analysis: stock_name='{stock_name_to_pass}', sector='{sector_to_pass}' for {stock_code}")

            # 检查是否有错误
            if hasattr(df, 'error'):
                error_msg = df.error
                logger.error(f"获取股票数据时出错: {error_msg}")
                yield json.dumps({
                    "stock_code": stock_code,
                    "stock_name": stock_name_to_pass, # 添加股票名称
                    "market_type": market_type,
                    "error": error_msg,
                    "status": "error"
                })
                return
            
            # 检查数据是否为空
            if df.empty:
                error_msg = f"获取到的股票 {stock_code} ({stock_name_to_pass}) 数据为空"
                logger.error(error_msg)
                yield json.dumps({
                    "stock_code": stock_code,
                    "stock_name": stock_name_to_pass, # 添加股票名称
                    "market_type": market_type,
                    "error": error_msg,
                    "status": "error"
                })
                return
            
            # 计算技术指标
            df_with_indicators = self.indicator.calculate_indicators(df)
            # 确保股票名称和行业信息在指标计算后仍然存在
            if not hasattr(df_with_indicators, 'stock_name') and stock_name_to_pass != stock_code:
                df_with_indicators.stock_name = stock_name_to_pass
            if not hasattr(df_with_indicators, 'sector') and sector_to_pass:
                df_with_indicators.sector = sector_to_pass
            
            # 重新获取，确保使用的是 df_with_indicators 上的属性（如果存在）
            current_stock_name = getattr(df_with_indicators, 'stock_name', stock_name_to_pass)
            current_sector = getattr(df_with_indicators, 'sector', sector_to_pass)

            # 计算评分
            score = self.scorer.calculate_score(df_with_indicators)
            recommendation = self.scorer.get_recommendation(score)
            
            # 获取最新数据
            latest_data = df_with_indicators.iloc[-1]
            previous_data = df_with_indicators.iloc[-2] if len(df_with_indicators) > 1 else latest_data
            
            # 价格变动绝对值
            price_change_value = latest_data['Close'] - previous_data['Close']
            
            # 优先使用原始数据中的涨跌幅(Change_pct)
            change_percent = latest_data.get('Change_pct')
            
            # 如果原始数据中没有涨跌幅，才进行计算
            if change_percent is None and previous_data['Close'] != 0:
                change_percent = (price_change_value / previous_data['Close']) * 100
            
            # 确定MA趋势
            ma_short = latest_data.get('MA5', 0)
            ma_medium = latest_data.get('MA20', 0)
            ma_long = latest_data.get('MA60', 0)
            
            if ma_short > ma_medium > ma_long:
                ma_trend = "UP"
            elif ma_short < ma_medium < ma_long:
                ma_trend = "DOWN"
            else:
                ma_trend = "FLAT"
                
            # 确定MACD信号
            macd = latest_data.get('MACD', 0)
            signal = latest_data.get('Signal', 0) # 假设 'Signal' 是 MACD 信号线的列名
            
            if macd > signal:
                macd_signal = "BUY"
            elif macd < signal:
                macd_signal = "SELL"
            else:
                macd_signal = "HOLD"
                
            # 确定成交量状态
            volume = latest_data.get('Volume', 0)
            volume_ma = latest_data.get('Volume_MA', 0)
            
            if volume > volume_ma * 1.5:
                volume_status = "HIGH"
            elif volume < volume_ma * 0.5:
                volume_status = "LOW"
            else:
                volume_status = "NORMAL"
                
            # 当前分析日期
            analysis_date = datetime.now().strftime('%Y-%m-%d')
            
            # 生成基本分析结果
            basic_result = {
                "stock_code": stock_code,
                "stock_name": current_stock_name, # 添加股票名称
                "market_type": market_type,
                "analysis_date": analysis_date,
                "score": score,
                "price": latest_data['Close'],
                "price_change_value": price_change_value,  # 价格变动绝对值
                "price_change": change_percent,  # 兼容旧版前端，传递涨跌幅
                "change_percent": change_percent,  # 涨跌幅百分比，新字段
                "ma_trend": ma_trend,
                "rsi": latest_data.get('RSI', 0),
                "macd_signal": macd_signal,
                "volume_status": volume_status,
                "recommendation": recommendation,
                "ai_analysis": "" # 初始化AI分析为空字符串
            }
            
            # 输出基本分析结果
            logger.info(f"基本分析结果 ({stock_code} - {current_stock_name}): {json.dumps(basic_result)}")
            yield json.dumps({**basic_result, "status": "processing_ai"}) # 更新状态
            
            # 使用AI进行深入分析
            ai_analysis_full_text = ""
            ai_analysis_error = False
            try:
                async for analysis_chunk_str in self.ai_analyzer.get_ai_analysis(
                    df_with_indicators, 
                    stock_code, 
                    market_type, 
                    stream,
                    stock_name=current_stock_name, # 传递股票名称
                    sector=current_sector if current_sector is not None else "" # 传递行业信息，如果为None则使用空字符串
                ):
                    try:
                        chunk_data = json.loads(analysis_chunk_str)
                        if "error" in chunk_data:
                            logger.error(f"AI分析股票 {stock_code} ({current_stock_name}) 时返回错误: {chunk_data['error']}")
                            ai_analysis_full_text = chunk_data['error']
                            ai_analysis_error = True
                            break # 出现错误，停止接收后续AI块
                        
                        current_text_chunk = chunk_data.get("ai_analysis_chunk", chunk_data.get("ai_analysis", ""))
                        if current_text_chunk:
                            ai_analysis_full_text += current_text_chunk
                        
                        # 流式输出AI分析块
                        yield json.dumps({
                            "stock_code": stock_code,
                            "stock_name": current_stock_name,
                            "market_type": market_type,
                            "ai_analysis_chunk": current_text_chunk,
                            "status": "analyzing_ai"
                        })
                    except json.JSONDecodeError:
                        logger.error(f"无法解析AI分析块: {analysis_chunk_str} for stock {stock_code} ({current_stock_name})")
                        ai_analysis_full_text += analysis_chunk_str # 尝试附加原始字符串
                        yield json.dumps({
                            "stock_code": stock_code,
                            "stock_name": current_stock_name,
                            "market_type": market_type,
                            "ai_analysis_chunk": analysis_chunk_str,
                            "status": "analyzing_ai",
                            "warning": "Malformed AI chunk"
                        })

                if ai_analysis_error or not ai_analysis_full_text.strip():
                    error_msg_ai = f"AI分析股票 {stock_code} ({current_stock_name}) 失败或返回空." if not ai_analysis_error else ai_analysis_full_text
                    final_status = "error"
                else:
                    final_status = "completed"
                
                # 输出最终结果（包含完整AI分析或错误信息）
                final_result_payload = {
                    **basic_result, # 复用之前的基本结果
                    "ai_analysis": ai_analysis_full_text.strip(),
                    "status": final_status
                }
                if ai_analysis_error: # 如果AI分析出错，也把错误信息放入error字段
                    final_result_payload["error"] = ai_analysis_full_text.strip()

                yield json.dumps(final_result_payload)

            except Exception as e_ai:
                error_msg = f"AI分析股票 {stock_code} ({current_stock_name}) 时发生意外错误: {str(e_ai)}"
                logger.error(error_msg)
                logger.exception(e_ai)
                yield json.dumps({
                    **basic_result, # 复用之前的基本结果
                    "error": error_msg,
                    "status": "error",
                    "ai_analysis": ai_analysis_full_text # 包含部分AI文本（如果有）
                })
                
            logger.info(f"完成股票分析: {stock_code} ({current_stock_name})")
            
        except Exception as e:
            error_msg = f"分析股票 {stock_code} ({stock_name_to_pass}) 时出错: {str(e)}"
            logger.error(error_msg)
            logger.exception(e) # 记录完整的异常堆栈
            yield json.dumps({
                "stock_code": stock_code,
                "stock_name": stock_name_to_pass, # 确保错误响应中也包含股票名称
                "market_type": market_type,
                "error": error_msg,
                "status": "error"
            })
    
    async def scan_stocks(self, stock_codes: List[str], market_type: str = 'A', min_score: int = 0, stream: bool = False) -> AsyncGenerator[str, None]:
        """
        批量扫描股票
        
        Args:
            stock_codes: 股票代码列表
            market_type: 市场类型
            min_score: 最低评分阈值 (Note: AI analysis will be attempted for all stocks regardless of this score as per new requirements)
            stream: 是否使用流式响应 (Note: this implementation inherently streams)
            
        Returns:
            异步生成器，生成扫描结果的JSON字符串
        """
        original_codes_count = len(stock_codes)
        # 使用 dict.fromkeys 保留顺序并去重 (Python 3.7+)
        unique_stock_codes = list(dict.fromkeys(stock_codes))
        duplicates_excluded_count = original_codes_count - len(unique_stock_codes)
        
        # 使用去重后的列表进行后续操作
        stock_codes_to_process = unique_stock_codes 
        
        if duplicates_excluded_count > 0:
            logger.info(f"原始股票列表包含 {original_codes_count} 个代码，去重后得到 {len(stock_codes_to_process)} 个唯一代码进行分析。排除了 {duplicates_excluded_count} 个重复代码。")
        else:
            logger.info(f"股票列表包含 {original_codes_count} 个唯一代码，无需去重。")

        logger.info(f"开始批量扫描 {len(stock_codes_to_process)} 只股票, 市场: {market_type}, 最低分: {min_score}")
        # 港股代码格式化逻辑已移至 web 层

        yield json.dumps({
            "stream_type": "batch_start", # 更新流类型名称
            "original_codes_count": original_codes_count,
            "unique_codes_to_analyze": len(stock_codes_to_process),
            "duplicates_excluded_count": duplicates_excluded_count,
            "market_type": market_type,
            "min_score": min_score
        })

        total_unique_codes_to_scan = len(stock_codes_to_process) # 基于去重后的列表
        total_analyzed_successfully = 0
        batch_size = 4

        for i in range(0, total_unique_codes_to_scan, batch_size):
            batch_codes = stock_codes_to_process[i:i + batch_size] # 从去重后的列表中取批次
            logger.info(f"正在处理批次: {batch_codes}")

            try:
                # 获取当前批次所有股票的数据
                batch_stock_data = await self.data_provider.get_multiple_stocks_data(batch_codes, market_type)
            except Exception as e:
                logger.error(f"获取批次 {batch_codes} 数据时发生严重错误: {str(e)}")
                for code_in_batch_on_error in batch_codes: # 确保使用批次内的代码
                    yield json.dumps({
                        "stock_code": code_in_batch_on_error,
                        "market_type": market_type,
                        "error": f"获取批次数据失败: {str(e)}",
                        "status": "error"
                    })
                if i + batch_size < total_unique_codes_to_scan: # Only sleep if there are more batches
                    await asyncio.sleep(2)
                continue # Move to the next batch

            for code in batch_codes:
                try:
                    # Extract stock_name early, use code as fallback. This will be used in all subsequent messages for this stock.
                    # df is from batch_stock_data.get(code), which should have stock_name if stock_data_provider worked.
                    # df_with_indicators will be used later for AI, but stock_name should be on df already.
                    stock_name_early = getattr(batch_stock_data.get(code), 'stock_name', code) # Fallback to code if name not on df

                    yield json.dumps({
                        "stock_code": code,
                        "stock_name": stock_name_early,
                        "market_type": market_type,
                        "status": "processing_data"
                    })

                    df = batch_stock_data.get(code) # df is already retrieved
                    if df is None or df.empty or hasattr(df, 'error'):
                        error_msg = f"获取股票 {code} 数据为空或出错: {getattr(df, 'error', '未知错误') if hasattr(df, 'error') else '数据为空'}"
                        logger.error(error_msg)
                        yield json.dumps({
                            "stock_code": code,
                            "stock_name": stock_name_early, # Use extracted name
                            "market_type": market_type,
                            "error": error_msg,
                            "status": "error"
                        })
                        continue

                    # 计算技术指标
                    try:
                        df_with_indicators = self.indicator.calculate_indicators(df)
                        # Ensure stock_name is carried over if calculate_indicators creates a new df without attributes
                        if not hasattr(df_with_indicators, 'stock_name') and hasattr(df, 'stock_name'):
                            df_with_indicators.stock_name = df.stock_name
                    except Exception as e:
                        error_msg = f"计算股票 {code} 技术指标时出错: {str(e)}"
                        logger.error(error_msg)
                        yield json.dumps({
                            "stock_code": code,
                            "stock_name": stock_name_early, # Use extracted name
                            "market_type": market_type,
                            "error": error_msg,
                            "status": "error"
                        })
                        continue
                    
                    # Re-fetch stock_name from df_with_indicators, as it's the source for AI. Fallback to stock_name_early.
                    current_stock_name = getattr(df_with_indicators, 'stock_name', stock_name_early)

                    # 计算评分
                    score = self.scorer.calculate_score(df_with_indicators)
                    recommendation = self.scorer.get_recommendation(score)

                    # 获取最新数据用于基础分析
                    latest_data = df_with_indicators.iloc[-1]
                    previous_data = df_with_indicators.iloc[-2] if len(df_with_indicators) > 1 else latest_data
                    price_change_value = latest_data['Close'] - previous_data['Close']
                    change_percent = latest_data.get('Change_pct')
                    if change_percent is None and previous_data['Close'] != 0:
                        change_percent = (price_change_value / previous_data['Close']) * 100
                    
                    ma_short = latest_data.get('MA5', 0)
                    ma_medium = latest_data.get('MA20', 0)
                    ma_long = latest_data.get('MA60', 0)
                    ma_trend = "UP" if ma_short > ma_medium > ma_long else ("DOWN" if ma_short < ma_medium < ma_long else "FLAT")
                    
                    macd_val = latest_data.get('MACD', 0) # Renamed macd to macd_val to avoid conflict
                    signal_line = latest_data.get('Signal', 0) 
                    macd_signal_val = "BUY" if macd_val > signal_line else ("SELL" if macd_val < signal_line else "HOLD")

                    volume = latest_data.get('Volume', 0)
                    volume_ma = latest_data.get('Volume_MA', 0)
                    volume_status_val = "HIGH" if volume > volume_ma * 1.5 else ("LOW" if volume < volume_ma * 0.5 else "NORMAL")

                    basic_analysis_result = {
                        "stock_code": code,
                        "stock_name": current_stock_name, 
                        "market_type": market_type,
                        "analysis_date": datetime.now().strftime('%Y-%m-%d'),
                        "score": score,
                        "price": latest_data['Close'],
                        "price_change": price_change_value, 
                        "change_percent": change_percent,
                        "ma_trend": ma_trend,
                        "rsi": latest_data.get('RSI', 0),
                        "macd_signal": macd_signal_val,
                        "volume_status": volume_status_val,
                        "recommendation": recommendation,
                        "status": "processing_ai" 
                    }
                    yield json.dumps(basic_analysis_result)

                    # AI 分析
                    ai_analysis_full_text = ""
                    ai_analysis_error = False
                    try:
                        sector_to_pass = getattr(df_with_indicators, 'sector', None)
                        
                        logger.debug(f"Extracted for AI: stock_name='{current_stock_name}', sector='{sector_to_pass}' for {code}")

                        async for analysis_chunk_str in self.ai_analyzer.get_ai_analysis(
                            df_with_indicators,
                            code,
                            market_type,
                            stream=True, # Explicitly True for batch
                            stock_name=current_stock_name,
                            sector=sector_to_pass if sector_to_pass is not None else ""
                        ):
                            try:
                                chunk_data = json.loads(analysis_chunk_str)
                                if "error" in chunk_data:
                                    logger.error(f"AI分析股票 {code} ({current_stock_name}) 时返回错误: {chunk_data['error']}")
                                    ai_analysis_full_text = chunk_data['error']
                                    ai_analysis_error = True
                                    break
                                
                                current_text_chunk = chunk_data.get("ai_analysis_chunk", chunk_data.get("ai_analysis", "")) 
                                if current_text_chunk: 
                                     ai_analysis_full_text += current_text_chunk
                                
                                yield json.dumps({
                                    "stock_code": code,
                                    "stock_name": current_stock_name, 
                                    "market_type": market_type,
                                    "ai_analysis_chunk": current_text_chunk, 
                                    "status": "analyzing_ai"
                                })
                            except json.JSONDecodeError:
                                logger.error(f"无法解析AI分析块: {analysis_chunk_str} for stock {code} ({current_stock_name})")
                                ai_analysis_full_text += analysis_chunk_str 
                                yield json.dumps({
                                    "stock_code": code,
                                    "stock_name": current_stock_name, 
                                    "market_type": market_type,
                                    "ai_analysis_chunk": analysis_chunk_str, 
                                    "status": "analyzing_ai",
                                    "warning": "Malformed AI chunk"
                                })

                        if ai_analysis_error or not ai_analysis_full_text.strip():
                            error_msg_ai = f"AI分析股票 {code} ({current_stock_name}) 失败或返回空." if not ai_analysis_error else ai_analysis_full_text
                            final_ai_payload = {
                                "stock_code": code,
                                "stock_name": current_stock_name, 
                                "market_type": market_type,
                                "error": error_msg_ai,
                                "status": "error",
                                "ai_analysis": ai_analysis_full_text.strip() # Use "ai_analysis" for partial/error text too
                            }
                            # Merge with basic_analysis_result if needed, but ensure error status is primary
                            yield json.dumps({**basic_analysis_result, **final_ai_payload, "status": "error", "error": error_msg_ai})

                        else:
                            final_result = {
                                **basic_analysis_result, 
                                "ai_analysis": ai_analysis_full_text.strip(), 
                                "status": "completed"
                            }
                            yield json.dumps(final_result)
                            total_analyzed_successfully += 1
                            
                    except Exception as e_ai:
                        error_msg = f"AI分析股票 {code} ({current_stock_name}) 时发生意外错误: {str(e_ai)}"
                        logger.error(error_msg)
                        logger.exception(e_ai)
                        yield json.dumps({
                            **basic_analysis_result, # Start with basic result
                            "stock_name": current_stock_name, # Ensure name is present
                            "error": error_msg,
                            "status": "error",
                            "ai_analysis": ai_analysis_full_text.strip() # Include partial AI text if any
                        })

                except Exception as e_stock:
                    error_msg = f"处理股票 {code} 时发生意外错误: {str(e_stock)}"
                    logger.error(error_msg)
                    logger.exception(e_stock)
                    yield json.dumps({
                        "stock_code": code,
                        "stock_name": stock_name_early if 'stock_name_early' in locals() else code,
                        "market_type": market_type,
                        "error": error_msg,
                        "status": "error"
                    })
            
            if i + batch_size < total_unique_codes_to_scan: 
                logger.info(f"批次 {batch_codes} 处理完成，暂停2秒...")
                await asyncio.sleep(2)

        # 更新最终的总结信息
        final_summary_data = {
            "stream_type": "batch_summary",
            "scan_completed": True,
            "original_codes_count": original_codes_count,
            "duplicates_excluded_count": duplicates_excluded_count,
            "unique_codes_processed_count": total_unique_codes_to_scan, 
            "total_analyzed_successfully": total_analyzed_successfully
        }
        yield json.dumps(final_summary_data)
        logger.info(
            f"完成所有股票的批量扫描和分析。原始请求代码数: {original_codes_count}, "
            f"排除重复代码数: {duplicates_excluded_count}, "
            f"实际处理独特代码数: {total_unique_codes_to_scan}, "
            f"成功分析数: {total_analyzed_successfully}"
        )

# Global exception handler for the entire scan_stocks method (optional, but good practice)
# This was the original structure, so keeping it to catch overarching issues.
# However, individual stock errors are now handled within the loops.
# It might be redundant if all specific errors are caught inside.
# For now, let's keep it as a safety net.
        # except Exception as e:
        #     error_msg = f"批量扫描股票时发生未捕获的全局错误: {str(e)}"
        #     logger.error(error_msg)
        #     logger.exception(e)
        #     yield json.dumps({"error": error_msg, "status": "error", "scan_aborted": True})
