from flask import Flask, render_template, request, jsonify
from stock_analyzer import StockAnalyzer
from us_stock_service import USStockService
import threading
import os
import traceback
import requests

app = Flask(__name__)
analyzer = StockAnalyzer()
us_stock_service = USStockService()

@app.route('/')
def index():
    announcement = os.getenv('ANNOUNCEMENT_TEXT') or None
    # 获取默认API配置信息
    default_api_url = os.getenv('API_URL', '')
    default_api_model = os.getenv('API_MODEL', 'gpt-3.5-turbo')
    # 不传递API_KEY到前端，出于安全考虑
    return render_template('index.html', 
                          announcement=announcement,
                          default_api_url=default_api_url,
                          default_api_model=default_api_model)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        stock_codes = data.get('stock_codes', [])
        market_type = data.get('market_type', 'A') 
        
        # 获取自定义API配置
        custom_api_url = data.get('api_url')
        custom_api_key = data.get('api_key')
        custom_api_model = data.get('api_model')
        
        # 创建新的分析器实例，使用自定义配置
        custom_analyzer = StockAnalyzer(
            custom_api_url=custom_api_url,
            custom_api_key=custom_api_key,
            custom_api_model=custom_api_model
        )
        
        if not stock_codes:
            return jsonify({'error': '请输入代码'}), 400
            
        results = []
        for stock_code in stock_codes:
            try:
                # 使用自定义配置的分析器
                result = custom_analyzer.analyze_stock(stock_code.strip(), market_type)
                results.append(result)
            except Exception as e:
                print(f"分析股票 {stock_code} 失败: {str(e)}")
                print(f"详细错误: {traceback.format_exc()}")
                results.append({
                    'code': stock_code,
                    'error': f"分析失败: {str(e)}"
                })
            
        return jsonify({'results': results})
    except Exception as e:
        print(f"分析股票时出错: {str(e)}")
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
        print(f"搜索美股代码时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/test_api_connection', methods=['POST'])
def test_api_connection():
    """测试API连接"""
    try:
        data = request.json
        api_url = data.get('api_url')
        api_key = data.get('api_key')
        api_model = data.get('api_model')
        
        if not api_url:
            return jsonify({'error': '请提供API URL'}), 400
            
        if not api_key:
            return jsonify({'error': '请提供API Key'}), 400
            
        # 构建API URL
        test_url = api_url
        if not (api_url.endswith('/chat/completions') or api_url.endswith('/v1/chat/completions')):
            if api_url.endswith('/v1'):
                test_url = f"{api_url}/chat/completions"
            elif api_url.endswith('/'):
                test_url = f"{api_url}chat/completions"
            else:
                test_url = f"{api_url}/v1/chat/completions"
        
        # 发送测试请求
        response = requests.post(
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
            },
            timeout=10
        )
        
        # 检查响应
        if response.status_code == 200:
            return jsonify({'success': True, 'message': '连接成功'})
        else:
            error_message = response.json().get('error', {}).get('message', '未知错误')
            return jsonify({'success': False, 'message': f'连接失败: {error_message}', 'status_code': response.status_code}), 400
            
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'message': f'请求错误: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'测试连接时出错: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)