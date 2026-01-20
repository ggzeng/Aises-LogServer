from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from services.config_service import config_service

router = APIRouter()


class ConfigResponse(BaseModel):
    """配置响应"""
    max_logs_per_client: int
    server_host: str
    server_port: int
    server_reload: bool
    logging_level: str


class ConfigUpdateRequest(BaseModel):
    """配置更新请求"""
    max_logs_per_client: Optional[int] = Field(None, ge=1000, le=100000, description="每个客户端最多保留的日志数量")


@router.get("/config", response_model=ConfigResponse)
async def get_config():
    """获取当前配置"""
    config = config_service.get_config()
    return ConfigResponse(
        max_logs_per_client=config.max_logs_per_client,
        server_host=config.server.host,
        server_port=config.server.port,
        server_reload=config.server.reload,
        logging_level=config.logging.level
    )


@router.put("/config", response_model=ConfigResponse)
async def update_config(request: ConfigUpdateRequest):
    """更新配置"""
    try:
        # 构建更新字典
        updates = {}
        if request.max_logs_per_client is not None:
            updates["max_logs_per_client"] = request.max_logs_per_client

        if not updates:
            raise HTTPException(status_code=400, detail="没有提供任何更新字段")

        # 更新配置
        updated_config = config_service.update_config(updates)

        return ConfigResponse(
            max_logs_per_client=updated_config.max_logs_per_client,
            server_host=updated_config.server.host,
            server_port=updated_config.server.port,
            server_reload=updated_config.server.reload,
            logging_level=updated_config.logging.level
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")
