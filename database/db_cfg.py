from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_scoped_session, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from .models import Base, StatTable, AccountsTable  # импорт моделей
import asyncio

# Конфигурация для подключения к базе данных
DATABASE_URL_ACCOUNTS = "sqlite+aiosqlite:///./database/accounts.db"
DATABASE_URL_STATISTIC = "sqlite+aiosqlite:///./database/statistic.db"

# Создание асинхронного движка
engine_accounts: AsyncEngine = create_async_engine(DATABASE_URL_ACCOUNTS, echo=True)
engine_statistic: AsyncEngine = create_async_engine(DATABASE_URL_STATISTIC, echo=True)
def get_current_task():
    return asyncio.current_task()
# Создание сессий
accounts_db_session = async_scoped_session(
    async_sessionmaker
    (
        engine_accounts,
        expire_on_commit=False,
        class_=AsyncSession
    ),
    scopefunc=get_current_task
)

statistics_db_session = async_scoped_session(
    async_sessionmaker
    (
        engine_statistic,
        expire_on_commit=False,
        class_=AsyncSession
    ),
    scopefunc=get_current_task
)

# Базовый класс для моделей
# Функция для автоматического создания таблиц
async def init_db():
    async with engine_accounts.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=[AccountsTable.__table__])

    async with engine_statistic.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=[StatTable.__table__])


def create_db():
    asyncio.run(init_db())
