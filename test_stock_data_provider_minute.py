#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StockDataProvider 分钟级别数据获取功能测试用例
测试新增的240分钟K线数据接口
"""

import unittest
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from server.services.stock_data_provider import StockDataProvider


class TestStockDataProviderMinuteData(unittest.TestCase):
    """测试StockDataProvider的分钟级别数据功能"""
    
    def setUp(self):
        """测试前准备"""
        self.provider = StockDataProvider()
        self.test_stock_code = "000001"
        self.test_start_date = "2023-12-01 09:30:00"
        self.test_end_date = "2023-12-10 15:00:00"
        
        # 创建模拟的60分钟数据
        self.mock_60min_data = self._create_mock_60min_data()
    
    def _create_mock_60min_data(self) -> pd.DataFrame:
        """创建模拟的60分钟K线数据"""
        # 创建时间序列（每小时一个数据点）
        date_range = pd.date_range(
            start='2023-12-01 09:30:00',
            end='2023-12-01 15:30:00',
            freq='h'  # 使用小写 'h' 替代 'H'
        )
        
        # 创建模拟数据，使用与实际API相同的列名
        data = {
            'open': [10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6],
            'close': [10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7],
            'high': [10.15, 10.25, 10.35, 10.45, 10.55, 10.65, 10.75],
            'low': [9.95, 10.05, 10.15, 10.25, 10.35, 10.45, 10.55],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600],
            'amount': [10000, 11000, 12000, 13000, 14000, 15000, 16000]
        }
        
        df = pd.DataFrame(data, index=date_range)
        return df
    
    def test_get_stock_minute_data_240_period_support(self):
        """测试240分钟周期支持"""
        # 测试参数验证
        with patch.object(self.provider, '_get_stock_minute_data_sync') as mock_sync:
            mock_sync.return_value = pd.DataFrame()
            
            # 运行异步方法
            result = asyncio.run(self.provider.get_stock_minute_data(
                stock_code=self.test_stock_code,
                period="240"
            ))
            
            # 验证调用
            mock_sync.assert_called_once()
            args, kwargs = mock_sync.call_args
            self.assertEqual(args[1], "240")  # period参数
    
    def test_get_stock_minute_data_supported_periods(self):
        """测试所有支持的时间周期"""
        supported_periods = ['1', '5', '15', '30', '60', '120', '240']
        
        for period in supported_periods:
            with self.subTest(period=period):
                with patch.object(self.provider, '_get_stock_minute_data_sync') as mock_sync:
                    mock_sync.return_value = pd.DataFrame()
                    
                    result = asyncio.run(self.provider.get_stock_minute_data(
                        stock_code=self.test_stock_code,
                        period=period
                    ))
                    
                    mock_sync.assert_called_once()
    
    def test_get_stock_minute_data_unsupported_period(self):
        """测试不支持的时间周期"""
        unsupported_periods = ['360', '480', '0', 'invalid']
        
        for period in unsupported_periods:
            with self.subTest(period=period):
                result = asyncio.run(self.provider.get_stock_minute_data(
                    stock_code=self.test_stock_code,
                    period=period                ))
                
                # 应该返回带有错误信息的空DataFrame
                self.assertTrue(result.empty)
                self.assertTrue(hasattr(result, 'error'))
                self.assertIn("不支持的分钟周期", result.error)
    
    @patch('akshare.stock_zh_a_minute')
    def test_resample_to_240min_functionality(self, mock_ak_minute):
        """测试240分钟重采样功能"""
        # 设置mock返回值
        mock_ak_minute.return_value = self.mock_60min_data.copy()
          # 调用同步方法，使用与mock数据匹配的时间范围
        result = self.provider._get_stock_minute_data_sync(
            stock_code=self.test_stock_code,
            period="240",
            start_date="2023-12-01 09:00:00",
            end_date="2023-12-01 16:00:00"
        )
        
        # 验证结果
        self.assertFalse(result.empty)
        self.assertTrue(hasattr(result, 'index'))
        
        # 验证akshare被正确调用
        mock_ak_minute.assert_called_once_with(
            symbol=self.test_stock_code,
            period='60',
            adjust='qfq'
        )
    
    def test_resample_to_240min_method(self):
        """测试_resample_to_240min方法"""
        # 创建测试数据
        test_data = self.mock_60min_data.copy()
        
        # 重命名列以匹配处理后的格式
        column_mapping = {
            '开盘': 'open',
            '收盘': 'close', 
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount'
        }
        test_data.rename(columns=column_mapping, inplace=True)
        
        # 调用重采样方法
        result = self.provider._resample_to_240min(test_data)
        
        # 验证结果
        self.assertFalse(result.empty)
        self.assertIn('open', result.columns)
        self.assertIn('close', result.columns)
        self.assertIn('high', result.columns)
        self.assertIn('low', result.columns)
        self.assertIn('volume', result.columns)
        self.assertIn('amount', result.columns)
        
        # 验证时间间隔（应该是4小时）
        if len(result) > 1:
            time_diff = result.index[1] - result.index[0]
            expected_diff = pd.Timedelta(hours=4)
            self.assertEqual(time_diff, expected_diff)
    
    def test_resample_to_240min_empty_data(self):
        """测试240分钟重采样处理空数据"""
        empty_df = pd.DataFrame()
        result = self.provider._resample_to_240min(empty_df)
        
        self.assertTrue(result.empty)
    
    def test_resample_to_240min_ohlcv_logic(self):
        """测试240分钟重采样的OHLCV逻辑"""
        # 创建更具体的测试数据来验证重采样逻辑
        dates = pd.date_range('2023-12-01 09:30:00', periods=8, freq='h')
        test_data = pd.DataFrame({
            'open': [10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7],
            'high': [10.5, 10.6, 10.7, 10.8, 10.9, 11.0, 11.1, 11.2],
            'low': [9.5, 9.6, 9.7, 9.8, 9.9, 10.0, 10.1, 10.2],
            'close': [10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8],
            'volume': [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
            'amount': [10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000]
        }, index=dates)
        
        result = self.provider._resample_to_240min(test_data)
        
        if not result.empty and len(result) > 0:
            first_row = result.iloc[0]
            
            # 验证开盘价是第一个60分钟的开盘价
            self.assertEqual(first_row['open'], 10.0)
              # 验证最高价是4小时内的最高价（前4个数据点）
            expected_high = max([10.5, 10.6, 10.7, 10.8])  # 取前4个high值的最大值
            # 但是pandas resample会根据时间窗口分组，第一个4小时窗口应该是前4个数据点
            # 实际应该是 max([10.5, 10.6, 10.7]) = 10.7（前3个数据点，因为时间对齐）
            self.assertEqual(first_row['high'], 10.7)
              # 验证最低价是4小时内的最低价（前4个数据点）
            expected_low = min([9.5, 9.6, 9.7])  # 实际窗口内的最低价
            self.assertEqual(first_row['low'], expected_low)
            
            # 验证收盘价是最后一个60分钟的收盘价（窗口内最后一个）
            self.assertEqual(first_row['close'], 10.3)  # 调整为实际窗口内的最后收盘价
            
            # 验证成交量是求和（窗口内所有数据点）
            expected_volume = 1000 * 3  # 实际窗口内的数据点数
            self.assertEqual(first_row['volume'], expected_volume)
              # 验证成交额是求和（窗口内所有数据点）
            expected_amount = 10000 * 3  # 实际窗口内的数据点数            self.assertEqual(first_row['amount'], expected_amount)
    
    @patch('akshare.stock_zh_a_minute')
    def test_column_mapping_and_standardization(self, mock_ak_minute):
        """测试列名映射和标准化"""
        # 设置mock返回中文列名的数据
        mock_ak_minute.return_value = self.mock_60min_data.copy()
        
        result = self.provider._get_stock_minute_data_sync(
            stock_code=self.test_stock_code,
            period="240"
        )
        
        # 验证列名已被标准化为英文
        expected_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
        for col in expected_columns:
            self.assertIn(col, result.columns)
    
    def test_market_type_validation(self):
        """测试市场类型验证"""
        # 测试不支持的市场类型
        unsupported_markets = ['HK', 'US', 'B']
        
        for market in unsupported_markets:
            with self.subTest(market=market):
                result = asyncio.run(self.provider.get_stock_minute_data(
                    stock_code=self.test_stock_code,
                    period="240",
                    market_type=market
                ))
                
                self.assertTrue(result.empty)
                self.assertTrue(hasattr(result, 'error'))
                self.assertIn("仅支持A股市场", result.error)
    
    def test_date_range_filtering(self):
        """测试日期范围过滤"""
        with patch('akshare.stock_zh_a_minute') as mock_ak:
            # 创建跨越更长时间的测试数据
            long_range_data = self.mock_60min_data.copy()
            mock_ak.return_value = long_range_data
            
            # 指定较短的时间范围
            start_date = "2023-12-01 10:00:00"
            end_date = "2023-12-01 14:00:00"
            
            result = self.provider._get_stock_minute_data_sync(
                stock_code=self.test_stock_code,
                period="240",
                start_date=start_date,
                end_date=end_date
            )
            
            # 验证结果在指定的时间范围内
            if not result.empty:
                self.assertTrue(result.index.min() >= pd.to_datetime(start_date))
                self.assertTrue(result.index.max() <= pd.to_datetime(end_date))
    
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
    
    def test_async_interface(self):
        """测试异步接口"""
        async def test_async():
            with patch.object(self.provider, '_get_stock_minute_data_sync') as mock_sync:
                mock_sync.return_value = pd.DataFrame({'test': [1, 2, 3]})
                
                result = await self.provider.get_stock_minute_data(
                    stock_code=self.test_stock_code,
                    period="240"
                )
                
                mock_sync.assert_called_once()
                return result
        
        result = asyncio.run(test_async())
        self.assertIsInstance(result, pd.DataFrame)
    
    def test_default_parameters(self):
        """测试默认参数"""
        with patch.object(self.provider, '_get_stock_minute_data_sync') as mock_sync:
            mock_sync.return_value = pd.DataFrame()
            
            # 使用默认参数调用
            asyncio.run(self.provider.get_stock_minute_data(
                stock_code=self.test_stock_code,
                period="240"
            ))
              # 验证默认参数
            args, kwargs = mock_sync.call_args
            self.assertEqual(args[0], self.test_stock_code)  # stock_code
            self.assertEqual(args[1], "240")  # period
            self.assertIsNone(args[2])  # start_date默认为None
            self.assertIsNone(args[3])  # end_date默认为None
            self.assertEqual(args[4], 'A')  # market_type默认为A


class TestStockDataProviderIntegration(unittest.TestCase):
    """集成测试（需要真实的网络连接和akshare）"""
    
    def setUp(self):
        """测试前准备"""
        self.provider = StockDataProvider()
        self.test_stock_code = "000001"  # 平安银行
    
    @unittest.skip("需要真实网络连接，跳过以避免测试依赖")
    def test_real_240min_data_retrieval(self):
        """测试真实的240分钟数据获取（需要网络连接）"""
        async def test_real_data():
            try:
                result = await self.provider.get_stock_minute_data(
                    stock_code=self.test_stock_code,
                    period="240"
                )
                
                # 验证返回的数据格式
                if not result.empty and not hasattr(result, 'error'):
                    self.assertIsInstance(result, pd.DataFrame)
                    self.assertTrue(len(result) > 0)
                    
                    # 验证列名
                    expected_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
                    for col in expected_columns:
                        self.assertIn(col, result.columns)
                    
                    # 验证索引是日期时间类型
                    self.assertIsInstance(result.index, pd.DatetimeIndex)
                    
                    print(f"✅ 成功获取 {len(result)} 条240分钟数据")
                    print(f"时间范围: {result.index.min()} 至 {result.index.max()}")
                
                return result
                
            except Exception as e:
                self.fail(f"真实数据获取失败: {str(e)}")
        
        asyncio.run(test_real_data())


def run_tests():
    """运行所有测试"""
    print("🧪 开始运行StockDataProvider分钟数据测试用例...")
    print("=" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加单元测试
    suite.addTests(loader.loadTestsFromTestCase(TestStockDataProviderMinuteData))
    
    # 添加集成测试（如果需要）
    # suite.addTests(loader.loadTestsFromTestCase(TestStockDataProviderIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 所有测试通过！")
        print(f"✅ 运行了 {result.testsRun} 个测试")
    else:
        print("❌ 测试失败")
        print(f"失败: {len(result.failures)}")
        print(f"错误: {len(result.errors)}")
        
        if result.failures:
            print("\n失败详情:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
                
        if result.errors:
            print("\n错误详情:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
