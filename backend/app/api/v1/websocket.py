from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime  # ДОБАВИТЬ
from ...core.database import get_db
from ...models.user import User
from ...models.vm import VirtualMachine
import json
from typing import Dict

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_status(self, user_id: int, status: str, message: str = ""):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json({
                    "status": status,
                    "message": message,
                    "timestamp": str(datetime.utcnow())
                })
            except:
                self.disconnect(user_id)


manager = ConnectionManager()


@router.websocket("/ws/status/{user_id}")
async def websocket_status(
        websocket: WebSocket,
        user_id: int,
        db: AsyncSession = Depends(get_db)
):
    await manager.connect(user_id, websocket)

    try:
        # Отправляем начальный статус
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user and user.is_active:
            # Проверяем, есть ли у пользователя VM
            vm_result = await db.execute(
                select(VirtualMachine).where(VirtualMachine.current_user_id == user_id)
            )
            vm = vm_result.scalar_one_or_none()

            if vm:
                await manager.send_status(user_id, "connected", f"Connected to {vm.host}:{vm.port}")
            else:
                await manager.send_status(user_id, "disconnected", "No active connection")
        else:
            await manager.send_status(user_id, "inactive", "Account not activated")

        # Держим соединение открытым и слушаем события
        while True:
            data = await websocket.receive_text()
            # Обработка команд от клиента (опционально)
            if data == "ping":
                await websocket.send_json({"status": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        manager.disconnect(user_id)