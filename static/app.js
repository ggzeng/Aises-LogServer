// Log Server - 实时日志查看器

class LogServer {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.currentClientId = '';
        this.logs = [];
        this.clients = [];
        this.autoScroll = true;
        this.filters = {
            levels: ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            keyword: ''
        };
        this.logCounter = 0; // 用于生成唯一日志ID的计数器

        this.init();
    }

    init() {
        this.connectWebSocket();
        this.setupEventListeners();
        this.loadConfig();
        this.setupConfigPanel();
    }

    // WebSocket 连接
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket 已连接');
            this.updateConnectionStatus('connected');
            this.reconnectAttempts = 0;

            // 请求客户端列表
            this.send({ type: 'get_clients' });
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (e) {
                console.error('解析消息失败:', e);
            }
        };

        this.ws.onclose = () => {
            console.log('WebSocket 连接已关闭');
            this.updateConnectionStatus('disconnected');
            this.attemptReconnect();
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket 错误:', error);
        };
    }

    // WebSocket 重连
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            this.updateConnectionStatus('reconnecting');

            setTimeout(() => {
                this.connectWebSocket();
            }, this.reconnectDelay);
        } else {
            console.log('重连失败，已达到最大尝试次数');
            this.updateConnectionStatus('failed');
        }
    }

    // 发送消息
    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }

    // 处理服务器消息
    handleMessage(data) {
        switch (data.type) {
            case 'connected':
                console.log('已连接到服务器');
                break;

            case 'clients_list':
                this.updateClientsList(data.clients);
                break;

            case 'log':
                this.addLog(data.data, data.client_id);
                break;

            case 'logs_data':
                // 为历史日志生成唯一ID（反转顺序，让最新的在前面）
                this.logs = data.logs.reverse().map(log => ({
                    ...log,
                    _id: ++this.logCounter
                }));
                this.renderLogs();
                break;

            case 'client_stats':
                this.updateStats(data.stats);
                break;

            default:
                console.log('未知消息类型:', data.type);
        }
    }

    // 添加日志
    addLog(log, clientId) {
        // 如果当前选择了客户端，且日志不属于该客户端，则不显示
        if (this.currentClientId && this.currentClientId !== clientId) {
            return;
        }

        // 为每条日志生成唯一ID（使用递增计数器）
        const logId = ++this.logCounter;

        // 将新日志添加到数组开头，让最新的日志在最上面
        this.logs.unshift({ ...log, client_id: clientId, _id: logId });
        this.renderLogs();

        // 如果是新客户端，更新客户端列表
        if (!this.clients.includes(clientId)) {
            this.clients.push(clientId);
            this.updateClientsListUI();
        }

        // 自动滚动到顶部
        if (this.autoScroll) {
            this.scrollToTop();
        }
    }

    // 渲染日志
    renderLogs() {
        const container = document.getElementById('logContainer');

        if (this.logs.length === 0) {
            container.innerHTML = '<div class="log-empty">暂无日志</div>';
            return;
        }

        const html = this.logs.map(log => this.formatLog(log)).join('');
        container.innerHTML = html;

        // 应用筛选
        this.applyFilters();

        // 更新筛选统计
        this.updateFilterStats();
    }

    // 格式化日志条目
    formatLog(log) {
        const level = log.level || 'INFO';
        const timestamp = this.formatTimestamp(log.timestamp);
        const location = `${log.logger}:${log.function}:${log.line}`;
        const message = this.highlightNumbers(log.message);

        return `
            <div class="log-entry" data-level="${level}" data-client="${log.client_id}">
                <span class="log-timestamp">${timestamp}</span>
                <span class="log-level ${level}">${level}</span>
                <span class="log-location">[${location}]</span>
                <span class="log-message">${this.highlightKeyword(message)}</span>
            </div>
        `;
    }

    // 格式化时间戳
    formatTimestamp(timestamp) {
        try {
            const date = new Date(timestamp);
            return date.toLocaleTimeString('zh-CN', { hour12: false }) + '.' +
                   String(date.getMilliseconds()).padStart(3, '0');
        } catch {
            return timestamp;
        }
    }

    // 高亮数字
    highlightNumbers(text) {
        return text.replace(/\b(\d+)\b/g, '<span class="log-number">$1</span>');
    }

    // 高亮关键字
    highlightKeyword(text) {
        if (!this.filters.keyword) {
            return text;
        }
        const regex = new RegExp(`(${this.escapeRegex(this.filters.keyword)})`, 'gi');
        return text.replace(regex, '<span class="log-highlight">$1</span>');
    }

    // 转义正则表达式特殊字符
    escapeRegex(text) {
        return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // 更新客户端列表
    updateClientsList(clients) {
        this.clients = clients;
        this.updateClientsListUI();
    }

    updateClientsListUI() {
        const select = document.getElementById('clientSelect');

        // 保存当前选择
        const currentValue = select.value;

        // 清空并重新填充
        select.innerHTML = '<option value="">所有客户端</option>';
        this.clients.forEach(client => {
            const option = document.createElement('option');
            option.value = client;
            option.textContent = client;
            select.appendChild(option);
        });

        // 恢复选择
        if (currentValue && this.clients.includes(currentValue)) {
            select.value = currentValue;
        }
    }

    // 选择客户端
    selectClient(clientId) {
        this.currentClientId = clientId;

        if (clientId) {
            // 请求该客户端的日志
            this.send({ type: 'get_logs', client_id: clientId });
            this.logs = []; // 清空当前显示
            document.getElementById('currentClient').textContent = `当前客户端: ${clientId}`;
            document.getElementById('clientInfo').style.display = 'flex';
        } else {
            this.logs = [];
            this.renderLogs();
            document.getElementById('currentClient').textContent = '当前客户端: -';
            document.getElementById('clientInfo').style.display = 'none';
        }
    }

    // 更新统计信息
    updateStats(stats) {
        const statsText = `日志统计: 总计 ${stats.total} (DEBUG: ${stats.DEBUG}, INFO: ${stats.INFO}, WARNING: ${stats.WARNING}, ERROR: ${stats.ERROR}, CRITICAL: ${stats.CRITICAL})`;
        document.getElementById('logStats').textContent = statsText;
    }

    // 更新筛选统计
    updateFilterStats() {
        const total = this.logs.length;
        const visible = document.querySelectorAll('.log-entry:not(.hidden)').length;
        document.getElementById('filterStats').textContent = `显示: ${visible}/${total}`;
    }

    // 应用筛选
    applyFilters() {
        const entries = document.querySelectorAll('.log-entry');

        entries.forEach(entry => {
            const level = entry.dataset.level;
            const message = entry.querySelector('.log-message').textContent;

            // 级别筛选
            const levelMatch = this.filters.levels.includes(level);

            // 关键字筛选
            const keywordMatch = !this.filters.keyword ||
                                message.toLowerCase().includes(this.filters.keyword.toLowerCase());

            if (levelMatch && keywordMatch) {
                entry.classList.remove('hidden');
            } else {
                entry.classList.add('hidden');
            }
        });

        this.updateFilterStats();
    }

    // 更新连接状态
    updateConnectionStatus(status) {
        const statusEl = document.getElementById('connectionStatus');
        const dot = statusEl.querySelector('.status-dot');
        const text = statusEl.querySelector('.status-text');

        dot.className = 'status-dot';
        text.textContent = '';

        switch (status) {
            case 'connected':
                dot.classList.add('connected');
                text.textContent = '已连接';
                break;
            case 'disconnected':
                dot.classList.add('disconnected');
                text.textContent = '连接断开';
                break;
            case 'reconnecting':
                text.textContent = '重连中...';
                break;
            case 'failed':
                dot.classList.add('disconnected');
                text.textContent = '连接失败';
                break;
        }
    }

    // 滚动到顶部
    scrollToTop() {
        const container = document.getElementById('logContainer');
        container.scrollTop = 0;
    }

    // 滚动到底部（保留方法用于其他可能的需求）
    scrollToBottom() {
        const container = document.getElementById('logContainer');
        container.scrollTop = container.scrollHeight;
    }

    // 清空日志
    clearLogs() {
        this.logs = [];
        this.renderLogs();
    }

    // 加载配置
    async loadConfig() {
        try {
            const response = await fetch('/api/config');
            const config = await response.json();
            console.log('配置已加载:', config);
        } catch (error) {
            console.error('加载配置失败:', error);
        }
    }

    // 设置事件监听器
    setupEventListeners() {
        // 客户端选择
        document.getElementById('clientSelect').addEventListener('change', (e) => {
            this.selectClient(e.target.value);
        });

        // 日志级别筛选
        document.querySelectorAll('.level-filters input').forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.filters.levels = Array.from(document.querySelectorAll('.level-filters input:checked'))
                    .map(cb => cb.value);
                this.applyFilters();
            });
        });

        // 关键字搜索
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.filters.keyword = e.target.value;
            this.applyFilters();
        });

        // 自动滚动开关
        document.getElementById('autoScroll').addEventListener('change', (e) => {
            this.autoScroll = e.target.checked;
        });

        // 清空按钮
        document.getElementById('clearBtn').addEventListener('click', () => {
            this.clearLogs();
        });
    }

    // ============ 配置面板管理 ============

    setupConfigPanel() {
        // 打开配置面板
        document.getElementById('configBtn').addEventListener('click', () => {
            this.openConfigPanel();
        });

        // 关闭配置面板
        document.getElementById('closeConfigBtn').addEventListener('click', () => {
            this.closeConfigPanel();
        });

        document.getElementById('configOverlay').addEventListener('click', () => {
            this.closeConfigPanel();
        });

        // 保存配置
        document.getElementById('saveConfigBtn').addEventListener('click', () => {
            this.saveConfig();
        });

        // 重置配置
        document.getElementById('resetConfigBtn').addEventListener('click', () => {
            this.resetConfig();
        });

        // 输入验证
        document.getElementById('maxLogsInput').addEventListener('input', (e) => {
            this.validateConfigInput(e.target);
        });
    }

    async openConfigPanel() {
        const panel = document.getElementById('configPanel');
        const overlay = document.getElementById('configOverlay');

        // 加载当前配置
        await this.loadConfig();

        // 填充表单
        document.getElementById('maxLogsInput').value = this.configData.max_logs_per_client;

        // 显示面板
        panel.classList.add('show');
        overlay.classList.add('show');

        // 清除错误和状态消息
        this.clearConfigError();
        this.clearConfigStatus();
    }

    closeConfigPanel() {
        const panel = document.getElementById('configPanel');
        const overlay = document.getElementById('configOverlay');

        panel.classList.remove('show');
        overlay.classList.remove('show');
    }

    async loadConfig() {
        try {
            const response = await fetch('/api/config');
            if (response.ok) {
                const config = await response.json();
                this.configData = {
                    max_logs_per_client: config.max_logs_per_client
                };
                console.log('配置已加载:', this.configData);
            }
        } catch (error) {
            console.error('加载配置失败:', error);
        }
    }

    validateConfigInput(input) {
        const value = parseInt(input.value);
        const errorEl = document.getElementById('configError');

        if (isNaN(value)) {
            input.classList.add('error');
            errorEl.textContent = '请输入有效的数字';
            return false;
        }

        if (value < 1000 || value > 100000) {
            input.classList.add('error');
            errorEl.textContent = '值必须在 1000 到 100000 之间';
            return false;
        }

        input.classList.remove('error');
        errorEl.textContent = '';
        return true;
    }

    async saveConfig() {
        const input = document.getElementById('maxLogsInput');
        const newValue = parseInt(input.value);

        // 验证输入
        if (!this.validateConfigInput(input)) {
            return;
        }

        try {
            // 发送更新请求
            const response = await fetch('/api/config', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    max_logs_per_client: newValue
                })
            });

            if (response.ok) {
                const updatedConfig = await response.json();
                this.configData.max_logs_per_client = updatedConfig.max_logs_per_client;

                // 显示成功消息
                this.showConfigStatus('配置已保存', 'success');

                // 2秒后关闭面板
                setTimeout(() => {
                    this.closeConfigPanel();
                }, 2000);
            } else {
                const error = await response.json();
                this.showConfigError(error.detail || '保存配置失败');
            }
        } catch (error) {
            console.error('保存配置失败:', error);
            this.showConfigError('网络错误，请重试');
        }
    }

    resetConfig() {
        document.getElementById('maxLogsInput').value = this.configData.max_logs_per_client;
        this.clearConfigError();
        this.clearConfigStatus();
    }

    showConfigError(message) {
        const errorEl = document.getElementById('configError');
        errorEl.textContent = message;
    }

    clearConfigError() {
        document.getElementById('configError').textContent = '';
        document.getElementById('maxLogsInput').classList.remove('error');
    }

    showConfigStatus(message, type) {
        const statusEl = document.getElementById('configStatus');
        statusEl.textContent = message;
        statusEl.className = `config-status show ${type}`;
    }

    clearConfigStatus() {
        const statusEl = document.getElementById('configStatus');
        statusEl.className = 'config-status';
        statusEl.textContent = '';
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    window.logServer = new LogServer();
});
