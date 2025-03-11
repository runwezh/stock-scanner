<template>
  <div v-if="showAnnouncement" class="announcement-container mobile-announcement-container" :class="{ 'login-page-announcement mobile-login-announcement': isLoginPage }">
    <n-card class="announcement-card mobile-card" :class="{ 'login-card-style': isLoginPage }">
      <template #header>
        <div class="announcement-header mobile-announcement-header">
          <n-icon size="18" :component="InformationCircleIcon" class="info-icon" />
          <span>系统公告</span>
        </div>
      </template>
      <div class="announcement-content mobile-announcement-content" v-html="processedContent"></div>
      <div class="announcement-timer mobile-announcement-timer">{{ remainingTimeText }}</div>
      <template #action>
        <n-button quaternary circle size="small" @click="closeAnnouncement" class="mobile-touch-target">
          <template #icon>
            <n-icon :component="CloseIcon" />
          </template>
        </n-button>
      </template>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { NCard, NIcon, NButton } from 'naive-ui';
import { InformationCircleOutline as InformationCircleIcon } from '@vicons/ionicons5';
import { Close as CloseIcon } from '@vicons/ionicons5';
import { useRoute } from 'vue-router';

const props = defineProps<{
  content: string;
  autoCloseTime?: number;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const route = useRoute();
const isLoginPage = computed(() => route.path === '/login');

const showAnnouncement = ref(true);
const remainingTime = ref(props.autoCloseTime || 5);
const timer = ref<number | null>(null);

const remainingTimeText = computed(() => {
  return `${remainingTime.value}秒后自动关闭`;
});

const processedContent = computed(() => {
  // 处理文本中的URL
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  return props.content.replace(
    urlRegex, 
    '<a href="$1" target="_blank" class="announcement-link">$1</a>'
  );
});

function closeAnnouncement() {
  showAnnouncement.value = false;
  if (timer.value !== null) {
    window.clearInterval(timer.value);
    timer.value = null;
  }
  emit('close');
}

function updateTimer() {
  if (remainingTime.value <= 1) {
    closeAnnouncement();
  } else {
    remainingTime.value--;
  }
}

onMounted(() => {
  timer.value = window.setInterval(updateTimer, 1000);
});

onBeforeUnmount(() => {
  if (timer.value !== null) {
    window.clearInterval(timer.value);
  }
});
</script>

<style scoped>
.announcement-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  max-width: 24rem;
  z-index: 50;
  animation: fadeInDown 0.3s ease-out;
}

.announcement-card {
  border-left: 4px solid var(--n-primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 0.5rem;
  overflow: hidden;
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.9);
}

.announcement-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.info-icon {
  color: var(--n-primary-color);
}

.announcement-content {
  margin-bottom: 0.5rem;
  white-space: pre-line;
}

.announcement-timer {
  font-size: 0.75rem;
  color: var(--n-text-color-disabled);
}

.announcement-link {
  color: var(--n-primary-color);
  text-decoration: underline;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 登录页面适配 */
.login-page-announcement {
  z-index: 1000;
  top: 1.5rem;
  right: 1.5rem;
}

.login-card-style {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border-left: 4px solid #2080f0;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

</style>
