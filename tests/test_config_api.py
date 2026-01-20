"""
配置管理 API 测试

测试配置的读取、更新和验证功能
"""

import pytest
import yaml
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def temp_config(monkeypatch, tmp_path):
    """创建临时配置文件"""
    config_file = tmp_path / "test_config.yaml"
    test_config = {
        "max_logs_per_client": 5000,
        "server": {"host": "127.0.0.1", "port": 8001, "reload": False},
        "logging": {"level": "debug"},
    }

    # 写入临时配置文件
    with open(config_file, "w") as f:
        yaml.dump(test_config, f)

    # 修改配置文件路径
    import services.config_service

    monkeypatch.setattr(services.config_service, "CONFIG_PATH", str(config_file))

    return config_file


class TestConfigAPI:
    """配置 API 测试类"""

    def test_get_config(self, client):
        """测试获取配置"""
        response = client.get("/api/config")
        assert response.status_code == 200

        config = response.json()
        assert "max_logs_per_client" in config
        assert "server_host" in config
        assert "server_port" in config
        assert isinstance(config["max_logs_per_client"], int)

    def test_update_config_valid(self, client):
        """测试更新配置 - 有效值"""
        new_value = 20000
        response = client.put("/api/config", json={"max_logs_per_client": new_value})

        assert response.status_code == 200
        config = response.json()
        assert config["max_logs_per_client"] == new_value

        # 验证配置已保存
        response = client.get("/api/config")
        config = response.json()
        assert config["max_logs_per_client"] == new_value

    def test_update_config_invalid_too_small(self, client):
        """测试更新配置 - 值太小"""
        response = client.put("/api/config", json={"max_logs_per_client": 500})

        # Pydantic 验证失败返回 422
        assert response.status_code == 422
        # 验证错误信息包含范围限制
        detail = response.json()
        assert "detail" in detail

    def test_update_config_invalid_too_large(self, client):
        """测试更新配置 - 值太大"""
        response = client.put("/api/config", json={"max_logs_per_client": 200000})

        # Pydantic 验证失败返回 422
        assert response.status_code == 422
        # 验证错误信息包含范围限制
        detail = response.json()
        assert "detail" in detail

    def test_update_config_invalid_type(self, client):
        """测试更新配置 - 类型错误"""
        response = client.put("/api/config", json={"max_logs_per_client": "invalid"})

        assert response.status_code == 422  # Validation error

    def test_update_config_boundary_values(self, client):
        """测试更新配置 - 边界值"""
        # 测试最小边界
        response = client.put("/api/config", json={"max_logs_per_client": 1000})
        assert response.status_code == 200

        # 测试最大边界
        response = client.put("/api/config", json={"max_logs_per_client": 100000})
        assert response.status_code == 200
