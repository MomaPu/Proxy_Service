from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime  # ДОБАВИТЬ ЭТУ СТРОКУ
from pydantic import BaseModel
from ...core.database import get_db
from ...models.user import User
from ...models.vm import VirtualMachine
from ...core.dependencies import get_current_user
from ...tasks.email_tasks import send_activation_email  # ДОБАВИТЬ ДЛЯ ОБНОВЛЕНИЯ КЛЮЧА

router = APIRouter(prefix="/activate", tags=["activate"])


class ActivationRequest(BaseModel):
    activation_key: str


class VMInfo(BaseModel):
    host: str
    port: int
    protocol: str
    vm_id: int


@router.post("/key", response_model=VMInfo)
async def activate_with_key(
        request: ActivationRequest,
        db: AsyncSession = Depends(get_db)
):
    """Активация ключа и получение свободной виртуальной машины"""

    # 1. Находим пользователя по ключу
    result = await db.execute(
        select(User).where(
            User.activation_key == request.activation_key,
            User.is_active == False  # ещё не активирован
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or already used activation key"
        )

    # 2. Проверяем срок действия ключа
    if user.activation_key_expires and user.activation_key_expires.replace(tzinfo=None) < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activation key expired"
        )

    # 3. Ищем свободную виртуальную машину
    result = await db.execute(
        select(VirtualMachine).where(
            VirtualMachine.is_active == True,
            VirtualMachine.current_user_id == None
        ).limit(1)
    )
    free_vm = result.scalar_one_or_none()

    if not free_vm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="All proxy servers are busy. Please try again later."
        )

    # 4. Привязываем VM к пользователю
    free_vm.current_user_id = user.id
    free_vm.last_used_at = datetime.utcnow()

    # 5. Активируем пользователя
    user.is_active = True
    user.activation_key = None  # одноразовый ключ
    user.activation_key_expires = None

    await db.commit()
    await db.refresh(free_vm)

    return VMInfo(
        host=free_vm.host,
        port=free_vm.port,
        protocol=free_vm.protocol,
        vm_id=free_vm.id
    )


@router.post("/refresh-key")
async def refresh_activation_key(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Обновление ключа активации (для личного кабинета)"""

    # Генерируем новый ключ
    current_user.generate_activation_key()
    current_user.is_active = False  # деактивируем до активации

    # Если у пользователя была VM, освобождаем её
    from ...models.vm import VirtualMachine
    await db.execute(
        update(VirtualMachine)
        .where(VirtualMachine.current_user_id == current_user.id)
        .values(current_user_id=None)
    )

    await db.commit()

    # Отправляем новый ключ на почту
    send_activation_email.delay(current_user.email, current_user.activation_key)

    return {"message": "New activation key sent to your email"}


@router.post("/disconnect")
async def disconnect_from_vm(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Отключение от виртуальной машины"""

    await db.execute(
        update(VirtualMachine)
        .where(VirtualMachine.current_user_id == current_user.id)
        .values(current_user_id=None)
    )

    await db.commit()

    return {"message": "Disconnected from proxy server"}