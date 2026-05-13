from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...core.database import get_db
from ...models.user import User
from ...models.vm import VirtualMachine
from ...schemas.user import UserResponse, ChangePassword
from ...core.security import verify_password, get_password_hash
from ...core.dependencies import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/my-vm")
async def get_my_vm(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(VirtualMachine).where(VirtualMachine.current_user_id == current_user.id)
    )
    vm = result.scalar_one_or_none()

    if vm:
        return {
            "has_vm": True,
            "host": vm.host,
            "port": vm.port,
            "protocol": vm.protocol,
            "last_used": vm.last_used_at
        }
    return {"has_vm": False}


@router.post("/change-password")
async def change_password(
        passwords: ChangePassword,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if not verify_password(passwords.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    current_user.password_hash = get_password_hash(passwords.new_password)
    await db.commit()

    return {"message": "Password changed successfully"}


@router.get("/activation-key")
async def get_activation_key(
        current_user: User = Depends(get_current_user)
):
    if current_user.activation_key:
        return {"activation_key": current_user.activation_key}
    return {"activation_key": None, "message": "No active activation key"}