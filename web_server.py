from flask import Flask, render_template, request, jsonify
from stock_analyzer import StockAnalyzer
from us_stock_service import USStockService
import threading
import logging
from logging.handlers import RotatingFileHandler
import traceback
import os

app = Flask(__name__)
analyzer = StockAnalyzer()
us_stock_service = USStockService()

# 配置日志
logging.basicConfig(level=logging.INFO)
handler = RotatingFileHandler('flask_app.log', maxBytes=10000000, backupCount=5)
handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))
app.logger.addHandler(handler)

@app.route('/')
def index():
    # 如果环境变量不存在或为空，返回 None
    announcement = os.getenv('ANNOUNCEMENT_TEXT') or None
    return render_template('index.html', announcement=announcement)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        stock_codes = data.get('stock_codes', [])
        market_type = data.get('market_type', 'A') 
        
        if not stock_codes:
            return jsonify({'error': '请输入代码'}), 400
            
        results = []
        for stock_code in stock_codes:
            try:
                result = analyzer.analyze_stock(stock_code.strip(), market_type)
                results.append(result)
            except Exception as e:
                app.logger.error(f"分析股票 {stock_code} 失败: {str(e)}")
                app.logger.error(f"详细错误: {traceback.format_exc()}")
                results.append({
                    'code': stock_code,
                    'error': f"分析失败: {str(e)}"
                })
            
        return jsonify({'results': results})
    except Exception as e:
        app.logger.error(f"处理请求失败: {str(e)}")
        app.logger.error(f"详细错误: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/search_us_stocks', methods=['GET'])
def search_us_stocks():
    try:
        keyword = request.args.get('keyword', '')
        if not keyword:
            return jsonify({'error': '请输入搜索关键词'}), 400
            
        results = us_stock_service.search_us_stocks(keyword)
        return jsonify({'results': results})
        
    except Exception as e:
        app.logger.error(f"搜索美股代码时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 将 host 设置为 '0.0.0.0' 使其支持所有网络接口访问
    app.run(host='0.0.0.0', port=8888, debug=True)

    