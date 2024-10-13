import asyncio

from datetime import datetime

from sqlalchemy.future import select
from sqlalchemy import Table, MetaData
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_scoped_session, async_sessionmaker
from .models import Base, AccountsTable, LikedAccountsTable, create_stat_table  # импорт моделей

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
        await conn.run_sync(Base.metadata.create_all, tables=[AccountsTable.__table__, LikedAccountsTable.__table__])

    # async with engine_statistic.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all, tables=[StatTable.__table__])


async def transfer_data(chat_id, accounts_session, statistics_session):
    # Извлекаем данные пользователя из таблицы AccountsTable
    async with accounts_session() as session:
        result = await session.execute(
            select(AccountsTable).where(AccountsTable.chat_id == chat_id)
        )
        account = result.scalar_one_or_none()

    if account:
        # Создаем таблицу для статистики с именем stat_{chat_id}
        await create_stat_table(chat_id, engine_statistic)

        # Открываем соединение с асинхронным движком
        async with engine_statistic.begin() as conn:
            # Используем run_sync для выполнения синхронных операций
            def load_table(connection):
                metadata = MetaData()
                stat_table = Table(f"stat_{chat_id}", metadata, autoload_with=connection)
                return stat_table

            # Выполняем операцию синхронной загрузки таблицы
            stat_table = await conn.run_sync(load_table)

            # Заполняем статистическую таблицу данными из AccountsTable
            insert_stmt = stat_table.insert().values(
                chat_id=account.chat_id,
                tg_id=account.tg_id,
                isMale=account.isMale,
                age=account.age,
                friend_sex=account.friend_sex,
                registration_time=account.registration_time  # например, текущее время регистрации
            )
            await statistics_session.execute(insert_stmt)
            await statistics_session.commit()


async def transfer_all_accounts_data(accounts_session, statistics_session):
    async with accounts_session() as session:
        # Получаем всех пользователей из AccountsTable
        result = await session.execute(select(AccountsTable))
        accounts = result.scalars().all()

    # Для каждого пользователя создаем таблицу и переносим данные
    for account in accounts:
        await transfer_data(account.chat_id, accounts_session, statistics_session)


def create_db():
    asyncio.run(init_db())
    asyncio.run(transfer_all_accounts_data(accounts_db_session, statistics_db_session))
