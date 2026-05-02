from redis.asyncio import from_url

from app.core.config import settings

redis_client = from_url(settings.REDIS_URL, decode_responses=True)

async def invalidate_cache(item_id: int | None = None):
    keys = await redis_client.keys("items:*")
    if keys:
        await redis_client.delete(*keys)
    if item_id is not None:
        await redis_client.delete(f"item:{item_id}")