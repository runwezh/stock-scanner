<template>
  <n-card class="stock-card" :bordered="false" :class="{ 'is-analyzing': isAnalyzing }">
    <div class="card-header">
      <div class="stock-info">
        <div class="stock-code">{{ stock.code }}</div>
      </div>
      <div class="stock-price-info" v-if="stock.price !== undefined">
        <div class="stock-price">当前价格: {{ stock.price.toFixed(2) }}</div>
        <div class="stock-change" :class="{ 
          'up': calculatedChangePercent && calculatedChangePercent > 0,
          'down': calculatedChangePercent && calculatedChangePercent < 0
        }">
          涨跌幅: {{ formatChangePercent(calculatedChangePercent) }}
        </div>
      </div>
    </div>
    
    <div class="stock-summary" v-if="stock.score !== undefined || stock.recommendation">
      <div class="summary-item score-item" v-if="stock.score !== undefined">
        <div class="summary-value" :class="getScoreClass(stock.score)">{{ stock.score }}</div>
        <div class="summary-label">评分</div>
      </div>
      <div class="summary-item recommendation-item" v-if="stock.recommendation">
        <div class="summary-value recommendation">{{ stock.recommendation }}</div>
        <div class="summary-label">推荐</div>
      </div>
    </div>
    
    <div class="analysis-date" v-if="stock.analysis_date">
      <n-tag type="info" size="small">
        <template #icon>
          <n-icon><CalendarOutline /></n-icon>
        </template>
        分析日期: {{ formatDate(stock.analysis_date) }}
      </n-tag>
    </div>
    
    <div class="technical-indicators" v-if="hasAnyTechnicalIndicator">
      <n-divider dashed style="margin: 12px 0 8px 0">技术指标</n-divider>
      
      <div class="indicators-grid">
        <div class="indicator-item" v-if="stock.rsi !== undefined">
          <div class="indicator-value" :class="getRsiClass(stock.rsi)">{{ stock.rsi.toFixed(2) }}</div>
          <div class="indicator-label">RSI</div>
        </div>
        
        <div class="indicator-item" v-if="stock.price_change !== undefined">
          <div class="indicator-value" :class="{ 
            'up': stock.price_change > 0,
            'down': stock.price_change < 0
          }">{{ formatPriceChange(stock.price_change) }}</div>
          <div class="indicator-label">价格变动</div>
        </div>
        
        <div class="indicator-item" v-if="stock.ma_trend">
          <div class="indicator-value" :class="getTrendClass(stock.ma_trend)">
            {{ getChineseTrend(stock.ma_trend) }}
          </div>
          <div class="indicator-label">均线趋势</div>
        </div>
        
        <div class="indicator-item" v-if="stock.macd_signal">
          <div class="indicator-value" :class="getSignalClass(stock.macd_signal)">
            {{ getChineseSignal(stock.macd_signal) }}
          </div>
          <div class="indicator-label">MACD信号</div>
        </div>
        
        <div class="indicator-item" v-if="stock.volume_status">
          <div class="indicator-value" :class="getVolumeStatusClass(stock.volume_status)">
            {{ getChineseVolumeStatus(stock.volume_status) }}
          </div>
          <div class="indicator-label">成交量</div>
        </div>
      </div>
    </div>
    
    <n-divider />
    
    <div class="card-content">
      <template v-if="stock.analysisStatus === 'waiting'">
        <div class="waiting-status">
          <n-spin size="small" />
          <span>等待分析...</span>
        </div>
      </template>
      
      <template v-else-if="stock.analysisStatus === 'analyzing'">
        <div class="analyzing-status">
          <n-spin size="small" />
          <span>正在分析...</span>
        </div>
        <div class="analysis-result analysis-streaming" v-if="parsedAnalysis" v-html="parsedAnalysis" :key="analysisContentKey"></div>
      </template>
      
      <template v-else-if="stock.analysisStatus === 'error'">
        <div class="error-status">
          <n-icon :component="AlertCircleIcon" class="error-icon" />
          <span>分析出错: {{ stock.error || '未知错误' }}</span>
        </div>
      </template>
      
      <template v-else-if="stock.analysisStatus === 'completed'">
        <div class="analysis-result analysis-completed" v-html="parsedAnalysis"></div>
      </template>
    </div>
    
  </n-card>
</template>

