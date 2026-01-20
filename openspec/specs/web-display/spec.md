# web-display Specification

## Purpose
TBD - created by archiving change add-initial-log-server. Update Purpose after archive.
## Requirements
### Requirement: Web 日志展示页面
系统 SHALL 提供一个基于 HTML 的日志展示页面,通过 GET / 端点访问。

#### Scenario: 访问日志页面
- **WHEN** 用户通过浏览器访问根路径 `/`
- **THEN** 系统返回 HTML 页面
- **AND** 页面包含日志显示区域和控制元素

#### Scenario: 页面自动连接 WebSocket
- **WHEN** 页面加载完成
- **THEN** JavaScript 自动连接到 WebSocket 端点 `/ws`
- **AND** 页面显示连接状态指示器

### Requirement: 彩色日志显示
系统 SHALL 根据日志级别使用不同颜色展示日志,并对日志消息中的数字进行着色。

#### Scenario: 日志级别配色
- **WHEN** 显示日志时
- **THEN** 系统使用以下颜色方案:
  - DEBUG: 灰色/蓝色 (#888 或 #3498db)
  - INFO: 绿色/白色 (#27ae60 或 #fff)
  - WARNING: 黄色/橙色 (#f39c12)
  - ERROR: 红色 (#e74c3c)
  - CRITICAL: 红色加粗/背景色 (#c0392b 背景)

#### Scenario: 数字彩色显示
- **WHEN** 日志消息中包含数字
- **THEN** 系统使用与日志级别颜色协调但不冲突的颜色高亮数字
- **AND** 数字颜色使用独立的颜色空间 (如紫色/青色) 确保可读性
- **AND** 数字颜色在不同日志级别下都保持清晰可见
- **EXAMPLE**: INFO 日志 (绿色) 中的数字使用紫色 (#9b59b6)

#### Scenario: 日志元素展示
- **WHEN** 显示每条日志
- **THEN** 系统包含以下元素:
  - 时间戳 (格式化显示)
  - 日志级别 (彩色标签)
  - Logger 名称
  - 函数名和行号
  - 日志消息内容 (包含彩色数字)
  - 客户端 ID (可选显示)

### Requirement: 自动滚动控制
系统 SHALL 提供开关控制是否自动滚动到最新日志。

#### Scenario: 自动滚动开启
- **WHEN** 自动滚动开关为开启状态
- **AND** 系统接收到新日志
- **THEN** 页面自动滚动到最新日志
- **AND** 最新日志始终可见

#### Scenario: 自动滚动关闭
- **WHEN** 用户关闭自动滚动开关
- **AND** 系统接收到新日志
- **THEN** 页面不自动滚动
- **AND** 用户可以手动滚动查看历史日志

#### Scenario: 切换滚动状态
- **WHEN** 用户点击自动滚动开关
- **THEN** 系统立即切换滚动状态
- **AND** 开关显示当前状态 (开启/关闭)

### Requirement: 客户端筛选
系统 SHALL 允许用户按 client_id 切换查看不同客户端的日志,切换相当于查看另一台客户端的日志视图。

#### Scenario: 切换到指定客户端
- **WHEN** 用户从下拉框选择特定的 client_id
- **THEN** 系统仅显示该客户端的日志
- **AND** 日志按时间戳升序排列
- **AND** 视图切换不显示其他客户端的日志
- **AND** 切换后滚动位置重置到最新日志

#### Scenario: 动态更新客户端列表
- **WHEN** 系统接收到新 client_id 的日志
- **THEN** 系统自动将该 client_id 添加到筛选下拉框
- **AND** 用户可以选择新客户端进行筛选

#### Scenario: 显示当前客户端信息
- **WHEN** 用户查看某个 client_id 的日志
- **THEN** 页面顶部显示当前查看的 client_id
- **AND** 显示该客户端的日志统计信息 (总数量、日志级别分布)

### Requirement: 多级筛选
系统 SHALL 支持在选定客户端后,进一步按日志级别和关键字筛选日志。

#### Scenario: 按日志级别筛选
- **WHEN** 用户在选定 client_id 后,勾选特定日志级别 (如 ERROR, WARNING)
- **THEN** 系统仅显示该客户端的这些级别日志
- **AND** 其他级别的日志被隐藏
- **AND** 筛选结果保持时间顺序

#### Scenario: 按关键字筛选
- **WHEN** 用户在搜索框输入关键字
- **THEN** 系统实时过滤当前客户端的日志
- **AND** 仅显示消息内容包含关键字的日志
- **AND** 关键字匹配不区分大小写
- **AND** 高亮显示匹配的关键字

#### Scenario: 组合筛选
- **WHEN** 用户同时使用日志级别和关键字筛选
- **THEN** 系统应用 AND 逻辑 (同时满足两个条件)
- **AND** 实时更新筛选结果
- **AND** 显示筛选结果数量 (如"显示 15/234 条日志")

#### Scenario: 清除筛选
- **WHEN** 用户点击"清除筛选"按钮
- **THEN** 系统清除所有级别和关键字筛选
- **AND** 显示当前客户端的所有日志

### Requirement: WebSocket 自动重连
系统 SHALL 在 WebSocket 连接断开时自动尝试重连。

#### Scenario: 连接断开时重连
- **WHEN** WebSocket 连接断开
- **THEN** 系统显示"连接断开,正在重连..."状态
- **AND** 系统在 3 秒后自动尝试重连
- **AND** 最多重连 5 次

#### Scenario: 重连成功
- **WHEN** 重连成功
- **THEN** 系统显示"已连接"状态
- **AND** 系统继续接收并显示新日志

#### Scenario: 重连失败
- **WHEN** 重连 5 次后仍失败
- **THEN** 系统显示"连接失败"状态
- **AND** 系统提供手动重连按钮

### Requirement: 日志清空功能
系统 SHALL 提供清空当前显示日志的按钮。

#### Scenario: 清空日志显示
- **WHEN** 用户点击"清空日志"按钮
- **THEN** 系统清空页面上显示的日志
- **AND** 服务器端存储的日志不受影响
- **AND** 新日志继续正常显示

### Requirement: 日志数量配置
系统 SHALL 允许用户在页面上设置每个客户端最多保留的日志数量,并持久化到后端配置文件。

#### Scenario: 显示当前配置
- **WHEN** 页面加载完成
- **THEN** 系统从后端 GET /config 获取当前配置
- **AND** 页面显示 max_logs_per_client 的当前值
- **AND** 显示配置值的输入框和保存按钮

#### Scenario: 更新日志数量配置
- **WHEN** 用户修改 max_logs_per_client 值并点击保存
- **THEN** 系统发送 PUT /config 请求到后端
- **AND** 后端验证值在 1000-100000 范围内
- **AND** 后端将新配置保存到 config.yaml
- **AND** 系统显示"配置已保存"提示
- **AND** 新配置立即生效

#### Scenario: 配置刷新后读取
- **WHEN** 用户刷新页面
- **THEN** 系统从后端重新读取配置
- **AND** 页面显示最新的配置值

#### Scenario: 配置验证错误
- **WHEN** 用户输入的配置值超出范围 (1000-100000)
- **THEN** 系统显示错误提示
- **AND** 系统不发送请求到后端
- **AND** 输入框显示错误状态

### Requirement: 响应式布局
系统 SHALL 提供响应式布局,适应不同屏幕尺寸。

#### Scenario: 桌面端显示
- **WHEN** 用户在桌面端 (宽度 >1024px) 访问
- **THEN** 系统显示完整布局
- **AND** 控制面板在页面顶部或侧边

#### Scenario: 移动端显示
- **WHEN** 用户在移动端 (宽度 <768px) 访问
- **THEN** 系统调整布局为垂直堆叠
- **AND** 控制面板在页面顶部
- **AND** 日志区域占据主要空间

