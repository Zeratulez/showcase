from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.security import hash_password, verify_password
from app.crud import user_crud
from app.database import get_async_session
from app.schemas.user_schema import ChangePassword, UserInDB

router = APIRouter(
    tags=["users"]
)

@router.post("/me/change_password")
async def change_password(session: Annotated[AsyncSession, Depends(get_async_session)],
                          user_db: Annotated[UserInDB, Depends(get_current_user)],
                          password: Annotated[ChangePassword, Body()]):
    verified = verify_password(password.current_password, user_db.hashed_password)
    if not verified:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Incorrect current password")
    if password.current_password == password.new_password:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="New password cannot be same as current password")
    new_password_hash = hash_password(password.new_password)
    user = await user_crud.get_user_by_id(session, user_db.id)
    return await user_crud.change_password(session, user, new_password_hash)
