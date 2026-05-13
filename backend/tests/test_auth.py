import pytest
from httpx import AsyncClient


class TestAuth:

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient, mock_celery):
        """Успешная регистрация"""
        response = await client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "test123",
            "confirm_password": "test123"
        })
        assert response.status_code == 201
        assert "Registration successful" in response.json()["message"]
        # Проверяем, что Celery был вызван
        mock_celery.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_password_mismatch(self, client: AsyncClient):
        """Регистрация с несовпадающими паролями"""
        response = await client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "test123",
            "confirm_password": "test456"
        })
        assert response.status_code == 400
        assert "Passwords do not match" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Регистрация с уже существующим email"""
        response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "test123",
            "confirm_password": "test123"
        })
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user, test_vm):
        """Успешный вход"""
        # Активируем пользователя через API (а не напрямую в БД)
        activate_response = await client.post("/api/v1/activate/key", json={
            "activation_key": test_user.activation_key
        })
        assert activate_response.status_code == 200

        # Теперь логинимся
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "test123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Вход с неверным паролем"""
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_not_activated(self, client: AsyncClient, test_user):
        """Вход неактивированного пользователя"""
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "test123"
        })
        assert response.status_code == 403
        assert "not activated" in response.json()["detail"]