# Change: 初始化日志服务器

## Why
需要创建一个日志服务器来接收 loguru 客户端通过 API 发送的日志,并通过 web 界面实时展示,以便于监控和调试分布式应用程序的日志输出。

## What Changes
- **添加日志接收 API**: HTTP POST 端点接收 loguru 客户端发送的 JSON 格式日志批次
- **实现 WebSocket 推送**: 将接收到的日志实时推送到所有连接的 web 客户端
- **创建 Web 展示界面**: 提供一个基于浏览器的日志查看器,支持:
  - 按行滚动显示日志
  - 根据日志级别彩色输出 (DEBUG//INFO/WARNING/ERROR/CRITICAL)
  - 数字也以彩色显示，注意避免与日志级别颜色混迹而无法看清
  - 自动滚动开关
  - 按 clientId 筛选日志, 不同的clientId表示不同的客户端发来的日志。这些日志应该按时间顺序在一起展示，切换clientId相当于是查看另一台客户端上的日志。
  - 在通过 clientId 下还能根据日志级别，以及自定义关键字筛选日志
- **多客户端支持**: 维护多个客户端的日志流,允许用户切换查看。 一个clientId就相当于一个客户端。
- **内存管理**: 每个客户端默认最多保留 10000 条日志,超出后删除旧日志。最多保留的日志数可以再页面上设置，设置的结果后端保存到yaml配置文件中。页面刷新后从后端重新读取配置。
- **字段命名**: API 使用驼峰命名（clientId），内部使用下划线命名（client_id）

## Impact
- **影响规范**: 无 (这是初始实现)
- **影响代码**:
  - `main.py` - 应用入口和 FastAPI 实例
  - `models/` - Pydantic 数据模型 (LogEntry, LogBatch)
  - `routes/` - API 路由 (POST /logs) 和 WebSocket 端点 (/ws)
  - `services/` - 日志管理服务 (LogManager, WebSocketConnectionManager)
  - `static/` - 前端 HTML/CSS/JS 文件
- **新增依赖**: 无 (已在 pyproject.toml 中定义)

## 非功能需求
- **性能**: 支持 10+ 并发客户端,WebSocket 推送延迟 <100ms
- **兼容性**: 支持现代浏览器 (Chrome/Firefox/Safari)
- **可靠性**: WebSocket 断开时客户端自动重连
