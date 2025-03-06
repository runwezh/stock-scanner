# 使用 Python 3.10 作为基础镜像
FROM python:3.10-slim as builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖和构建依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    ca-certificates \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt /app/

# 安装 Python 依赖
RUN pip install --no-cache-dir --user -r requirements.txt

# 第二阶段：运行阶段
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制Python依赖
COPY --from=builder /root/.local /root/.local

# 确保脚本路径在PATH中
ENV PATH=/root/.local/bin:$PATH

# 设置环境变量
ENV PYTHONPATH=/app

# 复制应用代码
COPY . /app/

# 暴露端口
EXPOSE 8888

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8888/config || exit 1

# 启动命令
CMD ["python", "web_server.py"]