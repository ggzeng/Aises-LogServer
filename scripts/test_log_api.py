#!/usr/bin/env python3
"""测试日志 API 的脚本"""

import json
import sys

import requests


def test_log_api(server_url: str = "http://localhost:8000"):
    """测试日志接收 API"""
    # 构建测试数据
    test_data = {
        "clientId": "test-client-windows",
        "hostname": "windows-pc",
        "timestamp": "2026-01-20 12:00:00.000",
        "messages": [
            {
                "timestamp": "2026-01-20 12:00:00.123",
                "level": "INFO",
                "message": "这是一条来自 Windows 的测试日志，包含数字 12345",
                "logger": "my.module",
                "function": "my_function",
                "line": 42,
            },
            {
                "timestamp": "2026-01-20 12:00:01.456",
                "level": "WARNING",
                "message": "这是一条警告日志",
                "logger": "my.module",
                "function": "test_function",
                "line": 100,
            },
            {
                "timestamp": "2026-01-20 12:00:02.789",
                "level": "ERROR",
                "message": "这是一条错误日志",
                "logger": "error.module",
                "function": "error_function",
                "line": 200,
            },
        ],
    }

    # 发送请求
    url = f"{server_url}/logs"
    print(f"发送请求到: {url}")
    print("测试数据:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    print("-" * 60)

    try:
        response = requests.post(
            url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        print(f"响应状态码: {response.status_code}")
        print("响应内容:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        if response.status_code == 200:
            print("\n✓ 测试成功！")
            return 0
        else:
            print(f"\n✗ 测试失败，状态码: {response.status_code}")
            return 1

    except requests.exceptions.ConnectionError:
        print(f"\n✗ 连接失败，请确保服务器正在运行: {server_url}")
        return 1
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        return 1


if __name__ == "__main__":
    # 从命令行参数获取服务器 URL
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    sys.exit(test_log_api(server_url))
