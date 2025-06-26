#!/bin/bash

# 1. 进入前端目录
cd frontend || exit 1

# 2. 智能检测是否需要安装依赖
NEED_INSTALL=false

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
  echo "未检测到 node_modules，需要安装依赖"
  NEED_INSTALL=true
else
  # 检查 package.json 或 package-lock.json 是否比 node_modules 更新
  if [ "package.json" -nt "node_modules" ] || [ "package-lock.json" -nt "node_modules" ]; then
    echo "检测到依赖文件有更新，需要重新安装依赖"
    NEED_INSTALL=true
  else
    echo "依赖无变化，跳过 npm install"
  fi
fi

# 根据检测结果决定是否安装
if [ "$NEED_INSTALL" = true ]; then
  echo "正在安装/更新依赖..."
  npm install
fi

# 3. 编译前端
echo "正在编译前端..."
npm run build

# 4. 回到项目根目录
cd ..

# 5. 关闭并重启所有 docker-compose 服务
echo "正在重启 docker 服务..."
docker-compose down
docker-compose build
docker-compose up -d

echo "全部完成！"