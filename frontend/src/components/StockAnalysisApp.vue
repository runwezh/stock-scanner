<template>
  <div class="app-container">
    <!-- 公告栏 -->
    <AnnouncementBanner v-if="announcement" :content="announcement" :auto-close-time="5" />
    
    <n-layout class="main-layout">
      <n-layout-content class="main-content">
        <n-page-header title="股票分析系统">
          <template #avatar>
            <n-icon :component="BarChartIcon" color="#2080f0" size="28" />
          </template>
        </n-page-header>
        
        <!-- 市场时间显示 -->
        <MarketTimeDisplay />
        
        <!-- API配置面板 -->
        <ApiConfigPanel
          :default-api-url="defaultApiUrl"
          :default-api-model="defaultApiModel"
          :default-api-timeout="defaultApiTimeout"
          @update:api-config="updateApiConfig"
        />
        
        <!-- 主要内容 -->
        <n-card class="analysis-container">
          <template #header>
            <div class="card-title">股票批量分析</div>
          </template>
          
          <n-grid :cols="24" :x-gap="16" :y-gap="16">
            <!-- 左侧配置区域 -->
            <n-grid-item :span="24" :lg-span="8">
              <div class="config-section">
                <n-form-item label="选择市场类型">
                  <n-select
                    v-model:value="marketType"
                    :options="marketOptions"
                    @update:value="handleMarketTypeChange"
                  />
                </n-form-item>
                
                <n-form-item label="股票搜索" v-if="marketType === 'US'">
                  <StockSearch :market-type="marketType" @select="addSelectedStock" />
                </n-form-item>
                
                <n-form-item label="输入代码">
                  <n-input
                    v-model:value="stockCodes"
                    type="textarea"
                    placeholder="输入股票代码，多个代码用逗号、空格或换行分隔"
                    :autosize="{ minRows: 3, maxRows: 6 }"
                  />
                </n-form-item>
                
                <div class="action-buttons">
                  <n-button
                    type="primary"
                    :loading="isAnalyzing"
                    :disabled="!stockCodes.trim()"
                    @click="analyzeStocks"
                  >
                    {{ isAnalyzing ? '分析中...' : '开始分析' }}
                  </n-button>
                  
                  <n-button
                    :disabled="analyzedStocks.length === 0"
                    @click="copyAnalysisResults"
                  >
                    复制结果
                  </n-button>
                </div>
              </div>
            </n-grid-item>
            
            <!-- 右侧结果区域 -->
            <n-grid-item :span="24" :lg-span="16">
              <div class="results-section">
                <template v-if="analyzedStocks.length === 0 && !isAnalyzing">
                  <n-empty description="尚未分析股票" size="large">
                    <template #icon>
                      <n-icon :component="DocumentTextIcon" />
                    </template>
                  </n-empty>
                </template>
                
                <template v-else>
                  <n-grid :cols="1" :x-gap="16" :y-gap="16" :lg-cols="2">
                    <n-grid-item v-for="stock in analyzedStocks" :key="stock.code">
                      <StockCard :stock="stock" />
                    </n-grid-item>
                  </n-grid>
                </template>
              </div>
            </n-grid-item>
          </n-grid>
        </n-card>
      </n-layout-content>
    </n-layout>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { 
  NLayout, 
  NLayoutContent, 
  NCard, 
  NPageHeader, 
  NIcon, 
  NGrid, 
  NGridItem, 
  NFormItem, 
  NSelect, 
  NInput, 
  NButton,
  NEmpty,
  useMessage
} from 'naive-ui';
import { useClipboard } from '@vueuse/core'
import { 
  BarChart as BarChartIcon,
  DocumentText as DocumentTextIcon
} from '@vicons/ionicons5';

import AnnouncementBanner from './AnnouncementBanner.vue';
import MarketTimeDisplay from './MarketTimeDisplay.vue';
import ApiConfigPanel from './ApiConfigPanel.vue';
import StockSearch from './StockSearch.vue';
import StockCard from './StockCard.vue';

