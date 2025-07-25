<template>
  <div class="app-container mobile-bottom-extend">
    <!-- 滑动菜单 -->
    <div
      class="slide-menu-container"
      :class="{ 'menu-open': isMenuOpen }"
    >
      <div
        class="menu-overlay"
        @click="toggleMenu"
      />
      <div class="slide-menu">        
        <div class="menu-header">
          <NText strong>
            菜单
          </NText>
        </div>
        <NButton
          class="menu-item"
          style="background-color: #f0f0f0; margin: 4px 0;"
          @click="navigateToHome"
        >
          <template #icon>
            <NIcon><HomeIcon /></NIcon>
          </template>
          首页
        </NButton>
        <NButton
          class="menu-item"
          style="background-color: #e8f4fd; margin: 4px 0;"
          @click="navigateToWatchlist"
        >
          <template #icon>
            <NIcon><HeartIcon /></NIcon>
          </template>
          自选股管理
        </NButton>
        <NDivider class="menu-divider" />
        <NButton
          class="menu-item"
          style="background-color: #ffe6e6; margin: 4px 0;"
          @click="handleLogout"
        >
          <template #icon>
            <NIcon><LogoutIcon /></NIcon>
          </template>
          登出
        </NButton>
      </div>
    </div>
    <!-- 菜单按钮 -->
    <NButton
      class="menu-button"
      circle
      style="background: #18a058 !important;"
      @click="toggleMenu"
    >
      <template #icon>
        <NIcon><MenuIcon /></NIcon>
      </template>
    </NButton>

    
    <!-- 公告横幅 -->
    <AnnouncementBanner 
      v-if="announcement && showAnnouncementBanner" 
      :content="announcement" 
      :auto-close-time="5"
      @close="handleAnnouncementClose"
    />
    
    <NLayout class="main-layout">
      <NLayoutContent class="main-content mobile-content-container">
        <!-- 市场时间显示 -->
        <MarketTimeDisplay :is-mobile="isMobile" />
        
        <!-- API配置面板 -->
        <ApiConfigPanel
          :default-api-url="defaultApiUrl"
          :default-api-model="defaultApiModel"
          :default-api-timeout="defaultApiTimeout"
          @update:api-config="updateApiConfig"
        />
        
        <!-- 主要内容 -->
        <NCard class="analysis-container mobile-card mobile-card-spacing mobile-shadow">
          <NGrid
            cols="1 xl:24"
            :x-gap="16"
            :y-gap="16"
            responsive="screen"
          >
            <!-- 左侧配置区域 -->
            <NGridItem span="1 xl:8">
              <div class="config-section">
                <NFormItem label="选择市场类型">
                  <NSelect
                    v-model="marketType"
                    :options="marketOptions"
                    @update:value="handleMarketTypeChange"
                  />
                </NFormItem>
                
                <NFormItem
                  v-if="showSearch"
                  :label="marketType === 'US' ? '股票搜索' : '基金搜索'"
                >
                  <StockSearch
                    :market-type="marketType"
                    @select="addSelectedStock"
                  />
                </NFormItem>
                
                <NFormItem label="输入代码">
                  <NInput
                    v-model:value="stockCodes"
                    type="textarea"
                    placeholder="输入股票、基金代码，多个代码用逗号、空格或换行分隔"
                    :autosize="{ minRows: 3, maxRows: 6 }"
                  />
                </NFormItem>
                
                <div class="action-buttons">
                  <NButton
                    type="primary"
                    :loading="isAnalyzing"
                    :disabled="!stockCodes.trim()"
                    @click="analyzeStocks"
                  >
                    {{ isAnalyzing ? '分析中...' : '开始分析' }}
                  </NButton>
                  
                  <NButton
                    :disabled="analyzedStocks.length === 0"
                    @click="copyAnalysisResults"
                  >
                    复制结果
                  </NButton>
                </div>
              </div>
            </NGridItem>
            
            <!-- 右侧结果区域 -->
            <NGridItem span="1 xl:16">
              <div class="results-section">
                <div class="results-header">
                  <NSpace
                    align="center"
                    justify="space-between"
                  >
                    <NText>分析结果 ({{ analyzedStocks.length }})</NText>
                    <NSpace>
                      <NSelect 
                        v-model="displayMode" 
                        size="small" 
                        style="width: 120px"
                        :options="[
                          { label: '卡片视图', value: 'card' },
                          { label: '表格视图', value: 'table' }
                        ]"
                      />
                      <NButton 
                        size="small" 
                        :disabled="analyzedStocks.length === 0"
                        @click="copyAnalysisResults"
                      >
                        复制结果
                      </NButton>
                      <NDropdown 
                        trigger="click" 
                        :disabled="analyzedStocks.length === 0"
                        :options="exportOptions"
                        @select="handleExportSelect"
                      >
                        <NButton
                          size="small"
                          :disabled="analyzedStocks.length === 0"
                        >
                          导出
                          <template #icon>
                            <NIcon>
                              <DownloadIcon />
                            </NIcon>
                          </template>
                        </NButton>
                      </NDropdown>
                    </NSpace>
                  </NSpace>
                </div>
                
                <template v-if="analyzedStocks.length === 0 && !isAnalyzing">
                  <NEmpty
                    description="尚未分析股票"
                    size="large"
                  >
                    <template #icon>
                      <NIcon :component="DocumentTextIcon" />
                    </template>
                  </NEmpty>
                </template>
                
                <template v-else-if="displayMode === 'card'">
                  <NGrid
                    cols="1"
                    :x-gap="8"
                    :y-gap="8"
                    responsive="screen"
                  >
                    <NGridItem
                      v-for="stock in analyzedStocks"
                      :key="stock.code"
                    >
                      <StockCard :stock="stock" />
                    </NGridItem>
                  </NGrid>
                </template>
                
                <template v-else>
                  <div class="table-container">
                    <NDataTable
                      :columns="stockTableColumns"
                      :data="analyzedStocks"
                      :pagination="{ pageSize: 10 }"
                      :row-key="(row) => row.code"
                      :bordered="false"
                      :single-line="false"
                      striped
                      :scroll-x="1200"
                    />
                  </div>
                </template>
              </div>
            </NGridItem>
          </NGrid>
        </NCard>
      </NLayoutContent>
    </NLayout>
  </div>
