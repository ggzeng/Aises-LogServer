#!/bin/bash

echo "=== 测试日志服务器 ==="
echo ""

# 检查Python环境
echo "1. 检查Python环境..."
python --version

# 检查依赖
echo ""
echo "2. 检查依赖..."
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import uvicorn; print(f'Uvicorn: {uvicorn.__version__}')"

# 启动服务器
echo ""
echo "3. 启动服务器..."
python main.py &
SERVER_PID=$!
echo "服务器 PID: $SERVER_PID"

# 等待服务器启动
sleep 3

# 测试API
echo ""
echo "4. 测试API..."
curl -s http://localhost:8000/ | python -m json.tool

# 测试配置API
echo ""
echo "5. 测试配置API..."
curl -s http://localhost:8000/api/config | python -m json.tool

# 发送测试日志
echo ""
echo "6. 发送测试日志..."
curl -s -X POST http://localhost:8000/logs \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "test-frontend",
    "logs": [{
      "message": {
        "timestamp": "2026-01-20 13:00:00.000",
        "level": "INFO",
        "message": "前端测试日志，数字 12345",
        "name": "test",
        "function": "test",
        "line": 1
      },
      "client_id": "test-frontend",
      "timestamp": "2026-01-20T13:00:00.000000",
      "level": "INFO",
      "logger": "test",
      "function": "test",
      "line": 1
    }]
  }' | python -m json.tool

echo ""
echo "=== 服务器正在运行，PID: $SERVER_PID ==="
echo "请访问: http://localhost:8000/static/index.html"
echo ""
echo "按 Ctrl+C 停止服务器"

# 保持运行
wait $SERVER_PID
