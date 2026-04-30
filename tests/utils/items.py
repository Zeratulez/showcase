from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils import random_lower_string, random_float, create_random_user_factory
from app.crud.item_crud import create_item
from app.models import Item, User
from app.schemas import item_schema, user_schema

async def create_random_item(db_session: AsyncSession, user: User | None = None, item_name: str | None = None) -> Item:
    if not user:
        factory = await create_random_user_factory(db_session)
    test_user = user_schema.UserInDB.model_validate(user or factory.user)
    item_data = item_schema.ItemCreate(
        name=item_name or random_lower_string(),
        description=random_lower_string(),
        price=random_float()+5,
        tax=random_float()
    )
    new_item = await create_item(db_session, test_user, item_data)
    return new_item