<template>
  <div class="api-config-section mobile-api-config-section">
    <NButton
      class="toggle-button mobile-touch-target mobile-toggle-button"
      size="small"
      :quaternary="true"
      :type="expanded ? 'primary' : 'default'"
      @click="toggleConfig"
    >
      <template #icon>
        <NIcon :component="expanded ? ChevronUpIcon : ChevronDownIcon" />
      </template>
      <span class="toggle-text mobile-toggle-text">API配置 {{ expanded ? '收起' : '展开' }}</span>
    </NButton>
    
    <NCollapseTransition :show="expanded">
      <NCard
        class="api-config-card mobile-card mobile-shadow mobile-api-config-card"
        :bordered="false"
      >
        <NAlert
          v-if="isApiInfoVisible"
          title="OpenAI API配置"
          type="info"
          class="api-info-alert mobile-api-info-alert mobile-api-info-alert-small"
        >
          <template #icon>
            <NIcon :component="InformationCircleIcon" />
          </template>
          <p>您可以配置自己的API，也可以使用系统默认配置。API密钥仅在您的浏览器中使用，不会发送到服务器存储。</p>
          <div class="alert-actions">
            <NButton
              text
              @click="isApiInfoVisible = false"
            >
              <template #icon>
                <NIcon :component="CloseIcon" />
              </template>
            </NButton>
          </div>
        </NAlert>

        <NGrid
          :cols="24"
          :x-gap="16"
          :y-gap="16"
          responsive="screen"
          class="mobile-grid mobile-grid-small"
        >
          <NGridItem
            :span="24"
            :md-span="14"
            :lg-span="14"
            class="mobile-grid-item mobile-grid-item-small"
          >
            <NFormItem
              label="API URL"
              path="apiUrl"
              class="mobile-form-item"
            >
              <NInput 
                v-model:value="apiConfig.apiUrl" 
                placeholder="https://api.openai.com/v1/chat/completions"
                round
                @update:value="handleConfigChange"
              >
                <template #prefix>
                  <NIcon :component="GlobeIcon" />
                </template>
              </NInput>
              <template #feedback>
                <div class="url-feedback mobile-url-feedback">
                  <span class="formatted-url">实际请求地址: {{ formattedUrl }}</span>
                  <div class="url-tips">
                    <div>提示: URL以/结尾将忽略v1路径</div>
                    <div>URL以#结尾将使用原始地址</div>
                  </div>
                </div>
              </template>
            </NFormItem>
          </NGridItem>

          <NGridItem
            :span="24"
            :md-span="10"
            :lg-span="10"
            class="mobile-grid-item mobile-grid-item-small"
          >
            <NFormItem
              label="API Key"
              path="apiKey"
              class="mobile-form-item"
            >
              <NInput 
                v-model:value="apiConfig.apiKey" 
                type="password" 
                placeholder="sk-..."
                show-password-on="click"
                round
                @update:value="handleConfigChange"
              >
                <template #prefix>
                  <NIcon :component="KeyIcon" />
                </template>
              </NInput>
            </NFormItem>
          </NGridItem>

          <NGridItem
            :span="12"
            :md-span="12"
            :lg-span="12"
            class="mobile-grid-item mobile-grid-item-small"
          >
            <NFormItem
              label="模型"
              path="apiModel"
              class="mobile-form-item"
            >
              <NInput
                v-model:value="apiConfig.apiModel"
                placeholder="输入或选择模型名称"
                round
                @update:value="handleConfigChange"
              >
                <template #prefix>
                  <NIcon :component="CodeIcon" />
                </template>
                <template #suffix>
                  <NDropdown
                    trigger="click"
                    :options="modelOptions"
                    placement="bottom-end"
                    @select="selectModel"
                  >
                    <NButton
                      quaternary
                      circle
                      size="small"
                      class="model-dropdown-btn"
                    >
                      <template #icon>
                        <NIcon :component="ChevronDownIcon" />
                      </template>
                    </NButton>
                  </NDropdown>
                </template>
              </NInput>
              <template #feedback>
                <div class="model-suggestions">
                  <div class="model-tip">
                    您可以直接输入模型名称，或点击右侧按钮从下拉菜单选择
                  </div>
                  <span>常用模型:</span>
                  <div class="model-chips mobile-model-chips">
                    <NTag 
                      v-for="model in commonModels" 
                      :key="model.key"
                      size="small"
                      round
                      clickable
                      class="mobile-model-tag"
                      @click="selectModel(model.key)"
                    >
                      {{ model.label }}
                    </NTag>
                  </div>
                </div>
              </template>
            </NFormItem>
          </NGridItem>

          <NGridItem
            :span="12"
            :md-span="12"
            :lg-span="12"
            class="mobile-grid-item mobile-grid-item-small"
          >
            <NFormItem
              label="超时时间(秒)"
              path="apiTimeout"
              class="mobile-form-item"
            >
              <NInputNumber 
                v-model:value="apiTimeout" 
                placeholder="60"
                :min="1"
                :max="300"
                :show-button="false"
                class="timeout-input"
                @update:value="handleTimeoutChange"
              >
                <template #suffix>
                  <div class="timeout-controls">
                    <NButton
                      size="tiny"
                      quaternary
                      @click="decreaseTimeout"
                    >
                      <template #icon>
                        <NIcon :component="RemoveIcon" />
                      </template>
                    </NButton>
                    <NButton
                      size="tiny"
                      quaternary
                      @click="increaseTimeout"
                    >
                      <template #icon>
                        <NIcon :component="AddIcon" />
                      </template>
                    </NButton>
                  </div>
                </template>
              </NInputNumber>
            </NFormItem>
          </NGridItem>
        </NGrid>

        <div class="api-actions mobile-api-actions">
          <div class="api-save-option mobile-api-save-option">
            <NButton 
              tertiary
              size="small"
              round
              class="mobile-api-save-option-button"
              @click="saveConfig"
            >
              <template #icon>
                <NIcon :component="SaveIcon" />
              </template>
              保存配置到本地
            </NButton>
          </div>
          
          <div class="api-buttons mobile-api-buttons mobile-api-buttons-small">
            <NButton 
              type="primary" 
              :loading="testingConnection" 
              :disabled="!isConfigValid"
              round
              class="mobile-api-button"
              @click="testConnection"
            >
              <template #icon>
                <NIcon :component="CheckmarkIcon" />
              </template>
              测试连接
            </NButton>

            <NButton
              round
              class="mobile-api-button"
              @click="resetConfig"
            >
              <template #icon>
                <NIcon :component="RefreshIcon" />
              </template>
              重置
            </NButton>
          </div>
        </div>
        
        <NDivider
          v-if="connectionStatus"
          style="margin: 16px 0 12px"
        />
        
        <div
          v-if="connectionStatus"
          class="connection-status mobile-connection-status"
          :class="connectionStatus.type"
        >
          <NIcon
            :component="connectionStatus.icon"
            class="status-icon"
          />
          <span class="status-message">{{ connectionStatus.message }}</span>
        </div>
      </NCard>
    </NCollapseTransition>
  </div>
