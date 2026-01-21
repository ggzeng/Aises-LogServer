import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket 连接管理器 - 负责管理所有 WebSocket 连接和广播消息"""

    def __init__(self):
        # 存储所有活动的 WebSocket 连接
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """接受新的 WebSocket 连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"新的 WebSocket 连接已建立，当前连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """断开 WebSocket 连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket 连接已断开，当前连接数: {len(self.active_connections)}")

    async def broadcast(self, message: dict) -> None:
        """向所有连接的客户端广播消息"""
        # 不再在此处记录日志，由调用方记录批次级别的广播信息
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                # 连接已断开，标记为待删除
                logger.debug(f"发送消息失败，标记连接为断开: {e}")
                disconnected.append(connection)

        # 清理已断开的连接
        if disconnected:
            for conn in disconnected:
                self.disconnect(conn)
            logger.info(f"清理了 {len(disconnected)} 个已断开的 WebSocket 连接")

    async def send_personal_message(self, message: dict, websocket: WebSocket) -> None:
        """向特定客户端发送消息"""
        try:
            await websocket.send_json(message)
        except Exception:
            pass  # 连接可能已断开

    def get_connection_count(self) -> int:
        """获取当前连接数量"""
        return len(self.active_connections)


# 全局连接管理器实例
connection_manager = ConnectionManager()
