<template>
  <NCard
    class="market-time-card mobile-card mobile-shadow mobile-market-time-card"
  >
    <NGrid
      :x-gap="16"
      :y-gap="16"
      cols="1 s:2 m:4"
      responsive="screen"
    >
      <!-- 当前时间 -->
      <NGridItem>
        <div class="time-block current-time-block mobile-time-block">
          <p class="time-label mobile-time-label">
            当前时间
          </p>
          <p class="current-time mobile-current-time">
            {{ marketInfo.currentTime }}
          </p>
        </div>
      </NGridItem>

      <!-- A股状态 -->
      <NGridItem>
        <div
          class="time-block market-block mobile-time-block"
          :class="{
            'market-open-block mobile-market-open-block':
              marketInfo.cnMarket.isOpen,
            'market-closed-block mobile-market-closed-block':
              !marketInfo.cnMarket.isOpen,
          }"
        >
          <p class="time-label mobile-time-label">
            A股市场
          </p>
          <div
            class="market-status"
            :class="
              marketInfo.cnMarket.isOpen ? 'status-open' : 'status-closed'
            "
          >
            <NTag
              v-if="marketInfo.cnMarket.isOpen"
              type="success"
              size="medium"
              round
              class="status-tag mobile-touch-target mobile-status-tag"
            >
              <template #icon>
                <NIcon size="18">
                  <pulse-icon />
                </NIcon>
              </template>
              交易中
            </NTag>
            <NTag
              v-else
              type="default"
              size="medium"
              round
              class="status-tag mobile-touch-target mobile-status-tag"
            >
              <template #icon>
                <NIcon size="18">
                  <time-icon />
                </NIcon>
              </template>
              已休市
            </NTag>
          </div>
          <p class="time-counter mobile-time-counter">
            {{ marketInfo.cnMarket.nextTime }}
          </p>
          <div class="market-progress-container">
            <div
              class="market-progress-bar"
              :class="
                marketInfo.cnMarket.isOpen ? 'progress-open' : 'progress-closed'
              "
              :style="{ width: marketInfo.cnMarket.progressPercentage + '%' }"
            />
            <div
              class="progress-markers"
              :class="{ 'reverse-markers': !marketInfo.cnMarket.isOpen }"
            >
              <div
                class="progress-marker"
                :class="marketInfo.cnMarket.isOpen ? 'start' : 'end'"
              >
                开盘
              </div>
              <div
                class="progress-marker"
                :class="marketInfo.cnMarket.isOpen ? 'end' : 'start'"
              >
                收盘
              </div>
            </div>
          </div>
        </div>
      </NGridItem>

      <!-- 港股状态 -->
      <NGridItem>
        <div
          class="time-block market-block"
          :class="{
            'market-open-block': marketInfo.hkMarket.isOpen,
            'market-closed-block': !marketInfo.hkMarket.isOpen,
          }"
        >
          <p class="time-label">
            港股市场
          </p>
          <div
            class="market-status"
            :class="
              marketInfo.hkMarket.isOpen ? 'status-open' : 'status-closed'
            "
          >
            <NTag
              v-if="marketInfo.hkMarket.isOpen"
              type="success"
              size="medium"
              round
              class="status-tag mobile-touch-target"
            >
              <template #icon>
                <NIcon size="18">
                  <pulse-icon />
                </NIcon>
              </template>
              交易中
            </NTag>
            <NTag
              v-else
              type="default"
              size="medium"
              round
              class="status-tag mobile-touch-target"
            >
              <template #icon>
                <NIcon size="18">
                  <time-icon />
                </NIcon>
              </template>
              已休市
            </NTag>
          </div>
          <p class="time-counter">
            {{ marketInfo.hkMarket.nextTime }}
          </p>
          <div class="market-progress-container">
            <div
              class="market-progress-bar"
              :class="
                marketInfo.hkMarket.isOpen ? 'progress-open' : 'progress-closed'
              "
              :style="{ width: marketInfo.hkMarket.progressPercentage + '%' }"
            />
            <div
              class="progress-markers"
              :class="{ 'reverse-markers': !marketInfo.hkMarket.isOpen }"
            >
              <div
                class="progress-marker"
                :class="marketInfo.hkMarket.isOpen ? 'start' : 'end'"
              >
                开盘
              </div>
              <div
                class="progress-marker"
                :class="marketInfo.hkMarket.isOpen ? 'end' : 'start'"
              >
                收盘
              </div>
            </div>
          </div>
        </div>
      </NGridItem>

      <!-- 美股状态 -->
      <NGridItem>
        <div
          class="time-block market-block"
          :class="{
            'market-open-block': marketInfo.usMarket.isOpen,
            'market-closed-block': !marketInfo.usMarket.isOpen,
          }"
        >
          <p class="time-label">
            美股市场
          </p>
          <div
            class="market-status"
            :class="
              marketInfo.usMarket.isOpen ? 'status-open' : 'status-closed'
            "
          >
            <NTag
              v-if="marketInfo.usMarket.isOpen"
              type="success"
              size="medium"
              round
              class="status-tag mobile-touch-target"
            >
              <template #icon>
                <NIcon size="18">
                  <pulse-icon />
                </NIcon>
              </template>
              交易中
            </NTag>
            <NTag
              v-else
              type="default"
              size="medium"
              round
              class="status-tag mobile-touch-target"
            >
              <template #icon>
                <NIcon size="18">
                  <time-icon />
                </NIcon>
              </template>
              已休市
            </NTag>
          </div>
          <p class="time-counter">
            {{ marketInfo.usMarket.nextTime }}
          </p>
          <div class="market-progress-container">
            <div
              class="market-progress-bar"
              :class="
                marketInfo.usMarket.isOpen ? 'progress-open' : 'progress-closed'
              "
              :style="{ width: marketInfo.usMarket.progressPercentage + '%' }"
            />
            <div
              class="progress-markers"
              :class="{ 'reverse-markers': !marketInfo.usMarket.isOpen }"
            >
              <div
                class="progress-marker"
                :class="marketInfo.usMarket.isOpen ? 'start' : 'end'"
              >
                开盘
              </div>
              <div
                class="progress-marker"
                :class="marketInfo.usMarket.isOpen ? 'end' : 'start'"
              >
                收盘
              </div>
            </div>
          </div>
        </div>
      </NGridItem>
    </NGrid>
  </NCard>
