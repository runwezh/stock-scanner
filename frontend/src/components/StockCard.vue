<template>
  <n-card class="stock-card" :bordered="false" :class="{ 'is-analyzing': isAnalyzing }">
    <div class="card-header">
      <div class="stock-info">
        <div class="stock-code">{{ stock.code }}</div>
        <div class="stock-name">{{ stock.name || '加载中...' }}</div>
      </div>
      <div class="stock-price-info" v-if="stock.price !== undefined">
        <div class="stock-price">{{ stock.price.toFixed(2) }}</div>
        <div class="stock-change" :class="{ 
          'up': stock.changePercent && stock.changePercent > 0,
          'down': stock.changePercent && stock.changePercent < 0
        }">
          {{ formatChangePercent(stock.changePercent) }}
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
      </template>
      
      <template v-else-if="stock.analysisStatus === 'error'">
        <div class="error-status">
          <n-icon :component="AlertCircleIcon" class="error-icon" />
          <span>分析出错: {{ stock.error || '未知错误' }}</span>
        </div>
      </template>
      
      <template v-else-if="stock.analysisStatus === 'completed'">
        <div class="analysis-result" v-html="parsedAnalysis"></div>
      </template>
    </div>
    
    <template #footer>
      <div class="card-footer">
        <div class="market-value" v-if="stock.marketValue">
          市值: {{ formatMarketValue(stock.marketValue) }}
        </div>
        <div class="market-type">
          {{ getMarketName(stock.marketType) }}
        </div>
      </div>
    </template>
  </n-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { NCard, NDivider, NSpin, NIcon } from 'naive-ui';
import { AlertCircleOutline as AlertCircleIcon } from '@vicons/ionicons5';
import { parseMarkdown, formatMarketValue as formatMarketValueFn } from '@/utils';
import type { StockInfo } from '@/types';

const props = defineProps<{
  stock: StockInfo;
}>();

const isAnalyzing = computed(() => {
  return props.stock.analysisStatus === 'analyzing';
});

const parsedAnalysis = computed(() => {
  if (props.stock.analysis) {
    return parseMarkdown(props.stock.analysis);
  }
  return '';
});

function formatChangePercent(percent: number | undefined): string {
  if (percent === undefined) return '--';
  
  const sign = percent > 0 ? '+' : '';
  return `${sign}${percent.toFixed(2)}%`;
}

function formatMarketValue(value: number): string {
  return formatMarketValueFn(value);
}

function getMarketName(marketType: string): string {
  const marketMap: Record<string, string> = {
    'A': 'A股',
    'HK': '港股',
    'US': '美股'
  };
  
  return marketMap[marketType] || marketType;
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
}

.stock-name {
  font-size: 0.875rem;
  color: var(--n-text-color-3);
  margin-top: 0.25rem;
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
}

.waiting-status,
.analyzing-status,
.error-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--n-text-color-3);
  font-size: 0.875rem;
}

.error-icon {
  color: var(--n-error-color);
}

.analysis-result {
  font-size: 0.875rem;
  line-height: 1.5;
}

.analysis-result :deep(p) {
  margin: 0.5rem 0;
}

.analysis-result :deep(ul) {
  margin: 0.5rem 0;
  padding-left: 1.25rem;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--n-text-color-3);
}
</style>
