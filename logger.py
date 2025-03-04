from loguru import logger
import sys
import os
from datetime import datetime

# 获取当前时间作为日志文件名的一部分
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

# 创建日志目录
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)

# 配置日志
logger.remove()  # 移除默认的处理器

# 添加标准输出处理器（控制台）
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG"
)

# 添加文件处理器（debug级别）
logger.add(
    os.path.join(log_dir, f"debug_{current_time}.log"),
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{line} - {message}",
    level="DEBUG",
    rotation="100 MB",
    retention="1 week"
)

# 添加文件处理器（error级别）
logger.add(
    os.path.join(log_dir, f"error_{current_time}.log"),
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{line} - {message}",
    level="ERROR",
    rotation="100 MB",
    retention="1 month"
)

# 添加流处理器（用于记录流式输出）
logger.add(
    os.path.join(log_dir, f"stream_{current_time}.log"),
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}",
    filter=lambda record: "STREAM" in record["extra"],
    level="INFO"
)

# 创建专用于流式输出的日志器
stream_logger = logger.bind(STREAM=True)

def get_logger():
    """获取通用日志器"""
    return logger

def get_stream_logger():
    """获取流式输出专用日志器"""
    return stream_logger
