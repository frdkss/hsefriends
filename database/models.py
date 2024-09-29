from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

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

# class MyTable2(Base):
#     __tablename__ = 'my_table2'
#     id = Column(Integer, primary_key=True)
#     value = Column(Integer)