</template>

<script setup lang="ts">
import {
  DocumentTextOutline as DocumentTextIcon,
  DownloadOutline as DownloadIcon,
  HeartOutline as HeartIcon,
  HomeOutline as HomeIcon,
  LogOutOutline as LogoutIcon,
  MenuOutline as MenuIcon,
} from "@vicons/ionicons5";
import { useClipboard } from "@vueuse/core";
import {
  type DataTableColumns,
  NButton,
  NCard,
  NDataTable,
  NDivider,
  NDropdown,
  NEmpty,
  NFormItem,
  NGrid,
  NGridItem,
  NIcon,
  NInput,
  NLayout,
  NLayoutContent,
  NSelect,
  NSpace,
  NText,
  useMessage,
} from "naive-ui";
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import AnnouncementBanner from "./AnnouncementBanner.vue";
import ApiConfigPanel from "./ApiConfigPanel.vue";
import MarketTimeDisplay from "./MarketTimeDisplay.vue";
import StockCard from "./StockCard.vue";
import StockSearch from "./StockSearch.vue";

import { apiService } from "@/services/api";
import type {
  ApiConfig,
  StockInfo,
  StreamAnalysisUpdate,
  StreamInitMessage,
} from "@/types";
import { loadApiConfig } from "@/utils";
import { MarketType, validateMultipleStockCodes } from "@/utils/stockValidator";

// 使用Naive UI的组件API
const message = useMessage();
const { copy } = useClipboard();
const router = useRouter();

// 菜单状态
const isMenuOpen = ref(false);

// 切换菜单
function toggleMenu() {
  console.log(
    "切换菜单状态，当前状态:",
    isMenuOpen.value,
    "新状态:",
    !isMenuOpen.value,
  );
  isMenuOpen.value = !isMenuOpen.value;
}

// 处理登出
function handleLogout() {
  localStorage.removeItem("token");
  window.location.reload();
}

// 导航到首页
function navigateToHome() {
  toggleMenu();
  // 当前就在首页，不需要跳转
}

// 导航到自选股管理
function navigateToWatchlist() {
  toggleMenu();
  router.push("/watchlist");
}

// 从环境变量获取的默认配置
const defaultApiUrl = ref("");
const defaultApiModel = ref("");
const defaultApiTimeout = ref("60");
const announcement = ref("");
const showAnnouncementBanner = ref(true);

// 股票分析配置
const marketType = ref("A");
const stockCodes = ref("");
const isAnalyzing = ref(false);
const analyzedStocks = ref<StockInfo[]>([]);
const displayMode = ref<"card" | "table">("card");

// API配置
const apiConfig = ref<ApiConfig>({
  apiUrl: "",
  apiKey: "",
  apiModel: "",
  apiTimeout: "60",
  saveApiConfig: false,
});

// 移动端检测
const isMobile = computed(() => {
  return window.innerWidth <= 768;
});

// 监听窗口大小变化
function handleResize() {
  // 窗口大小变化时，isMobile计算属性会自动更新
  // 这里可以添加其他需要在窗口大小变化时执行的逻辑
}

// 显示系统公告
const showAnnouncement = (content: string) => {
  if (!content) {
    return;
  }

  // 使用AnnouncementBanner组件显示公告
  announcement.value = content;
  showAnnouncementBanner.value = true;
};

// 市场选项
const marketOptions = [
  { label: "A股", value: "A" },
  { label: "港股", value: "HK" },
  { label: "美股", value: "US", showSearch: true },
  { label: "ETF", value: "ETF", showSearch: true },
  { label: "LOF", value: "LOF", showSearch: true },
];

