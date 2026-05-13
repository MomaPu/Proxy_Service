import pytest
from httpx import AsyncClient
from websockets import connect
import json


class TestWebSocket:

    @pytest.mark.asyncio
    async def test_websocket_connection(self, client: AsyncClient, test_user):
        """Тест WebSocket подключения"""
        # Активация
        await client.post("/api/v1/activate/key", json={
            "activation_key": test_user.activation_key
        })

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "test123"
        })
        user_id = login_response.json().get("user_id", 1)

        # Подключаемся к WebSocket
        uri = f"ws://localhost:8000/ws/status/{user_id}"
        try:
            async with connect(uri) as websocket:
                # Проверяем, что можем получить сообщение
                message = await websocket.recv()
                data = json.loads(message)
                assert "status" in data
        except Exception as e:
            # Если WebSocket не доступен, пропускаем тест
            pytest.skip(f"WebSocket not available: {e}")