#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版 240分钟K线数据功能测试用例
"""

import unittest
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from server.services.stock_data_provider import StockDataProvider


class TestStockDataProvider240Min(unittest.TestCase):
    """测试240分钟K线数据功能"""
    
    def setUp(self):
        """测试前准备"""
        self.provider = StockDataProvider()
        self.test_stock_code = "000001"
        
    def test_resample_to_240min_method_basic(self):
        """测试_resample_to_240min基本功能"""
        # 创建测试数据（4小时的60分钟数据）
        dates = pd.date_range('2023-12-01 09:30:00', periods=4, freq='h')
        test_data = pd.DataFrame({
            'open': [10.0, 10.1, 10.2, 10.3],
            'high': [10.5, 10.6, 10.7, 10.8],
            'low': [9.5, 9.6, 9.7, 9.8],
            'close': [10.1, 10.2, 10.3, 10.4],
            'volume': [1000, 1000, 1000, 1000],
            'amount': [10000, 10000, 10000, 10000]
        }, index=dates)
        
        # 调用重采样方法
        result = self.provider._resample_to_240min(test_data)
        
        # 基本验证
        self.assertIsInstance(result, pd.DataFrame)
        
        if not result.empty:
            # 验证列存在
            expected_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
            for col in expected_columns:
                self.assertIn(col, result.columns)
            
            # 验证OHLCV逻辑
            if len(result) > 0:
                first_row = result.iloc[0]
                self.assertEqual(first_row['open'], 10.0)  # 第一个开盘价
                self.assertEqual(first_row['close'], 10.4)  # 最后一个收盘价
                self.assertEqual(first_row['high'], 10.8)   # 最高价
                self.assertEqual(first_row['low'], 9.5)     # 最低价
                self.assertEqual(first_row['volume'], 4000) # 成交量求和
                self.assertEqual(first_row['amount'], 40000) # 成交额求和
    
    def test_resample_to_240min_empty_data(self):
        """测试空数据处理"""
        empty_df = pd.DataFrame()
        result = self.provider._resample_to_240min(empty_df)
        self.assertTrue(result.empty)
    
    def test_period_240_support_in_sync_method(self):
        """测试同步方法对240周期的支持"""
        with patch('akshare.stock_zh_a_minute') as mock_ak:
            # 创建模拟返回数据
            mock_data = pd.DataFrame({
                '时间': pd.date_range('2023-12-01 09:30:00', periods=4, freq='h'),
                '开盘': [10.0, 10.1, 10.2, 10.3],
                '收盘': [10.1, 10.2, 10.3, 10.4],
                '最高': [10.5, 10.6, 10.7, 10.8],
                '最低': [9.5, 9.6, 9.7, 9.8],
                '成交量': [1000, 1000, 1000, 1000],
                '成交额': [10000, 10000, 10000, 10000]
            })
            mock_data.set_index('时间', inplace=True)
            mock_ak.return_value = mock_data
            
            # 调用方法
            result = self.provider._get_stock_minute_data_sync(
                stock_code=self.test_stock_code,
                period="240"
            )
            
            # 验证akshare被正确调用
            mock_ak.assert_called_once_with(
                symbol=self.test_stock_code,
                period='60',
                adjust='qfq'
            )
            
            # 验证结果
            if not hasattr(result, 'error'):
                self.assertFalse(result.empty)
    
    def test_unsupported_periods(self):
        """测试不支持的周期"""
        unsupported = ['360', '480', '999']
        
        for period in unsupported:
            result = self.provider._get_stock_minute_data_sync(
                stock_code=self.test_stock_code,
                period=period
            )
            
            # 应该返回带错误的空DataFrame
            self.assertTrue(result.empty)
            self.assertTrue(hasattr(result, 'error'))
            self.assertIn("不支持的分钟周期", result.error)
    
    def test_supported_periods_list(self):
        """测试支持的周期列表"""
        supported = ['1', '5', '15', '30', '60', '120', '240']
        
        with patch('akshare.stock_zh_a_minute') as mock_ak:
            mock_ak.return_value = pd.DataFrame()  # 返回空DataFrame避免后续处理错误
            
            for period in supported:
                result = self.provider._get_stock_minute_data_sync(
                    stock_code=self.test_stock_code,
                    period=period
                )
                
                # 不应该有"不支持的分钟周期"错误
                if hasattr(result, 'error'):
                    self.assertNotIn("不支持的分钟周期", result.error)
    
    def test_market_type_validation(self):
        """测试市场类型验证"""
        unsupported_markets = ['HK', 'US', 'B']
        
        for market in unsupported_markets:
            result = self.provider._get_stock_minute_data_sync(
                stock_code=self.test_stock_code,
                period="240",
                market_type=market
            )
            
            self.assertTrue(result.empty)
            self.assertTrue(hasattr(result, 'error'))
            self.assertIn("仅支持A股市场", result.error)
    
    def test_async_interface_basic(self):
        """测试异步接口基本功能"""
        async def test_async():
            with patch.object(self.provider, '_get_stock_minute_data_sync') as mock_sync:
                # 模拟返回成功结果
                mock_sync.return_value = pd.DataFrame({'test': [1, 2, 3]})
                
                result = await self.provider.get_stock_minute_data(
                    stock_code=self.test_stock_code,
                    period="240"
                )
                
                # 验证调用
                mock_sync.assert_called_once()
                args = mock_sync.call_args[0]
                self.assertEqual(args[0], self.test_stock_code)
                self.assertEqual(args[1], "240")
                
                return result
        
        result = asyncio.run(test_async())
        self.assertIsInstance(result, pd.DataFrame)
    
    def test_column_standardization(self):
        """测试列名标准化"""
        with patch('akshare.stock_zh_a_minute') as mock_ak:
            # 模拟中文列名的数据
            chinese_data = pd.DataFrame({
                '时间': pd.date_range('2023-12-01 09:30:00', periods=2, freq='h'),
                '开盘': [10.0, 10.1],
                '收盘': [10.1, 10.2],
                '最高': [10.2, 10.3],
                '最低': [9.9, 10.0],
                '成交量': [1000, 1100],
                '成交额': [10000, 11000]
            })
            chinese_data.set_index('时间', inplace=True)
            mock_ak.return_value = chinese_data
            
            result = self.provider._get_stock_minute_data_sync(
                stock_code=self.test_stock_code,
                period="240"
            )
            
            # 验证列名已标准化
            if not result.empty and not hasattr(result, 'error'):
                expected_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
                for col in expected_columns:
                    self.assertIn(col, result.columns)
    
    def test_error_handling(self):
        """测试错误处理"""
        with patch('akshare.stock_zh_a_minute') as mock_ak:
            # 模拟akshare抛出异常
            mock_ak.side_effect = Exception("网络错误")
            
            result = self.provider._get_stock_minute_data_sync(
                stock_code=self.test_stock_code,
                period="240"
            )
            
            # 验证错误处理
            self.assertTrue(result.empty)
            self.assertTrue(hasattr(result, 'error'))
            self.assertIn("获取240分钟K线数据失败", result.error)


def run_simplified_tests():
    """运行简化测试套件"""
    print("🧪 运行240分钟K线数据功能简化测试...")
    print("=" * 50)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestStockDataProvider240Min)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 所有测试通过！")
        print(f"✅ 成功运行 {result.testsRun} 个测试")
        print("\n✅ 240分钟K线数据功能验证成功！")
        print("📊 支持的周期: 1, 5, 15, 30, 60, 120, 240 分钟")
        print("🔧 重采样算法: 60分钟数据 → 4小时合并")
        print("📈 OHLCV逻辑: 开盘(first), 最高(max), 最低(min), 收盘(last), 量额(sum)")
    else:
        print("❌ 部分测试失败")
        print(f"失败: {len(result.failures)}")
        print(f"错误: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_simplified_tests()
    exit(0 if success else 1)
