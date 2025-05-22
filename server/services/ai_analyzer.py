import pandas as pd
import os
import json
import httpx
import re
from typing import AsyncGenerator
from dotenv import load_dotenv
from server.utils.logger import get_logger
from server.utils.api_utils import APIUtils
from datetime import datetime
import inspect
import asyncio

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
    
    async def get_ai_analysis(self, df: pd.DataFrame, stock_code: str, market_type: str = 'A', stream: bool = False, stock_name: str = None, sector: str = None) -> AsyncGenerator[str, None]:
        """
        对股票数据进行AI分析 (使用手动迭代处理流)
        Args:
            df: DataFrame containing stock data.
            stock_code: The stock code.
            market_type: Market type ('A', 'US', 'HK', 'ETF', 'LOF').
            stream: Whether to stream the response.
            stock_name: Optional stock name.
            sector: Optional sector information.
        """
        try:
            current_frame = inspect.currentframe()
            lineno_start = current_frame.f_lineno + 1 if current_frame else 0
            logger.info(f"L{lineno_start}: 开始AI分析 {stock_code}, 流式模式: {stream}")

            # 提取关键技术指标
            latest_data = df.iloc[-1]

            # --- Safely get basic indicators ---
            rsi = None
            price = None
            price_change = None
            try:
                rsi = latest_data.get('RSI')
                price = latest_data.get('Close')
                price_change = latest_data.get('Change')
            except Exception as data_get_e:
                current_frame = inspect.currentframe()
                lineno_get_err = current_frame.f_back.f_lineno if current_frame and current_frame.f_back else 0
                logger.error(f"L{lineno_get_err}: 获取基础指标 (RSI, Price, Change) 时出错", exc_info=True)
                yield json.dumps({"stock_code": stock_code,"error": f"获取基础指标时出错: {str(data_get_e)}","status": "error"})
                return
            # --- End Safely get basic indicators ---

            ma_trend = 'UP' if latest_data.get('MA5', 0) > latest_data.get('MA20', 0) else 'DOWN'
            macd = latest_data.get('MACD', 0)
            macd_signal = latest_data.get('MACD_Signal', 0)
            macd_signal_type = 'BUY' if macd > macd_signal else 'SELL'
            volume_ratio = latest_data.get('Volume_Ratio', 1)
            volume_status = 'HIGH' if volume_ratio > 1.5 else ('LOW' if volume_ratio < 0.5 else 'NORMAL')
            recent_data = df.tail(14).to_dict('records')

            # --- Safely create technical_summary ---
            technical_summary = {
                'trend': 'upward' if latest_data.get('MA5', 0) > latest_data.get('MA20', 0) else 'downward',
                'volatility': f"{latest_data.get('Volatility', 0):.2f}%", # Use get
                'volume_trend': 'increasing' if latest_data.get('Volume_Ratio', 1) > 1 else 'decreasing', # Use get
                'rsi_level': latest_data.get('RSI', 50.0) # Use get with default
            }
            lineno_summary = inspect.currentframe().f_lineno
            logger.debug(f"L{lineno_summary}: technical_summary created. Content (truncated): {self._truncate_json_for_logging(technical_summary)}")
            # --- End Safely create technical_summary ---

            # --- Prompt Creation ---
            prompt_intro_base = ""
            market_specific_name = stock_code # Default to stock_code

            if stock_name and stock_name.strip():
                market_specific_name = f"{stock_name.strip()} ({stock_code})"
            
            # Constructing the introductory part of the prompt
            if market_type in ['ETF', 'LOF']:
                prompt_intro_base = f"基金 {market_specific_name}"
                if sector and sector.strip():
                    prompt_intro_base += f", 类型: {sector.strip()}" # ETFs/LOFs might use 'type' or 'category' instead of 'sector'
            elif market_type == 'US':
                prompt_intro_base = f"美股 {market_specific_name}"
                if sector and sector.strip():
                    prompt_intro_base += f", 所处行业: {sector.strip()}"
            elif market_type == 'HK':
                prompt_intro_base = f"港股 {market_specific_name}"
                if sector and sector.strip():
                    prompt_intro_base += f", 所处行业: {sector.strip()}"
            else:  # A股 or default
                prompt_intro_base = f"A股 {market_specific_name}"
                if sector and sector.strip():
                    prompt_intro_base += f", 所处行业: {sector.strip()}"

            # Constructing the full prompt
            if market_type in ['ETF', 'LOF']:
                prompt = f"分析{prompt_intro_base}...\n技术指标概要: {technical_summary}\n近14日交易数据: {recent_data}\n请提供: 1.净值走势分析(支撑压力位) 2.成交量分析 3.风险评估(波动率/折溢价) 4.短期中期预测 5.关键价格位 6.申购赎回建议(止损)"
            elif market_type == 'US':
                 prompt = f"分析{prompt_intro_base}...\n技术指标概要: {technical_summary}\n近14日交易数据: {recent_data}\n请提供: 1.趋势分析(支撑压力位,美元) 2.成交量分析 3.风险评估(波动率/美股风险) 4.短期中期目标价(美元) 5.关键技术位 6.交易建议(止损) 7.相关投资主题或热点分析"
            elif market_type == 'HK':
                 prompt = f"分析{prompt_intro_base}...\n技术指标概要: {technical_summary}\n近14日交易数据: {recent_data}\n请提供: 1.趋势分析(支撑压力位,港币) 2.成交量分析 3.风险评估(波动率/港股风险) 4.短期中期目标价(港币) 5.关键技术位 6.交易建议(止损) 7.相关投资主题或热点分析"
            else: # A股
                # 获取概念板块信息
                concept_info = ""
                if hasattr(df, 'concepts') and df.concepts is not None and len(df.concepts) > 0:
                    concept_info = f"\n股票题材和概念板块: {', '.join(df.concepts)}"
                    logger.debug(f"添加题材概念信息到提示中: {concept_info}")
                
                prompt = f"分析{prompt_intro_base}...{concept_info}\n技术指标概要: {technical_summary}\n近14日交易数据: {recent_data}\n请提供: 1.趋势分析(支撑压力位) 2.成交量分析 3.风险评估(波动率) 4.短期中期目标价 5.关键技术位 6.交易建议(止损) 7.相关题材概念分析"
            # --- End Prompt Creation ---

            api_url = APIUtils.format_api_url(self.API_URL)
            request_data = { "model": self.API_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "stream": stream }
            headers = { "Content-Type": "application/json", "Authorization": f"Bearer {self.API_KEY}" }
            analysis_date = datetime.now().strftime("%Y-%m-%d")

            async with httpx.AsyncClient(timeout=self.API_TIMEOUT) as client:
                lineno_pre_req = inspect.currentframe().f_lineno + 1
                logger.debug(f"L{lineno_pre_req}: 发送AI请求前. Type(technical_summary)={type(technical_summary)}")
                # Initial yield with basic data
                yield json.dumps({ "stock_code": stock_code, "status": "analyzing", "rsi": rsi, "price": price, "price_change": price_change, "ma_trend": ma_trend, "macd_signal": macd_signal_type, "volume_status": volume_status, "analysis_date": analysis_date })

                lineno_pre_stream = inspect.currentframe().f_lineno
                logger.debug(f"L{lineno_pre_stream}: Before 'if stream:'. Type(technical_summary)={type(technical_summary)}")

                if stream:
                    lineno_in_stream = inspect.currentframe().f_lineno
                    logger.debug(f"L{lineno_in_stream}: 进入 'if stream:'. Type(technical_summary)={type(technical_summary)}")
                    buffer = ""
                    chunk_count = 0
                    iterator = None

                    try: # Outer try for stream connection, iteration, and final processing
                        async with client.stream("POST", api_url, json=request_data, headers=headers) as response:
                            lineno_resp = inspect.currentframe().f_lineno
                            logger.info(f"L{lineno_resp}: Got stream response, status: {response.status_code}")
                            if response.status_code != 200:
                                lineno_err_resp = inspect.currentframe().f_back.f_lineno
                                error_text = await response.aread()
                                logger.error(f"L{lineno_err_resp}: AI API 请求失败: {response.status_code}.Url: {api_url}.Request: {request_data}.Response: {error_text[:500]}")
                                yield json.dumps({ "stock_code": stock_code, "error": f"API请求失败: {response.status_code}", "status": "error" })
                                return

                            # --- Get Iterator ---
                            try:
                                lineno_get_iter = inspect.currentframe().f_lineno + 1
                                logger.info(f"L{lineno_get_iter}: Preparing to get stream iterator")
                                iterator = response.aiter_text()
                                logger.info(f"L{inspect.currentframe().f_lineno}: Got stream iterator")
                            except AttributeError as iter_init_ae:
                                logger.error(f"!!! L{inspect.currentframe().f_back.f_lineno}: AttributeError caught getting async iterator !!!")
                                logger.exception("Traceback (Iterator Creation):")
                                yield json.dumps({"stock_code": stock_code,"error": f"获取流迭代器错误: {str(iter_init_ae)}","status": "error"})
                                return
                            except Exception as iter_init_other_e:
                                logger.error(f"!!! L{inspect.currentframe().f_back.f_lineno}: Other exception caught getting async iterator: {type(iter_init_other_e).__name__} !!!", exc_info=True)
                                yield json.dumps({"stock_code": stock_code,"error": f"获取流迭代器错误: {str(iter_init_other_e)}","status": "error"})
                                return

                            if iterator is None:
                                logger.error(f"L{inspect.currentframe().f_lineno}: Iterator is None, stopping.")
                                yield json.dumps({"stock_code": stock_code,"error": "无法获取流数据","status": "error"})
                                return
                            # --- Iterator Obtained ---

                            # --- Manual Iteration Loop ---
                            logger.info(f"L{inspect.currentframe().f_lineno}: Starting manual iteration with while loop")
                            while True:
                                chunk = None
                                current_line_for_error = None
                                try:
                                    # Explicitly get the next chunk
                                    lineno_anext = inspect.currentframe().f_lineno + 1
                                    logger.debug(f"L{lineno_anext}: Calling await iterator.__anext__()")
                                    try:
                                        chunk = await asyncio.wait_for(iterator.__anext__(), timeout=30)
                                    except asyncio.TimeoutError:
                                        logger.error("AI流式分析超时，主动退出循环")
                                        break
                                    logger.debug(f">>> Manual Iteration: Got chunk (len={len(chunk)}) <<<")

                                    # --- Try processing the loop body ---
                                    try:
                                        if chunk:
                                            lines = chunk.strip().split('\n')
                                            for line in lines:
                                                current_line_for_error = line
                                                line = line.strip()
                                                if not line: continue
                                                if line.startswith("data: "): line = line[6:]

                                                lineno_proc = inspect.currentframe().f_lineno
                                                logger.debug(f"L{lineno_proc}: Processing line: {line[:100]}")
                                                content = self._extract_content_from_line(line) # Use refactored extract function

                                                if content:
                                                    chunk_count += 1
                                                    buffer += content
                                                    yield json.dumps({ "stock_code": stock_code, "ai_analysis_chunk": content, "status": "analyzing" })
                                                # No extensive error checks needed here as _extract handles them

                                        logger.debug("<<< Manual Iteration End: Chunk processed successfully <<<")

                                    except AttributeError as ae_body:
                                        logger.error(f"!!! L{inspect.currentframe().f_back.f_lineno}: AttributeError caught within MANUAL loop BODY !!!")
                                        logger.error(f"Chunk: {chunk[:200]}, Line: {current_line_for_error[:200] if current_line_for_error else 'N/A'}")
                                        logger.exception("Traceback (Manual Loop Body AE):")
                                        yield json.dumps({"stock_code": stock_code, "error": f"内部处理错误: {str(ae_body)}", "status": "error"})
                                        return
                                    except Exception as loop_e_body:
                                        logger.error(f"!!! L{inspect.currentframe().f_back.f_lineno}: Other exception caught within MANUAL loop BODY: {type(loop_e_body).__name__} !!!", exc_info=True)
                                        logger.error(f"Chunk: {chunk[:200]}, Line: {current_line_for_error[:200] if current_line_for_error else 'N/A'}")
                                        yield json.dumps({"stock_code": stock_code, "error": f"内部循环错误: {str(loop_e_body)}", "status": "error"})
                                        return
                                    # --- End Try processing the loop body ---

                                except StopAsyncIteration:
                                    # Normal exit from the iterator
                                    logger.info(f"L{inspect.currentframe().f_lineno}: StopAsyncIteration received, exiting loop normally.")
                                    break # Exit the while True loop
                                except AttributeError as anext_ae:
                                    # Catch AttributeError specifically from __anext__()
                                    logger.error(f"!!! L{inspect.currentframe().f_back.f_lineno}: AttributeError caught calling iterator.__anext__() !!!")
                                    logger.exception("Traceback (__anext__ call AE):")
                                    yield json.dumps({"stock_code": stock_code, "error": f"流迭代错误 (anext AE): {str(anext_ae)}", "status": "error"})
                                    return
                                except Exception as anext_other_e:
                                    # Catch any other error during __anext__()
                                    logger.error(f"!!! L{inspect.currentframe().f_back.f_lineno}: Other exception caught calling iterator.__anext__(): {type(anext_other_e).__name__} !!!", exc_info=True)
                                    yield json.dumps({"stock_code": stock_code, "error": f"流迭代错误 (anext Other): {str(anext_other_e)}", "status": "error"})
                                    return
                            # --- End of while True loop ---

                        # --- Processing after loop ---
                        lineno_post_loop = inspect.currentframe().f_lineno
                        logger.info(f"L{lineno_post_loop}: Exited manual iteration loop. Received {chunk_count} content chunks.")
                        logger.debug(f"L{lineno_post_loop}: After loop. Type(technical_summary)={type(technical_summary)}")
                        full_content = buffer
                        score = 50
                        recommendation = "观望"
                        try:
                            recommendation = self._extract_recommendation(full_content)
                            lineno_call_score = inspect.currentframe().f_lineno + 1
                            logger.debug(f"L{lineno_call_score}: PRE-CALL _calculate_analysis_score. Type(technical_summary)={type(technical_summary)}")
                            if isinstance(technical_summary, dict):
                                score = self._calculate_analysis_score(full_content, technical_summary)
                                logger.debug(f"L{inspect.currentframe().f_lineno}: Score calculated: {score}")
                            else:
                                logger.error(f"L{lineno_call_score}: ERROR - technical_summary is NOT dict!")
                        except Exception as final_proc_e:
                             lineno_final_err = inspect.currentframe().f_back.f_lineno
                             logger.error(f"L{lineno_final_err}: Error in final stream result processing", exc_info=True)

                        yield json.dumps({ "stock_code": stock_code, "status": "completed", "score": score, "recommendation": recommendation })
                        logger.info(f"L{inspect.currentframe().f_lineno}: Final stream result yielded.")

                    except Exception as stream_outer_e:
                        # Outer exception handler for stream block
                        lineno_outer_err = inspect.currentframe().f_back.f_lineno
                        logger.error(f"!!! L{lineno_outer_err}: Outer exception caught during stream handling! Type: {type(stream_outer_e).__name__} !!!", exc_info=True)
                        yield json.dumps({ "stock_code": stock_code, "error": f"流处理错误: {str(stream_outer_e)}", "status": "error" })
                        return
                else:
                    # --- Non-Streaming Path ---
                    lineno_nonstream = inspect.currentframe().f_lineno
                    logger.debug(f"L{lineno_nonstream}: Entering non-stream path. Type(technical_summary)={type(technical_summary)}")
                    response = await client.post(api_url, json=request_data, headers=headers)
                    lineno_nonstream_resp = inspect.currentframe().f_lineno
                    logger.info(f"L{lineno_nonstream_resp}: Got non-stream response, status: {response.status_code}")
                    
                    if response.status_code != 200:
                        error_message = '未知API错误'
                        try:
                            error_data = response.json()
                            if isinstance(error_data, dict):
                                error_content = error_data.get('error', {})
                                error_message = error_content.get('message', str(error_data)) if isinstance(error_content, dict) else str(error_content)
                            else: error_message = str(error_data)
                        except json.JSONDecodeError: error_message = response.text[:500]
                        logger.error(f"L{inspect.currentframe().f_back.f_lineno}: AI API请求失败 (non-stream): {response.status_code} - {error_message}")
                        yield json.dumps({ "stock_code": stock_code, "error": f"API请求失败: {error_message}", "status": "error" })
                        return
                        
                    try:
                        response_text = response.text 
                        response_data = json.loads(response_text) 
                        
                        analysis_text = ""
                        if isinstance(response_data, dict):
                            choices = response_data.get("choices")
                            if isinstance(choices, list) and choices:
                                message = choices[0].get("message")
                                if isinstance(message, dict):
                                    analysis_text = message.get("content", "")
                        
                        if not analysis_text:
                             logger.warning(f"L{inspect.currentframe().f_lineno}: Could not extract content via choices/message in non-stream.")
                             analysis_text = response_text 

                        recommendation = self._extract_recommendation(analysis_text or "")
                        score = 50
                        lineno_call_score_ns = inspect.currentframe().f_lineno + 1
                        logger.debug(f"L{lineno_call_score_ns}: PRE-CALL _calculate_analysis_score (non-stream). Type(technical_summary)={type(technical_summary)}")
                        if isinstance(technical_summary, dict):
                            score = self._calculate_analysis_score(analysis_text or "", technical_summary)
                            logger.debug(f"L{inspect.currentframe().f_lineno}: Score calculated (non-stream): {score}")
                        else:
                             logger.error(f"L{lineno_call_score_ns}: ERROR - technical_summary is NOT dict (non-stream)!")
                             
                        yield json.dumps({ "stock_code": stock_code, "status": "completed", "ai_analysis": analysis_text, "score": score, "recommendation": recommendation, "rsi": rsi, "price": price, "price_change": price_change, "ma_trend": ma_trend, "macd_signal": macd_signal_type, "volume_status": volume_status, "analysis_date": analysis_date })
                    except json.JSONDecodeError as json_e:
                         lineno_json_err_ns = inspect.currentframe().f_back.f_lineno
                         logger.error(f"L{lineno_json_err_ns}: Error decoding non-stream JSON response", exc_info=True)
                         yield json.dumps({ "stock_code": stock_code, "error": f"解析响应错误: {str(json_e)}", "status": "error" })
                    except Exception as non_stream_e:
                         lineno_proc_err_ns = inspect.currentframe().f_back.f_lineno
                         logger.error(f"L{lineno_proc_err_ns}: Error processing non-stream response", exc_info=True)
                         yield json.dumps({ "stock_code": stock_code, "error": f"处理响应错误: {str(non_stream_e)}", "status": "error" })

        except Exception as e:
            # Radically Simplified final exception handler
            lineno_top_err = inspect.currentframe().f_back.f_lineno if inspect.currentframe().f_back else inspect.currentframe().f_lineno
            exception_type = type(e).__name__
            # ONLY log type and traceback. Do NOT call str(e) here.
            logger.error(f"L{lineno_top_err}: AI分析顶层出错. 类型: {exception_type}", exc_info=True)

            try:
                yield json.dumps({
                    "stock_code": stock_code,
                    "error": f"分析顶层出错 ({exception_type})", # Report only type
                    "status": "error"
                })
            except Exception as yield_e:
                 logger.error(f"L{inspect.currentframe().f_lineno}: 发送顶层错误时再次出错: {str(yield_e)}")

    def _extract_recommendation(self, analysis_text: str) -> str:
        """从分析文本中提取投资建议"""
        # 查找投资建议部分
        investment_advice_pattern = r"##\s*投资建议\s*\n(.*?)(?:\n##|\Z)"
        match = re.search(investment_advice_pattern, analysis_text, re.DOTALL)
        
        if match:
            advice_text = match.group(1).strip()
            
            # 提取关键建议
            if "买入" in advice_text or "增持" in advice_text:
                return "买入"
            elif "卖出" in advice_text or "减持" in advice_text:
                return "卖出"
            elif "持有" in advice_text:
                return "持有"
            else:
                return "观望"
        
        return "观望"  # 默认建议
        
    def _calculate_analysis_score(self, analysis_text: str, technical_summary: dict) -> int:
        """计算分析评分"""
        score = 50  # 基础分数
        
        # 根据技术指标调整分数
        if technical_summary['trend'] == 'upward':
            score += 10
        else:
            score -= 10
            
        if technical_summary['volume_trend'] == 'increasing':
            score += 5
        else:
            score -= 5
            
        rsi = technical_summary['rsi_level']
        if rsi < 30:  # 超卖
            score += 15
        elif rsi > 70:  # 超买
            score -= 15
            
        # 根据分析文本中的关键词调整分数
        if "强烈买入" in analysis_text or "显著上涨" in analysis_text:
            score += 20
        elif "买入" in analysis_text or "看涨" in analysis_text:
            score += 10
        elif "强烈卖出" in analysis_text or "显著下跌" in analysis_text:
            score -= 20
        elif "卖出" in analysis_text or "看跌" in analysis_text:
            score -= 10
            
        # 确保分数在0-100范围内
        return max(0, min(100, score))
    
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

    def _extract_content_from_line(self, line: str) -> str | None:
        """
        从各种响应格式中提取内容，优化对碎片和非字典JSON的处理。
        
        Args:
            line: 响应行
            
        Returns:
            提取的内容字符串，如果无法提取或行无效则返回None
        """
        try:
            # 1. Common pre-processing and checks
            if not line or line.isspace(): return None
            if line == "[DONE]":
                logger.debug("Stream ended with [DONE].")
                return None
            # Ignore fragments of [DONE] marker explicitly if they are the whole line
            if line in ("[", "D", "O", "N", "E", "]"): 
                logger.debug(f"Ignoring likely fragment of [DONE]: '{line}'")
                return None
                
            # Remove SSE prefix
            if line.startswith("data: "): 
                line = line[len("data: "):].strip() # Strip whitespace after removing prefix
            if not line: return None # Ignore empty lines after prefix removal

            # Ignore likely single character fragments unless it starts JSON
            if len(line) == 1 and not line.startswith(('{', '[')):
                 logger.debug(f"Ignoring likely single character fragment: '{line}'")
                 return None

            # 2. Attempt General JSON Parsing
            try:
                chunk_data = json.loads(line)
                
                # Handle cases where API returns non-dict JSON (e.g., an int)
                if not isinstance(chunk_data, dict):
                    logger.warning(f"Parsed valid JSON, but it's not a dictionary (type: {type(chunk_data)}). Line: {line[:100]}")
                    return None # Treat as non-content

                # --- Extract content from known dictionary structures ---
                
                # OpenAI / Anthropic / Compatible Choices Structure
                choices = chunk_data.get("choices")
                if isinstance(choices, list) and choices:
                    choice = choices[0]
                    if isinstance(choice, dict):
                        finish_reason = choice.get("finish_reason")
                        if finish_reason == "stop":
                            logger.debug("Finish reason 'stop' detected in choices.")
                            return None 
                        delta = choice.get("delta")
                        if isinstance(delta, dict):
                            content = delta.get("content")
                            if isinstance(content, str) and content: 
                                logger.debug("[General Path] Extracted content from choices/delta.")
                                return content
                        message = choice.get("message")
                        if isinstance(message, dict):
                             content = message.get("content")
                             if isinstance(content, str) and content:
                                 logger.debug("[General Path] Extracted content from choices/message.")
                                 return content

                # Gemini Candidates Structure (Check even if not strictly Gemini API)
                candidates = chunk_data.get("candidates")
                if isinstance(candidates, list) and candidates:
                     candidate = candidates[0]
                     if isinstance(candidate, dict):
                         content_obj = candidate.get("content")
                         if isinstance(content_obj, dict):
                             parts = content_obj.get("parts")
                             if isinstance(parts, list) and parts:
                                 part = parts[0]
                                 if isinstance(part, dict):
                                     text = part.get("text")
                                     if isinstance(text, str) and text:
                                         logger.debug("[General Path] Extracted content from candidates structure.")
                                         return text

                # DeepSeek Structure / Other common fields
                output = chunk_data.get("output")
                if isinstance(output, str) and output: 
                    logger.debug("[General Path] Extracted content from DeepSeek 'output'.")
                    return output
                text = chunk_data.get("text")
                if isinstance(text, str) and text: 
                    logger.debug("[General Path] Extracted content from 'text' field.")
                    return text

                # If JSON parsed but no known content structure found
                logger.debug(f"JSON parsed, but no known content structure found: {line[:100]}")
                return None

            except json.JSONDecodeError:
                # Log JSON errors at DEBUG level normally to reduce noise
                # Log as WARNING only if it looks like it should have been JSON
                log_level = "warning" if line.startswith('{') or line.startswith('[') else "debug"
                getattr(logger, log_level)(f"JSON decode failed for line: {line[:100]}")
                return None 
            except Exception as e:
                 logger.error(f"Unexpected error during JSON parsing/extraction: {e}", exc_info=True)
                 return None

        except Exception as outer_e:
            # Catch-all for unexpected errors within the function itself
            logger.error(f"Unexpected error in _extract_content_from_line: {outer_e}", exc_info=True)
            return None