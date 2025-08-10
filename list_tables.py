import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = os.getenv("DATABASE_URL")

async def main():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT table_schema, table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'"))
        tables = result.fetchall()
        if not tables:
            print("Nenhuma tabela encontrada.")
        for schema, name in tables:
            print(f"{schema}.{name}")

asyncio.run(main())
