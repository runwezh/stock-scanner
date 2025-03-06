import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'

// 获取当前文件的目录路径（在ESM中替代__dirname）
const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    cors: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8888',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/analyze': {
        target: 'http://127.0.0.1:8888',
        changeOrigin: true,
      },
      '/test_api_connection': {
        target: 'http://127.0.0.1:8888',
        changeOrigin: true,
      },
      '/search_us_stocks': {
        target: 'http://127.0.0.1:8888',
        changeOrigin: true,
      },
      '/config': {
        target: 'http://127.0.0.1:8888',
        changeOrigin: true,
      },
      '/login': {
        target: 'http://127.0.0.1:8888',
        changeOrigin: true,
      },
      '/check_auth': {
        target: 'http://127.0.0.1:8888',
        changeOrigin: true,
      },
      '/need_login': {
        target: 'http://127.0.0.1:8888',
        changeOrigin: true,
      },
      '/us_stock_detail': {
        target: 'http://127.0.0.1:8888',
        changeOrigin: true,
      },
      '/fund_detail': {
        target: 'http://127.0.0.1:8888',
        changeOrigin: true,
      },
      '/search_funds': {
        target: 'http://127.0.0.1:8888',
        changeOrigin: true,
      },
    },
  },
})