// 表格列定义
const stockTableColumns = ref<DataTableColumns<StockInfo>>([
  {
    title: "代码",
    key: "code",
    width: 100,
    fixed: "left",
  },
  {
    title: "状态",
    key: "analysisStatus",
    width: 100,
    render(row: StockInfo) {
      const statusMap = {
        waiting: "等待分析",
        analyzing: "分析中",
        completed: "已完成",
        error: "出错",
      };
      return statusMap[row.analysisStatus] || row.analysisStatus;
    },
  },
  {
    title: "价格",
    key: "price",
    width: 100,
    render(row: StockInfo) {
      return row.price !== undefined ? row.price.toFixed(2) : "--";
    },
  },
  {
    title: "涨跌额",
    key: "price_change",
    width: 100,
    render(row: StockInfo) {
      if (row.price_change === undefined) {
        return "--";
      }
      const sign = row.price_change > 0 ? "+" : "";
      return `${sign}${row.price_change.toFixed(2)}`;
    },
  },
  {
    title: "涨跌幅",
    key: "changePercent",
    width: 100,
    render(row: StockInfo) {
      if (row.changePercent === undefined) {
        // 如果没有changePercent但有price_change和price，尝试计算
        if (row.price_change !== undefined && row.price !== undefined) {
          const basePrice = row.price - row.price_change;
          if (basePrice !== 0) {
            const calculatedPercent = (row.price_change / basePrice) * 100;
            const sign = calculatedPercent > 0 ? "+" : "";
            return `${sign}${calculatedPercent.toFixed(2)}%`;
          }
        }
        return "--";
      }
      const sign = row.changePercent > 0 ? "+" : "";
      return `${sign}${row.changePercent.toFixed(2)}%`;
    },
  },
  {
    title: "RSI",
    key: "rsi",
    width: 80,
    render(row: StockInfo) {
      return row.rsi !== undefined ? row.rsi.toFixed(2) : "--";
    },
  },
  {
    title: "均线趋势",
    key: "ma_trend",
    width: 100,
    render(row: StockInfo) {
      const trendMap: Record<string, string> = {
        UP: "上升",
        DOWN: "下降",
        NEUTRAL: "平稳",
      };
      return row.ma_trend ? trendMap[row.ma_trend] || row.ma_trend : "--";
    },
  },
  {
    title: "MACD信号",
    key: "macd_signal",
    width: 100,
    render(row: StockInfo) {
      const signalMap: Record<string, string> = {
        BUY: "买入",
        SELL: "卖出",
        HOLD: "持有",
        NEUTRAL: "中性",
      };
      return row.macd_signal
        ? signalMap[row.macd_signal] || row.macd_signal
        : "--";
    },
  },
  {
    title: "评分",
    key: "score",
    width: 80,
    render(row: StockInfo) {
      return row.score !== undefined ? row.score : "--";
    },
  },
  {
    title: "推荐",
    key: "recommendation",
    width: 100,
  },
  {
    title: "分析日期",
    key: "analysis_date",
    width: 120,
    render(row: StockInfo) {
      if (!row.analysis_date) {
        return "--";
      }
      try {
        const date = new Date(row.analysis_date);
        if (Number.isNaN(date.getTime())) {
          return row.analysis_date;
        }
        return date.toISOString().split("T")[0];
      } catch {
        return row.analysis_date;
      }
    },
  },
  {
    title: "分析结果",
    key: "analysis",
    ellipsis: {
      tooltip: true,
    },
    width: 300,
    className: "analysis-cell",
  },
]);

// 导出选项
const exportOptions = [
  {
    label: "导出为CSV",
    key: "csv",
  },
  {
    label: "导出为Excel",
    key: "excel",
  },
  {
    label: "导出为PDF",
    key: "pdf",
  },
];

const showSearch = computed(
  () =>
    marketOptions.find((option) => option.value === marketType.value)
      ?.showSearch,
);

// 更新API配置
function updateApiConfig(config: ApiConfig) {
  apiConfig.value = { ...config };
}

// 处理市场类型变更
function handleMarketTypeChange() {
  stockCodes.value = "";
  analyzedStocks.value = [];
}

// 添加选择的股票
function addSelectedStock(symbol: string) {
  // 确保symbol不包含序号或其他不需要的信息
  const cleanSymbol = symbol.trim().replace(/^\d+\.\s*/, "");

  if (stockCodes.value) {
    stockCodes.value += `, ${cleanSymbol}`;
  } else {
    stockCodes.value = cleanSymbol;
  }
}

