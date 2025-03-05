<template>
  <n-card class="market-time-card">
    <n-grid :x-gap="16" :y-gap="16" :cols="gridCols">
      <!-- 当前时间 -->
      <n-grid-item>
        <div class="time-block">
          <p class="time-label">当前时间</p>
          <p class="current-time">{{ marketInfo.currentTime }}</p>
        </div>
      </n-grid-item>
      
      <!-- A股状态 -->
      <n-grid-item>
        <div class="time-block">
          <p class="time-label">A股市场</p>
          <p class="market-status" :class="marketInfo.cnMarket.isOpen ? 'status-open' : 'status-closed'">
            {{ marketInfo.cnMarket.isOpen ? '交易中' : '已休市' }}
          </p>
          <p class="time-counter">{{ marketInfo.cnMarket.nextTime }}</p>
        </div>
      </n-grid-item>

      <!-- 港股状态 -->
      <n-grid-item>
        <div class="time-block">
          <p class="time-label">港股市场</p>
          <p class="market-status" :class="marketInfo.hkMarket.isOpen ? 'status-open' : 'status-closed'">
            {{ marketInfo.hkMarket.isOpen ? '交易中' : '已休市' }}
          </p>
          <p class="time-counter">{{ marketInfo.hkMarket.nextTime }}</p>
        </div>
      </n-grid-item>
      
      <!-- 美股状态 -->
      <n-grid-item>
        <div class="time-block">
          <p class="time-label">美股市场</p>
          <p class="market-status" :class="marketInfo.usMarket.isOpen ? 'status-open' : 'status-closed'">
            {{ marketInfo.usMarket.isOpen ? '交易中' : '已休市' }}
          </p>
          <p class="time-counter">{{ marketInfo.usMarket.nextTime }}</p>
        </div>
      </n-grid-item>
    </n-grid>
  </n-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { NCard, NGrid, NGridItem } from 'naive-ui';
import { updateMarketTimeInfo } from '@/utils';
import type { MarketTimeInfo } from '@/types';

const props = defineProps({
  isMobile: {
    type: Boolean,
    default: false
  }
});

const marketInfo = ref<MarketTimeInfo>({
  currentTime: '',
  cnMarket: { isOpen: false, nextTime: '' },
  hkMarket: { isOpen: false, nextTime: '' },
  usMarket: { isOpen: false, nextTime: '' }
});

const gridCols = computed(() => {
  return props.isMobile ? 1 : 4;
});

let intervalId: number | null = null;

function updateMarketTime() {
  marketInfo.value = updateMarketTimeInfo();
}

onMounted(() => {
  updateMarketTime(); // 立即更新一次
  intervalId = window.setInterval(updateMarketTime, 1000);
});

onBeforeUnmount(() => {
  if (intervalId !== null) {
    window.clearInterval(intervalId);
    intervalId = null;
  }
});
</script>

<style scoped>
.market-time-card {
  margin-bottom: 1.5rem;
}

.time-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.time-label {
  font-size: 0.875rem;
  color: var(--n-text-color-3);
  margin-bottom: 0.5rem;
}

.current-time {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--n-text-color);
}

.market-status {
  font-size: 1.125rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.status-open {
  color: var(--n-success-color);
}

.status-closed {
  color: var(--n-text-color-3);
}

.time-counter {
  font-size: 0.75rem;
  color: var(--n-text-color-3);
}
</style>
