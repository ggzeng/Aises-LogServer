#!/usr/bin/env python3
"""测试 clientId 字段名（驼峰命名）"""

import requests
import json

SERVER_URL = "http://localhost:8000"

# 使用 clientId 的新格式消息
test_message = {
    "clientId": "test-camel-case",
    "hostname": "MacBook-Pro",
    "timestamp": "2026-01-20 16:00:00.000",
    "messages": [
        {
            "timestamp": "2026-01-20 16:00:00.000",
            "level": "INFO",
            "message": "测试驼峰命名 clientId 字段",
            "logger": "test",
            "function": "main",
            "line": 10
        },
        {
            "timestamp": "2026-01-20 16:00:01.000",
            "level": "WARNING",
            "message": "警告信息，包含数字 12345",
            "logger": "test",
            "function": "check",
            "line": 25
        }
    ]
}

print("=" * 60)
print("测试 clientId 字段名（驼峰命名）")
print("=" * 60)
print("\n发送的消息:")
print(json.dumps(test_message, indent=2, ensure_ascii=False))

try:
    response = requests.post(
        f"{SERVER_URL}/logs",
        json=test_message,
        timeout=5
    )

    print(f"\n状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ 成功！")
        print(f"  - 已接收 {len(test_message['messages'])} 条日志")
        print(f"  - 客户端 ID: {result['client_id']}")
        print(f"\n响应内容:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"✗ 失败: {response.status_code}")
        print(f"  错误信息: {response.text}")

except Exception as e:
    print(f"\n✗ 异常: {e}")

print("\n" + "=" * 60)
print("请访问 http://localhost:8000/static/index.html 查看日志")
print("客户端列表应该显示: test-camel-case")
print("=" * 60)
