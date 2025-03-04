import akshare as ak
import pandas as pd

class USStockService:
        
    def search_us_stocks(self, keyword):
        """
        搜索美股代码
        :param keyword: 搜索关键词
        :return: 匹配的股票列表
        """
        try:
            # 获取美股数据
            df = ak.stock_us_spot_em()
            
            # 转换列名
            df = df.rename(columns={
                "序号": "index",
                "名称": "name",
                "最新价": "price",
                "涨跌额": "price_change",
                "涨跌幅": "price_change_percent",
                "开盘价": "open",
                "最高价": "high",
                "最低价": "low",
                "昨收价": "pre_close",
                "总市值": "market_value",
                "市盈率": "pe_ratio",
                "成交量": "volume",
                "成交额": "turnover",
                "振幅": "amplitude",
                "换手率": "turnover_rate",
                "代码": "symbol"
            })
            
            # 模糊匹配搜索
            mask = df['name'].str.contains(keyword, case=False, na=False)
            results = df[mask]
            
            # 格式化返回结果并处理 NaN 值
            formatted_results = []
            for _, row in results.iterrows():
                formatted_results.append({
                    'name': row['name'] if pd.notna(row['name']) else '',
                    'symbol': str(row['symbol']) if pd.notna(row['symbol']) else '',
                    'price': float(row['price']) if pd.notna(row['price']) else 0.0,
                    'market_value': float(row['market_value']) if pd.notna(row['market_value']) else 0.0
                })
                
            return formatted_results
            
        except Exception as e:
            raise Exception(f"搜索美股代码失败: {str(e)}")