<script setup lang="ts">
import { computed, watch, ref } from 'vue';
import { NCard, NDivider, NSpin, NIcon, NTag } from 'naive-ui';
import { 
  AlertCircleOutline as AlertCircleIcon,
  CalendarOutline
} from '@vicons/ionicons5';
import { parseMarkdown, formatMarketValue as formatMarketValueFn } from '@/utils';
import type { StockInfo } from '@/types';

const props = defineProps<{
  stock: StockInfo;
}>();

const isAnalyzing = computed(() => {
  return props.stock.analysisStatus === 'analyzing';
});

const lastAnalysisLength = ref(0);

// 监听分析内容变化
watch(() => props.stock.analysis, (newVal) => {
  if (newVal && props.stock.analysisStatus === 'analyzing') {
    lastAnalysisLength.value = newVal.length;
  }
}, { immediate: true });

// 添加一个计算属性，用于监控分析内容是否更新
const analysisContentKey = ref(0);
watch(() => props.stock.analysis, (newVal, oldVal) => {
  if (newVal && oldVal && newVal.length > oldVal.length && props.stock.analysisStatus === 'analyzing') {
    analysisContentKey.value++;
  }
}, { immediate: false });

const parsedAnalysis = computed(() => {
  if (props.stock.analysis) {
    let result = parseMarkdown(props.stock.analysis);
    
    // 为关键词添加样式类
    result = highlightKeywords(result);
    
    return result;
  }
  return '';
});

// 关键词高亮处理函数
function highlightKeywords(html: string): string {
  // 买入/卖出/持有信号
  html = html.replace(/(<strong>)(买入|卖出|持有)(<\/strong>)/g, '$1<span class="buy">$2</span>$3');
  
  // 上涨/增长相关词
  html = html.replace(/(<strong>)(上涨|看涨|增长|增加|上升)(<\/strong>)/g, '$1<span class="up">$2</span>$3');
  
  // 下跌/减少相关词
  html = html.replace(/(<strong>)(下跌|看跌|减少|降低|下降)(<\/strong>)/g, '$1<span class="down">$2</span>$3');
  
  // 技术指标相关词
  html = html.replace(/(<strong>)(RSI|MACD|MA|KDJ|均线|成交量|布林带|Bollinger|移动平均|相对强弱|背离)(<\/strong>)/g, 
                      '$1<span class="indicator">$2</span>$3');
  
  // 高亮重要的百分比数字 (如 +12.34%, -12.34%)
  html = html.replace(/([+-]?\d+\.?\d*\s*%)/g, '<span class="number">$1</span>');
  
  // 高亮重要的数值 (如带小数位的数字)
  html = html.replace(/(\s|>)(\d+\.\d+)(\s|<)/g, '$1<span class="number">$2</span>$3');
  
  return html;
}

// 计算涨跌幅
const calculatedChangePercent = computed(() => {
  // 如果已有changePercent，则直接使用
  if (props.stock.changePercent !== undefined) {
    return props.stock.changePercent;
  }
  
  // 如果有price_change和price，则计算涨跌幅
  if (props.stock.price_change !== undefined && props.stock.price !== undefined) {
    // 计算涨跌幅百分比 = (价格变动 / (当前价格 - 价格变动)) * 100
    const basePrice = props.stock.price - props.stock.price_change;
    if (basePrice !== 0) {
      return (props.stock.price_change / basePrice) * 100;
    }
  }
  
  // 无法计算则返回undefined
  return undefined;
});

const hasAnyTechnicalIndicator = computed(() => {
  return props.stock.rsi !== undefined || 
         props.stock.price_change !== undefined || 
         props.stock.ma_trend !== undefined || 
         props.stock.macd_signal !== undefined || 
         props.stock.volume_status !== undefined;
});

function formatChangePercent(percent: number | undefined): string {
  if (percent === undefined) return '--';
  
  const sign = percent > 0 ? '+' : '';
  return `${sign}${percent.toFixed(2)}%`;
}

function formatPriceChange(change: number): string {
  const sign = change > 0 ? '+' : '';
  return `${sign}${change.toFixed(2)}`;
}

function formatMarketValue(value: number): string {
  return formatMarketValueFn(value);
}

function formatDate(dateStr: string): string {
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      return dateStr;
    }
    
    return date.toISOString().split('T')[0];
  } catch (e) {
    return dateStr;
  }
}

function getMarketName(marketType: string): string {
  const marketMap: Record<string, string> = {
    'A': 'A股',
    'HK': '港股',
    'US': '美股'
  };
  
  return marketMap[marketType] || marketType;
}

