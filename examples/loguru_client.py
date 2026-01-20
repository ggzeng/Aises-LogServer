"""
Loguru 客户端示例 - 将日志发送到 Log Server

使用方法:
    python loguru_client.py                    # 使用默认 client_id
    python loguru_client.py my-app-instance-1  # 指定 client_id
"""

import sys
import socket
import requests
from loguru import logger
from datetime import datetime
import time

# ============ 配置 ============
LOG_SERVER_URL = "http://localhost:8000/logs"
CLIENT_ID = f"app-{sys.argv[1] if len(sys.argv) > 1 else 'default'}"
HOSTNAME = socket.gethostname()
# ================================


def send_log_to_server(message):
    """
    Loguru 处理器函数 - 将日志发送到服务器

    Args:
        message: Loguru 的日志记录对象
    """
    log_entry = message.record

    # 构建新格式的日志数据
    log_data = {
        "clientId": CLIENT_ID,
        "hostname": HOSTNAME,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "messages": [
            {
                "timestamp": datetime.fromtimestamp(log_entry["time"].timestamp()).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "level": log_entry["level"].name,
                "message": log_entry["message"],
                "logger": log_entry["name"],
                "function": log_entry["function"],
                "line": log_entry["line"],
                "extra": log_entry.get("extra")
            }
        ]
    }

    try:
        # 发送到日志服务器 (timeout=1 避免阻塞主程序)
        response = requests.post(LOG_SERVER_URL, json=log_data, timeout=1)
        if response.status_code == 200:
            # 可选: 在控制台显示发送成功
            pass
    except requests.exceptions.Timeout:
        # 超时不影响主程序
        pass
    except Exception as e:
        # 静默处理错误，避免日志发送失败影响主程序
        pass


def setup_logger():
    """配置 Loguru 日志系统"""

    # 移除默认的处理器
    logger.remove()

    # 1. 添加控制台输出 (彩色格式)
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        level="DEBUG"
    )

    # 2. 添加日志服务器处理器
    logger.add(
        send_log_to_server,
        format="{message}",  # 消息格式在 send_log_to_server 中构建
        level="DEBUG"        # 发送所有级别的日志
    )

    logger.info(f"日志客户端已启动 (CLIENT_ID: {CLIENT_ID})")
    logger.info(f"日志服务器: {LOG_SERVER_URL}")


def demo_logging():
    """演示各种日志级别"""
    logger.debug("这是一条调试日志，包含数字 12345")
    logger.info(f"应用程序启动，客户端 ID: {CLIENT_ID}")
    logger.warning("内存使用率达到 85%，当前使用 2048 MB")
    logger.error("无法连接到数据库，端口 5432，重试中...")
    logger.critical("磁盘空间不足，剩余空间小于 1024 MB")


def demo_loop():
    """演示循环日志输出"""
    logger.info("开始处理任务队列...")

    for i in range(10):
        logger.info(f"正在处理任务 {i+1}/10")
        time.sleep(0.5)

        if i == 5:
            logger.warning("任务处理速度较慢，已耗时 2.5 秒")
        elif i == 8:
            logger.error(f"任务 {i+1} 处理失败，错误代码 500")

    logger.success("所有任务完成！成功处理 8 个任务，失败 2 个")


def demo_structured_data():
    """演示结构化数据日志"""
    user_data = {
        "user_id": 12345,
        "username": "test_user",
        "action": "login",
        "ip": "192.168.1.100"
    }

    logger.info(f"用户登录: {user_data}")
    logger.debug(f"请求数据: headers={123}, params={456}")


if __name__ == "__main__":
    # 配置日志系统
    setup_logger()

    # 运行演示
    print("\n" + "="*60)
    print("Loguru 客户端演示")
    print("="*60 + "\n")

    logger.info("=== 开始演示 ===")

    # 演示各种日志级别
    print("\n1. 各种日志级别演示:")
    demo_logging()

    time.sleep(1)

    # 演示结构化数据
    print("\n2. 结构化数据日志演示:")
    demo_structured_data()

    time.sleep(1)

    # 演示循环日志
    print("\n3. 循环任务演示:")
    demo_loop()

    logger.info("=== 演示结束 ===")
    logger.success(f"客户端 {CLIENT_ID} 演示完成")

    print("\n" + "="*60)
    print("提示: 打开浏览器访问 http://localhost:8000/static/index.html 查看实时日志")
    print("="*60 + "\n")
