from typing import Annotated

import jwt
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_password
from app.crud.user_crud import get_user_by_username
from app.database import get_async_session
from app.schemas.user_schema import UserInDB

logger: structlog.stdlib.BoundLogger = structlog.get_logger()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            await logger.awarning("token_missing_subject")
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        await logger.awarning("invalid_token", exc_info=True)
        raise credentials_exception
    user = await get_user_by_username(session, token_data.username)
    if user is None:
        await logger.awarning("token_user_not_found", username=token_data.username)
        raise credentials_exception
    user = UserInDB.model_validate(user)
    if not user.is_active:
        await logger.awarning("user_inactive", username=user.username)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    await logger.ainfo("user_authenticated", username=user.username)
    return user

async def authenticate_user(session: AsyncSession, username: str, password: str) -> UserInDB | None:
    user = await get_user_by_username(session, username)
    if not user:
        await logger.awarning("user_not_found", username=username)
        return False
    if not verify_password(password, user.hashed_password):
        await logger.awarning("wrong_password", username=username)
        return False
    await logger.ainfo("authentication_successful", username=username)
    return UserInDB.model_validate(user)