</template>

<script lang="ts">
import { apiService } from "@/services/api";
import type { ApiConfig } from "@/types";
import { loadApiConfig, saveApiConfigToLocalStorage } from "@/utils";
import {
  AddOutline as AddIcon,
  CheckmarkCircleOutline as CheckmarkIcon,
  ChevronDown as ChevronDownIcon,
  ChevronUp as ChevronUpIcon,
  Close as CloseIcon,
  CodeSlashOutline as CodeIcon,
  CloseCircle as ErrorIcon,
  Globe as GlobeIcon,
  InformationCircleOutline as InformationCircleIcon,
  Key as KeyIcon,
  RefreshOutline as RefreshIcon,
  RemoveOutline as RemoveIcon,
  SaveOutline as SaveIcon,
  CheckmarkCircle as SuccessIcon,
} from "@vicons/ionicons5";
import {
  NAlert,
  NButton,
  NCard,
  NCollapseTransition,
  NDivider,
  NDropdown,
  NFormItem,
  NGrid,
  NGridItem,
  NIcon,
  NInput,
  NInputNumber,
  NTag,
  useMessage,
} from "naive-ui";
import { computed, defineComponent, markRaw, onMounted, ref } from "vue";

export default defineComponent({
  name: "ApiConfigPanel",
  components: {
    NButton,
    NIcon,
    NCard,
    NCollapseTransition,
    NGrid,
    NGridItem,
    NFormItem,
    NInput,
    NInputNumber,
    NAlert,
    NDivider,
    NDropdown,
    NTag,
  },
  props: {
    defaultApiUrl: {
      type: String,
      default: "",
    },
    defaultApiModel: {
      type: String,
      default: "",
    },
    defaultApiTimeout: {
      type: String,
      default: "60",
    },
  },
  emits: ["update:apiConfig"],
  setup(props, { emit }) {
    const message = useMessage();
    const expanded = ref(false);
    const testingConnection = ref(false);
    const isApiInfoVisible = ref(true);

    // 连接状态
    const connectionStatus = ref<{
      type: "success" | "error";
      message: string;
      icon: any;
    } | null>(null);

    // 模型选项
    const modelOptions = [
      { label: "GPT-3.5", key: "gpt-3.5-turbo" },
      { label: "GPT-4o", key: "gpt-4o" },
      { label: "DeepSeek V3", key: "deepseek-chat" },
      { label: "DeepSeek R1", key: "deepseek-reasoner" },
      { label: "Claude 3.5 Sonnet", key: "claude-3-5-sonnet" },
      {
        label: "Claude 3.5 Sonnet 20241022",
        key: "claude-3-5-sonnet-20241022",
      },
      { label: "Gemini 1.5 Pro", key: "gemini-1.5-pro" },
      { label: "Gemini 1.5 Flash", key: "gemini-1.5-flash" },
      { label: "Gemini 2.0 Pro", key: "gemini-2.0-pro" },
      { label: "Gemini 2.0 Flash", key: "gemini-2.0-flash" },
    ];

    // 常用模型（用于快速选择）
    const commonModels = [
      { label: "GPT-3.5", key: "gpt-3.5-turbo" },
      { label: "GPT-4o", key: "gpt-4o" },
      { label: "Claude 3.5", key: "claude-3-5-sonnet" },
      { label: "Gemini 2.0", key: "gemini-2.0-flash" },
      { label: "DeepSeek V3", key: "deepseek-chat" },
    ];

    // API配置
    const apiConfig = ref<ApiConfig>({
      apiUrl: props.defaultApiUrl || "",
      apiKey: "",
      apiModel: props.defaultApiModel || "",
      apiTimeout: props.defaultApiTimeout || "60",
      saveApiConfig: true, // 默认启用保存配置
    });

    const apiTimeout = computed({
      get: () => Number.parseInt(apiConfig.value.apiTimeout) || 60,
      set: (val: number) => {
        apiConfig.value.apiTimeout = val.toString();
      },
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
      console.log("API配置变更:", apiConfig.value);

      // 不再在每次配置变更时自动保存
      // 仅向父组件发送更新事件
      emit("update:apiConfig", { ...apiConfig.value });
    }

    function handleTimeoutChange(value: number | null) {
      if (value !== null) {
        apiConfig.value.apiTimeout = value.toString();

        // 仅通知父组件更新，不自动保存
        emit("update:apiConfig", { ...apiConfig.value });
      }
    }

    function increaseTimeout() {
      if (apiTimeout.value < 300) {
        apiTimeout.value += 10;

        // 通知父组件
        emit("update:apiConfig", { ...apiConfig.value });
      }
    }

    function decreaseTimeout() {
      if (apiTimeout.value > 10) {
        apiTimeout.value -= 10;

        // 通知父组件
        emit("update:apiConfig", { ...apiConfig.value });
      }
    }

    function formatApiUrl(url: string): string {
      if (!url) {
        return "";
      }

      try {
        // 使用与后端一致的URL格式化逻辑
        if (url.endsWith("/")) {
          return `${url}chat/completions`;
        }
        if (url.endsWith("#")) {
          return url.replace("#", "");
        }

        return `${url}/v1/chat/completions`;
      } catch {
        // 如果URL格式错误，则返回原始字符串
        return url;
      }
    }

    async function testConnection() {
      if (!isConfigValid.value) {
        message.error("请填写完整的API配置信息");
        return;
      }

      testingConnection.value = true;
      connectionStatus.value = null;

      try {
        const response = await apiService.testApiConnection({
          api_url: apiConfig.value.apiUrl,
          api_key: apiConfig.value.apiKey,
          api_model: apiConfig.value.apiModel || undefined,
          api_timeout: Number.parseInt(apiConfig.value.apiTimeout) || 60,
        });

        if (response.success) {
          message.success("API连接测试成功");
          connectionStatus.value = {
            type: "success",
            message: "连接成功！API配置有效。",
            icon: markRaw(SuccessIcon),
          };
        } else {
          message.error(`API连接测试失败: ${response.message}`);
          connectionStatus.value = {
            type: "error",
            message: `连接失败: ${response.message}`,
            icon: markRaw(ErrorIcon),
          };
        }
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : "未知错误";
        message.error(`测试连接出错: ${errorMessage}`);
        connectionStatus.value = {
          type: "error",
          message: `连接错误: ${errorMessage}`,
          icon: markRaw(ErrorIcon),
        };
      } finally {
        testingConnection.value = false;
      }
    }

    function resetConfig() {
      apiConfig.value = {
        apiUrl: props.defaultApiUrl || "",
        apiKey: "",
        apiModel: props.defaultApiModel || "",
        apiTimeout: props.defaultApiTimeout || "60",
        saveApiConfig: true,
      };

      // 清除本地存储
      if (window.localStorage) {
        localStorage.removeItem("apiConfig");
        message.success("已重置API配置并清除本地存储");
      } else {
        message.success("已重置API配置");
      }

      connectionStatus.value = null;
      emit("update:apiConfig", { ...apiConfig.value });
    }

    // 选择模型
    function selectModel(key: string) {
      console.log("选择模型:", key);
      apiConfig.value.apiModel = key;

      // 通知父组件
      emit("update:apiConfig", { ...apiConfig.value });
    }

    // 显式保存配置的函数
    function saveConfig() {
      saveApiConfigToLocalStorage({
        apiUrl: apiConfig.value.apiUrl,
        apiKey: apiConfig.value.apiKey,
        apiModel: apiConfig.value.apiModel,
        apiTimeout: apiConfig.value.apiTimeout,
        saveApiConfig: true,
      });
      message.success("已将配置保存到本地");
    }

    onMounted(() => {
      // 加载保存的配置
      const savedConfig = loadApiConfig();

      if (savedConfig.saveApiConfig) {
        apiConfig.value = {
          apiUrl: savedConfig.apiUrl || props.defaultApiUrl || "",
          apiKey: savedConfig.apiKey || "",
          apiModel: savedConfig.apiModel || props.defaultApiModel || "",
          apiTimeout: savedConfig.apiTimeout || props.defaultApiTimeout || "60",
          saveApiConfig: true,
        };

        // 通知父组件配置已加载
        emit("update:apiConfig", { ...apiConfig.value });
      }
    });

    return {
      ChevronDownIcon,
      ChevronUpIcon,
      InformationCircleIcon,
      CloseIcon,
      GlobeIcon,
      KeyIcon,
      CheckmarkIcon,
      RefreshIcon,
      AddIcon,
      RemoveIcon,
      CodeIcon,
      SaveIcon,
      expanded,
      testingConnection,
      isApiInfoVisible,
      connectionStatus,
      modelOptions,
      commonModels,
      apiConfig,
      apiTimeout,
      isConfigValid,
      formattedUrl,
      toggleConfig,
      handleConfigChange,
      handleTimeoutChange,
      increaseTimeout,
      decreaseTimeout,
      testConnection,
      resetConfig,
      selectModel,
      saveConfig,
    };
  },
});
</script>

<style scoped>
.api-config-section {
  margin-bottom: 2rem;
  position: relative;
  padding-bottom: 10px;
}

.toggle-button {
  margin-bottom: 0.75rem;
  font-weight: 500;
  transition: all 0.3s ease;
  border-radius: 16px;
  padding: 4px 12px;
}

.toggle-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.toggle-text {
  margin-left: 4px;
}

.api-config-card {
  margin-bottom: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  background: linear-gradient(to bottom, rgba(240, 240, 245, 0.5), rgba(250, 250, 252, 0.8));
  padding: 16px;
  transition: all 0.3s ease;
  overflow: visible;
  min-height: 100px;
}

.api-info-alert {
  margin-bottom: 16px;
  border-radius: 8px;
}

.url-feedback {
  padding: 6px 0;
}

.formatted-url {
  color: var(--n-text-color-info);
  font-size: 0.85rem;
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.url-tips {
  color: var(--n-text-color-info);
  font-size: 0.75rem;
  opacity: 0.8;
  line-height: 1.4;
}

.alert-actions {
  margin-top: 0.5rem;
  text-align: right;
}

.api-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  flex-wrap: wrap;
  gap: 12px;
}

.api-save-option {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 16px;
}

.api-save-option button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-weight: 500;
  background-color: rgba(0, 0, 0, 0.02);
  transition: all 0.2s ease;
}

