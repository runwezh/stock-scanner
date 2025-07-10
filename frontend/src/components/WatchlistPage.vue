<template>
  <div class="watchlist-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <NButton
        class="back-button"
        @click="goBack"
      >
        <template #icon>
          <NIcon><ArrowBackIcon /></NIcon>
        </template>
        返回首页
      </NButton>
      <h1 class="page-title">
        自选股管理
      </h1>
    </div>

    <!-- 自选股管理组件 -->
    <WatchlistManagement 
      ref="watchlistRef"
      @analyze-watchlist="handleAnalyzeWatchlist"
    />
  </div>
</template>

<script setup lang="ts">
import { ArrowBackOutline as ArrowBackIcon } from "@vicons/ionicons5";
import { NButton, NIcon } from "naive-ui";
import { ref } from "vue";
import { useRouter } from "vue-router";

import WatchlistManagement from "./WatchlistManagement.vue";

const router = useRouter();
const watchlistRef = ref();

// 返回首页
function goBack() {
  router.push("/");
}

// 处理自选股分析
function handleAnalyzeWatchlist(codes: string[], marketType: string) {
  // 跳转到首页并传递分析参数
  router.push({
    path: "/",
    query: {
      codes: codes.join(","),
      marketType: marketType,
      source: "watchlist",
    },
  });
}
</script>

<style scoped>
.watchlist-page {
  min-height: 100vh;
  background-color: #f6f6f6;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-button {
  flex-shrink: 0;
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .page-header {
    padding: 12px 16px;
  }
  
  .page-title {
    font-size: 16px;
  }
}
</style>