#!/bin/bash

echo "========================================="
echo "测试 clientId 字段名"
echo "========================================="
echo ""

echo "发送测试日志（使用 clientId）..."
echo ""

curl -X POST http://localhost:8000/logs \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "my-app-production",
    "hostname": "server-01",
    "timestamp": "2026-01-20 16:30:00.000",
    "messages": [
      {
        "timestamp": "2026-01-20 16:30:00.000",
        "level": "INFO",
        "message": "应用启动成功，监听端口 8080",
        "logger": "app",
        "function": "start",
        "line": 42
      },
      {
        "timestamp": "2026-01-20 16:30:01.000",
        "level": "INFO",
        "message": "数据库连接建立，连接池大小 10",
        "logger": "database",
        "function": "connect",
        "line": 15
      },
      {
        "timestamp": "2026-01-20 16:30:02.000",
        "level": "WARNING",
        "message": "内存使用率达到 75%，已用 3072 MB",
        "logger": "monitor",
        "function": "check_memory",
        "line": 88
      }
    ]
  }' | python -m json.tool

echo ""
echo "========================================="
echo "✓ 测试完成！"
echo "========================================="
echo ""
echo "访问地址: http://localhost:8000/static/index.html"
echo "客户端列表应该显示: my-app-production"
echo "========================================="
