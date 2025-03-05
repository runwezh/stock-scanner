import akshare as ak
import pandas as pd

class FundService:
    def search_funds(self, keyword, market_type='ETF'):
        """
        搜索基金代码
        :param keyword: 搜索关键词
        :return: 匹配的基金列表
        """
        try:
            # 获取ETF和LOF数据
            if market_type == 'ETF':
                df = ak.fund_etf_spot_em()
            else:
                df = ak.fund_lof_spot_em()
            
            # 转换列名
            df = df.rename(columns={
                "代码": "symbol",
                "名称": "name",
                "最新价": "price",
                "涨跌额": "price_change",
                "涨跌幅": "price_change_percent",
                "成交量": "volume",
                "流通市值": "market_value",
                "总市值": "total_value",
                "基金折价率": "discount_rate",
            })
            
            # 模糊匹配搜索（同时匹配代码和名称）
            mask = (df['name'].str.contains(keyword, case=False, na=False) | 
                   df['symbol'].str.contains(keyword, case=False, na=False))
            results = df[mask]
            
            # 格式化返回结果并处理 NaN 值
            formatted_results = []
            for _, row in results.iterrows():
                formatted_results.append({
                    'name': row['name'] if pd.notna(row['name']) else '',
                    'symbol': str(row['symbol']) if pd.notna(row['symbol']) else '',
                    'price': float(row['price']) if pd.notna(row['price']) else 0.0,
                    'volume': float(row['volume']) if pd.notna(row['volume']) else 0.0,
                    'market_value': float(row['market_value']) if pd.notna(row['market_value']) else 0.0,
                    'total_value': float(row['total_value']) if pd.notna(row['total_value']) else 0.0,
                })
                
            return formatted_results
            
        except Exception as e:
            raise Exception(f"搜索基金代码失败: {str(e)}")