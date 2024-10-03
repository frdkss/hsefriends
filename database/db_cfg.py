from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, async_scoped_session
import asyncio

accounts_db_engine = create_async_engine('sqlite+aiosqlite:///./database/accounts.db')
def get_current_task():
    return asyncio.current_task()
accounts_db_session = async_scoped_session(
    async_sessionmaker(bind=accounts_db_engine),
    scopefunc=get_current_task
)
# Настройка второй базы данных
# db2_engine = create_engine('sqlite:///./databases/my_database2.db')
# db2_session = scoped_session(sessionmaker(bind=db2_engine))

async def create_db():
    from .models import Base
    async with accounts_db_engine.begin() as conn:
        # This creates the tables in the database.
        await conn.run_sync(Base.metadata.create_all)


