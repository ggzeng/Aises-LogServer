from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class LogLevel(str, Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogMessage(BaseModel):
    """单条日志消息（接收格式）"""
    timestamp: str = Field(..., description="日志时间戳")
    level: LogLevel = Field(..., description="日志级别")
    message: str = Field(..., description="日志消息内容")
    logger: str = Field(..., description="Logger 名称", alias="name")
    function: str = Field(..., description="函数名")
    line: int = Field(..., description="代码行号")
    extra: Optional[Dict[str, Any]] = Field(None, description="额外信息")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "timestamp": "2026-01-20 12:00:02.222",
                "level": "WARNING",
                "message": "这是一条警告",
                "logger": "drivers.tonghuashun",
                "function": "connect",
                "line": 150,
                "extra": {}
            }
        }


class StoredLog(BaseModel):
    """存储的完整日志（包含客户端信息）"""
    timestamp: str
    level: LogLevel
    message: str
    logger: str
    function: str
    line: int
    client_id: str
    hostname: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


class LogBatch(BaseModel):
    """日志批次（接收格式）"""
    clientId: str = Field(..., description="客户端唯一标识符")
    hostname: Optional[str] = Field(None, description="客户端主机名")
    timestamp: str = Field(..., description="日志发送时间")
    messages: list[LogMessage] = Field(..., min_length=1, description="日志消息数组")

    class Config:
        json_schema_extra = {
            "example": {
                "clientId": "opsterminal-a1b2c3d4e5f6",
                "hostname": "DESKTOP-ABC123",
                "timestamp": "2026-01-20 12:00:03.333",
                "messages": [
                    {
                        "timestamp": "2026-01-20 12:00:02.222",
                        "level": "WARNING",
                        "message": "这是第二条警告",
                        "logger": "drivers.tonghuashun",
                        "function": "connect",
                        "line": 150,
                        "extra": {}
                    },
                    {
                        "timestamp": "2026-01-20 12:00:01.111",
                        "level": "WARNING",
                        "message": "这是第一条警告",
                        "logger": "drivers.tonghuashun",
                        "function": "connect",
                        "line": 150,
                        "extra": {}
                    }
                ]
            }
        }


# 为了向后兼容，保留旧的 LogEntry 作为别名
LogEntry = StoredLog