import { apiService } from '@/services/api';
import type { StockInfo, ApiConfig, StreamInitMessage, StreamAnalysisUpdate } from '@/types';
import { loadApiConfig } from '@/utils';

// 使用Naive UI的消息组件
const message = useMessage();
const { copy } = useClipboard();

// 从环境变量获取的默认配置
const defaultApiUrl = ref('');
const defaultApiModel = ref('gpt-3.5-turbo');
const defaultApiTimeout = ref('60');
const announcement = ref('');

// 股票分析配置
const marketType = ref('A');
const stockCodes = ref('');
const isAnalyzing = ref(false);
const analyzedStocks = ref<StockInfo[]>([]);

// API配置
const apiConfig = ref<ApiConfig>({
  apiUrl: '',
  apiKey: '',
  apiModel: 'gpt-3.5-turbo',
  apiTimeout: '60',
  saveApiConfig: false
});

// 市场选项
const marketOptions = [
  { label: 'A股', value: 'A' },
  { label: '港股', value: 'HK' },
  { label: '美股', value: 'US' }
];

// 更新API配置
function updateApiConfig(config: ApiConfig) {
  apiConfig.value = { ...config };
}

// 处理市场类型变更
function handleMarketTypeChange() {
  stockCodes.value = '';
  analyzedStocks.value = [];
}

// 添加选择的股票
function addSelectedStock(symbol: string) {
  if (stockCodes.value) {
    stockCodes.value += ', ' + symbol;
  } else {
    stockCodes.value = symbol;
  }
}

// 处理流式响应的数据
function processStreamData(text: string) {
  try {
    // 尝试解析为JSON
    const data = JSON.parse(text);
    
    // 判断是初始消息还是更新消息
    if (data.stream_type === 'single' || data.stream_type === 'batch') {
      // 初始消息
      handleStreamInit(data as StreamInitMessage);
    } else if (data.stock_code) {
      // 更新消息
      handleStreamUpdate(data as StreamAnalysisUpdate);
    }
  } catch (e) {
    console.error('解析流数据出错:', e);
  }
}

// 处理流式初始化消息
function handleStreamInit(data: StreamInitMessage) {
  if (data.stream_type === 'single' && data.stock_code) {
    // 单个股票分析
    analyzedStocks.value = [{
      code: data.stock_code,
      name: '',
      marketType: marketType.value,
      analysisStatus: 'waiting'
    }];
  } else if (data.stream_type === 'batch' && data.stock_codes) {
    // 批量分析
    analyzedStocks.value = data.stock_codes.map(code => ({
      code,
      name: '',
      marketType: marketType.value,
      analysisStatus: 'waiting'
    }));
  }
}

// 处理流式更新消息
function handleStreamUpdate(data: StreamAnalysisUpdate) {
  const stockIndex = analyzedStocks.value.findIndex((s: StockInfo) => s.code === data.stock_code);
  
  if (stockIndex >= 0) {
    const stock = { ...analyzedStocks.value[stockIndex] };
    
    // 更新分析状态
    if (data.status) {
      stock.analysisStatus = data.status;
    }
    
    // 如果有分析结果，则更新
    if (data.analysis !== undefined) {
      stock.analysis = data.analysis;
    }
    
    // 处理AI分析片段
    if (data.ai_analysis_chunk !== undefined) {
      // 如果之前没有分析内容，则初始化
      if (!stock.analysis) {
        stock.analysis = '';
      }
      // 追加新的分析片段
      stock.analysis += data.ai_analysis_chunk;
      // 确保分析状态为正在分析
      stock.analysisStatus = 'analyzing';
    }
    
    // 如果有错误，则更新
    if (data.error !== undefined) {
      stock.error = data.error;
      stock.analysisStatus = 'error';
    }
    
    // 更新股票名称、价格等信息
    if (data.name !== undefined) {
      stock.name = data.name;
    }
    
    if (data.price !== undefined) {
      stock.price = data.price;
    }
    
    if (data.change_percent !== undefined) {
      stock.changePercent = data.change_percent;
    }
    
    if (data.market_value !== undefined) {
      stock.marketValue = data.market_value;
    }
    
    // 添加新字段的处理
    if (data.score !== undefined) {
      stock.score = data.score;
    }
    
    if (data.recommendation !== undefined) {
      stock.recommendation = data.recommendation;
    }
    
    if (data.price_change !== undefined) {
      stock.price_change = data.price_change;
    }
    
    if (data.rsi !== undefined) {
      stock.rsi = data.rsi;
    }
    
    // 添加技术指标字段的处理
    if (data.ma_trend !== undefined) {
      stock.ma_trend = data.ma_trend;
    }
    
    if (data.macd_signal !== undefined) {
      stock.macd_signal = data.macd_signal;
    }
    
    if (data.volume_status !== undefined) {
      stock.volume_status = data.volume_status;
    }
    
    // 添加分析日期字段的处理
    if (data.analysis_date !== undefined) {
      stock.analysis_date = data.analysis_date;
    }
    
    // 更新数组中的股票信息
    analyzedStocks.value[stockIndex] = stock;
  }
}

