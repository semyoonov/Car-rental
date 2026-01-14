import asyncio
from tortoise import Tortoise

DB_URL = "sqlite://db.sqlite3"

async def init_db():
    await Tortoise.init(
        db_url=DB_URL,
        modules={"models": ["database.models"]}
    )
    await Tortoise.generate_schemas()

def init_db_sync():
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(init_db())
    except RuntimeError:
        asyncio.run(init_db())