// 处理流式响应的数据
function processStreamData(text: string) {
  try {
    // 尝试解析为JSON
    const data = JSON.parse(text);

    // 判断是初始消息还是更新消息
    if (data.stream_type === "single" || data.stream_type === "batch") {
      // 初始消息
      handleStreamInit(data as StreamInitMessage);
    } else if (data.stock_code) {
      // 更新消息
      handleStreamUpdate(data as StreamAnalysisUpdate);
    } else if (data.scan_completed) {
      // 批量扫描完成的总结消息
      let summaryMessage = "批量分析完成。";
      if (data.original_codes_count !== undefined) {
        summaryMessage += ` 原始请求 ${data.original_codes_count} 个代码。`;
      }
      if (
        data.duplicates_excluded_count !== undefined &&
        data.duplicates_excluded_count > 0
      ) {
        summaryMessage += ` 已排除 ${data.duplicates_excluded_count} 个重复代码。`;
      }
      if (data.unique_codes_processed_count !== undefined) {
        // Changed from total_scanned
        summaryMessage += ` 实际分析 ${data.unique_codes_processed_count} 个唯一代码。`;
      }
      if (data.total_analyzed_successfully !== undefined) {
        // Changed from total_matched
        summaryMessage += ` 成功分析 ${data.total_analyzed_successfully} 个。`;
      }
      message.success(summaryMessage.trim(), { duration: 5000 });
      // 扫描完成消息
      // message.success(`分析完成，共扫描 ${data.total_scanned} 只股票，符合条件 ${data.total.matched} 只`);

      // 将所有分析中的股票状态更新为已完成
      analyzedStocks.value = analyzedStocks.value.map((stock) => {
        if (stock.analysisStatus === "analyzing") {
          return {
            ...stock,
            analysisStatus: "completed" as const,
          };
        }
        return stock;
      });

      isAnalyzing.value = false;
    }
  } catch (e) {
    console.error("解析流数据出错:", e);
  }
}

// 处理流式初始化消息
function handleStreamInit(data: StreamInitMessage) {
  if (data.stream_type === "single" && data.stock_code) {
    // 单个股票分析
    analyzedStocks.value = [
      {
        code: data.stock_code,
        name: "",
        marketType: marketType.value,
        analysisStatus: "waiting",
      },
    ];
  } else if (data.stream_type === "batch" && data.stock_codes) {
    // 批量分析
    analyzedStocks.value = data.stock_codes.map((code) => ({
      code,
      name: "",
      marketType: marketType.value,
      analysisStatus: "waiting",
    }));
  }
}

// 处理流式更新消息
function handleStreamUpdate(data: StreamAnalysisUpdate) {
  const stockIndex = analyzedStocks.value.findIndex(
    (s: StockInfo) => s.code === data.stock_code,
  );

  if (stockIndex >= 0) {
    const stock = { ...analyzedStocks.value[stockIndex] };

    // 确保所有数值类型的字段都有默认值
    stock.price = data.price ?? stock.price ?? undefined;
    stock.price_change =
      data.price_change_value ??
      data.price_change ??
      stock.price_change ??
      undefined;
    stock.changePercent =
      data.change_percent ?? stock.changePercent ?? undefined;
    stock.marketValue = data.market_value ?? stock.marketValue ?? undefined;
    stock.score = data.score ?? stock.score ?? undefined;
    stock.rsi = data.rsi ?? stock.rsi ?? undefined;

    // 更新分析状态
    if (data.status) {
      stock.analysisStatus = data.status;
    }

    // 如果有分析结果，则更新
    if (data.analysis !== undefined) {
      stock.analysis = data.analysis;
    }

    // 处理AI分析片段
    if (data.ai_analysis_chunk !== undefined) {
      stock.analysis = (stock.analysis || "") + data.ai_analysis_chunk;
      stock.analysisStatus = "analyzing";
    }

    // 如果有错误，则更新
    if (data.error !== undefined) {
      stock.error = data.error;
      stock.analysisStatus = "error";
    }

    // 更新其他字段
    if (data.name !== undefined) {
      stock.name = data.name;
    }

    if (data.recommendation !== undefined) {
      stock.recommendation = data.recommendation;
    }

    if (data.ma_trend !== undefined) {
      stock.ma_trend = data.ma_trend;
    }

    if (data.macd_signal !== undefined) {
      stock.macd_signal = data.macd_signal;
    }

    if (data.volume_status !== undefined) {
      stock.volume_status = data.volume_status;
    }

    if (data.analysis_date !== undefined) {
      stock.analysis_date = data.analysis_date;
    }

    // 使用Vue的响应式API更新数组
    analyzedStocks.value[stockIndex] = stock;
  }
}

