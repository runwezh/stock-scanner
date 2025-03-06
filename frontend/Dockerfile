# 构建阶段
FROM node:18-alpine as build-stage

# 设置工作目录
WORKDIR /app

# 安装 yarn
RUN apk add --no-cache yarn

# 复制 package.json 和 yarn.lock（如果有）
COPY package*.json yarn*.lock ./

# 安装依赖
RUN yarn install --frozen-lockfile

# 复制项目文件
COPY . .

# 构建应用
RUN yarn build

# 生产阶段
FROM nginx:stable-alpine as production-stage

# 复制自定义nginx配置（如需要）
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制构建结果到nginx服务目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 暴露80端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:80 || exit 1

# 启动nginx
CMD ["nginx", "-g", "daemon off;"] 