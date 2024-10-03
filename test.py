from static.algoritm_search import search_accounts

results = search_accounts(True, 'dont_care', user_age=18, user_chat_id=6073391200)
print(f"Найдено {len(results)} анкет:")
for account in results:
    print(account.name, account.age, account.isMale, account.friend_sex)