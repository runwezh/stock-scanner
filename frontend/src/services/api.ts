import axios from 'axios';
import type { AnalyzeRequest, TestApiRequest, TestApiResponse, SearchResult } from '@/types';

// 在开发环境中前缀为空，因为已经在vite.config.ts中配置了代理
const API_PREFIX = '';

export const apiService = {
  // 分析股票
  analyzeStocks: async (request: AnalyzeRequest) => {
    return axios.post(`${API_PREFIX}/analyze`, request, {
      responseType: 'stream'
    });
  },

  // 测试API连接
  testApiConnection: async (request: TestApiRequest): Promise<TestApiResponse> => {
    try {
      const response = await axios.post(`${API_PREFIX}/test_api_connection`, request);
      return response.data;
    } catch (error: any) {
      if (error.response) {
        return error.response.data;
      }
      return {
        success: false,
        message: error.message || '连接失败'
      };
    }
  },

  // 搜索美股
  searchUsStocks: async (keyword: string): Promise<SearchResult[]> => {
    try {
      const response = await axios.get(`${API_PREFIX}/search_us_stocks`, {
        params: { keyword }
      });
      return response.data.results || [];
    } catch (error) {
      console.error('搜索美股时出错:', error);
      return [];
    }
  },
  
  // 获取配置
  getConfig: async () => {
    try {
      const response = await axios.get(`${API_PREFIX}/config`);
      return response.data;
    } catch (error) {
      console.error('获取配置时出错:', error);
      return {
        announcement: '',
        default_api_url: '',
        default_api_model: 'gpt-3.5-turbo',
        default_api_timeout: '60'
      };
    }
  }
};