// 分析股票
async function analyzeStocks() {
  if (!stockCodes.value.trim()) {
    message.warning("请输入股票代码");
    return;
  }

  // 解析股票代码
  const codes = stockCodes.value
    .split(/[,\s\n]+/)
    .map((code: string) => code.trim())
    .filter((code: string) => code);

  if (codes.length === 0) {
    message.warning("未找到有效的股票代码");
    return;
  }

  // 去除重复的股票代码
  const uniqueCodes = Array.from(new Set(codes));

  // 检查是否有重复代码被移除
  if (uniqueCodes.length < codes.length) {
    message.info(
      `已自动去除${codes.length - uniqueCodes.length}个重复的股票代码`,
    );
  }

  // 在前端验证股票代码
  const marketTypeEnum = marketType.value as keyof typeof MarketType;
  const invalidCodes = validateMultipleStockCodes(
    uniqueCodes,
    MarketType[marketTypeEnum],
  );

  // 如果有无效代码，显示错误信息并返回
  if (invalidCodes.length > 0) {
    const errorMessages = invalidCodes
      .map((item) => item.errorMessage)
      .join("\n");
    message.error(`股票代码验证失败:${errorMessages}`);
    return;
  }

  isAnalyzing.value = true;
  analyzedStocks.value = [];

  try {
    // 构建请求参数
    const requestData = {
      stock_codes: uniqueCodes,
      market_type: marketType.value,
    } as any;

    // 添加自定义API配置
    if (apiConfig.value.apiUrl) {
      requestData.api_url = apiConfig.value.apiUrl;
    }

    if (apiConfig.value.apiKey) {
      requestData.api_key = apiConfig.value.apiKey;
    }

    if (apiConfig.value.apiModel) {
      requestData.api_model = apiConfig.value.apiModel;
    }

    if (apiConfig.value.apiTimeout) {
      requestData.api_timeout = apiConfig.value.apiTimeout;
    }

    // 获取身份验证令牌
    const token = localStorage.getItem("token");

    // 构建请求头
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    // 如果有令牌，添加到请求头
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    // 发送分析请求
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers,
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      if (response.status === 401) {
        message.error("未授权访问，请登录后再试");
        // 可以在这里触发登录流程
        return;
      }
      if (response.status === 404) {
        throw new Error("服务器接口未找到，请检查服务是否正常运行");
      }
      throw new Error(`服务器响应错误: ${response.status}`);
    }

    // 处理流式响应
    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("无法读取响应流");
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        break;
      }

      // 解码并处理数据
      const text = decoder.decode(value, { stream: true });
      buffer += text;

      // 按行处理数据
      const lines = buffer.split("\n");
      buffer = lines.pop() || ""; // 最后一行可能不完整，保留到下一次

      for (const line of lines) {
        if (line.trim()) {
          try {
            processStreamData(line);
          } catch (e: unknown) {
            console.error("处理数据流时出错:", e);
            message.error(
              `处理数据时出错: ${e instanceof Error ? e.message : "未知错误"}`,
            );
          }
        }
      }
    }

    // 处理最后可能剩余的数据
    if (buffer.trim()) {
      try {
        processStreamData(buffer);
      } catch (e: unknown) {
        console.error("处理最后的数据块时出错:", e);
        message.error(
          `处理数据时出错: ${e instanceof Error ? e.message : "未知错误"}`,
        );
      }
    }

    message.success("分析完成", { duration: 3000 });
  } catch (error: any) {
    let errorMessage = "分析出错: ";
    if (error.message.includes("404")) {
      errorMessage += "服务器接口未找到，请确保后端服务正常运行";
    } else {
      errorMessage += error.message || "未知错误";
    }
    message.error(errorMessage);
    console.error("分析股票时出错:", error);

    // 清空分析状态
    analyzedStocks.value = [];
  } finally {
    isAnalyzing.value = false;
  }
}

// 复制分析结果
async function copyAnalysisResults() {
  if (analyzedStocks.value.length === 0) {
    message.warning("没有可复制的分析结果");
    return;
  }

  try {
    // 格式化分析结果
    const formattedResults = analyzedStocks.value
      .filter((stock: StockInfo) => stock.analysisStatus === "completed")
      .map((stock: StockInfo) => {
        let result = `【${stock.code} ${stock.name || ""}】\n`;

        // 添加分析日期
        if (stock.analysis_date) {
          try {
            const date = new Date(stock.analysis_date);
            if (!Number.isNaN(date.getTime())) {
              result += `分析日期: ${date.toISOString().split("T")[0]}\n`;
            } else {
              result += `分析日期: ${stock.analysis_date}\n`;
            }
          } catch {
            result += `分析日期: ${stock.analysis_date}\n`;
          }
        }

        // 添加评分和推荐信息
        if (stock.score !== undefined) {
          result += `评分: ${stock.score}\n`;
        }

        if (stock.recommendation) {
          result += `推荐: ${stock.recommendation}\n`;
        }

        // 添加技术指标信息
        if (stock.rsi !== undefined) {
          result += `RSI: ${stock.rsi.toFixed(2)}\n`;
        }

        if (stock.price_change !== undefined) {
          const sign = stock.price_change > 0 ? "+" : "";
          result += `涨跌额: ${sign}${stock.price_change.toFixed(2)}\n`;
        }

        if (stock.ma_trend) {
          const trendMap: Record<string, string> = {
            UP: "上升",
            DOWN: "下降",
            NEUTRAL: "平稳",
          };
          const trend = trendMap[stock.ma_trend] || stock.ma_trend;
          result += `均线趋势: ${trend}\n`;
        }

        if (stock.macd_signal) {
          const signalMap: Record<string, string> = {
            BUY: "买入",
            SELL: "卖出",
            HOLD: "持有",
            NEUTRAL: "中性",
          };
          const signal = signalMap[stock.macd_signal] || stock.macd_signal;
          result += `MACD信号: ${signal}\n`;
        }

        if (stock.volume_status) {
          const statusMap: Record<string, string> = {
            HIGH: "放量",
            LOW: "缩量",
            NORMAL: "正常",
          };
          const status = statusMap[stock.volume_status] || stock.volume_status;
          result += `成交量: ${status}\n`;
        }

        // 添加分析结果
        result += `\n${stock.analysis || "无分析结果"}\n`;

        return result;
      })
      .join("\n");

    if (!formattedResults) {
      message.warning("没有已完成的分析结果可复制");
      return;
    }

    // 复制到剪贴板
    await copy(formattedResults);
    message.success("已复制分析结果到剪贴板");
  } catch (error) {
    message.error("复制失败，请手动复制");
    console.error("复制分析结果时出错:", error);
  }
}

