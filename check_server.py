#!/usr/bin/env python3
"""快速检查服务器配置"""

import sys
import asyncio
import websockets
import json

async def test_websocket():
    """测试WebSocket连接"""
    uri = "ws://localhost:8000/ws"
    print(f"连接到: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✓ WebSocket 连接成功!")
            
            # 接收欢迎消息
            message = await websocket.recv()
            print(f"✓ 收到消息: {message}")
            
            # 请求客户端列表
            await websocket.send(json.dumps({"type": "get_clients"}))
            response = await websocket.recv()
            print(f"✓ 客户端列表: {response}")
            
    except Exception as e:
        print(f"✗ WebSocket 连接失败: {e}")
        return False
    
    return True

async def test_http_api():
    """测试HTTP API"""
    import httpx
    
    try:
        # 测试根路径
        response = httpx.get("http://localhost:8000/")
        print(f"✓ 根路径: {response.status_code}")
        
        # 测试配置API
        response = httpx.get("http://localhost:8000/api/config")
        config = response.json()
        print(f"✓ 配置API: {config}")
        
        # 发送测试日志
        response = httpx.post("http://localhost:8000/logs", json={
            "client_id": "check-test",
            "logs": [{
                "message": {
                    "timestamp": "2026-01-20 13:00:00.000",
                    "level": "INFO",
                    "message": "检查脚本测试",
                    "name": "check",
                    "function": "test",
                    "line": 1
                },
                "client_id": "check-test",
                "timestamp": "2026-01-20T13:00:00.000000",
                "level": "INFO",
                "logger": "check",
                "function": "test",
                "line": 1
            }]
        })
        print(f"✓ 发送日志: {response.status_code} {response.json()}")
        
    except Exception as e:
        print(f"✗ HTTP API 测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=== 服务器健康检查 ===\n")
    
    print("1. 测试 HTTP API...")
    if asyncio.run(test_http_api()):
        print("\n2. 测试 WebSocket...")
        asyncio.run(test_websocket())
    else:
        print("\n✗ HTTP API 不可用，请确认服务器正在运行")
        sys.exit(1)
