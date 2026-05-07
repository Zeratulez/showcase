from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item
from app.schemas import item_schema, user_schema


async def get_item_by_id(session: AsyncSession, item_id: int):
    return await session.get(Item, item_id)

async def get_items(session: AsyncSession, name: str, skip: int, limit: int):
    query = select(Item).filter(Item.name.contains(name)).offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()

async def create_item(session: AsyncSession, user: user_schema.UserInDB, item: item_schema.ItemCreate):
    new_item = Item(**item.model_dump(), owner_id=user.id)
    session.add(new_item)
    await session.commit()
    await session.refresh(new_item)
    return new_item

async def update_item(session: AsyncSession, item_db: Item, new_item_data: item_schema.ItemUpdate):
    for key, value in new_item_data.model_dump(exclude_unset=True).items():
        setattr(item_db, key, value)
    await session.commit()
    await session.refresh(item_db)
    return item_db

async def delete_item(session: AsyncSession, item: Item):
    await session.delete(item)
    await session.commit()
    return {"message": "Item successfully deleted"}