</template>

<script lang="ts">
import type { MarketStatus, MarketTimeInfo } from "@/types";
import { updateMarketTimeInfo } from "@/utils";
import {
  PulseOutline as PulseIcon,
  TimeOutline as TimeIcon,
} from "@vicons/ionicons5";
import { NCard, NGrid, NGridItem, NIcon, NTag } from "naive-ui";
import { defineComponent, onBeforeUnmount, onMounted, ref } from "vue";

export default defineComponent({
  name: "MarketTimeDisplay",
  components: {
    NCard,
    NGrid,
    NGridItem,
    NTag,
    NIcon,
  },
  props: {
    isMobile: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    const marketInfo = ref<MarketTimeInfo>({
      currentTime: "",
      cnMarket: { isOpen: false, nextTime: "" },
      hkMarket: { isOpen: false, nextTime: "" },
      usMarket: { isOpen: false, nextTime: "" },
    });

    let intervalId: number | null = null;

    function updateMarketTime() {
      const baseInfo = updateMarketTimeInfo();

      // 计算各市场的进度百分比
      marketInfo.value = {
        currentTime: baseInfo.currentTime,
        cnMarket: {
          ...baseInfo.cnMarket,
          progressPercentage: calculateProgressPercentage(baseInfo.cnMarket),
        },
        hkMarket: {
          ...baseInfo.hkMarket,
          progressPercentage: calculateProgressPercentage(baseInfo.hkMarket),
        },
        usMarket: {
          ...baseInfo.usMarket,
          progressPercentage: calculateProgressPercentage(baseInfo.usMarket),
        },
      };
    }

    // 计算进度百分比的函数
    function calculateProgressPercentage(market: MarketStatus): number {
      // 从nextTime中提取时间信息来计算进度
      const timeText = market.nextTime;

      // 如果没有时间文本，返回默认值50%
      if (!timeText) {
        return 50;
      }

      try {
        // 特殊情况处理
        if (timeText.includes("已休市") || timeText.includes("已闭市")) {
          return market.isOpen ? 100 : 0; // 休市状态：开市时为100%，休市时为0%
        }

        if (timeText.includes("即将开市") || timeText.includes("即将开盘")) {
          return market.isOpen ? 5 : 95; // 即将开市：开市时为5%，休市时为95%
        }

        // 提取小时和分钟，支持多种格式
        let hours = 0;
        let minutes = 0;

        // 匹配"XX小时XX分钟"格式
        const hourMinuteMatch = timeText.match(/(\d+)\s*小时\s*(\d+)\s*分钟/);
        if (hourMinuteMatch) {
          hours = Number.parseInt(hourMinuteMatch[1]);
          minutes = Number.parseInt(hourMinuteMatch[2]);
        } else {
          // 单独匹配小时和分钟
          const hourMatch = timeText.match(/(\d+)\s*小时/);
          const minuteMatch = timeText.match(/(\d+)\s*分钟/);

          hours = hourMatch ? Number.parseInt(hourMatch[1]) : 0;
          minutes = minuteMatch ? Number.parseInt(minuteMatch[1]) : 0;
        }

        // 总分钟数
        const totalMinutes = hours * 60 + minutes;

        // 根据市场类型设置不同的交易时长
        let tradingMinutes = 240; // 默认交易时长4小时
        let nonTradingMinutes = 1200; // 默认非交易时长20小时

        // 根据市场调整时长
        if (
          timeText.includes("A股") ||
          timeText.includes("沪深") ||
          (!timeText.includes("港股") && !timeText.includes("美股"))
        ) {
          tradingMinutes = 240; // A股交易4小时
          nonTradingMinutes = 1200; // 非交易20小时
        } else if (timeText.includes("港股")) {
          tradingMinutes = 390; // 港股交易6.5小时
          nonTradingMinutes = 1050; // 非交易17.5小时
        } else if (timeText.includes("美股")) {
          tradingMinutes = 390; // 美股交易6.5小时
          nonTradingMinutes = 1050; // 非交易17.5小时
        }

        // 根据市场状态计算进度
        if (market.isOpen) {
          // 市场开市状态 - 从开盘到收盘方向
          if (
            timeText.includes("距离收市") ||
            timeText.includes("距离闭市") ||
            timeText.includes("距离休市") ||
            timeText.includes("距离收盘")
          ) {
            // 计算已经交易的时间比例
            const tradedMinutes = tradingMinutes - totalMinutes;
            const percentage = (tradedMinutes / tradingMinutes) * 100;
            return Math.max(0, Math.min(100, percentage));
          }
          // 处理交易开始阶段但没有明确提示的情况
          return 5; // 开盘初期设为5%
        }
        // 市场休市状态 - 从收盘到开盘方向
        if (timeText.includes("距离开市") || timeText.includes("距离开盘")) {
          // 计算接近开盘的时间比例
          const closedMinutes = nonTradingMinutes - totalMinutes;
          const percentage = (closedMinutes / nonTradingMinutes) * 100;
          // 反转比例：0% 表示刚刚休市，100% 表示即将开盘
          return Math.max(0, Math.min(100, 100 - percentage));
        }
        // 处理休市开始阶段但没有明确提示的情况
        return 5; // 刚休市设为5%
      } catch (error) {
        console.error("计算市场进度时出错:", error);
        // 出错时返回默认值
        return market.isOpen ? 50 : 5;
      }
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

    return {
      PulseIcon,
      TimeIcon,
      marketInfo,
    };
  },
});
</script>

<style scoped>
.market-time-card {
  margin-bottom: 1.5rem;
  padding: 0.75rem;
  border-radius: 0.75rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  background: linear-gradient(
    to bottom,
    rgba(250, 250, 252, 0.8),
    rgba(245, 245, 250, 0.5)
  );
  min-height: 200px; /* 确保卡片有最小高度 */
}

/* 确保网格布局在各种屏幕尺寸下正确显示 */
:deep(.n-grid) {
  justify-content: center;
  width: 100%;
}

:deep(.n-grid-item) {
  display: flex;
  justify-content: center;
}

.time-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 0.75rem;
  border-radius: 0.625rem;
  transition: all 0.3s ease;
  height: 100%;
  box-sizing: border-box;
  max-width: 100%; /* 确保不超过父容器宽度 */
}