// 分析股票
async function analyzeStocks() {
  if (!stockCodes.value.trim()) {
    message.warning('请输入股票代码');
    return;
  }
  
  isAnalyzing.value = true;
  analyzedStocks.value = [];
  
  // 解析股票代码
  const codes = stockCodes.value
    .split(/[,\s\n]+/)
    .map((code: string) => code.trim())
    .filter((code: string) => code);
  
  if (codes.length === 0) {
    message.warning('未找到有效的股票代码');
    isAnalyzing.value = false;
    return;
  }
  
  try {
    // 构建请求参数
    const requestData = {
      stock_codes: codes,
      market_type: marketType.value
    } as any;
    
    // 添加自定义API配置
    if (apiConfig.value.apiUrl) {
      requestData.api_url = apiConfig.value.apiUrl;
    }
    
    if (apiConfig.value.apiKey) {
      requestData.api_key = apiConfig.value.apiKey;
    }
    
    if (apiConfig.value.apiModel) {
      requestData.api_model = apiConfig.value.apiModel;
    }
    
    if (apiConfig.value.apiTimeout) {
      requestData.api_timeout = apiConfig.value.apiTimeout;
    }
    
    // 发送分析请求
    const response = await fetch('/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    // 处理流式响应
    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('无法读取响应流');
    }
    
    const decoder = new TextDecoder();
    let buffer = '';
    
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        break;
      }
      
      // 解码并处理数据
      const text = decoder.decode(value, { stream: true });
      buffer += text;
      
      // 按行处理数据
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // 最后一行可能不完整，保留到下一次
      
      for (const line of lines) {
        if (line.trim()) {
          processStreamData(line);
        }
      }
    }
    
    // 处理最后可能剩余的数据
    if (buffer.trim()) {
      processStreamData(buffer);
    }
    
    // 将所有分析中的股票状态更新为已完成
    analyzedStocks.value.forEach((stock, index) => {
      if (stock.analysisStatus === 'analyzing') {
        const updatedStock = { ...stock, analysisStatus: 'completed' };
        analyzedStocks.value[index] = updatedStock;
      }
    });
    
    message.success('分析完成');
  } catch (error: any) {
    message.error(`分析出错: ${error.message || '未知错误'}`);
    console.error('分析股票时出错:', error);
  } finally {
    isAnalyzing.value = false;
  }
}

