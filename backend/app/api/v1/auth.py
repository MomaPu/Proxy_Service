from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...core.database import get_db
from ...models.user import User
from ...schemas.user import UserCreate, UserLogin, Token, ChangePassword
from ...core.security import verify_password, get_password_hash, create_access_token
from ...core.dependencies import get_current_user  # ДОБАВИТЬ ЭТУ СТРОКУ
from ...tasks.email_tasks import send_activation_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверка совпадения паролей
    if user_data.password != user_data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Проверка существования пользователя
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Создание пользователя
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        is_active=False
    )
    user.generate_activation_key()

    db.add(user)
    await db.commit()

    # Отправка письма через Celery
    send_activation_email.delay(user.email, user.activation_key)

    return {"message": "Registration successful. Check your email for activation key."}


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403,
                            detail="Account not activated. Please activate with the key sent to your email.")

    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}