.current-time-block {
  background-color: rgba(32, 128, 240, 0.05);
  border: 1px solid rgba(32, 128, 240, 0.1);
  max-width: 360px; /* 限制当前时间块的最大宽度 */
  width: 100%; /* 确保响应式 */
  margin: 0 auto; /* 居中显示 */
}

.market-block {
  position: relative;
  overflow: hidden;
  border: 1px solid transparent;
  max-width: 360px; /* 限制市场块的最大宽度 */
  width: 100%; /* 确保响应式 */
  margin: 0 auto; /* 居中显示 */
}

.market-open-block {
  background-color: rgba(24, 160, 88, 0.05);
  border-color: rgba(24, 160, 88, 0.1);
}

.market-closed-block {
  background-color: rgba(128, 128, 128, 0.05);
  border-color: rgba(128, 128, 128, 0.1);
}

.time-label {
  font-size: 1rem;
  color: var(--n-text-color-3);
  margin-bottom: 0.75rem;
  font-weight: 500;
}

.current-time {
  font-size: 1.75rem;
  font-weight: bold;
  color: var(--n-text-color);
}

.market-status {
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 36px;
  width: 100%;
  flex-wrap: wrap; /* 允许内容在必要时换行 */
}

.status-tag {
  padding: 0 16px !important;
  height: 36px !important;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 100px;
  max-width: 100%; /* 确保不超过父容器宽度 */
}

