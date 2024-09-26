from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Настройка первой базы данных
accounts_db_engine = create_engine('sqlite:///./database/accounts.db')
accounts_db_session = scoped_session(sessionmaker(bind=accounts_db_engine))

# Настройка второй базы данных
# db2_engine = create_engine('sqlite:///./databases/my_database2.db')
# db2_session = scoped_session(sessionmaker(bind=db2_engine))

def create_db():
    from .models import Base
    # Создаем таблицы в обеих базах
    Base.metadata.create_all(accounts_db_engine)
#     Base.metadata.create_all(db2_engine)


