import asyncio

from sqlalchemy.future import select
from sqlalchemy import Table, MetaData
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_scoped_session, \
    async_sessionmaker
from .models import Base, AccountsTable, create_stat_table, create_liked_table  # импорт моделей

# Конфигурация для подключения к базе данных
DATABASE_URL_ACCOUNTS = "sqlite+aiosqlite:///./database/accounts.db"
DATABASE_URL_STATISTIC = "sqlite+aiosqlite:///./database/statistic.db"
DATABASE_URL_LIKE = "sqlite+aiosqlite:///./database/liked_accounts.db"

# Создание асинхронного движка
engine_accounts: AsyncEngine = create_async_engine(DATABASE_URL_ACCOUNTS, echo=True)
engine_statistic: AsyncEngine = create_async_engine(DATABASE_URL_STATISTIC, echo=True)
engine_like: AsyncEngine = create_async_engine(DATABASE_URL_LIKE, echo=True)


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

liked_db_session = async_scoped_session(
    async_sessionmaker
        (
        engine_like,
        expire_on_commit=False,
        class_=AsyncSession
    ),
    scopefunc=get_current_task
)


async def transfer_data(chat_id, accounts_session, statistics_session, liked_session):
    # Извлекаем данные пользователя из таблицы AccountsTable
    async with accounts_session() as session:
        result = await session.execute(
            select(AccountsTable).where(AccountsTable.chat_id == chat_id)
        )
        account = result.scalar_one_or_none()

    if account:
        # Создаем таблицу для статистики с именем stat_{chat_id}
        await create_stat_table(chat_id, engine_statistic)
        await create_liked_table(chat_id, engine_like)

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


async def transfer_all_accounts_data(accounts_session, statistics_session, liked_session):
    async with accounts_session() as session:
        # Получаем всех пользователей из AccountsTable
        result = await session.execute(select(AccountsTable))
        accounts = result.scalars().all()

    # Для каждого пользователя создаем таблицу и переносим данные
    for account in accounts:
        await transfer_data(account.chat_id, accounts_session, statistics_session, liked_session)


async def save_like(user_chat_id: int, liked_chat_id: int):
    """Сохраняет факт лайка в базу данных."""
    async with liked_db_session() as session:
        liked_table = await create_liked_table(user_chat_id, engine_like)
        insert_stmt = liked_table.insert().values(
            chat_id=user_chat_id,
            liked_account=liked_chat_id
        )
        await session.execute(insert_stmt)
        await session.commit()


async def check_mutual_like(liked_chat_id: int, user_chat_id: int) -> bool:
    """Проверяет, был ли взаимный лайк."""
    async with liked_db_session() as session:
        liked_table = await create_liked_table(liked_chat_id, engine_like)
        result = await session.execute(
            select(liked_table).where(liked_table.c.liked_account == user_chat_id)
        )
        return result.scalar_one_or_none() is not None


# Базовый класс для моделей
# Функция для автоматического создания таблиц
async def init_db():
    async with engine_accounts.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=[AccountsTable.__table__])


def create_db():
    asyncio.run(init_db())
    asyncio.run(transfer_all_accounts_data(accounts_db_session, statistics_db_session, liked_db_session))
