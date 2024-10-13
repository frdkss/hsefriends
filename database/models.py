from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy import Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncEngine

Base = declarative_base()


class AccountsTable(Base):
    __tablename__ = 'Accounts'
    # autofill
    uid = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False, unique=True)
    tg_id = Column(String, nullable=False, unique=True)
    isActive = Column(Boolean, nullable=False)
    deleted_in = Column(String, nullable=True)
    registration_time = Column(String, nullable=False)
    # user info
    name = Column(String(30), nullable=False)
    age = Column(Integer, nullable=False)
    isMale = Column(Boolean, nullable=False)
    faculty = Column(String(130), nullable=False)
    isBaccalaureate = Column(Boolean, nullable=False)
    course = Column(Integer, nullable=False)
    photo = Column(String, nullable=True)
    about = Column(String, nullable=True)
    friend_sex = Column(String, nullable=False)
    # temp
    last_uid = Column(Integer, default=0)


class LikedAccountsTable(Base):
    __tablename__ = 'LikedAccounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey('Accounts.chat_id'), nullable=False)  # Идентификатор пользователя
    liked_uid = Column(Integer, ForeignKey('Accounts.uid'), nullable=False)  # Идентификатор лайкнутой анкеты


async def create_stat_table(chat_id, engine: AsyncEngine):
    table_name = f"stat_{chat_id}"
    metadata = MetaData()

    stat_table = Table(
        table_name,
        metadata,
        # autofill from accounts
        Column('id', Integer, primary_key=True),
        Column('chat_id', Integer, nullable=False),
        Column('tg_id', String, nullable=False),
        Column('isMale', Boolean, nullable=False),
        Column('age', Integer, nullable=False),
        Column('friend_sex', String, nullable=False),
        Column('registration_time', String(17)),
        # autofill from user action
        Column('likes', Integer, default=0),
        Column('dislikes', Integer, default=0),
        Column('profile_likes', Integer, default=0),
        Column('profile_dislikes', Integer, default=0),
        Column('user_sessions', Integer),
        Column('time_session', Integer),
        extend_existing=True
    )

    # Используем асинхронный контекст для создания таблицы
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    return stat_table
