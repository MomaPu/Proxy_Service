import asyncio
from app.core.database import engine, AsyncSessionLocal
from app.models.user import User
from app.models.vm import VirtualMachine
from app.core.security import get_password_hash


async def init_test_data():
    async with engine.begin() as conn:
        await conn.run_sync(User.metadata.drop_all)
        await conn.run_sync(VirtualMachine.metadata.drop_all)
        await conn.run_sync(User.metadata.create_all)
        await conn.run_sync(VirtualMachine.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Создаём тестовые виртуальные машины
        test_vms = [
            VirtualMachine(
                name="proxy-1",
                host="proxy1.example.com",
                port=1080,
                protocol="socks5",
                is_active=True
            ),
            VirtualMachine(
                name="proxy-2",
                host="proxy2.example.com",
                port=8080,
                protocol="http",
                is_active=True
            ),
            VirtualMachine(
                name="proxy-3",
                host="proxy3.example.com",
                port=3128,
                protocol="https",
                is_active=True
            ),
        ]

        for vm in test_vms:
            session.add(vm)

        await session.commit()
        print("Test data created!")


if __name__ == "__main__":
    asyncio.run(init_test_data())