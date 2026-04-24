from typing import Annotated
from fastapi import APIRouter, Query, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.crud import item_crud
from app.schemas import item_schema, user_schema
from app.api.dependencies import get_current_user

router = APIRouter(
    tags=["items"]
)

@router.get("/items", response_model=list[item_schema.ItemPydantic])
async def get_items(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    search: Annotated[str | None, Query()] = "",
    skip: Annotated[int | None, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=100)] = 100
):
    items = await item_crud.get_items(session, search, skip, limit)
    return items

@router.post("/items/create", response_model=item_schema.ItemPydantic)
async def create_item(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[user_schema.UserInDB, Depends(get_current_user)],
    item_data: Annotated[item_schema.ItemCreate, Body()],
):
    new_item = await item_crud.create_item(session, user, item_data)
    return new_item

@router.patch("/items/update/{item_id}", response_model=item_schema.ItemPydantic)
async def update_item(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[user_schema.UserInDB, Depends(get_current_user)],
    new_item_data: Annotated[item_schema.ItemUpdate, Body()],
    item_id: int,
):
    item = await item_crud.get_item_by_id(session, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You not owner of the item")
    updated_item = await item_crud.update_item(session, item, new_item_data)
    return updated_item

@router.delete("/items/delete/{item_id}")
async def delete_item(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[user_schema.UserInDB, Depends(get_current_user)],
    item_id: int
):
    item = await item_crud.get_item_by_id(session, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You not owner of the item")
    return await item_crud.delete_item(session, item)

@router.get("/items/{item_id}", response_model=item_schema.ItemPydantic)
async def get_item(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    item_id: int
):
    item = await item_crud.get_item_by_id(session, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item