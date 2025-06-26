#!/bin/bash

# 1. 进入前端目录
cd frontend || exit 1

# 2. 判断是否已安装依赖
if [ -d "node_modules" ]; then
  echo "依赖已安装，跳过 npm install"
else
  echo "未检测到 node_modules，正在安装依赖..."
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