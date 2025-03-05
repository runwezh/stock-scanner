<template>
  <div class="api-config-section">
    <n-button
      class="toggle-button"
      size="small"
      @click="toggleConfig"
      :quaternary="true"
    >
      <template #icon>
        <n-icon :component="expanded ? ChevronUpIcon : ChevronDownIcon" />
      </template>
      API配置 {{ expanded ? '收起' : '展开' }}
    </n-button>
    
    <n-collapse-transition :show="expanded">
      <n-card class="api-config-card" content-style="padding: 0.75rem;">
        <n-alert title="OpenAI API配置" type="info" v-if="isApiInfoVisible">
          <template #icon>
            <n-icon :component="InformationCircleIcon" />
          </template>
          <p>您可以配置自己的API，也可以使用系统默认配置。API密钥仅在您的浏览器中使用，不会发送到服务器存储。</p>
          <div class="alert-actions">
            <n-button text @click="isApiInfoVisible = false">
              <template #icon>
                <n-icon :component="CloseIcon" />
              </template>
            </n-button>
          </div>
        </n-alert>

        <n-grid :cols="24" :x-gap="12">
          <n-grid-item :span="14">
            <n-form-item label="API URL" path="apiUrl">
              <n-input 
                v-model:value="apiConfig.apiUrl" 
                placeholder="https://api.openai.com/v1/chat/completions"
                @update:value="handleConfigChange"
              />
              <template #feedback>
                <span class="formatted-url">{{ formattedUrl }}</span>
              </template>
            </n-form-item>
          </n-grid-item>

          <n-grid-item :span="10">
            <n-form-item label="API Key" path="apiKey">
              <n-input 
                v-model:value="apiConfig.apiKey" 
                type="password" 
                placeholder="sk-..."
                show-password-on="click"
                @update:value="handleConfigChange"
              />
            </n-form-item>
          </n-grid-item>

          <n-grid-item :span="12">
            <n-form-item label="模型" path="apiModel">
              <n-input 
                v-model:value="apiConfig.apiModel" 
                placeholder="gpt-3.5-turbo"
                @update:value="handleConfigChange"
              />
            </n-form-item>
          </n-grid-item>

          <n-grid-item :span="12">
            <n-form-item label="超时时间(秒)" path="apiTimeout">
              <n-input-number 
                v-model:value="apiTimeout" 
                placeholder="60"
                :min="1"
                :max="300"
                @update:value="handleTimeoutChange"
              />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <div class="api-actions">
          <div class="api-save-option">
            <n-switch 
              v-model:value="apiConfig.saveApiConfig"
              @update:value="handleConfigChange"
            />
            <span class="save-label">保存配置到本地</span>
          </div>
          
          <div class="api-buttons">
            <n-button 
              type="primary" 
              :loading="testingConnection" 
              :disabled="!isConfigValid"
              @click="testConnection"
            >
              测试连接
            </n-button>

            <n-button @click="resetConfig">
              重置
            </n-button>
          </div>
        </div>
      </n-card>
    </n-collapse-transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { 
  NButton, 
  NIcon, 
  NCard, 
  NCollapseTransition, 
  NGrid, 
  NGridItem, 
  NFormItem, 
  NInput,
  NInputNumber,
  NSwitch,
  NAlert,
  useMessage
} from 'naive-ui';
import { 
  ChevronDown as ChevronDownIcon, 
  ChevronUp as ChevronUpIcon,
  InformationCircleOutline as InformationCircleIcon,
  Close as CloseIcon
} from '@vicons/ionicons5';
import { apiService } from '@/services/api';
import { saveApiConfigToLocalStorage, loadApiConfig } from '@/utils';
import type { ApiConfig } from '@/types';

const props = defineProps<{
  defaultApiUrl?: string;
  defaultApiModel?: string;
  defaultApiTimeout?: string;
}>();

const emit = defineEmits<{
  (e: 'update:apiConfig', value: ApiConfig): void;
}>();

const message = useMessage();
const expanded = ref(false);
const testingConnection = ref(false);
const isApiInfoVisible = ref(true);

// API配置
const apiConfig = ref<ApiConfig>({
  apiUrl: props.defaultApiUrl || '',
  apiKey: '',
  apiModel: props.defaultApiModel || 'gpt-3.5-turbo',
  apiTimeout: props.defaultApiTimeout || '60',
  saveApiConfig: false
});

