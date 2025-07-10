<template>
  <div class="watchlist-container">
    <NCard
      title="自选股管理"
      class="watchlist-card"
    >
      <template #header-extra>
        <NSpace>
          <NButton
            type="primary"
            @click="showAddDialog = true"
          >
            <template #icon>
              <NIcon><AddIcon /></NIcon>
            </template>
            添加股票
          </NButton>
          <NButton @click="refreshWatchlist">
            <template #icon>
              <NIcon><RefreshIcon /></NIcon>
            </template>
            刷新
          </NButton>
        </NSpace>
      </template>

      <!-- 自选股列表 -->
      <div class="watchlist-list">
        <template v-if="watchlist.length === 0 && !loading">
          <NEmpty description="暂无自选股">
            <template #icon>
              <NIcon><HeartIcon /></NIcon>
            </template>
            <template #extra>
              <NButton
                size="small"
                @click="showAddDialog = true"
              >
                添加第一只股票
              </NButton>
            </template>
          </NEmpty>
        </template>

        <template v-else>
          <NGrid
            cols="1 s:2 m:3 l:4"
            :x-gap="12"
            :y-gap="12"
          >
            <NGridItem
              v-for="stock in watchlist"
              :key="stock.id"
            >
              <NCard 
                size="small" 
                class="stock-item-card"
                :class="getPriceChangeClass(stock.price_change)"
              >
                <template #header>
                  <div class="stock-header">
                    <div class="stock-code-name">
                      <span class="stock-code">{{ stock.code }}</span>
                      <span class="stock-name">{{ stock.name }}</span>
                    </div>
                    <NDropdown
                      trigger="click"
                      :options="getStockMenuOptions(stock)"
                      @select="(key) => handleStockMenuSelect(key, stock)"
                    >
                      <NButton
                        text
                        size="small"
                      >
                        <template #icon>
                          <NIcon><MoreIcon /></NIcon>
                        </template>
                      </NButton>
                    </NDropdown>
                  </div>
                </template>

                <div class="stock-info">
                  <div class="price-info">
                    <div class="current-price">
                      {{ stock.price !== undefined ? stock.price.toFixed(2) : '--' }}
                    </div>
                    <div class="price-change">
                      <span class="change-amount">
                        {{ formatPriceChange(stock.price_change) }}
                      </span>
                      <span class="change-percent">
                        {{ formatPercentChange(stock.change_percent) }}
                      </span>
                    </div>
                  </div>
                  <div class="market-info">
                    <NTag
                      size="small"
                      :type="getMarketTagType(stock.market_type) as any"
                    >
                      {{ getMarketName(stock.market_type) }}
                    </NTag>
                  </div>
                  
                  <div class="update-time">
                    <NText
                      depth="3"
                      style="font-size: 12px;"
                    >
                      {{ formatUpdateTime(stock.updated_at) }}
                    </NText>
                  </div>
                </div>
              </NCard>
            </NGridItem>
          </NGrid>
        </template>
      </div>

      <!-- 加载状态 -->
      <NSpin
        :show="loading"
        style="min-height: 200px;"
      />
    </NCard>

    <!-- 添加股票对话框 -->
    <NModal
      v-model:show="showAddDialog"
      preset="dialog"
      title="添加自选股"
    >
      <template #default>
        <NForm
          ref="addFormRef"
          :model="addForm"
          :rules="addFormRules"
        >
          <NFormItem
            label="市场类型"
            path="marketType"
          >
            <NSelect
              v-model:value="addForm.marketType"
              :options="marketOptions"
              @update:value="handleMarketTypeChange"
            />
          </NFormItem>
          
          <NFormItem
            v-if="showSearch"
            label="股票搜索"
          >
            <StockSearch 
              :market-type="addForm.marketType" 
              @select="handleStockSelect"
            />
          </NFormItem>
          
          <NFormItem
            label="股票代码"
            path="code"
          >
            <NInput
              v-model:value="addForm.code"
              placeholder="请输入股票代码"
              @keyup.enter="handleAddStock"
            />
          </NFormItem>
          
          <NFormItem
            label="备注"
            path="note"
          >
            <NInput
              v-model:value="addForm.note"
              placeholder="可选：添加备注信息"
              type="textarea"
              :autosize="{ minRows: 2, maxRows: 4 }"
            />
          </NFormItem>
        </NForm>
      </template>
      
      <template #action>
        <NSpace>
          <NButton @click="showAddDialog = false">
            取消
          </NButton>
          <NButton
            type="primary"
            :loading="adding"
            @click="handleAddStock"
          >
            确定添加
          </NButton>
        </NSpace>
      </template>
    </NModal>

    <!-- 编辑股票对话框 -->
    <NModal
      v-model:show="showEditDialog"
      preset="dialog"
      title="编辑自选股"
    >
      <template #default>
        <NForm
          ref="editFormRef"
          :model="editForm"
          :rules="editFormRules"
        >
          <NFormItem label="股票代码">
            <NInput
              v-model:value="editForm.code"
              disabled
            />
          </NFormItem>
          
          <NFormItem label="股票名称">
            <NInput
              v-model:value="editForm.name"
              disabled
            />
          </NFormItem>
          
          <NFormItem
            label="备注"
            path="note"
          >
            <NInput
              v-model:value="editForm.note"
              placeholder="可选：添加备注信息"
              type="textarea"
              :autosize="{ minRows: 2, maxRows: 4 }"
            />
          </NFormItem>
        </NForm>
      </template>
      
      <template #action>
        <NSpace>
          <NButton @click="showEditDialog = false">
            取消
          </NButton>
          <NButton
            type="primary"
            :loading="updating"
            @click="handleUpdateStock"
          >
            保存修改
          </NButton>
        </NSpace>
      </template>
    </NModal>
  </div>
