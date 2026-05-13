import pytest
from httpx import AsyncClient


class TestVM:

    @pytest.mark.asyncio
    async def test_get_my_vm(self, client: AsyncClient, test_user, test_vm):
        """Получение своей VM"""
        # Активация
        await client.post("/api/v1/activate/key", json={
            "activation_key": test_user.activation_key
        })

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "test123"
        })
        token = login_response.json()["access_token"]

        response = await client.get(
            "/api/v1/profile/my-vm",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["has_vm"] == True
        assert data["host"] == test_vm.host

    @pytest.mark.asyncio
    async def test_disconnect_from_vm(self, client: AsyncClient, test_user, test_vm):
        """Отключение от VM"""
        # Активация
        await client.post("/api/v1/activate/key", json={
            "activation_key": test_user.activation_key
        })

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "test123"
        })
        token = login_response.json()["access_token"]

        # Отключение
        response = await client.post(
            "/api/v1/activate/disconnect",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert "Disconnected" in response.json()["message"]

        # Проверяем, что VM освободилась
        vm_response = await client.get(
            "/api/v1/profile/my-vm",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert vm_response.json()["has_vm"] == False