#!/usr/bin/env python3
"""测试新的消息格式"""

import json

import requests

# 服务器地址
SERVER_URL = "http://localhost:8000"

# 新格式的消息
new_format_message = {
    "clientId": "opsterminal-a1b2c3d4e5f6",
    "hostname": "DESKTOP-ABC123",
    "timestamp": "2026-01-20 12:00:03.333",
    "messages": [
        {
            "timestamp": "2026-01-20 12:00:02.222",
            "level": "WARNING",
            "message": "这是第二条警告，包含错误代码 500",
            "logger": "drivers.tonghuashun",
            "function": "connect",
            "line": 150,
            "extra": {"retry_count": 3},
        },
        {
            "timestamp": "2026-01-20 12:00:01.111",
            "level": "WARNING",
            "message": "这是第一条警告，端口 8080 被占用",
            "logger": "drivers.tonghuashun",
            "function": "connect",
            "line": 150,
            "extra": {"port": 8080},
        },
        {
            "timestamp": "2026-01-20 12:00:00.000",
            "level": "INFO",
            "message": "系统启动，PID: 12345，内存使用 2048 MB",
            "logger": "system",
            "function": "init",
            "line": 42,
            "extra": None,
        },
    ],
}

print("=" * 60)
print("测试新消息格式")
print("=" * 60)
print("\n发送的消息:")
print(json.dumps(new_format_message, indent=2, ensure_ascii=False))

try:
    response = requests.post(f"{SERVER_URL}/logs", json=new_format_message, timeout=5)

    print(f"\n状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        print("\n✓ 成功！")
        print(f"  - 已接收 {len(new_format_message['messages'])} 条日志")
        print(f"  - 客户端 ID: {result['client_id']}")
    else:
        print(f"错误: {response.text}")

except Exception as e:
    print(f"\n✗ 失败: {e}")

print("\n" + "=" * 60)
print("请查看浏览器 http://localhost:8000/static/index.html")
print("应该能看到新的日志显示！")
print("=" * 60)