function getScoreClass(score: number): string {
  if (score >= 80) return 'score-high';
  if (score >= 70) return 'score-medium-high';
  if (score >= 60) return 'score-medium';
  if (score >= 40) return 'score-medium-low';
  return 'score-low';
}

function getRsiClass(rsi: number): string {
  if (rsi >= 70) return 'rsi-overbought';
  if (rsi <= 30) return 'rsi-oversold';
  return '';
}

function getTrendClass(trend: string): string {
  if (trend === 'UP') return 'trend-up';
  if (trend === 'DOWN') return 'trend-down';
  return 'trend-neutral';
}

function getSignalClass(signal: string): string {
  if (signal === 'BUY') return 'signal-buy';
  if (signal === 'SELL') return 'signal-sell';
  return 'signal-neutral';
}

function getVolumeStatusClass(status: string): string {
  if (status === 'HIGH') return 'volume-high';
  if (status === 'LOW') return 'volume-low';
  return 'volume-normal';
}

function getChineseTrend(trend: string): string {
  const trendMap: Record<string, string> = {
    'UP': '上升',
    'DOWN': '下降',
    'NEUTRAL': '平稳'
  };
  
  return trendMap[trend] || trend;
}

function getChineseSignal(signal: string): string {
  const signalMap: Record<string, string> = {
    'BUY': '买入',
    'SELL': '卖出',
    'HOLD': '持有',
    'NEUTRAL': '中性'
  };
  
  return signalMap[signal] || signal;
}

function getChineseVolumeStatus(status: string): string {
  const statusMap: Record<string, string> = {
    'HIGH': '放量',
    'LOW': '缩量',
    'NORMAL': '正常'
  };
  
  return statusMap[status] || status;
}
</script>

