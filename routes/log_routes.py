from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from models.log_models import LogBatch
from services.connection_manager import connection_manager
from services.log_manager import log_manager

router = APIRouter()


@router.post("/logs")
async def receive_logs(batch: LogBatch) -> dict[str, str]:
    """
    接收 loguru 客户端发送的日志批次

    Args:
        batch: 包含 clientId 和日志消息的批次数据

    Returns:
        成功响应消息
    """
    try:
        # 存储日志（包含 hostname）
        log_manager.add_logs(batch.clientId, batch.messages, batch.hostname)

        # 广播到所有 WebSocket 连接
        for msg in batch.messages:
            # 构建完整的日志对象，包含客户端信息
            log_data = {
                "timestamp": msg.timestamp,
                "level": msg.level.value if hasattr(msg.level, "value") else msg.level,
                "message": msg.message,
                "logger": msg.logger,
                "function": msg.function,
                "line": msg.line,
                "client_id": batch.clientId,
                "hostname": batch.hostname,
                "extra": msg.extra,
            }

            message = {"type": "log", "data": log_data, "client_id": batch.clientId}
            await connection_manager.broadcast(message)

        return {
            "status": "success",
            "message": f"已接收 {len(batch.messages)} 条日志",
            "client_id": batch.clientId,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理日志失败: {str(e)}")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 端点，用于实时推送日志到 web 客户端
    """
    await connection_manager.connect(websocket)

    try:
        # 发送连接成功消息
        await websocket.send_json(
            {
                "type": "connected",
                "message": "已连接到日志服务器",
                "connection_count": connection_manager.get_connection_count(),
            }
        )

        # 持续接收客户端消息（保持连接）
        while True:
            data = await websocket.receive_text()

            # 处理客户端请求
            if data:
                import json

                try:
                    request = json.loads(data)

                    # 处理获取客户端列表请求
                    if request.get("type") == "get_clients":
                        clients = log_manager.get_all_clients()
                        await websocket.send_json({"type": "clients_list", "clients": clients})

                    # 处理获取特定客户端日志请求
                    elif request.get("type") == "get_logs":
                        client_id = request.get("client_id")
                        if client_id:
                            logs = log_manager.get_logs(client_id)
                            await websocket.send_json(
                                {
                                    "type": "logs_data",
                                    "client_id": client_id,
                                    "logs": [log.model_dump() for log in logs],
                                }
                            )

                            # 发送统计信息
                            stats = log_manager.get_client_stats(client_id)
                            await websocket.send_json(
                                {"type": "client_stats", "client_id": client_id, "stats": stats}
                            )

                except json.JSONDecodeError:
                    pass  # 忽略无效的 JSON

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception as e:
        connection_manager.disconnect(websocket)
        print(f"WebSocket 错误: {e}")
