from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Body, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import Token, authenticate_user
from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.crud import user_crud
from app.database import get_async_session
from app.schemas import user_schema

router = APIRouter(
    tags=["auth"]
)

@router.post("/auth/login", response_model=user_schema.UserPydantic)
async def register(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user_data: Annotated[user_schema.UserCreate, Body()]
):
    user = await user_crud.get_user_by_username(session, user_data.username)
    hashed_password = hash_password(user_data.password)
    if user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this nickname already exists")
    return await user_crud.create_user(session, user_data, hashed_password)

@router.post("/auth/login", response_model=Token)
async def login_for_access_token(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")