from pathlib import Path

from app.database.db import Database


DEFAULT_CATEGORIES = [
    "Продукты",
    "Транспорт",
    "Квартира",
    "Развлечения",
]


async def init_db(db: Database) -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    sql = schema_path.read_text(encoding="utf-8")
    async with db.pool.acquire() as conn:
        await conn.execute(sql)
