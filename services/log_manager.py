from typing import Dict, List, Deque
from collections import deque
from datetime import datetime

from models.log_models import StoredLog, LogMessage
from services.config_service import config_service


class LogManager:
    """日志管理服务 - 负责日志的存储和查询"""

    def __init__(self):
        # 按客户端 ID 分组的日志存储
        self._logs: Dict[str, Deque[StoredLog]] = {}

    def add_logs(self, client_id: str, messages: List[LogMessage], hostname: str = None) -> None:
        """添加日志批次"""
        if client_id not in self._logs:
            self._logs[client_id] = deque()

        client_logs = self._logs[client_id]

        # 将 LogMessage 转换为 StoredLog 并添加
        for msg in messages:
            stored_log = StoredLog(
                timestamp=msg.timestamp,
                level=msg.level,
                message=msg.message,
                logger=msg.logger,
                function=msg.function,
                line=msg.line,
                client_id=client_id,
                hostname=hostname,
                extra=msg.extra
            )
            client_logs.append(stored_log)

        # 获取配置的上限
        max_logs = config_service.get_config().max_logs_per_client

        # 如果超过上限，删除旧日志
        while len(client_logs) > max_logs:
            client_logs.popleft()

    def get_logs(self, client_id: str) -> List[StoredLog]:
        """获取指定客户端的所有日志"""
        if client_id not in self._logs:
            return []
        return list(self._logs[client_id])

    def get_all_clients(self) -> List[str]:
        """获取所有客户端 ID"""
        return list(self._logs.keys())

    def get_client_stats(self, client_id: str) -> Dict[str, int]:
        """获取客户端日志统计信息"""
        if client_id not in self._logs:
            return {"total": 0, "DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}

        logs = self._logs[client_id]
        stats = {"total": len(logs), "DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}

        for log in logs:
            level = log.level.value
            if level in stats:
                stats[level] += 1

        return stats

    def clear_logs(self, client_id: str) -> None:
        """清空指定客户端的日志"""
        if client_id in self._logs:
            self._logs[client_id].clear()


# 全局日志管理器实例
log_manager = LogManager()