// 从本地存储恢复API配置
function restoreLocalApiConfig() {
  const savedConfig = loadApiConfig();
  //  if (savedConfig && savedConfig.saveApiConfig) {
  if (savedConfig?.saveApiConfig) {
    apiConfig.value = {
      apiUrl: savedConfig.apiUrl || "",
      apiKey: savedConfig.apiKey || "",
      apiModel: savedConfig.apiModel || defaultApiModel.value,
      apiTimeout: savedConfig.apiTimeout || defaultApiTimeout.value,
      saveApiConfig: savedConfig.saveApiConfig,
    };

    // 通知父组件配置已更新
    updateApiConfig(apiConfig.value);
  }
}

// 处理导出选择
function handleExportSelect(key: string) {
  switch (key) {
  case "csv":
    exportToCSV();
    break;
  case "excel":
    message.info("Excel导出功能即将推出");
    break;
  case "pdf":
    message.info("PDF导出功能即将推出");
    break;
  }
}

// 导出为CSV
function exportToCSV() {
  if (analyzedStocks.value.length === 0) {
    message.warning("没有可导出的分析结果");
    return;
  }

  try {
    // 创建CSV内容
    const headers = [
      "代码",
      "名称",
      "价格",
      "涨跌幅",
      "RSI",
      "均线趋势",
      "MACD信号",
      "成交量状态",
      "评分",
      "推荐",
      "分析日期",
    ];
    let csvContent = `${headers.join(",")}\n`;

    // 添加数据行

    analyzedStocks.value.forEach((stock) => {
      const row = [
        `"${stock.code}"`,
        `"${stock.name || ""}"`,
        stock.price !== undefined ? stock.price.toFixed(2) : "",
        stock.changePercent !== undefined
          ? `${stock.changePercent > 0 ? "+" : ""}${stock.changePercent.toFixed(2)}%`
          : "",
        stock.rsi !== undefined ? stock.rsi.toFixed(2) : "",
        stock.ma_trend ? getChineseTrend(stock.ma_trend) : "",
        stock.macd_signal ? getChineseSignal(stock.macd_signal) : "",
        stock.volume_status ? getChineseVolumeStatus(stock.volume_status) : "",
        stock.score !== undefined ? stock.score : "",
        `"${stock.recommendation || ""}"`,
        stock.analysis_date || "",
      ];

      csvContent += `${row.join(",")}\n`;
    });

    // 创建Blob对象
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    // 创建下载链接
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute(
      "download",
      `股票分析结果_${new Date().toISOString().split("T")[0]}.csv`,
    );
    link.style.visibility = "hidden";

    // 添加到文档并触发点击
    document.body.appendChild(link);
    link.click();

    // 清理
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    message.success("已导出CSV文件");
  } catch (error) {
    message.error("导出失败");
    console.error("导出CSV时出错:", error);
  }
}

// 辅助函数：获取中文趋势描述
function getChineseTrend(trend: string): string {
  const trendMap: Record<string, string> = {
    UP: "上升",
    DOWN: "下降",
    NEUTRAL: "平稳",
  };
  return trendMap[trend] || trend;
}

// 辅助函数：获取中文信号描述
function getChineseSignal(signal: string): string {
  const signalMap: Record<string, string> = {
    BUY: "买入",
    SELL: "卖出",
    HOLD: "持有",
    NEUTRAL: "中性",
  };
  return signalMap[signal] || signal;
}

// 辅助函数：获取中文成交量状态描述
function getChineseVolumeStatus(status: string): string {
  const statusMap: Record<string, string> = {
    HIGH: "放量",
    LOW: "缩量",
    NORMAL: "正常",
  };
  return statusMap[status] || status;
}

