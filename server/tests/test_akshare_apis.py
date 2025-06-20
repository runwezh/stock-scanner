#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 akshare 接口连通性
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import traceback

def test_stock_list_apis():
    """测试股票列表获取接口"""
    print("=== 测试股票列表接口 ===")
    
    # 测试上海股票列表
    try:
        print("\n1. 测试上海股票列表...")
        sh_df = ak.stock_info_sh_name_code(symbol="主板A股")
        print(f"✅ 上海股票数量: {len(sh_df)}")
        print(f"   列名: {sh_df.columns.tolist()}")
        if len(sh_df) > 0:
            print(f"   示例数据:\n{sh_df.head(3)}")
    except Exception as e:
        print(f"❌ 上海股票列表获取失败: {e}")
        print(f"   详细错误: {traceback.format_exc()}")
    
    # 测试深圳股票列表
    try:
        print("\n2. 测试深圳股票列表...")
        sz_df = ak.stock_info_sz_name_code(symbol="A股列表")
        print(f"✅ 深圳股票数量: {len(sz_df)}")
        print(f"   列名: {sz_df.columns.tolist()}")
        if len(sz_df) > 0:
            print(f"   示例数据:\n{sz_df.head(3)}")
    except Exception as e:
        print(f"❌ 深圳股票列表获取失败: {e}")
        print(f"   详细错误: {traceback.format_exc()}")

def test_stock_data_api():
    """测试股票历史数据接口"""
    print("\n=== 测试股票历史数据接口 ===")
    
    test_stocks = ["000001", "000002", "600000"]
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
    end_date = datetime.now().strftime('%Y%m%d')
    
    for stock_code in test_stocks:
        try:
            print(f"\n测试股票 {stock_code}...")
            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
            print(f"✅ 股票 {stock_code} 数据行数: {len(df)}")
            print(f"   列名: {df.columns.tolist()}")
            if len(df) > 0:
                print(f"   最新数据: {df.iloc[-1]['日期']} 收盘价: {df.iloc[-1]['收盘']}")
        except Exception as e:
            print(f"❌ 股票 {stock_code} 数据获取失败: {e}")
            print(f"   详细错误: {traceback.format_exc()}")

def test_akshare_version():
    """测试 akshare 版本信息"""
    print("=== akshare 版本信息 ===")
    try:
        print(f"akshare 版本: {ak.__version__}")
    except:
        print("无法获取 akshare 版本信息")

if __name__ == "__main__":
    print("开始测试 akshare 接口连通性...\n")
    
    test_akshare_version()
    test_stock_list_apis()
    test_stock_data_api()
    
    print("\n测试完成！")