.market-status :deep(.n-tag__icon) {
  margin-right: 6px;
}

.status-open :deep(.n-tag) {
  background-color: rgba(24, 160, 88, 0.15);
  border: 1px solid var(--n-success-color);
  animation: pulse 2s infinite;
}

.status-closed :deep(.n-tag) {
  background-color: rgba(128, 128, 128, 0.1);
  border: 1px solid rgba(128, 128, 128, 0.3);
}

.time-counter {
  font-size: 0.875rem;
  color: var(--n-text-color-3);
  margin-top: 0.5rem;
  width: 100%; /* 确保文本容器占满宽度 */
  text-align: center; /* 文本居中 */
  white-space: nowrap; /* 防止文本换行 */
  overflow: hidden; /* 隐藏溢出内容 */
  text-overflow: ellipsis; /* 显示省略号 */
}

/* 进度条样式 */
.market-progress-container {
  width: 100%;
  height: 6px;
  background-color: rgba(200, 200, 200, 0.3);
  border-radius: 3px;
  margin-top: 0.75rem;
  overflow: visible;
  position: relative;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(200, 200, 200, 0.4);
  max-width: 100%; /* 确保不超过父容器宽度 */
}

.market-progress-bar {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s ease;
  position: relative;
}

.market-progress-bar::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.15) 0%,
    rgba(255, 255, 255, 0.4) 50%,
    rgba(255, 255, 255, 0.15) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
}