// 页面加载时获取默认配置和公告
onMounted(async () => {
  try {
    // 添加窗口大小变化监听
    window.addEventListener("resize", handleResize);

    // 处理路由参数
    handleRouteParams();

    // 从API获取配置信息
    const config = await apiService.getConfig();

    if (config.default_api_url) {
      defaultApiUrl.value = config.default_api_url;
    }

    if (config.default_api_model) {
      defaultApiModel.value = config.default_api_model;
    }

    if (config.default_api_timeout) {
      defaultApiTimeout.value = config.default_api_timeout;
    }

    if (config.announcement) {
      announcement.value = config.announcement;
      // 使用通知显示公告
      showAnnouncement(config.announcement);
    }
    // 初始化后恢复本地保存的配置
    restoreLocalApiConfig();
  } catch (error) {
    console.error("获取默认配置时出错:", error);
  }
});

// 组件销毁前移除事件监听
onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
});

// 处理公告关闭事件
function handleAnnouncementClose() {
  showAnnouncementBanner.value = false;
}

// 处理路由参数
function handleRouteParams() {
  const route = router.currentRoute.value;
  const { codes, marketType: routeMarketType, source } = route.query;

  if (codes && routeMarketType && source === "watchlist") {
    // 从自选股跳转过来的分析请求
    const codeList = (codes as string).split(",");
    stockCodes.value = codeList.join(", ");
    marketType.value = routeMarketType as string;

    // 显示提示信息
    message.info(
      `已从自选股导入 ${codeList.length} 只股票，点击"开始分析"进行分析`,
    );

    // 清除URL参数，避免重复处理
    router.replace({ path: "/", query: {} });
  }
}
</script>

<style scoped>
/* 滑动菜单样式 */
.slide-menu-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 999;
  pointer-events: none;
  transition: all 0.3s ease;
}

.menu-open {
  pointer-events: auto;
}

.menu-open .menu-overlay {
  pointer-events: auto;
  background: rgba(0, 0, 0, 0.3);
}

.menu-overlay {
  position: absolute;
  width: 100%;
  height: 100%;
  background: transparent;
  transition: all 0.3s ease;
}

.slide-menu {
  position: absolute;
  top: 0;
  left: -300px;
  width: 280px;
  height: 100%;
  background: white;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  pointer-events: auto;
  display: flex;
  flex-direction: column;
  border: 2px solid #ff0000; /* 调试：红色边框 */
}

.menu-open .slide-menu {
  left: 0;
  border: 2px solid #00ff00; /* 调试：打开时绿色边框 */
}

.menu-button {
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 1000;
  background: #18a058 !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  border: 2px solid #0000ff; /* 调试：蓝色边框 */
}

