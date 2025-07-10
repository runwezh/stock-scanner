<template>
  <NConfigProvider :theme="theme">
    <NMessageProvider>
      <NLoadingBarProvider>
        <NDialogProvider>
          <NNotificationProvider>
            <router-view />
          </NNotificationProvider>
        </NDialogProvider>
      </NLoadingBarProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>

<script setup lang="ts">
import {
  type GlobalTheme,
  NConfigProvider,
  NDialogProvider,
  NLoadingBarProvider,
  NMessageProvider,
  NNotificationProvider,
} from "naive-ui";
import { ref } from "vue";

// 主题设置 (默认使用亮色主题)
const theme = ref<GlobalTheme | null>(null); // 可以切换为 darkTheme 以启用暗色模式
</script>

<style>
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, 
    Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  margin: 0;
  padding: 0;
  min-height: 100vh;
  background-color: #f6f6f6;
}
</style>