<style scoped>
.stock-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.stock-card.is-analyzing {
  border-left: 3px solid var(--n-info-color);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.stock-info {
  display: flex;
  flex-direction: column;
}

.stock-code {
  font-size: 1.125rem;
  font-weight: bold;
  color: var(--n-text-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.stock-price-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.stock-price {
  font-size: 1.125rem;
  font-weight: bold;
  color: var(--n-text-color);
}

.stock-change {
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.stock-summary {
  display: flex;
  justify-content: space-around;
  margin: 0.75rem 0;
  padding: 0.5rem;
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 0.5rem;
}

.summary-value {
  font-size: 1.25rem;
  font-weight: 700;
}

.summary-label {
  font-size: 0.75rem;
  color: var(--n-text-color-3);
  margin-top: 0.25rem;
}

.analysis-date {
  margin: 0.5rem 0;
  display: flex;
  justify-content: flex-end;
}

.technical-indicators {
  margin-top: 0.5rem;
}

.indicators-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.indicator-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.indicator-value {
  font-size: 0.875rem;
  font-weight: 600;
}

.indicator-label {
  font-size: 0.75rem;
  color: var(--n-text-color-3);
  margin-top: 0.25rem;
}

.score-high {
  color: #18a058;
}

.score-medium-high {
  color: #63e2b7;
}

.score-medium {
  color: #f0a020;
}

.score-medium-low {
  color: #f5a623;
}

.score-low {
  color: #d03050;
}

.rsi-overbought {
  color: #d03050;
}

.rsi-oversold {
  color: #18a058;
}

.trend-up {
  color: #d03050;
}

.trend-down {
  color: #18a058;
}

.trend-neutral {
  color: #f0a020;
}

.signal-buy {
  color: #d03050;
}

.signal-sell {
  color: #18a058;
}

.signal-neutral {
  color: #f0a020;
}

.volume-high {
  color: #d03050;
}

.volume-low {
  color: #18a058;
}

.volume-normal {
  color: #f0a020;
}

.recommendation {
  color: #2080f0;
}

.up {
  color: var(--n-error-color);
}

.down {
  color: var(--n-success-color);
}

.card-content {
  flex: 1;
  min-height: 100px;
  margin-bottom: 0.5rem;
  text-align: left;
  display: flex;
  flex-direction: column;
}

.waiting-status,
.analyzing-status,
.error-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--n-text-color-3);
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
}

.error-icon {
  color: var(--n-error-color);
}

.analysis-result {
  font-size: 0.875rem;
  line-height: 1.6;
  text-align: left;
  padding: 0.75rem 1rem;
  border-radius: 4px;
  background-color: rgba(0, 0, 0, 0.01);
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.05);
  max-height: 400px;
  overflow-y: auto;
  word-break: break-word;
  hyphens: auto;
}

.analysis-streaming {
  position: relative;
  border-left: 2px solid var(--n-info-color);
  animation: fadePulse 2s infinite;
}

/* 改进流式输出的动画效果，消除闪烁 */
.analysis-streaming > :deep(*) {
  animation: none;
}

/* 添加打字机光标效果 */
.analysis-streaming::after {
  content: '|';
  display: inline-block;
  color: var(--n-info-color);
  animation: blink 1s step-end infinite;
  margin-left: 2px;
  font-weight: bold;
  vertical-align: middle;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.analysis-completed {
  border-left: 2px solid var(--n-success-color);
}

@keyframes fadePulse {
  0% { border-left-color: var(--n-info-color); }
  50% { border-left-color: rgba(31, 126, 212, 0.4); }
  100% { border-left-color: var(--n-info-color); }
}

/* 优化标题样式，增加颜色显示 */
.analysis-result :deep(h1), .analysis-result :deep(h2), .analysis-result :deep(h3) {
  margin: 1.25rem 0 0.75rem 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding-bottom: 0.4rem;
  font-weight: 600;
}

.analysis-result :deep(h1) {
  font-size: 1.4rem;
  color: #2080f0;
}

.analysis-result :deep(h2) {
  font-size: 1.2rem;
  color: #2080f0;
}

.analysis-result :deep(h3) {
  font-size: 1.1rem;
  color: #2080f0;
}

/* 优化列表样式 */
.analysis-result :deep(ul), .analysis-result :deep(ol) {
  margin: 0.75rem 0;
  padding-left: 1.5rem;
}

.analysis-result :deep(ul) li, .analysis-result :deep(ol) li {
  margin-bottom: 0.3rem;
}

/* 优化段落样式 */
.analysis-result :deep(p) {
  margin: 0.75rem 0;
  text-align: left;
}

/* 优化代码样式 */
.analysis-result :deep(code) {
  background: rgba(0, 0, 0, 0.05);
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.85em;
}

.analysis-result :deep(pre) {
  background: rgba(0, 0, 0, 0.05);
  padding: 0.75rem;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0.75rem 0;
  border-left: 3px solid #2080f0;
}

.analysis-result :deep(pre code) {
  background: transparent;
  padding: 0;
}

/* 优化引用样式 */
.analysis-result :deep(blockquote) {
  margin: 0.75rem 0;
  padding: 0.5rem 1rem;
  border-left: 3px solid #f0a020;
  background-color: rgba(240, 160, 32, 0.05);
  color: var(--n-text-color-2);
}

/* 优化表格样式 */
.analysis-result :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 0.75rem 0;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.analysis-result :deep(th) {
  background-color: rgba(32, 128, 240, 0.1);
  color: #2080f0;
  font-weight: 600;
  padding: 0.6rem;
  text-align: left;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.analysis-result :deep(td) {
  padding: 0.6rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.analysis-result :deep(tr:nth-child(even)) {
  background-color: rgba(0, 0, 0, 0.02);
}

/* 优化文本强调和术语显示 */
.analysis-result :deep(strong) {
  font-weight: 600;
  color: #2080f0;
}

/* 特定指标和信号的样式 */
.analysis-result :deep(.buy), 
.analysis-result :deep(.sell), 
.analysis-result :deep(.hold) {
  color: #d03050;
  background-color: rgba(208, 48, 80, 0.1);
  padding: 0 0.3rem;
  border-radius: 2px;
  font-weight: 600;
}

.analysis-result :deep(.up), 
.analysis-result :deep(.increase) {
  color: #d03050;
  font-weight: 600;
}

.analysis-result :deep(.down), 
.analysis-result :deep(.decrease) {
  color: #18a058;
  font-weight: 600;
}

.analysis-result :deep(.indicator) {
  color: #2080f0;
  background-color: rgba(32, 128, 240, 0.1);
  padding: 0 0.3rem;
  border-radius: 2px;
  font-weight: 600;
}

.analysis-result :deep(.number) {
  font-family: 'Consolas', monospace;
  font-weight: 600;
  color: #f0a020;
}

/* 优化链接样式 */
.analysis-result :deep(a) {
  color: #2080f0;
  text-decoration: none;
  border-bottom: 1px dotted #2080f0;
  transition: all 0.2s ease;
  font-weight: 500;
}

.analysis-result :deep(a:hover) {
  color: #36ad6a;
  border-bottom: 1px solid #36ad6a;
}
</style>