.progress-open {
  background-color: rgba(24, 160, 88, 0.9);
  box-shadow: 0 0 8px rgba(24, 160, 88, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  border: 1px solid rgba(24, 160, 88, 1);
}

.progress-closed {
  background-color: rgba(100, 100, 100, 0.8);
  box-shadow: 0 0 5px rgba(100, 100, 100, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(80, 80, 80, 1);
}

/* 进度条标记 */
.progress-markers {
  position: absolute;
  top: -20px;
  left: 0;
  width: 100%;
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--n-text-color-2);
  padding: 0 2px;
  font-weight: 500;
  text-shadow: 0 1px 1px rgba(255, 255, 255, 0.7);
  box-sizing: border-box; /* 确保内边距不会增加宽度 */
}

/* 反向标记（休市状态） */
.reverse-markers {
  flex-direction: row-reverse;
}

.progress-marker {
  position: relative;
  white-space: nowrap; /* 防止文本换行 */
  max-width: 45%; /* 限制宽度，防止重叠 */
  overflow: hidden; /* 隐藏溢出内容 */
  text-overflow: ellipsis; /* 显示省略号 */
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(24, 160, 88, 0.4);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(24, 160, 88, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(24, 160, 88, 0);
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .market-time-card {
    padding: 0.5rem;
    margin-bottom: 1rem;
    min-height: 180px; /* 移动端下的最小高度 */
  }

  .time-block {
    padding: 0.625rem;
    margin-bottom: 0.75rem; /* 增加底部外边距 */
  }

  .current-time {
    font-size: 1.5rem;
  }

  .time-label {
    font-size: 0.9375rem;
    margin-bottom: 0.5rem;
  }

  .status-tag {
    min-width: 100px; /* 减小移动端下的最小宽度 */
    height: 36px !important;
    font-size: 0.875rem; /* 减小字体大小 */
  }

  .time-counter {
    font-size: 0.75rem; /* 减小字体大小 */
    margin-top: 0.375rem;
  }

  /* 增强视觉层次 */
  .market-open-block::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background-color: var(--n-success-color);
    border-radius: 2px;
  }

  .market-closed-block::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background-color: rgba(128, 128, 128, 0.5);
    border-radius: 2px;
  }

  .market-progress-container {
    height: 5px;
    margin-top: 0.5rem;
    border-width: 1px;
  }

  .progress-markers {
    top: -18px; /* 调整位置 */
    font-size: 0.6875rem;
  }

  .progress-marker {
    max-width: 40%; /* 移动端下进一步限制宽度 */
  }

  .progress-marker.start::before,
  .progress-marker.end::before {
    top: -10px;
    height: 6px;
  }

  /* 增强移动端进度条可见性 */
  .progress-open {
    background-color: rgba(24, 160, 88, 1);
    box-shadow: 0 0 6px rgba(24, 160, 88, 0.6);
  }

  .progress-closed {
    background-color: rgba(90, 90, 90, 0.9);
    box-shadow: 0 0 4px rgba(90, 90, 90, 0.5);
  }

  .current-time-block {
    max-width: 360px; /* 移动端下的最大宽度 */
  }

  .market-block {
    max-width: 360px; /* 移动端下的最大宽度 */
  }
}

/* 小屏幕手机适配 */
@media (max-width: 480px) {
  .market-time-card {
    padding: 0.375rem;
    min-height: 160px; /* 小屏幕下的最小高度 */
  }

  .time-block {
    padding: 0.5rem;
    margin-bottom: 1rem; /* 增加小屏幕下的底部外边距 */
  }

  .current-time {
    font-size: 1.25rem;
  }

  .time-label {
    font-size: 0.875rem;
  }

  .time-counter {
    font-size: 0.75rem;
  }

  .status-tag {
    min-width: 90px; /* 进一步减小最小宽度 */
    font-size: 0.8125rem;
    padding: 0 12px !important; /* 减小内边距 */
  }

  /* 确保边框在小屏幕上清晰可见 */
  .time-block {
    border-width: 1px !important;
  }

  .market-progress-container {
    height: 4px;
    margin-top: 0.375rem;
    box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.1);
  }

  .progress-markers {
    top: -16px; /* 调整位置 */
    font-size: 0.625rem;
  }

  .progress-marker {
    max-width: 35%; /* 小屏幕下进一步限制宽度 */
  }

  .progress-marker.start::before,
  .progress-marker.end::before {
    top: -8px;
    height: 5px;
  }

  /* 进一步增强小屏幕进度条可见性 */
  .market-progress-container {
    border-width: 1px;
  }

  .progress-open,
  .progress-closed {
    border-width: 0;
  }

  .current-time-block {
    max-width: 300px; /* 小屏幕下的最大宽度 */
  }

  .market-block {
    max-width: 300px; /* 小屏幕下的最大宽度 */
  }
}

/* 确保API配置面板有足够的空间 */
.n-collapse {
  margin-bottom: 16px; /* 添加底部间距 */
  padding-bottom: 8px; /* 增加内边距底部 */
}
</style>
