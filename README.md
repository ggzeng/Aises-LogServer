# Log Server

实时日志服务器 - 接收 Loguru 客户端日志并通过 Web 界面实时展示

## 功能特性

### 核心功能
- ✅ **HTTP API 接收日志** - 接收 Loguru 客户端 POST 的 JSON 格式日志
- ✅ **WebSocket 实时推送** - 毫秒级延迟推送日志到所有 Web 客户端
- ✅ **多客户端支持** - 同时接收和展示多个客户端的日志
- ✅ **内存管理** - 每个客户端可配置日志数量上限 (默认 10000 条)
- ✅ **数据验证** - Pydantic 模型验证所有日志数据

### Web 界面
- ✅ **彩色日志显示** - 5 种日志级别不同颜色 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- ✅ **数字高亮** - 日志中的数字使用独立颜色高亮显示
- ✅ **客户端切换** - 切换查看不同客户端的日志视图
- ✅ **多级筛选** - 按日志级别、关键字组合筛选
- ✅ **自动滚动** - 可选的自动滚动到最新日志
- ✅ **实时统计** - 显示客户端日志统计信息
- ✅ **WebSocket 自动重连** - 连接断开时自动重连 (最多 5 次)

### 配置管理
- ✅ **YAML 配置文件** - `config.yaml` 管理所有配置
- ✅ **API 配置管理** - GET/PUT `/api/config` 动态配置
- ✅ **配置验证** - 自动验证配置范围
- ✅ **热重载** - 配置变更立即生效

## 快速开始

### 方式一：使用 Makefile (推荐)

项目提供了 Makefile 来简化常用操作：

#### 安装与启动

```bash
# 查看所有可用命令
make help

# 安装项目依赖
make install

# 启动开发服务器（支持热重载）
make dev

# 启动生产服务器
make run
```

#### 后台运行

生产环境建议使用后台运行模式：

```bash
# 后台启动服务器（日志保存到 logs/ 目录）
make start

# 查看实时日志
make logs

# 停止后台服务器
make stop

# 重启服务器
make restart
```

**日志说明**：
- 日志文件保存在 `logs/` 目录下
- 文件命名格式：`server-YYYYMMDD-HHMMSS.log`
- 使用 `make logs` 可以实时查看最新日志
- `logs/` 目录已被 git 排除，不会被提交到版本控制

#### 测试与代码质量

```bash
# 运行所有测试
make test

# 运行测试并生成覆盖率报告
make test-cov

# 格式化代码
make format

# 运行代码检查
make lint

# 运行所有检查（代码检查 + 测试 + 覆盖率）
make check
```

#### 其他常用命令

```bash
# 查看项目信息
make info

# 查看依赖列表
make deps

# 清理临时文件
make clean

# 深度清理（包括虚拟环境）
make clean-all
```

### 方式二：使用独立脚本

项目提供了 `server.sh` 脚本，功能与 Makefile 的后台运行命令一致：

```bash
# 查看帮助信息
./server.sh help

# 后台启动服务器
./server.sh start

# 查看服务器运行状态
./server.sh status

# 查看实时日志
./server.sh logs

# 停止服务器
./server.sh stop

# 重启服务器
./server.sh restart
```

**自定义配置**：
```bash
# 指定监听地址和端口
HOST=127.0.0.1 PORT=9000 ./server.sh start
```

### 方式三：手动操作

#### 1. 安装依赖

```bash
# 使用 uv (推荐)
uv sync

# 或使用 pip
pip install fastapi uvicorn[standard] loguru pydantic websockets pyyaml
```

#### 2. 启动服务器

```bash
# 方式 1: 直接运行
python main.py

# 方式 2: 使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 访问 Web 界面

打开浏览器访问:
```
http://localhost:8000/static/index.html
```

#### 4. 发送日志

使用 curl 测试:
```bash
curl -X POST http://localhost:8000/logs \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "my-app",
    "hostname": "my-host",
    "timestamp": "2026-01-20 12:00:00.000",
    "messages": [
      {
        "timestamp": "2026-01-20 12:00:00.123",
        "level": "INFO",
        "message": "这是一条测试日志，包含数字 12345",
        "logger": "my.module",
        "function": "my_function",
        "line": 42
      }
    ]
  }'
```

或使用 Python 客户端 (见下文)

## API 文档

详细的 API 文档请访问: http://localhost:8000/docs

### 主要端点

- `POST /logs` - 接收日志批次
- `WebSocket /ws` - 实时日志推送
- `GET /api/config` - 获取配置
- `PUT /api/config` - 更新配置

### API 格式说明

#### POST /logs 请求格式

```json
{
  "clientId": "string (必需)",
  "hostname": "string (可选)",
  "timestamp": "string (必需)",
  "messages": [
    {
      "timestamp": "string (必需)",
      "level": "DEBUG|INFO|WARNING|ERROR|CRITICAL (必需)",
      "message": "string (必需)",
      "logger": "string (必需)",
      "function": "string (必需)",
      "line": "integer (必需)"
    }
  ]
}
```

#### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `clientId` | string | ✅ | 客户端唯一标识符（驼峰命名）|
| `hostname` | string | ❌ | 客户端主机名 |
| `timestamp` | string | ✅ | 日志批次发送时间 |
| `messages` | array | ✅ | 日志消息数组 |

**注意**: `clientId` 使用驼峰命名（camelCase），而不是下划线命名（snake_case）。

## 项目结构

```
log-server/
├── main.py                   # FastAPI 应用入口
├── Makefile                  # 项目管理命令
├── config.yaml               # 配置文件
├── models/                   # Pydantic 数据模型
│   └── log_models.py
├── routes/                   # API 路由
│   ├── log_routes.py        # 日志 API + WebSocket
│   └── config_routes.py     # 配置 API
├── services/                 # 业务逻辑
│   ├── config_service.py    # 配置管理
│   ├── log_manager.py       # 日志管理
│   └── connection_manager.py # WebSocket 管理
├── tests/                    # 测试文件
│   ├── test_log_api.py      # 日志 API 测试
│   └── test_config_api.py   # 配置 API 测试
└── static/                   # 前端静态文件
    ├── index.html           # 主页面
    ├── style.css            # 样式表
    └── app.js               # WebSocket 客户端
```

## 技术栈

- **后端**: Python 3.11+ / FastAPI / Uvicorn
- **WebSocket**: websockets 16.0+
- **数据验证**: Pydantic v2.12+
- **日志**: Loguru
- **配置**: YAML (pyyaml)
- **前端**: 原生 HTML/CSS/JavaScript
- **包管理**: uv
- **构建工具**: Make
- **测试**: pytest / pytest-cov

## 性能

- 支持 10+ 并发客户端
- WebSocket 推送延迟 < 100ms
- 每客户端最多 100,000 条日志 (可配置)
- 内存占用: 约 50-100MB (取决于日志数量)

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request!