// 复制分析结果
async function copyAnalysisResults() {
  if (analyzedStocks.value.length === 0) {
    message.warning('没有可复制的分析结果');
    return;
  }
  
  try {
    // 格式化分析结果
    const formattedResults = analyzedStocks.value
      .filter((stock: StockInfo) => stock.analysisStatus === 'completed')
      .map((stock: StockInfo) => {
        let result = `【${stock.code} ${stock.name || ''}】\n`;
        
        // 添加分析日期
        if (stock.analysis_date) {
          try {
            const date = new Date(stock.analysis_date);
            if (!isNaN(date.getTime())) {
              result += `分析日期: ${date.toISOString().split('T')[0]}\n`;
            } else {
              result += `分析日期: ${stock.analysis_date}\n`;
            }
          } catch (e) {
            result += `分析日期: ${stock.analysis_date}\n`;
          }
        }
        
        // 添加评分和推荐信息
        if (stock.score !== undefined) {
          result += `评分: ${stock.score}\n`;
        }
        
        if (stock.recommendation) {
          result += `推荐: ${stock.recommendation}\n`;
        }
        
        // 添加技术指标信息
        if (stock.rsi !== undefined) {
          result += `RSI: ${stock.rsi.toFixed(2)}\n`;
        }
        
        if (stock.price_change !== undefined) {
          const sign = stock.price_change > 0 ? '+' : '';
          result += `价格变动: ${sign}${stock.price_change.toFixed(2)}\n`;
        }
        
        if (stock.ma_trend) {
          const trendMap: Record<string, string> = {
            'UP': '上升',
            'DOWN': '下降',
            'NEUTRAL': '平稳'
          };
          const trend = trendMap[stock.ma_trend] || stock.ma_trend;
          result += `均线趋势: ${trend}\n`;
        }
        
        if (stock.macd_signal) {
          const signalMap: Record<string, string> = {
            'BUY': '买入',
            'SELL': '卖出',
            'HOLD': '持有',
            'NEUTRAL': '中性'
          };
          const signal = signalMap[stock.macd_signal] || stock.macd_signal;
          result += `MACD信号: ${signal}\n`;
        }
        
        if (stock.volume_status) {
          const statusMap: Record<string, string> = {
            'HIGH': '放量',
            'LOW': '缩量',
            'NORMAL': '正常'
          };
          const status = statusMap[stock.volume_status] || stock.volume_status;
          result += `成交量: ${status}\n`;
        }
        
        // 添加分析结果
        result += `\n${stock.analysis || '无分析结果'}\n`;
        
        return result;
      })
      .join('\n');
    
    if (!formattedResults) {
      message.warning('没有已完成的分析结果可复制');
      return;
    }
    
    // 复制到剪贴板
    await copy(formattedResults);
    message.success('已复制分析结果到剪贴板');
  } catch (error) {
    message.error('复制失败，请手动复制');
    console.error('复制分析结果时出错:', error);
  }
}

// 从本地存储恢复API配置
function restoreLocalApiConfig() {
  const savedConfig = loadApiConfig();
  if (savedConfig && savedConfig.saveApiConfig) {
    apiConfig.value = {
      apiUrl: savedConfig.apiUrl || '',
      apiKey: savedConfig.apiKey || '',
      apiModel: savedConfig.apiModel || defaultApiModel.value,
      apiTimeout: savedConfig.apiTimeout || defaultApiTimeout.value,
      saveApiConfig: savedConfig.saveApiConfig
    };
    
    // 通知父组件配置已更新
    updateApiConfig(apiConfig.value);
  }
}

// 页面加载时获取默认配置和公告
onMounted(async () => {
  try {
    // 从API获取配置信息
    const config = await apiService.getConfig();
    
    if (config.default_api_url) {
      defaultApiUrl.value = config.default_api_url;
    }
    
    if (config.default_api_model) {
      defaultApiModel.value = config.default_api_model;
    }
    
    if (config.default_api_timeout) {
      defaultApiTimeout.value = config.default_api_timeout;
    }
    
    if (config.announcement) {
      announcement.value = config.announcement;
    }
    
    // 初始化后恢复本地保存的配置
    restoreLocalApiConfig();
  } catch (error) {
    console.error('获取默认配置时出错:', error);
  }
});
</script>

<style scoped>
.app-container {
  min-height: 100vh;
}

.main-layout {
  background-color: #f6f6f6;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
}

.analysis-container {
  margin-bottom: 2rem;
}

.config-section {
  padding: 0.5rem;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
}

.results-section {
  padding: 0.5rem;
  min-height: 200px;
}
</style>
