#!/usr/bin/env python3
"""测试客户端列表功能"""

import asyncio
import json

import httpx
import websockets


async def test_clients_list():
    """测试客户端列表获取"""

    print("=" * 60)
    print("测试客户端列表功能")
    print("=" * 60)

    # 1. 发送测试日志
    print("\n1. 发送测试日志...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/logs",
            json={
                "client_id": "test-client-123",
                "logs": [
                    {
                        "message": {
                            "timestamp": "2026-01-20 14:00:00.000",
                            "level": "INFO",
                            "message": "测试日志",
                            "name": "test",
                            "function": "test",
                            "line": 1,
                        },
                        "client_id": "test-client-123",
                        "timestamp": "2026-01-20T14:00:00.000000",
                        "level": "INFO",
                        "logger": "test",
                        "function": "test",
                        "line": 1,
                    }
                ],
            },
        )
        print(f"   响应: {response.json()}")

    # 2. 连接 WebSocket
    print("\n2. 连接 WebSocket...")
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as ws:
        print("   ✓ WebSocket 已连接")

        # 接收连接消息
        msg = await ws.recv()
        print(f"   收到: {msg}")

        # 3. 请求客户端列表
        print("\n3. 请求客户端列表...")
        await ws.send(json.dumps({"type": "get_clients"}))

        # 4. 接收客户端列表
        msg = await ws.recv()
        data = json.loads(msg)
        print(f"   收到: {json.dumps(data, indent=2, ensure_ascii=False)}")

        if data.get("type") == "clients_list":
            clients = data.get("clients", [])
            print(f"\n   客户端列表: {clients}")
            if len(clients) > 0:
                print(f"   ✓ 找到 {len(clients)} 个客户端")
            else:
                print("   ✗ 客户端列表为空")
        else:
            print("   ✗ 未收到 clients_list 消息")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(test_clients_list())
