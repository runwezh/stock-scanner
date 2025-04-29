# 阶段一: 构建Vue前端
FROM node:20.19.1-slim as frontend-builder

# 设置工作目录
WORKDIR /app/frontend

# 复制前端项目文件
COPY frontend/package*.json ./

# 安装依赖
# 使用 npm ci 以确保一致性安装
RUN npm ci

# 复制前端源代码
COPY frontend/ ./

# 构建前端应用
RUN npm run build

# 阶段二: 构建Python后端依赖
FROM python:3.12.10-slim as backend-builder

# 设置工作目录
WORKDIR /app

# ******** 修改点 1: 切换到阿里云镜像源 ********
# 在执行 apt-get update 前切换到阿里云镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 安装系统依赖和构建依赖
# 添加 --no-install-recommends 减少镜像体积
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    ca-certificates \
    build-essential \
    # 清理 apt 缓存
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件 (requirements.txt)
COPY requirements.txt /app/

# 安装 Python 依赖
# 使用 --no-cache-dir 减少缓存, --user 安装到用户目录
RUN pip install --no-cache-dir --user -r requirements.txt

# 阶段三: 运行阶段
FROM python:3.12.10-slim

# 设置工作目录
WORKDIR /app

# ******** 修改点 2: 再次切换到阿里云镜像源 ********
# 确保运行时也使用阿里云镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 安装运行时依赖
# 添加 --no-install-recommends 减少镜像体积
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    ca-certificates \
    curl \
    # 清理 apt 缓存
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制Python依赖
# --user 安装的包位于 /root/.local
COPY --from=backend-builder /root/.local /root/.local

# 确保脚本路径在PATH中
# 将用户安装的 Python 包的 bin 目录添加到 PATH
ENV PATH=/root/.local/bin:$PATH

# 设置环境变量 (通常不需要显式设置 PYTHONPATH)
# ENV PYTHONPATH=/app

# 复制应用代码
# 注意：这会复制构建上下文中的所有内容，请使用 .dockerignore 排除不需要的文件
COPY . /app/

# 从前端构建阶段复制生成的静态文件到后端的前端目录
# 确认目标路径 /app/frontend/dist 是正确的
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# 暴露端口
EXPOSE 8888

# 健康检查
# 使用已安装的 curl 检查服务是否启动
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8888/api/config || exit 1

# 启动命令
CMD ["python", "web_server.py"]
