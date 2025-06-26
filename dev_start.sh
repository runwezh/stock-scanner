#!/bin/bash

# 开发环境前端启动脚本
# 用于快速启动前端开发服务器

echo "🚀 启动前端开发服务器..."

# 1. 进入前端目录
cd frontend || {
  echo "❌ 错误：无法进入 frontend 目录"
  exit 1
}

# 2. 智能检测是否需要安装依赖
NEED_INSTALL=false

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
  echo "📦 未检测到 node_modules，需要安装依赖"
  NEED_INSTALL=true
else
  # 检查 package.json 或 package-lock.json 是否比 node_modules 更新
  if [ "package.json" -nt "node_modules" ] || [ "package-lock.json" -nt "node_modules" ]; then
    echo "📦 检测到依赖文件有更新，需要重新安装依赖"
    NEED_INSTALL=true
  else
    echo "✅ 依赖无变化，跳过 npm install"
  fi
fi

# 根据检测结果决定是否安装
if [ "$NEED_INSTALL" = true ]; then
  echo "⏳ 正在安装/更新依赖..."
  npm install || {
    echo "❌ 依赖安装失败"
    exit 1
  }
  echo "✅ 依赖安装完成"
fi

# 3. 检查端口是否被占用
PORT=5173
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
  echo "⚠️  端口 $PORT 已被占用，尝试终止现有进程..."
  lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
  sleep 2
fi

# 4. 启动开发服务器
echo "🌐 启动开发服务器 (端口: $PORT)..."
echo "📱 本地访问: http://localhost:$PORT"
echo "🌍 网络访问: http://$(ipconfig getifaddr en0):$PORT"
echo "⏹️  按 Ctrl+C 停止服务器"
echo ""

# 启动 Vite 开发服务器
npm run dev