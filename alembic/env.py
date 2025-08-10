import asyncio
from logging.config import fileConfig
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from app.database import Base

load_dotenv()

config = context.config

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    """
    Rodar migrações no modo offline.

    Args:
        - None

    Author: Patrick Lima (patrickwsl)

    Date: 09th August 2025
    
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """
    Rodar migrações no modo online (async).
    
    Args:
        - None

    Author: Patrick Lima (patrickwsl)

    Date: 09th August 2025
    """
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=None,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda sync_conn: context.configure(
                connection=sync_conn,
                target_metadata=target_metadata
            )
        )

        await connection.run_sync(lambda _: context.run_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
