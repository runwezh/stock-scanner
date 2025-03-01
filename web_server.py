from flask import Flask, render_template, request, jsonify
from stock_analyzer import StockAnalyzer
import threading
import logging
from logging.handlers import RotatingFileHandler
import traceback

app = Flask(__name__)
analyzer = StockAnalyzer()

# 配置日志
logging.basicConfig(level=logging.INFO)
handler = RotatingFileHandler('flask_app.log', maxBytes=10000000, backupCount=5)
handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))
app.logger.addHandler(handler)

@app.route('/')
def index():
    return render_template('index.html')

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
            result = analyzer.analyze_stock(stock_code.strip(), market_type)
            results.append(result)
            
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 将 host 设置为 '0.0.0.0' 使其支持所有网络接口访问
    app.run(host='0.0.0.0', port=8888, debug=True)

    