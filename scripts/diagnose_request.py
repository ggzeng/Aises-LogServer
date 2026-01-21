#!/usr/bin/env python3
"""诊断工具：测试并显示详细的请求/响应信息"""

import json
import sys
from urllib.parse import urlparse

import requests


def diagnose_request(url: str = "http://localhost:8000/logs"):
    """发送测试请求并显示详细的诊断信息"""
    print("=" * 70)
    print("日志 API 诊断工具")
    print("=" * 70)
    print(f"目标 URL: {url}")
    print()

    # 解析 URL
    parsed = urlparse(url)
    print(f"协议: {parsed.scheme}")
    print(f"主机: {parsed.netloc}")
    print(f"路径: {parsed.path}")
    print()

    # 准备测试数据
    test_data = {
        "clientId": "diagnostic-client",
        "hostname": "test-machine",
        "timestamp": "2026-01-21 12:00:00.000",
        "messages": [
            {
                "timestamp": "2026-01-21 12:00:00.000",
                "level": "INFO",
                "message": "Diagnostic test message",
                "logger": "test",
                "function": "test",
                "line": 1,
            }
        ],
    }

    # 序列化为 JSON
    json_body = json.dumps(test_data, ensure_ascii=False)
    print(f"请求 JSON ({len(json_body)} 字节):")
    print(json_body[:200] + ("..." if len(json_body) > 200 else ""))
    print()

    # 准备请求头
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    print("发送请求...")
    print("-" * 70)

    try:
        # 发送请求，获取原始响应
        response = requests.post(url, data=json_body.encode("utf-8"), headers=headers, timeout=10)

        print(f"状态码: {response.status_code}")
        print(f"状态文本: {response.reason}")
        print("响应头:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        print()

        print(f"响应内容 ({len(response.content)} 字节):")
        try:
            json_response = response.json()
            print(json.dumps(json_response, indent=2, ensure_ascii=False))
        except ValueError:
            print(response.text[:500])

        print()
        print("-" * 70)

        # 分析结果
        if response.status_code == 200:
            print("✓ 成功！服务器正常处理请求")
            return 0
        elif response.status_code == 422:
            print("✗ 验证错误 - JSON 格式或字段有问题")
            print()
            print("可能的原因:")
            print("1. JSON 格式不正确")
            print("2. 缺少必需字段")
            print("3. 字段类型不匹配")
            print("4. 字段值超出允许范围")
            print()
            print("请检查响应中的 'error_summary' 字段获取详细信息")
            return 1
        elif response.status_code == 400:
            print("✗ 错误请求 - JSON 解析失败")
            print()
            print("可能的原因:")
            print("1. JSON 格式完全损坏")
            print("2. 字符编码问题")
            print("3. 换行符或特殊字符未正确转义")
            print()
            print("建议: 使用 Python 脚本或 PowerShell 而非 curl")
            return 1
        else:
            print(f"✗ 未知错误 (状态码: {response.status_code})")
            return 1

    except requests.exceptions.ConnectionError:
        print("✗ 连接失败")
        print()
        print("请检查:")
        print(f"1. 服务器是否在 {parsed.scheme}://{parsed.netloc} 运行")
        print("2. 防火墙是否允许连接")
        print("3. 网络连接是否正常")
        return 1
    except requests.exceptions.Timeout:
        print("✗ 请求超时")
        print()
        print("服务器响应时间过长，可能:")
        print("1. 服务器负载过高")
        print("2. 网络延迟过高")
        return 1
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        print()
        print(f"错误类型: {type(e).__name__}")
        import traceback

        print("\n详细错误信息:")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/logs"
    sys.exit(diagnose_request(url))
