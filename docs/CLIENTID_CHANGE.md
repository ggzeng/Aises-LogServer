# 字段名变更文档

## 变更内容

将 API 接收的日志消息中的 `client_id` 字段改为 `clientId`（驼峰命名）。

**变更时间**: 2026-01-20
**影响范围**: 破坏性变更

---

## 字段名对比

### API 接收格式（外部）

#### ❌ 旧格式（已弃用）
```json
{
  "client_id": "app-123",
  "hostname": "server-01",
  "timestamp": "2026-01-20 12:00:00.000",
  "messages": [...]
}
```

#### ✅ 新格式（当前使用）
```json
{
  "clientId": "app-123",
  "hostname": "server-01",
  "timestamp": "2026-01-20 12:00:00.000",
  "messages": [...]
}
```

### WebSocket 广播格式（内部）

WebSocket 推送的消息格式保持不变（下划线命名）：

```json
{
  "type": "log",
  "data": {
    "timestamp": "...",
    "level": "INFO",
    "message": "...",
    "logger": "...",
    "function": "...",
    "line": 123,
    "client_id": "app-123",
    "hostname": "server-01"
  }
}
```

---

## 已更新的文件

### 后端代码
- ✅ `models/log_models.py` - `LogBatch.clientId`
- ✅ `routes/log_routes.py` - 使用 `batch.clientId`

### 测试和示例
- ✅ `tests/test_log_api.py` - 所有测试用例
- ✅ `examples/loguru_client.py` - Loguru 客户端
- ✅ `test_new_format.py` - 测试脚本

### 文档
- ✅ `README.md` - 主文档，添加 API 格式说明
- ✅ `examples/README.md` - 客户端示例文档
- ✅ `openspec/project.md` - 项目规范文档
- ✅ `openspec/changes/add-initial-log-server/proposal.md` - 变更提案
- ✅ `openspec/changes/add-initial-log-server/specs/log-ingestion/spec.md` - 规范文档

### 新增测试脚本
- ✅ `test_clientid.py` - Python 测试脚本
- ✅ `test_clientid.sh` - Bash 测试脚本

---

## 测试验证

### 单元测试
```bash
✅ 15/15 测试全部通过
```

### API 测试命令

```bash
# 方法 1: 使用 curl
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

# 方法 2: 使用 Python 脚本
python test_clientid.py

# 方法 3: 使用 Loguru 客户端
python examples/loguru_client.py test-instance
```

---

## 迁移指南

### 对于客户端开发者

如果你有代码发送日志到服务器，请按以下步骤迁移：

#### 步骤 1: 更新字段名

将 `client_id` 改为 `clientId`：

```python
# ❌ 旧代码
log_data = {
    "client_id": "my-app",
    "hostname": "server-01",
    "timestamp": "2026-01-20 12:00:00.000",
    "messages": [...]
}

# ✅ 新代码
log_data = {
    "clientId": "my-app",  # 改为驼峰命名
    "hostname": "server-01",
    "timestamp": "2026-01-20 12:00:00.000",
    "messages": [...]
}
```

#### 步骤 2: 测试验证

1. 更新客户端代码
2. 发送测试日志
3. 检查服务器是否正确接收
4. 在 Web 界面验证日志显示

#### 步骤 3: 部署

- 确保所有客户端已更新
- 在测试环境验证
- 部署到生产环境

---

## 字段命名规范总结

| 上下文 | 字段名 | 命名风格 | 说明 |
|--------|--------|----------|------|
| **API 接收** | `clientId` | camelCase | 外部 API 接口 |
| **WebSocket 广播** | `client_id` | snake_case | 内部使用，前端引用 |
| **内部存储** | `client_id` | snake_case | 数据库和存储层 |
| **前端 JavaScript** | `client_id` | snake_case | 前端代码中引用 |

---

## 常见问题

### Q: 为什么要使用驼峰命名？
**A**:
- 与现代前端框架（JavaScript/TypeScript）保持一致
- JSON API 的常见惯例
- 更好的跨语言兼容性

### Q: 内部为什么还用下划线？
**A**:
- Python 代码风格指南（PEP 8）推荐使用下划线
- 数据库字段命名惯例
- 保持内部代码一致性

### Q: 旧格式还能用吗？
**A**: 不能。这是破坏性变更，所有客户端必须更新代码。

### Q: 如何验证字段名是否正确？
**A**:
- 查看响应中的 `client_id` 字段
- 检查客户端列表是否显示
- 运行测试脚本验证

---

## 相关文档

- [README.md](../README.md) - 主文档
- [examples/README.md](examples/README.md) - 客户端集成指南
- [openspec/project.md](../../openspec/project.md) - 项目规范

---

**更新日期**: 2026-01-20
**版本**: 1.0.0
