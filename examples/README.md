# Loguru 客户端示例

本目录包含如何将 Loguru 日志发送到 Log Server 的示例。

## loguru_client.py

完整的 Loguru 客户端实现示例。

### 使用方法

```bash
# 使用默认 clientId
python loguru_client.py

# 指定 clientId (用于区分不同的应用实例)
python loguru_client.py my-app-instance-1
python loguru_client.py web-server-prod-2
```

### 消息格式

客户端发送到服务器的日志格式：

```json
{
  "clientId": "app-my-app-instance-1",
  "hostname": "server-01.example.com",
  "timestamp": "2026-01-20 16:30:00.123",
  "messages": [
    {
      "timestamp": "2026-01-20 16:30:00.000",
      "level": "INFO",
      "message": "应用启动成功",
      "logger": "app",
      "function": "start",
      "line": 42
    }
  ]
}
```

### 功能特性

- ✅ 自动发送所有级别的日志到服务器
- ✅ 彩色控制台输出
- ✅ 非阻塞发送 (timeout=1s)
- ✅ 错误处理 (发送失败不影响主程序)
- ✅ 可配置 CLIENT_ID 和服务器 URL

### 集成到你的项目

1. **复制 `send_log_to_server` 函数到你的项目**

2. **配置 Loguru**

```python
from loguru import logger
import sys

logger.remove()

# 控制台输出
logger.add(sys.stderr, format="{time} | {level} | {message}")

# 发送到日志服务器
logger.add(
    send_log_to_server,
    format="{message}",
    level="INFO"
)
```

3. **开始使用**

```python
logger.info("应用启动")
logger.debug("调试信息: PID=12345")
logger.error("发生错误，代码 500")
```

## 高级用法

### 批量发送日志

为了提高性能,你可以批量收集日志然后一次性发送:

```python
import requests
from collections import deque

class BatchLogSender:
    def __init__(self, batch_size=10, flush_interval=5):
        self.batch = deque()
        self.batch_size = batch_size
        self.flush_interval = flush_interval

    def add_log(self, message):
        self.batch.append(message)
        if len(self.batch) >= self.batch_size:
            self.flush()

    def flush(self):
        if self.batch:
            # 批量发送
            log_data = {"client_id": "my-app", "logs": list(self.batch)}
            requests.post("http://localhost:8000/logs", json=log_data)
            self.batch.clear()
```

### 添加错误重试

```python
def send_log_with_retry(message, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(LOG_SERVER_URL, json=log_data, timeout=1)
            if response.status_code == 200:
                return True
        except:
            if attempt == max_retries - 1:
                return False
            time.sleep(0.5)
    return False
```

### 异步发送

使用 `asyncio` 或线程池异步发送日志:

```python
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=2)

def async_send_log(message):
    executor.submit(send_log_to_server, message)

logger.add(async_send_log, format="{message}")
```

## 故障排查

### 日志没有显示在 Web 界面

1. 检查服务器是否运行:
```bash
curl http://localhost:8000/api/config
```

2. 检查 client_id 是否正确:
```bash
# 在 Web 界面的客户端下拉框中选择对应的 client_id
```

3. 检查浏览器控制台是否有 WebSocket 连接错误

### 发送日志时程序变慢

- 调整 `timeout` 参数 (默认 1 秒)
- 使用异步发送 (见上文)
- 批量发送日志

## 更多示例

### Flask 应用集成

```python
from flask import Flask, request
from loguru import logger
import sys

app = Flask(__name__)

logger.remove()
logger.add(sys.stderr, format="{time} | {level} | {message}")
logger.add(send_log_to_server, format="{message}")

@app.route("/")
def home():
    logger.info(f"访问首页 - IP: {request.remote_addr}")
    return "Hello World"
```

### FastAPI 应用集成

```python
from fastapi import FastAPI, Request
from loguru import logger
import sys

app = FastAPI()

logger.remove()
logger.add(sys.stderr, format="{time} | {level} | {message}")
logger.add(send_log_to_server, format="{message}")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    return response
```
