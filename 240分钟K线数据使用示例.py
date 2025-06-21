#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
240分钟K线数据使用示例
"""

import asyncio
from datetime import datetime, timedelta
from server.services.stock_data_provider import StockDataProvider

async def demo_240min_data():
    """演示如何获取240分钟K线数据"""
    
    # 创建数据提供者实例
    provider = StockDataProvider()
    
    # 设置时间范围（最近15天）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=15)
    
    # 格式化日期
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
    
    print("=" * 60)
    print("📊 240分钟K线数据获取演示")
    print("=" * 60)
    
    # 测试股票列表
    test_stocks = ["000001", "000002", "600036", "600519"]
    
    for stock_code in test_stocks:
        print(f"\n🔍 正在获取股票 {stock_code} 的240分钟K线数据...")
        
        try:
            # 获取240分钟K线数据
            df = await provider.get_stock_minute_data(
                stock_code=stock_code,
                period="240",  # 240分钟（4小时）
                start_date=start_date_str,
                end_date=end_date_str,
                market_type="A"
            )
            
            # 检查是否有错误
            if hasattr(df, 'error'):
                print(f"❌ 获取数据失败: {df.error}")
                continue
                
            if df.empty:
                print(f"⚠️  股票 {stock_code} 无240分钟数据")
                continue
                
            print(f"✅ 成功获取 {len(df)} 条240分钟K线数据")
            print(f"📅 时间范围: {df.index.min()} 至 {df.index.max()}")
            
            # 显示数据统计
            print(f"📈 价格统计:")
            print(f"   - 最高价: {df['high'].max():.2f}")
            print(f"   - 最低价: {df['low'].min():.2f}")
            print(f"   - 平均收盘价: {df['close'].mean():.2f}")
            print(f"   - 总成交量: {df['volume'].sum():,.0f}")
            print(f"   - 总成交额: {df['amount'].sum():,.0f}")
            
            # 显示最近几条数据
            print(f"\n📋 最近3条240分钟K线数据:")
            recent_data = df.tail(3)
            for idx, row in recent_data.iterrows():
                print(f"   {idx}: 开盘={row['open']:.2f}, "
                      f"最高={row['high']:.2f}, "
                      f"最低={row['low']:.2f}, "
                      f"收盘={row['close']:.2f}, "
                      f"成交量={row['volume']:,.0f}")
                
        except Exception as e:
            print(f"❌ 处理股票 {stock_code} 时出错: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 240分钟K线数据应用场景:")
    print("   • 中长期趋势分析")
    print("   • 日内波动模式识别")
    print("   • 支撑阻力位确认")
    print("   • 量价关系分析")
    print("   • 量化策略回测")
    print("=" * 60)

async def compare_different_periods():
    """比较不同时间周期的K线数据"""
    
    provider = StockDataProvider()
    stock_code = "000001"  # 平安银行
    
    # 设置较短的时间范围用于比较
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
    
    print("\n" + "=" * 60)
    print(f"📊 不同时间周期K线数据比较 - {stock_code}")
    print("=" * 60)
    
    # 测试不同周期
    periods = ["60", "120", "240"]
    period_names = {"60": "60分钟(1小时)", "120": "120分钟(2小时)", "240": "240分钟(4小时)"}
    
    for period in periods:
        try:
            df = await provider.get_stock_minute_data(
                stock_code=stock_code,
                period=period,
                start_date=start_date_str,
                end_date=end_date_str
            )
            
            if hasattr(df, 'error') or df.empty:
                print(f"⚠️  {period_names[period]}: 无数据")
                continue
                
            print(f"📈 {period_names[period]}:")
            print(f"   - 数据点数: {len(df)}")
            print(f"   - 时间跨度: {df.index.max() - df.index.min()}")
            print(f"   - 价格波动: {((df['high'].max() - df['low'].min()) / df['close'].mean() * 100):.2f}%")
            
        except Exception as e:
            print(f"❌ {period_names[period]} 数据获取失败: {str(e)}")

if __name__ == "__main__":
    # 运行240分钟数据演示
    asyncio.run(demo_240min_data())
    
    # 运行不同周期比较
    asyncio.run(compare_different_periods())
