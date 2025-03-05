// API接口相关类型
export interface ApiConfig {
  apiUrl: string;
  apiKey: string;
  apiModel: string;
  apiTimeout: string;
  saveApiConfig: boolean;
}

export interface StockInfo {
  code: string;
  name: string;
  marketType: string;
  price?: number;
  changePercent?: number;
  marketValue?: number;
  analysis?: string;
  analysisStatus: 'waiting' | 'analyzing' | 'completed' | 'error';
  error?: string;
}

export interface SearchResult {
  symbol: string;
  name: string;
  market: string;
  marketValue?: number;
}

export interface MarketStatus {
  isOpen: boolean;
  nextTime: string;
}

export interface MarketTimeInfo {
  currentTime: string;
  cnMarket: MarketStatus;
  hkMarket: MarketStatus;
  usMarket: MarketStatus;
}

// 分析请求和响应
export interface AnalyzeRequest {
  stock_codes: string[];
  market_type: string;
  api_url?: string;
  api_key?: string;
  api_model?: string;
  api_timeout?: string;
}

export interface TestApiRequest {
  api_url: string;
  api_key: string;
  api_model: string;
  api_timeout: string;
}

export interface TestApiResponse {
  success: boolean;
  message: string;
  status_code?: number;
}

// 流式响应类型
export interface StreamInitMessage {
  stream_type: 'single' | 'batch';
  stock_code?: string;
  stock_codes?: string[];
}

export interface StreamAnalysisUpdate {
  stock_code: string;
  analysis?: string;
  status: 'analyzing' | 'completed' | 'error';
  error?: string;
  name?: string;
  price?: number;
  change_percent?: number;
  market_value?: number;
}
