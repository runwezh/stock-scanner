<template>
  <div class="safe-area-bottom"></div>
</template>

<script setup lang="ts">
// 底部安全区域组件，用于解决底部背景显示问题
</script>

<style scoped>
.safe-area-bottom {
  width: 100%;
  height: env(safe-area-inset-bottom, 0);
  min-height: 10px; /* 确保在不支持env()的浏览器上也有一定的空间 */
  background-color: inherit;
  position: relative;
  z-index: 1;
}

@media (max-width: 768px) {
  .safe-area-bottom {
    min-height: 20px;
  }
}
</style> 