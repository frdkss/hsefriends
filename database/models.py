from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
Base = declarative_base()

class AccountsTable(Base):
    __tablename__ = 'Accounts'
    # autofill
    uid = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False, unique=True)
    tg_id = Column(String, nullable=False, unique=True)
    isActive = Column(Boolean, nullable=False)
    deleted_in = Column(String, nullable=True)
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
    #temp
    last_uid = Column(Integer, default=0)

    # Связь с таблицей StatisticTable (один ко многим)
    statistics = relationship("StatTable", back_populates="account")


class StatTable(Base):
    __tablename__ = 'StatisticTable'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    tg_id = Column(String, nullable=False)
    isMale = Column(Boolean, nullable=False)
    age = Column(Integer, nullable=False)
    friend_sex = Column(String, nullable=False)

    reg = Column(String(10))

    # Связь с таблицей AccountsTable (многие к одному)
    account_id = Column(Integer, ForeignKey('Accounts.uid'))
    account = relationship("AccountsTable", back_populates="statistics")


# class StatisticTable(Base):
#     @declared_attr
#     def __tablename__(cls):
#         return f'Stat_{cls.account.chat_id}'
#     # autofill
#     id = Column(Integer, primary_key=True)
#
#     account_id = Column(Integer, ForeignKey('Accounts.uid'), nullable=False)
#     account = relationship("AccountsTable", back_populates="statistics")
#
#     chat_id = Column(Integer, nullable=False, unique=True)
#     age = Column(Integer, nullable=False)
#     isMale = Column(Boolean, nullable=False)
#     tg_id = Column(String, nullable=False, unique=True)
#
#     likes = Column(Integer, default=0)
#     dislikes = Column(Integer, default=0)
#
#     profile_likes = Column(Integer, default=0)
#     profile_dislikes = Column(Integer, default=0)
#
#     user_sessions = Column(Integer)
#     time_session = Column(Integer)
#
#     registration_time = Column(String(17))
#
#     def __init__(self, account: AccountsTable):
#         self.account = account
