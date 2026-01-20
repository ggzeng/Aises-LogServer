## ADDED Requirements

### Requirement: 日志接收 API
系统 SHALL 提供 HTTP POST 端点 `/logs` 来接收 loguru 客户端发送的日志数据。

#### Scenario: 成功接收日志批次
- **WHEN** 客户端 POST 有效的 JSON 日志批次到 `/logs`
- **THEN** 系统返回 200 OK 状态码
- **AND** 系统解析并存储日志数据
- **AND** 系统通过 WebSocket 广播日志到所有连接的客户端

#### Scenario: 接收无效数据
- **WHEN** 客户端 POST 无效的 JSON 数据到 `/logs`
- **THEN** 系统返回 422 Unprocessable Entity 状态码
- **AND** 系统返回验证错误详情

#### Scenario: 接收符合预期格式的日志
- **WHEN** 客户端 POST 包含以下字段的日志:
  - `clientId`: 客户端唯一标识符
  - `logs`: 日志条目数组,每条包含 message、level、timestamp、logger、function、line 等字段
- **THEN** 系统成功解析并处理所有日志条目
- **AND** 系统按 clientId 分组存储日志

### Requirement: WebSocket 实时推送
系统 SHALL 提供 WebSocket 端点 `/ws` 来实时推送日志到 web 客户端。

#### Scenario: 客户端成功连接
- **WHEN** web 客户端连接到 `/ws`
- **THEN** 系统接受连接
- **AND** 系统将客户端添加到广播列表
- **AND** 系统发送连接成功消息

#### Scenario: 广播新日志
- **WHEN** 系统接收到新日志
- **THEN** 系统在 100ms 内通过 WebSocket 推送到所有连接的客户端
- **AND** 推送消息包含完整的日志数据 (clientId、level、message、timestamp 等)

#### Scenario: 客户端断开连接
- **WHEN** WebSocket 客户端断开连接
- **THEN** 系统从广播列表中移除该客户端
- **AND** 系统记录断开事件

### Requirement: 日志存储管理
系统 SHALL 在内存中维护多个客户端的日志数据,并限制每个客户端的日志数量。

#### Scenario: 存储新日志
- **WHEN** 系统接收到新日志
- **THEN** 系统按 clientId 分组存储日志
- **AND** 系统保留日志的完整元数据 (timestamp、level、message、logger、function、line、hostname)

#### Scenario: 日志数量超限
- **WHEN** 某个客户端的日志数量达到配置的上限
- **THEN** 系统删除最旧的日志
- **AND** 系统保持最多配置上限数量的日志
- **AND** 默认上限为 10000 条

#### Scenario: 查询指定客户端的日志
- **WHEN** web 客户端请求指定 clientId 的日志
- **THEN** 系统返回该客户端的所有日志 (最多配置上限数量)
- **AND** 系统按时间戳升序返回日志

### Requirement: 多客户端支持
系统 SHALL 支持同时接收和展示多个客户端的日志。

#### Scenario: 同时处理多个客户端的日志
- **WHEN** 系统同时接收到来自不同 clientId 的日志
- **THEN** 系统正确区分并分组存储日志
- **AND** 系统能够查询任意客户端的日志

#### Scenario: WebSocket 推送包含客户端信息
- **WHEN** 系统通过 WebSocket 推送日志
- **THEN** 推送消息包含 clientId 字段
- **AND** web 客户端能够根据 clientId 筛选和分类显示日志

### Requirement: 日志数据验证
系统 SHALL 使用 Pydantic 模型验证所有接收到的日志数据。

#### Scenario: 验证必需字段
- **WHEN** 接收到日志数据
- **THEN** 系统验证以下必需字段存在:
  - `clientId` (字符串)
  - `logs` (数组)
  - 每条日志包含 `message`、`level`、`timestamp`、`logger`、`function`、`line`
- **AND** 如果验证失败,系统返回 422 错误

#### Scenario: 验证日志级别
- **WHEN** 接收到日志数据
- **THEN** 系统验证 level 字段为以下值之一:
  - DEBUG、INFO、WARNING、ERROR、CRITICAL
- **AND** 如果 level 无效,系统返回 422 错误

### Requirement: 配置管理
系统 SHALL 支持通过 YAML 配置文件管理日志数量上限。

#### Scenario: 读取配置文件
- **WHEN** 系统启动时
- **THEN** 系统从 config.yaml 读取 max_logs_per_client 配置
- **AND** 如果配置文件不存在,系统使用默认值 10000
- **AND** 如果配置值无效,系统使用默认值 10000

#### Scenario: 更新配置
- **WHEN** 管理员通过 API 更新 max_logs_per_client 配置
- **THEN** 系统验证配置值 (范围: 1000-100000)
- **AND** 系统将新配置保存到 config.yaml
- **AND** 系统立即应用新的日志数量上限

#### Scenario: 配置 API 端点
- **WHEN** web 客户端 GET /config 请求配置
- **THEN** 系统返回当前配置 (JSON 格式)
- **WHEN** 管理员 PUT /config 更新配置
- **THEN** 系统更新配置并返回成功响应
