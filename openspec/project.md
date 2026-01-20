# Project Context

## Purpose
本程序来接收 loguru 通过api发过来的日志，并通过web实时滚动，以行，以彩色的方式来展示日志内容。是否实施滚动到最新与开关控制，如果同时接收到不同客户端发过来的日志，网页上应该需要能根据客户端进行分类选择。接收到的body为json格式，示例内如如下：
```json
{
  "client_id": "opsterminal-a1b2c3d4e5f6",
  "logs": [
    {
      "message": {
        "timestamp": "2026-01-20 12:00:00.123",
        "level": "WARNING",
        "message": "这是一条警告",
        "name": "drivers.tonghuashun",
        "function": "connect",
        "line": 150,
        "extra": {...}
      },
      "client_id": "opsterminal-a1b2c3d4e5f6",
      "hostname": "DESKTOP-ABC123",
      "timestamp": "2026-01-20T12:00:00.123456",
      "level": "WARNING",
      "logger": "drivers.tonghuashun",
      "function": "connect",
      "line": 150
    }
  ]
}
```


## Tech Stack
- **语言**: Python 3.11+
- **Web 框架**: FastAPI (异步 ASGI 框架)
- **日志库**: Loguru (接收端) + client 端通过 API 发送
- **数据验证**: Pydantic v2.12+
- **服务器**: Uvicorn (标准配置,含 WebSocket 支持)
- **WebSocket**: websockets 16.0+
- **包管理**: uv (现代 Python 包管理器)
- **协议**: HTTP/HTTPS + WebSocket (实时日志推送)

## Project Conventions

### Code Style
- **格式化工具**: Black (默认配置,自动格式化)
- **代码规范**: PEP 8
- **命名约定**:
  - 变量/函数: `snake_case`
  - 类: `PascalCase`
  - 常量: `UPPER_SNAKE_CASE`
  - 私有成员: `_leading_underscore`
- **导入顺序**: stdlib → 第三方 → 本地 (每组空行分隔)
- **类型注解**: 所有公共函数必须包含类型提示,使用 Pydantic 模型进行数据验证

### Architecture Patterns
- **架构模式**: MVC/MVVM
  - **Model**: Pydantic 模型 (`models/`),定义数据结构和验证规则
  - **View**: FastAPI 路由 + WebSocket 端点 (`routes/` 或 `views/`)
  - **Controller/ViewModel**: 业务逻辑层 (`services/` 或 `controllers/`)
- **目录结构**:
  ```
  ├── models/         # Pydantic 数据模型
  ├── routes/         # API 路由和 WebSocket 端点
  ├── services/       # 业务逻辑 (日志处理、客户端管理等)
  ├── static/         # 前端静态文件 (HTML/CSS/JS)
  └── main.py         # 应用入口
  ```
- **关注点分离**: 路由层不包含业务逻辑,仅处理请求/响应;业务逻辑在 services 层
- **依赖注入**: 使用 FastAPI 的 Depends 进行依赖管理

### Testing Strategy
- **测试框架**: pytest
- **测试范围**: 核心功能测试
  - API 端点测试 (日志接收)
  - WebSocket 连接和消息推送测试
  - 多客户端分类和过滤逻辑测试
  - 边界情况和错误处理测试
- **测试文件**: 命名为 `test_*.py` 或 `*_test.py`,放在对应模块旁或 `tests/` 目录
- **覆盖率目标**: 核心业务逻辑 >70%,整体不强制追求高覆盖率

### Git Workflow
- **提交规范**: Conventional Commits
  ```
  feat: 添加新功能
  fix: 修复 bug
  docs: 文档更新
  style: 代码格式调整 (不影响功能)
  refactor: 重构 (不添加新功能,不修复 bug)
  test: 添加或修改测试
  chore: 构建/工具链变更
  ```
- **提交信息格式**:
  ```
  <type>: <简短描述>

  <详细描述 (可选)>

  <相关 issue 或 refs (可选)>
  ```
- **分支策略**:
  - `main`: 主分支,稳定版本
  - `feature/*`: 功能开发分支
  - `fix/*`: bug 修复分支
- **合并策略**: 使用 squash merge 保持历史清晰

## Domain Context
- **日志来源**: Loguru 客户端通过 HTTP API 发送日志批次
- **客户端标识**: 使用 `clientId` 字段区分不同的日志来源（驼峰命名）
- **日志级别**: DEBUG, INFO, WARNING, ERROR, CRITICAL (需要彩色显示)
- **实时性要求**: WebSocket 推送新日志,延迟 <100ms
- **展示需求**:
  - 按行滚动显示
  - 彩色输出 (根据日志级别)
  - 可切换自动滚动到最新
  - 支持按客户端筛选
- **字段命名规范**:
  - API 接口: 驼峰命名（`clientId`）
  - 内部处理: 下划线命名（`client_id`）

## Important Constraints
- **性能**: 支持至少 10 个并发客户端同时发送日志
- **内存**: 服务器端不持久化日志,仅存储当前会话的日志 (最多保留 10000 条/客户端)
- **实时性**: WebSocket 连接断开时,客户端应支持自动重连
- **安全性**:
  - 不暴露敏感信息
  - 考虑添加 API 认证 (未来需求)
- **浏览器兼容**: 支持现代浏览器 (Chrome/Firefox/Safari 最新版本)

## External Dependencies
- **Loguru 客户端**: 依赖外部 Python 应用正确配置和发送日志
- **WebSocket 客户端**: 前端 JavaScript 需实现 WebSocket 连接和重连逻辑
- **网络**: 要求稳定的网络连接以支持实时推送
