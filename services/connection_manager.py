from fastapi import WebSocket


class ConnectionManager:
    """WebSocket 连接管理器 - 负责管理所有 WebSocket 连接和广播消息"""

    def __init__(self):
        # 存储所有活动的 WebSocket 连接
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """接受新的 WebSocket 连接"""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """断开 WebSocket 连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict) -> None:
        """向所有连接的客户端广播消息"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # 连接已断开，标记为待删除
                disconnected.append(connection)

        # 清理已断开的连接
        for conn in disconnected:
            self.disconnect(conn)

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
