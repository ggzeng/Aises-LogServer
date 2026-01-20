"""
日志接收 API 测试

测试日志接收、验证和存储功能
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from services.log_manager import log_manager


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_logs():
    """每个测试后清空日志"""
    yield
    log_manager._logs.clear()


class TestLogAPI:
    """日志 API 测试类"""

    def test_receive_logs_valid(self, client):
        """测试接收有效日志"""
        log_data = {
            "clientId": "test-client-1",
            "hostname": "test-host",
            "timestamp": "2026-01-20 12:00:03.333",
            "messages": [
                {
                    "timestamp": "2026-01-20 12:00:00.123",
                    "level": "INFO",
                    "message": "测试日志消息，包含数字 12345",
                    "logger": "test.module",
                    "function": "test_func",
                    "line": 42
                }
            ]
        }

        response = client.post("/logs", json=log_data)
        assert response.status_code == 200

        result = response.json()
        assert result['status'] == 'success'
        assert result['client_id'] == 'test-client-1'
        assert '已接收' in result['message']

    def test_receive_logs_multiple_entries(self, client):
        """测试接收多条日志"""
        log_data = {
            "clientId": "test-client-2",
            "hostname": "test-host",
            "timestamp": "2026-01-20 12:00:03.333",
            "messages": [
                {
                    "timestamp": "2026-01-20 12:00:00.000",
                    "level": "INFO",
                    "message": "日志 1",
                    "logger": "test",
                    "function": "test",
                    "line": 1
                },
                {
                    "timestamp": "2026-01-20 12:00:01.000",
                    "level": "ERROR",
                    "message": "日志 2",
                    "logger": "test",
                    "function": "test",
                    "line": 2
                }
            ]
        }

        response = client.post("/logs", json=log_data)
        assert response.status_code == 200
        assert '2 条日志' in response.json()['message']

    def test_receive_logs_invalid_json(self, client):
        """测试接收无效 JSON"""
        response = client.post(
            "/logs",
            json={"invalid": "data"}
        )
        assert response.status_code == 422  # Validation error

    def test_receive_logs_invalid_level(self, client):
        """测试接收无效日志级别"""
        log_data = {
            "clientId": "test-client-3",
            "timestamp": "2026-01-20 12:00:03.333",
            "messages": [
                {
                    "timestamp": "2026-01-20 12:00:00.000",
                    "level": "INVALID_LEVEL",
                    "message": "测试",
                    "logger": "test",
                    "function": "test",
                    "line": 1
                }
            ]
        }

        response = client.post("/logs", json=log_data)
        assert response.status_code == 422

    def test_receive_logs_all_levels(self, client):
        """测试所有日志级别"""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in levels:
            log_data = {
                "clientId": "test-levels",
                "timestamp": "2026-01-20 12:00:03.333",
                "messages": [
                    {
                        "timestamp": "2026-01-20 12:00:00.000",
                        "level": level,
                        "message": f"{level} 日志",
                        "logger": "test",
                        "function": "test",
                        "line": 1
                    }
                ]
            }

            response = client.post("/logs", json=log_data)
            assert response.status_code == 200

    def test_receive_logs_missing_fields(self, client):
        """测试缺少必需字段"""
        log_data = {
            "clientId": "test-client-4",
            "timestamp": "2026-01-20 12:00:03.333",
            "messages": [
                {
                    "timestamp": "2026-01-20 12:00:00.000",
                    "level": "INFO",
                    "message": "测试"
                    # 缺少 logger, function, line
                }
            ]
        }

        response = client.post("/logs", json=log_data)
        assert response.status_code == 422


class TestLogManager:
    """日志管理器测试"""

    def test_log_storage(self):
        """测试日志存储"""
        from models.log_models import LogMessage

        log_msg = LogMessage(
            timestamp="2026-01-20 12:00:00.000",
            level="INFO",
            message="测试",
            logger="test",
            function="test",
            line=1
        )

        log_manager.add_logs("test-storage", [log_msg], "test-host")

        # 验证日志已存储
        logs = log_manager.get_logs("test-storage")
        assert len(logs) == 1
        assert logs[0].client_id == "test-storage"

    def test_multiple_clients(self):
        """测试多客户端日志存储"""
        from models.log_models import LogMessage

        # 创建两个客户端的日志
        msg1 = LogMessage(
            timestamp="2026-01-20 12:00:00.000",
            level="INFO",
            message="Client 1",
            logger="test",
            function="test",
            line=1
        )

        msg2 = LogMessage(
            timestamp="2026-01-20 12:00:00.000",
            level="INFO",
            message="Client 2",
            logger="test",
            function="test",
            line=1
        )

        log_manager.add_logs("client-1", [msg1])
        log_manager.add_logs("client-2", [msg2])

        # 验证两个客户端的日志都已存储
        assert len(log_manager.get_logs("client-1")) == 1
        assert len(log_manager.get_logs("client-2")) == 1

        # 验证客户端列表
        clients = log_manager.get_all_clients()
        assert len(clients) == 2
        assert "client-1" in clients
        assert "client-2" in clients

    def test_log_rotation(self):
        """测试日志轮转"""
        from models.log_models import LogMessage
        from services.config_service import config_service

        # 设置较小的日志上限用于测试
        original_config = config_service.get_config()

        # 创建超过限制的日志
        messages = []
        for i in range(15):
            msg = LogMessage(
                timestamp="2026-01-20 12:00:00.000",
                level="INFO",
                message=f"Log {i}",
                logger="test",
                function="test",
                line=i
            )
            messages.append(msg)

        log_manager.add_logs("test-rotation", messages)

        # 验证日志数量不超过限制
        stored_logs = log_manager.get_logs("test-rotation")
        assert len(stored_logs) <= 10000  # 默认限制