const apiTimeout = computed({
  get: () => parseInt(apiConfig.value.apiTimeout) || 60,
  set: (val: number) => {
    apiConfig.value.apiTimeout = val.toString();
  }
});

const isConfigValid = computed(() => {
  return apiConfig.value.apiUrl && apiConfig.value.apiKey;
});

const formattedUrl = computed(() => {
  return formatApiUrl(apiConfig.value.apiUrl);
});

function toggleConfig() {
  expanded.value = !expanded.value;
}

function handleConfigChange() {
  // 如果选择了保存配置，则自动保存
  if (apiConfig.value.saveApiConfig) {
    saveApiConfigToLocalStorage({
      apiUrl: apiConfig.value.apiUrl,
      apiKey: apiConfig.value.apiKey,
      apiModel: apiConfig.value.apiModel,
      apiTimeout: apiConfig.value.apiTimeout,
      saveApiConfig: true
    });
  }
  
  // 向父组件发送更新事件
  emit('update:apiConfig', { ...apiConfig.value });
}

function handleTimeoutChange(value: number | null) {
  if (value !== null) {
    apiConfig.value.apiTimeout = value.toString();
    handleConfigChange();
  }
}

function formatApiUrl(url: string): string {
  if (!url) return '';
  
  try {
    // 尝试解析URL
    const parsedUrl = new URL(url);
    return `${parsedUrl.origin}${parsedUrl.pathname}`;
  } catch (e) {
    // 如果URL格式错误，则返回原始字符串
    return url;
  }
}

async function testConnection() {
  if (!isConfigValid.value) {
    message.error('请填写完整的API配置信息');
    return;
  }
  
  testingConnection.value = true;
  
  try {
    const response = await apiService.testApiConnection({
      api_url: apiConfig.value.apiUrl,
      api_key: apiConfig.value.apiKey,
      api_model: apiConfig.value.apiModel,
      api_timeout: apiConfig.value.apiTimeout
    });
    
    if (response.success) {
      message.success('API连接测试成功');
      
      // 如果选择了保存配置，则保存
      if (apiConfig.value.saveApiConfig) {
        saveApiConfigToLocalStorage({
          apiUrl: apiConfig.value.apiUrl,
          apiKey: apiConfig.value.apiKey,
          apiModel: apiConfig.value.apiModel,
          apiTimeout: apiConfig.value.apiTimeout,
          saveApiConfig: true
        });
      }
    } else {
      message.error(`API连接测试失败: ${response.message}`);
    }
  } catch (error: any) {
    message.error(`测试连接出错: ${error.message || '未知错误'}`);
  } finally {
    testingConnection.value = false;
  }
}

function resetConfig() {
  apiConfig.value = {
    apiUrl: props.defaultApiUrl || '',
    apiKey: '',
    apiModel: props.defaultApiModel || 'gpt-3.5-turbo',
    apiTimeout: props.defaultApiTimeout || '60',
    saveApiConfig: false
  };
  
  // 清除本地存储
  if (window.localStorage) {
    localStorage.removeItem('apiConfig');
  }
  
  message.success('已重置API配置');
  emit('update:apiConfig', { ...apiConfig.value });
}

onMounted(() => {
  // 加载保存的配置
  const savedConfig = loadApiConfig();
  
  if (savedConfig.saveApiConfig) {
    apiConfig.value = {
      apiUrl: savedConfig.apiUrl || props.defaultApiUrl || '',
      apiKey: savedConfig.apiKey || '',
      apiModel: savedConfig.apiModel || props.defaultApiModel || 'gpt-3.5-turbo',
      apiTimeout: savedConfig.apiTimeout || props.defaultApiTimeout || '60',
      saveApiConfig: true
    };
    
    // 通知父组件配置已加载
    emit('update:apiConfig', { ...apiConfig.value });
  }
});
</script>

<style scoped>
.api-config-section {
  margin-bottom: 1rem;
}

.toggle-button {
  margin-bottom: 0.5rem;
}

.api-config-card {
  margin-bottom: 1rem;
}

.formatted-url {
  color: var(--n-text-color-info);
  font-size: 0.85rem;
}

.button-group {
  display: flex;
  gap: 0.75rem;
}

.alert-actions {
  margin-top: 0.5rem;
  text-align: right;
}

.api-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.api-save-option {
  display: flex;
  align-items: center;
}

.save-label {
  margin-left: 0.5rem;
  font-size: 0.875rem;
}

.api-buttons {
  display: flex;
  gap: 0.75rem;
}
</style>