.menu-header {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.menu-item {
  width: 100%;
  text-align: left;
  padding: 12px 20px;
  border-radius: 0;
  border: 2px solid #333 !important; /* 调试：黑色边框 */
  justify-content: flex-start;
  font-weight: bold !important;
  font-size: 16px !important;
}

.menu-item:hover {
  background: #f5f5f5;
  border: 2px solid #ff6600 !important; /* 调试：悬停时橙色边框 */
}

.menu-divider {
  margin: 8px 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .slide-menu {
    width: 250px;
  }
  
  .menu-button {
    top: 15px;
    left: 15px;
  }
}

.app-container {
  min-height: 100vh;
  width: 100%;
  max-width: 100vw;
  overflow-x: hidden;
  padding-bottom: 20px; /* 增加底部内边距 */
  box-sizing: border-box;
}

.main-layout {
  background-color: #f6f6f6;
  width: 100%;
  max-width: 100vw;
  overflow-x: hidden;
  min-height: calc(100vh - 20px); /* 确保至少占满视口高度减去底部空间 */
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
  width: 100%;
  box-sizing: border-box;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
}

.analysis-container {
  margin-bottom: 1rem;
}

/* 修改卡片内容区域的内边距 */
.analysis-container :deep(.n-card__content) {
  padding: 16px;
}

.config-section {
  padding: 0.5rem;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
}

.results-section {
  padding: 0.5rem;
  min-height: 200px;
}

.results-header {
  margin-bottom: 1rem;
}

.n-data-table .analysis-cell {
  max-width: 300px;
  white-space: normal;
  overflow: hidden;
  text-overflow: ellipsis;
  word-break: break-word;
}

/* 表格容器基础样式 */
.table-container {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch; /* 支持iOS的滚动惯性 */
  position: relative;
  border-radius: 0.5rem;
}

/* 表格横向滚动指示器 */
.table-container::after {
  content: '←→';
  position: absolute;
  bottom: 10px;
  right: 10px;
  color: rgba(32, 128, 240, 0.6);
  font-size: 14px;
  pointer-events: none;
  z-index: 2;
  animation: fadeInOut 2s infinite;
  display: none; /* 默认隐藏，只在移动端显示 */
}

/* 移动端适配的媒体查询 */
@media (max-width: 768px) {
  .main-content {
    padding: 0.5rem;
    max-width: 100%;
    width: 100%;
  }
  
  /* 显示滚动指示器 */
  .table-container::after {
    display: block;
  }
  
  /* 减少移动端卡片内容区域的内边距 */
  .analysis-container :deep(.n-card__content) {
    padding: 12px 8px;
  }
  
  /* 确保卡片内部没有多余边距 */
  :deep(.n-card > .n-card__content) {
    padding: 12px 8px;
  }
  
  /* 减少结果区域的内边距 */
  .results-section {
    padding: 0.25rem 0.125rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .action-buttons .n-button {
    width: 100%;
  }
  
  .card-title {
    font-size: 1.1rem;
  }
  
  .analysis-container {
    margin-bottom: 0.75rem;
    border-radius: 0.75rem;
    overflow: hidden;
    width: 100%;
    box-sizing: border-box;
  }
  
  .config-section {
    padding: 0.25rem;
    width: 100%;
    box-sizing: border-box;
  }
  
  /* 移动端表格样式优化 */
  .table-container {
    margin: 0 -4px; /* 抵消父容器的padding */
    padding: 0 4px;
  }

  /* 表格组件移动端优化 */
  :deep(.n-data-table-wrapper) {
    border-radius: 0.5rem;
  }

  :deep(.n-data-table-base-table-header, .n-data-table-base-table-body) {
    min-width: 100%;
  }

  :deep(.n-pagination) {
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 8px;
  }
  
  /* 保留原有移动端优化样式 */
  :deep(.n-form-item) {
    margin-bottom: 0.75rem;
  }

  :deep(.n-grid) {
    width: 100% !important;
  }

  :deep(.n-grid-item) {
    width: 100% !important;
    max-width: 100% !important;
  }

  :deep(.n-grid[cols="1 m\\:24"]) {
    gap: 8px !important;
  }

  :deep(.n-grid[cols="1 l\\:2"]) {
    gap: 6px !important;
  }

  :deep(.n-grid-item) > * {
    margin-bottom: 8px;
  }

  :deep(.n-dropdown-menu) {
    max-width: 90vw;
  }
  
  .app-container {
    padding-bottom: 30px; /* 增加移动端底部内边距 */
  }
}

/* 小屏幕手机适配 */
@media (max-width: 480px) {
  .main-content {
    padding: 0.25rem;
  }
  
  /* 进一步减少小屏幕卡片内容区域的内边距 */
  .analysis-container :deep(.n-card__content) {
    padding: 6px 4px;
  }
  
  /* 使用更精确的选择器确保覆盖 */
  :deep(.n-card) > :deep(.n-card__content),
  :deep(.n-card-header) {
    padding: 6px 4px !important;
  }
  
  /* 减少网格间距到最小 */
  :deep(.n-grid[cols="1 l\\:2"]) {
    gap: 4px !important;
  }
  
  .results-section {
    padding: 0.15rem 0.05rem;
  }
  
  .results-header {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }
  
  :deep(.n-space) {
    flex-wrap: wrap;
    width: 100%;
    justify-content: space-between;
  }
  
  :deep(.n-space .n-button) {
    margin-right: 0 !important;
  }
  
  .analysis-container {
    border-radius: 0.625rem;
    margin-bottom: 0.5rem;
  }
  
  /* 小屏幕下进一步优化n-grid */
  :deep(.n-grid) {
    gap: 4px !important;
  }
  
  :deep(.n-grid-item) {
    padding: 0 !important;
  }
  
  /* 确保n-grid-item内容在小屏幕下有更紧凑的间距 */
  :deep(.n-grid-item) > * {
    margin-bottom: 4px;
  }
  
  /* 小屏幕表格样式调整 */
  .table-container {
    margin: 0 -2px;
    padding: 0 2px;
  }
  
  /* 小屏幕分页控件优化 */
  :deep(.n-pagination .n-pagination-item) {
    margin: 0 2px;
  }
  
  .app-container {
    padding-bottom: 40px; /* 增加小屏幕底部内边距 */
  }
}

/* 超小屏幕适配 */
@media (max-width: 375px) {
  /* 超小屏幕卡片内容区域几乎无内边距 */
  .analysis-container :deep(.n-card__content) {
    padding: 4px 2px;
  }
  
  /* 使用更精确的选择器确保覆盖 */
  :deep(.n-card) > :deep(.n-card__content),
  :deep(.n-card-header) {
    padding: 3px 2px !important;
  }
  
  /* 网格间距最小化 */
  :deep(.n-grid[cols="1 l\\:2"]),
  :deep(.n-grid[cols="1 m\\:24"]) {
    gap: 3px !important;
  }
  
  /* 极简边距 */
  .results-section {
    padding: 0.1rem 0.025rem;
  }
  
  /* 进一步调整超小屏幕的间距和尺寸 */
  .main-content {
    padding: 0.15rem;
  }
  
  .config-section {
    padding: 0.15rem;
  }
  
  /* 确保StockCard组件最大化利用空间 */
  :deep(.stock-card) {
    margin: 2px 0 !important;
    border-radius: 4px !important;
  }
}
</style>
