from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from tests.utils import user_token, create_random_item, create_random_user_factory
from app.crud.item_crud import get_items


async def test_get_items(db_session: AsyncSession, client: AsyncClient):
    await create_random_item(db_session)
    await create_random_item(db_session)
    response = await client.get(
        "/items",

    )
    assert response.status_code == 200
    assert len(response.json()) == 2

async def test_get_items_with_skip(db_session: AsyncSession, client: AsyncClient):
    _ = await create_random_item(db_session)
    item_2 = await create_random_item(db_session)
    response = await client.get(
        "/items",
        params={"skip": 1}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    content = response.json()[0]
    assert content["name"] == item_2.name
    assert content["description"] == item_2.description
    assert content["price"] == item_2.price
    assert content["tax"] == item_2.tax

async def test_get_items_with_limit(db_session: AsyncSession, client: AsyncClient):
    item_1 = await create_random_item(db_session)
    _ = await create_random_item(db_session)
    response = await client.get(
        "/items",
        params={"limit": 1}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    content = response.json()[0]
    assert content["name"] == item_1.name
    assert content["description"] == item_1.description
    assert content["price"] == item_1.price
    assert content["tax"] == item_1.tax

async def test_get_items_full_search(db_session: AsyncSession, client: AsyncClient):
    item_1 = await create_random_item(db_session)
    response = await client.get(
        "/items",
        params={"search": item_1.name}
    )
    assert response.status_code == 200
    content = response.json()[0]
    assert content["name"] == item_1.name
    assert content["description"] == item_1.description
    assert content["price"] == item_1.price
    assert content["tax"] == item_1.tax

async def test_get_items_partial_search(db_session: AsyncSession, client: AsyncClient):
    item_1 = await create_random_item(db_session)
    response = await client.get(
        "/items",
        params={"search": item_1.name[5:10]}
    )
    assert response.status_code == 200
    content = response.json()[0]
    assert content["name"] == item_1.name
    assert content["description"] == item_1.description
    assert content["price"] == item_1.price
    assert content["tax"] == item_1.tax

async def test_get_multiple_items_partial_search(db_session: AsyncSession, client: AsyncClient):
    await create_random_item(db_session, item_name="Star Wars: knights of the old republic")
    await create_random_item(db_session, item_name="star wars jedi fallen order")
    response = await client.get(
        "/items",
        params={"search": "star wars"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 2

async def test_get_item(db_session: AsyncSession, client: AsyncClient):
    item = await create_random_item(db_session)
    response = await client.get(
        f"/items/{item.id}"
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == item.name
    assert content["description"] == item.description
    assert content["price"] == item.price
    assert content["tax"] == item.tax

async def test_get_item_not_found(client: AsyncClient):
    response = await client.get(
        "/items/1"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

async def test_create_item(db_session: AsyncSession, client: AsyncClient):
    token = await user_token(db_session, client)
    data = {"name": "foo", "description": "Foo Fighters", "price": 14.2, "tax": 2.1}
    response = await client.post(
        "/items/create",
        headers=token["headers"],
        json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert content["price"] == data["price"]
    assert content["tax"] == data["tax"]
    assert "id" in content
    assert "owner_id" in content

async def test_create_item_invalid_data(db_session: AsyncSession, client: AsyncClient):
    token = await user_token(db_session, client)
    data = {"name": "foo", "description": "Foo Fighters", "price": -999}
    response = await client.post(
        "/items/create",
        headers=token["headers"],
        json=data
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Input should be greater than or equal to 0"
    items = await get_items(db_session, name=data["name"], skip=0, limit=10)
    assert len(items) == 0

async def test_update_item(db_session: AsyncSession, client: AsyncClient):
    factory = await create_random_user_factory(db_session)
    item = await create_random_item(db_session, factory.user)
    token = await user_token(db_session, client, factory.user.username, factory.password)
    data = {"name": "updated_name", "description": "updated_description", "price": 100, "tax": 50}
    response = await client.patch(
        f"/items/update/{item.id}",
        headers=token["headers"],
        json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert content["price"] == data["price"]
    assert content["tax"] == data["tax"]
    assert content["id"] == item.id
    assert content["owner_id"] == item.owner_id

async def test_update_item_not_found(db_session: AsyncSession, client: AsyncClient):
    factory = await create_random_user_factory(db_session)
    token = await user_token(db_session, client, factory.user.username, factory.password)
    data = {"name": "updated_name", "description": "updated_description", "price": 100, "tax": 50}
    response = await client.patch(
        "/items/update/1",
        headers=token["headers"],
        json=data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

async def test_update_item_not_owner(db_session: AsyncSession, client: AsyncClient):
    item = await create_random_item(db_session)
    other_user_token = await user_token(db_session, client)
    data = {"name": "updated_name", "description": "updated_description", "price": 100, "tax": 50}
    response = await client.patch(
        f"/items/update/{item.id}",
        headers=other_user_token["headers"],
        json=data
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You not owner of the item"

async def test_delete_item(db_session: AsyncSession, client: AsyncClient):
    factory = await create_random_user_factory(db_session)
    item = await create_random_item(db_session, factory.user)
    token = await user_token(db_session, client, factory.user.username, factory.password)
    response = await client.delete(
        f"/items/delete/{item.id}",
        headers=token["headers"]
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Item successfully deleted"

async def test_delete_item_not_found(db_session: AsyncSession, client: AsyncClient):
    factory = await create_random_user_factory(db_session)
    token = await user_token(db_session, client, factory.user.username, factory.password)
    response = await client.delete(
        "/items/delete/1",
        headers=token["headers"]
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

async def test_delete_item_not_owner(db_session: AsyncSession, client: AsyncClient):
    item = await create_random_item(db_session)
    other_user_token = await user_token(db_session, client)
    response = await client.delete(
        f"/items/delete/{item.id}",
        headers=other_user_token["headers"]
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You not owner of the item"