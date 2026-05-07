import json
from typing import Annotated

import structlog
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core import redis_client
from app.crud import item_crud
from app.database import get_async_session
from app.schemas import item_schema, user_schema

router = APIRouter(
    tags=["items"]
)

logger: structlog.stdlib.BoundLogger = structlog.get_logger()

@router.get("/items", response_model=list[item_schema.ItemPydantic])
async def get_items(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    search: Annotated[str | None, Query()] = "",
    skip: Annotated[int | None, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=100)] = 100
):
    cache_key = f"items:search={search}:skip={skip}:limit={limit}"
    cache = await redis_client.redis_client.get(cache_key)
    if cache:
        return json.loads(cache)
    items = await item_crud.get_items(session, search, skip, limit)
    items_data = [item_schema.ItemPydantic.model_validate(item).model_dump(mode="json") for item in items]
    await redis_client.redis_client.set(cache_key, json.dumps(items_data), ex=300, nx=True)
    return items

@router.post("/items/create", response_model=item_schema.ItemPydantic)
async def create_item(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[user_schema.UserInDB, Depends(get_current_user)],
    item_data: Annotated[item_schema.ItemCreate, Body()],
):
    new_item = await item_crud.create_item(session, user, item_data)
    await logger.ainfo("item_created", item_id=new_item.id)
    await redis_client.invalidate_cache()
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
        await logger.awarning("item_not_found", item_id=item_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.owner_id != user.id:
        await logger.awarning("not_owner_of_the_item", owner_id=item.owner_id, user_id=user.id)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You not owner of the item")
    updated_item = await item_crud.update_item(session, item, new_item_data)
    await logger.ainfo("item_updated", item_id=item.id)
    await redis_client.invalidate_cache(item_id)
    return updated_item

@router.delete("/items/delete/{item_id}")
async def delete_item(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[user_schema.UserInDB, Depends(get_current_user)],
    item_id: int
):
    item = await item_crud.get_item_by_id(session, item_id)
    if not item:
        await logger.awarning("item_not_found", item_id=item_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.owner_id != user.id:
        await logger.awarning("not_owner_of_the_item", owner_id=item.owner_id, uesr_id=user.id)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You not owner of the item")
    await logger.ainfo("item_deleted", item_id=item.id)
    await redis_client.invalidate_cache(item_id)
    return await item_crud.delete_item(session, item)

@router.get("/items/{item_id}", response_model=item_schema.ItemPydantic)
async def get_item(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    item_id: int
):
    cache_key = f"item:{item_id}"
    cache = await redis_client.redis_client.get(cache_key)
    if cache:
        return json.loads(cache)
    item = await item_crud.get_item_by_id(session, item_id)
    if not item:
        await logger.awarning("item_not_found", item_id=item_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    item_data = item_schema.ItemPydantic.model_validate(item).model_dump(mode="json")
    await redis_client.redis_client.set(cache_key, json.dumps(item_data), ex=60, nx=True)
    return item