import axios from 'axios';

// 从环境变量读取 API 基础 URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

// 创建axios实例
const axiosInstance = axios.create({
  baseURL: API_BASE_URL
});

// 请求拦截器，添加token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器，处理401错误
axiosInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
    }
    return Promise.reject(error);
  }
);

// 自选股数据类型
export interface WatchlistItem {
  id: number;
  code: string;
  name?: string;
  market_type: string;
  price?: number;
  price_change?: number;
  change_percent?: number;
  market_value?: number;
  note?: string;
  created_at: string;
  updated_at: string;
}

export interface AddWatchlistRequest {
  code: string;
  market_type: string;
  note?: string;
}

export interface UpdateWatchlistRequest {
  note?: string;
}

export interface WatchlistResponse {
  items: WatchlistItem[];
  total: number;
}

export interface BatchAnalyzeWatchlistRequest {
  stock_ids?: number[];
  market_types?: string[];
  api_url?: string;
  api_key?: string;
  api_model?: string;
  api_timeout?: number;
}

// 自选股服务
export const watchlistService = {
  // 获取自选股列表
  getWatchlist: async (): Promise<WatchlistItem[]> => {
    try {
      const response = await axiosInstance.get('/watchlist');
      return response.data.items || [];
    } catch (error: any) {
      console.error('获取自选股列表失败:', error);
      throw new Error(error.response?.data?.detail || '获取自选股列表失败');
    }
  },

  // 添加自选股
  addStock: async (request: AddWatchlistRequest): Promise<WatchlistItem> => {
    try {
      const response = await axiosInstance.post('/watchlist', request);
      return response.data;
    } catch (error: any) {
      console.error('添加自选股失败:', error);
      throw new Error(error.response?.data?.detail || '添加自选股失败');
    }
  },

  // 删除自选股
  removeStock: async (stockId: number): Promise<void> => {
    try {
      await axiosInstance.delete(`/watchlist/${stockId}`);
    } catch (error: any) {
      console.error('删除自选股失败:', error);
      throw new Error(error.response?.data?.detail || '删除自选股失败');
    }
  },

  // 更新自选股
  updateStock: async (stockId: number, request: UpdateWatchlistRequest): Promise<WatchlistItem> => {
    try {
      const response = await axiosInstance.put(`/watchlist/${stockId}`, request);
      return response.data;
    } catch (error: any) {
      console.error('更新自选股失败:', error);
      throw new Error(error.response?.data?.detail || '更新自选股失败');
    }
  },

  // 批量分析自选股
  batchAnalyzeWatchlist: async (request: BatchAnalyzeWatchlistRequest) => {
    try {
      return axiosInstance.post('/watchlist/batch_analyze', request, {
        responseType: 'stream'
      });
    } catch (error: any) {
      console.error('批量分析自选股失败:', error);
      throw new Error(error.response?.data?.detail || '批量分析自选股失败');
    }
  },

  // 刷新自选股价格数据
  refreshWatchlistPrices: async (): Promise<void> => {
    try {
      await axiosInstance.post('/watchlist/refresh_prices');
    } catch (error: any) {
      console.error('刷新自选股价格失败:', error);
      throw new Error(error.response?.data?.detail || '刷新自选股价格失败');
    }
  },

  // 检查股票是否已在自选股中
  checkStockExists: async (code: string, marketType: string): Promise<boolean> => {
    try {
      const response = await axiosInstance.get('/watchlist/check', {
        params: { code, market_type: marketType }
      });
      return response.data.exists;
    } catch (error: any) {
      console.error('检查股票是否存在失败:', error);
      return false;
    }
  }
};