.api-save-option button:hover {
  background-color: rgba(32, 128, 240, 0.08);
  transform: translateY(-1px);
}

.api-save-option button .n-icon {
  font-size: 16px;
}

.api-buttons {
  display: flex;
  gap: 0.75rem;
}

.timeout-input {
  width: 100%;
}

.timeout-controls {
  display: flex;
  align-items: center;
  margin-left: 8px;
}

.connection-status {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  border-radius: 8px;
  margin-top: 8px;
  font-weight: 500;
  animation: fadeIn 0.3s ease;
}

.connection-status.success {
  background-color: rgba(24, 160, 88, 0.1);
  color: var(--n-success-color);
}

.connection-status.error {
  background-color: rgba(208, 48, 80, 0.1);
  color: var(--n-error-color);
}

.status-icon {
  margin-right: 8px;
  font-size: 1.25rem;
}

.status-message {
  font-size: 0.9rem;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

.model-suggestions {
  margin-top: 6px;
  font-size: 0.75rem;
  color: var(--n-text-color-3);
}

.model-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
}

.model-chips :deep(.n-tag) {
  cursor: pointer;
  transition: all 0.2s ease;
}

.model-chips :deep(.n-tag:hover) {
  background-color: rgba(32, 128, 240, 0.1);
  transform: translateY(-1px);
}

.model-tip {
  margin-bottom: 6px;
  font-size: 0.75rem;
  color: var(--n-text-color-3);
  font-style: italic;
}

.model-dropdown-btn {
  background-color: rgba(32, 128, 240, 0.1);
  transition: all 0.2s ease;
}

.model-dropdown-btn:hover {
  background-color: rgba(32, 128, 240, 0.2);
  transform: translateY(-1px);
}
</style>