</template>

<script setup lang="ts">
import {
  Add as AddIcon,
  Heart as HeartIcon,
  EllipsisHorizontal as MoreIcon,
  Refresh as RefreshIcon,
} from "@vicons/ionicons5";
import {
  type FormInst,
  type FormRules,
  NButton,
  NCard,
  NDropdown,
  NEmpty,
  NForm,
  NFormItem,
  NGrid,
  NGridItem,
  NIcon,
  NInput,
  NModal,
  NSelect,
  NSpace,
  NSpin,
  NTag,
  NText,
  useMessage,
} from "naive-ui";
import { computed, onMounted, ref } from "vue";

import { type WatchlistItem, watchlistService } from "@/services/watchlist";
import StockSearch from "./StockSearch.vue";

const message = useMessage();

// 响应式数据
const watchlist = ref<WatchlistItem[]>([]);
const loading = ref(false);
const adding = ref(false);
const updating = ref(false);
const showAddDialog = ref(false);
const showEditDialog = ref(false);

// 表单引用
const addFormRef = ref<FormInst | null>(null);
const editFormRef = ref<FormInst | null>(null);

// 添加表单数据
const addForm = ref({
  marketType: "A",
  code: "",
  note: "",
});

// 编辑表单数据
const editForm = ref({
  id: 0,
  code: "",
  name: "",
  note: "",
});

// 市场选项
const marketOptions = [
  { label: "A股", value: "A" },
  { label: "港股", value: "HK" },
  { label: "美股", value: "US" },
  { label: "ETF", value: "ETF" },
  { label: "LOF", value: "LOF" },
];

// 表单验证规则
const addFormRules: FormRules = {
  code: [{ required: true, message: "请输入股票代码", trigger: "blur" }],
};

const editFormRules: FormRules = {
  note: [{ max: 200, message: "备注长度不能超过200字符", trigger: "blur" }],
};

// 计算属性
const showSearch = computed(() =>
  ["US", "ETF", "LOF"].includes(addForm.value.marketType),
);

// 发送自选股分析事件
const emit = defineEmits<{
  analyzeWatchlist: [codes: string[], marketType: string];
}>();

// 获取价格变动样式类
function getPriceChangeClass(priceChange?: number) {
  if (priceChange === undefined) {
    return "";
  }
  if (priceChange > 0) {
    return "price-up";
  }
  if (priceChange < 0) {
    return "price-down";
  }
  return "";
}

// 格式化价格变动
function formatPriceChange(priceChange?: number) {
  if (priceChange === undefined) {
    return "--";
  }
  const sign = priceChange > 0 ? "+" : "";
  return `${sign}${priceChange.toFixed(2)}`;
}

// 格式化百分比变动
function formatPercentChange(changePercent?: number) {
  if (changePercent === undefined) {
    return "--";
  }
  const sign = changePercent > 0 ? "+" : "";
  return `${sign}${changePercent.toFixed(2)}%`;
}

// 获取市场标签类型
function getMarketTagType(marketType: string) {
  const typeMap: Record<string, string> = {
    A: "default",
    HK: "info",
    US: "warning",
    ETF: "success",
    LOF: "error",
  };
  return typeMap[marketType] || "default";
}

// 获取市场名称
function getMarketName(marketType: string) {
  const nameMap: Record<string, string> = {
    A: "A股",
    HK: "港股",
    US: "美股",
    ETF: "ETF",
    LOF: "LOF",
  };
  return nameMap[marketType] || marketType;
}

// 格式化更新时间
function formatUpdateTime(updateTime?: string) {
  if (!updateTime) {
    return "未更新";
  }

  try {
    const date = new Date(updateTime);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    if (diff < 60000) {
      return "刚才";
    }
    if (diff < 3600000) {
      return `${Math.floor(diff / 60000)}分钟前`;
    }
    if (diff < 86400000) {
      return `${Math.floor(diff / 3600000)}小时前`;
    }

    return date.toLocaleDateString();
  } catch {
    return updateTime;
  }
}

