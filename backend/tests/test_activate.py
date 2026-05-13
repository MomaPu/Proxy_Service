import pytest
from httpx import AsyncClient


class TestActivate:

    @pytest.mark.asyncio
    async def test_activate_key_success(self, client: AsyncClient, test_user, test_vm):
        """Успешная активация ключа"""
        response = await client.post("/api/v1/activate/key", json={
            "activation_key": test_user.activation_key
        })
        assert response.status_code == 200
        data = response.json()
        assert "host" in data
        assert "port" in data
        assert "protocol" in data
        assert data["host"] == test_vm.host

    @pytest.mark.asyncio
    async def test_activate_invalid_key(self, client: AsyncClient):
        """Активация с неверным ключом"""
        response = await client.post("/api/v1/activate/key", json={
            "activation_key": "invalid_key_123"
        })
        assert response.status_code == 400
        assert "Invalid" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_activate_key_already_used(self, client: AsyncClient, test_user, test_vm):
        """Повторная активация уже использованного ключа"""
        # Первая активация
        await client.post("/api/v1/activate/key", json={
            "activation_key": test_user.activation_key
        })
        # Вторая попытка
        response = await client.post("/api/v1/activate/key", json={
            "activation_key": test_user.activation_key
        })
        assert response.status_code == 400
        assert "Invalid or already used" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_activate_no_free_vms(self, client: AsyncClient, test_user, db):
        """Нет свободных VM"""
        # Занимаем все VM
        from app.models.vm import VirtualMachine
        from sqlalchemy import select

        result = await db.execute(select(VirtualMachine))
        vms = result.scalars().all()
        for vm in vms:
            vm.current_user_id = 999

        response = await client.post("/api/v1/activate/key", json={
            "activation_key": test_user.activation_key
        })
        assert response.status_code == 503
        assert "All proxy servers are busy" in response.json()["detail"]