# 字段名变更说明

## 变更内容

将日志消息中的 `client_id` 字段改为 `clientId`（驼峰命名）。

## 影响范围

### API 接口

#### 接收日志 (POST /logs)

**旧格式:**
```json
{
  "client_id": "app-123",
  "hostname": "server-01",
  "timestamp": "2026-01-20 12:00:00.000",
  "messages": [...]
}
```

**新格式:** ✅
```json
{
  "clientId": "app-123",
  "hostname": "server-01",
  "timestamp": "2026-01-20 12:00:00.000",
  "messages": [...]
}
```

### WebSocket 消息

WebSocket 广播的消息格式中 `client_id` 字段保持不变（下划线命名），因为：
- 前端 JavaScript 代码使用 `client_id`
- 保持内部一致性

```json
{
  "type": "log",
  "data": {...},
  "client_id": "app-123"
}
```

### 已更新的文件

#### 后端
- ✅ `models/log_models.py` - `LogBatch.clientId`
- ✅ `routes/log_routes.py` - 使用 `batch.clientId`

#### 测试和示例
- ✅ `tests/test_log_api.py` - 所有测试用例
- ✅ `examples/loguru_client.py` - 客户端示例
- ✅ `test_new_format.py` - 测试脚本

#### 测试脚本
- ✅ `test_clientid.py` - Python 测试脚本
- ✅ `test_clientid.sh` - Bash 测试脚本

## 测试方法

### 方法 1: 使用 Python 脚本
```bash
python test_clientid.py
```

### 方法 2: 使用 curl
```bash
bash test_clientid.sh
```

### 方法 3: 直接使用 curl
```bash
curl -X POST http://localhost:8000/logs \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "test-app",
    "hostname": "localhost",
    "timestamp": "2026-01-20 16:00:00.000",
    "messages": [{
      "timestamp": "2026-01-20 16:00:00.000",
      "level": "INFO",
      "message": "测试消息",
      "logger": "test",
      "function": "test",
      "line": 1
    }]
  }'
```

### 方法 4: 使用 Loguru 客户端
```bash
python examples/loguru_client.py test-instance
```

## 验证结果

- ✅ 所有单元测试通过 (9/9)
- ✅ API 接收正常
- ✅ 日志存储正常
- ✅ WebSocket 广播正常
- ✅ 客户端列表更新正常

## 注意事项

1. **外部调用方需要更新**: 所有发送日志到服务器的客户端需要将 `client_id` 改为 `clientId`
2. **内部保持不变**: WebSocket 消息和存储结构仍使用 `client_id`
3. **向后兼容性**: 这是破坏性变更，旧格式将无法使用