// 获取股票菜单选项
function getStockMenuOptions(_stock: WatchlistItem) {
  return [
    {
      label: "分析",
      key: "analyze",
    },
    {
      label: "编辑",
      key: "edit",
    },
    {
      label: "删除",
      key: "delete",
    },
  ];
}

// 处理股票菜单选择
function handleStockMenuSelect(key: string, stock: WatchlistItem) {
  switch (key) {
  case "analyze":
    handleAnalyzeStock(stock);
    break;
  case "edit":
    handleEditStock(stock);
    break;
  case "delete":
    handleDeleteStock(stock);
    break;
  }
}

// 处理市场类型变更
function handleMarketTypeChange() {
  addForm.value.code = "";
}

// 处理股票选择
function handleStockSelect(symbol: string) {
  addForm.value.code = symbol.trim().replace(/^\d+\.\s*/, "");
}

// 处理编辑股票
function handleEditStock(stock: WatchlistItem) {
  editForm.value = {
    id: stock.id,
    code: stock.code,
    name: stock.name || "",
    note: stock.note || "",
  };
  showEditDialog.value = true;
}

// 处理分析股票
function handleAnalyzeStock(stock: WatchlistItem) {
  emit("analyzeWatchlist", [stock.code], stock.market_type);
  message.info(`开始分析 ${stock.code}`);
}

// 处理删除股票
async function handleDeleteStock(stock: WatchlistItem) {
  try {
    await watchlistService.removeStock(stock.id);
    message.success(`已删除 ${stock.code}`);
    await loadWatchlist();
  } catch (error: any) {
    message.error(`删除失败: ${error.message}`);
  }
}

// 添加股票
async function handleAddStock() {
  if (!addFormRef.value) {
    return;
  }

  try {
    await addFormRef.value.validate();
    adding.value = true;

    await watchlistService.addStock({
      code: addForm.value.code.trim().toUpperCase(),
      market_type: addForm.value.marketType,
      note: addForm.value.note.trim() || undefined,
    });

    message.success("添加成功");
    showAddDialog.value = false;

    // 重置表单
    addForm.value = {
      marketType: "A",
      code: "",
      note: "",
    };

    // 重新加载列表
    await loadWatchlist();
  } catch (error: any) {
    message.error(`添加失败: ${error.message}`);
  } finally {
    adding.value = false;
  }
}

// 更新股票
async function handleUpdateStock() {
  if (!editFormRef.value) {
    return;
  }

  try {
    await editFormRef.value.validate();
    updating.value = true;

    await watchlistService.updateStock(editForm.value.id, {
      note: editForm.value.note.trim() || undefined,
    });

    message.success("更新成功");
    showEditDialog.value = false;

    // 重新加载列表
    await loadWatchlist();
  } catch (error: any) {
    message.error(`更新失败: ${error.message}`);
  } finally {
    updating.value = false;
  }
}

// 加载自选股列表
async function loadWatchlist() {
  try {
    loading.value = true;
    watchlist.value = await watchlistService.getWatchlist();
  } catch (error: any) {
    message.error(`加载自选股失败: ${error.message}`);
  } finally {
    loading.value = false;
  }
}

// 刷新自选股
async function refreshWatchlist() {
  await loadWatchlist();
  message.success("已刷新");
}

// 组件初始化
onMounted(() => {
  loadWatchlist();
});

// 暴露方法给父组件
defineExpose({
  refreshWatchlist,
  loadWatchlist,
});
</script>

<style scoped>
.watchlist-container {
  padding: 16px;
}

.watchlist-card {
  max-width: 1200px;
  margin: 0 auto;
}

.watchlist-list {
  min-height: 300px;
}

.stock-item-card {
  height: 100%;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.stock-item-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stock-item-card.price-up {
  border-color: #18a058;
  background: linear-gradient(135deg, #f0f9ff 0%, #f0f9f4 100%);
}

.stock-item-card.price-down {
  border-color: #d03050;
  background: linear-gradient(135deg, #fef2f2 0%, #fef1f1 100%);
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-code-name {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stock-code {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.stock-name {
  font-size: 12px;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 120px;
}

.stock-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.price-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.current-price {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.price-change {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.change-amount, .change-percent {
  font-size: 12px;
  font-weight: 500;
}

.price-up .change-amount,
.price-up .change-percent {
  color: #18a058;
}

.price-down .change-amount,
.price-down .change-percent {
  color: #d03050;
}

.market-info {
  display: flex;
  justify-content: flex-start;
}

.update-time {
  display: flex;
  justify-content: center;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .watchlist-container {
    padding: 8px;
  }
  
  .stock-name {
    max-width: 80px;
  }
  
  .current-price {
    font-size: 16px;
  }
  
  .change-amount, .change-percent {
    font-size: 11px;
  }
}
</style>
