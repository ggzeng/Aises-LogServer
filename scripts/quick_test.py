#!/usr/bin/env python3
import json

import requests

url = "http://localhost:8000/logs"
data = {
    "clientId": "my-app",
    "hostname": "my-host",
    "timestamp": "2026-01-20 12:00:00.000",
    "messages": [
        {
            "timestamp": "2026-01-20 12:00:00.123",
            "level": "INFO",
            "message": "这是一条测试日志，包含数字 12345",
            "logger": "my.module",
            "function": "my_function",
            "line": 42,
        }
    ],
}

print("发送测试日志...")
print(json.dumps(data, indent=2))

try:
    response = requests.post(url, json=data, timeout=5)
    print(f"\n状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print("\n✓ 日志已发送")
except Exception as e:
    print(f"\n✗ 错误: {e}")
