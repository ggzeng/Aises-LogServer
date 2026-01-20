from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator


class ServerConfig(BaseModel):
    """服务器配置"""

    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


class LoggingConfig(BaseModel):
    """日志配置"""

    level: str = "info"


class AppConfig(BaseModel):
    """应用配置"""

    max_logs_per_client: int = Field(default=10000, ge=1000, le=100000)
    server: ServerConfig = Field(default_factory=ServerConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @field_validator("max_logs_per_client")
    @classmethod
    def validate_max_logs(cls, v):
        """验证日志数量上限"""
        if not (1000 <= v <= 100000):
            raise ValueError("max_logs_per_client 必须在 1000-100000 范围内")
        return v


class ConfigService:
    """配置管理服务"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._config: AppConfig = AppConfig()
        self._load_config()

    def _load_config(self) -> None:
        """加载配置文件"""
        if self.config_path.exists():
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data:
                        self._config = AppConfig(**data)
            except Exception as e:
                print(f"加载配置文件失败: {e}, 使用默认配置")
                self._config = AppConfig()
        else:
            # 配置文件不存在，创建默认配置文件
            self._save_config()

    def _save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    self._config.model_dump(exclude_none=True),
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                )
        except Exception as e:
            raise RuntimeError(f"保存配置文件失败: {e}")

    def get_config(self) -> AppConfig:
        """获取当前配置"""
        return self._config

    def update_config(self, updates: dict[str, Any]) -> AppConfig:
        """更新配置"""
        # 获取当前配置字典
        current = self._config.model_dump()

        # 递归更新配置
        def update_dict(d: dict, u: dict) -> dict:
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = update_dict(d.get(k, {}), v)
                else:
                    d[k] = v
            return d

        updated = update_dict(current, updates)

        # 验证并创建新配置
        try:
            new_config = AppConfig(**updated)
            self._config = new_config
            self._save_config()
            return self._config
        except Exception as e:
            raise ValueError(f"配置验证失败: {e}")

    def reload_config(self) -> AppConfig:
        """重新加载配置文件"""
        self._load_config()
        return self._config


# 全局配置服务实例
config_service = ConfigService()
