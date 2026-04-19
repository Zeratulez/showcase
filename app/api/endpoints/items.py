from typing import Annotated
from fastapi import APIRouter, Query

router = APIRouter(
    tags=["items"]
)

@router.get("/items")
async def get_items(search: Annotated[str | None, Query()] = "",
                    skip: Annotated[int | None, Query(ge=0)] = 0,
                    limit: Annotated[int | None, Query(ge=1, le=100)] = 100):
    return {"items": "not ready yet"}