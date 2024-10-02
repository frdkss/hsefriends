from sqlalchemy import or_, and_
from database.db_cfg import accounts_db_session
from database.models import AccountsTable

def search_accounts(user_is_male: bool, user_preference: str):
    session = accounts_db_session()

    if user_preference not in ['males', 'females', 'dont_care']:
        return []  # Если предпочтение указано неправильно

    query = session.query(AccountsTable)

    if user_is_male:
        # Пользователь - мужчина
        if user_preference == 'males':
            # Ищет мужчин
            query = query.filter(
                AccountsTable.isMale == True,
                or_(
                    AccountsTable.friend_sex == 'males',
                    AccountsTable.friend_sex == 'dont_care'
                )
            )
        elif user_preference == 'females':
            # Ищет женщин
            query = query.filter(
                AccountsTable.isMale == False,
                or_(
                    AccountsTable.friend_sex == 'males',
                    AccountsTable.friend_sex == 'dont_care'
                )
            )
        elif user_preference == 'dont_care':
            # Ему все равно
            query = query.filter(
                or_(
                    and_(
                        AccountsTable.isMale == True,
                        or_(
                            AccountsTable.friend_sex == 'males',
                            AccountsTable.friend_sex == 'dont_care'
                        )
                    ),
                    and_(
                        AccountsTable.isMale == False,
                        or_(
                            AccountsTable.friend_sex == 'males',
                            AccountsTable.friend_sex == 'dont_care'
                        )
                    )
                )
            )

    else:
        # Пользователь - женщина
        if user_preference == 'males':
            # Ищет мужчин
            query = query.filter(
                AccountsTable.isMale == True,
                or_(
                    AccountsTable.friend_sex == 'females',
                    AccountsTable.friend_sex == 'dont_care'
                )
            )
        elif user_preference == 'females':
            # Ищет женщин
            query = query.filter(
                AccountsTable.isMale == False,
                or_(
                    AccountsTable.friend_sex == 'females',
                    AccountsTable.friend_sex == 'dont_care'
                )
            )
        elif user_preference == 'dont_care':
            # Ей все равно
            query = query.filter(
                or_(
                    and_(
                        AccountsTable.isMale == True,
                        or_(
                            AccountsTable.friend_sex == 'females',
                            AccountsTable.friend_sex == 'dont_care'
                        )
                    ),
                    and_(
                        AccountsTable.isMale == False,
                        or_(
                            AccountsTable.friend_sex == 'females',
                            AccountsTable.friend_sex == 'dont_care'
                        )
                    )
                )
            )

    print(str(query))  # Выводим запрос для отладки
    results = query.all()
    session.close()

    return results

# Пример: женщина ищет мужчин
results = search_accounts(True, 'females')
print(f"Найдено {len(results)} анкет:")
for account in results:
    print(account.name, account.age, account.isMale, account.friend_sex)
