import os
import html

from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile

from sqlalchemy.future import select
from sqlalchemy import or_, and_

from keyboards.inline_keyboards import assessment_menu, research

from database.db_cfg import accounts_db_session
from database.models import AccountsTable, LikedAccountsTable

router = Router()


async def search_accounts(user_is_male: bool, user_preference: str, user_age: int, user_chat_id: int):
    # Исключаем текущего пользователя из поиска
    query = select(AccountsTable).filter(AccountsTable.chat_id != user_chat_id)

    # Логика для мужчины
    if user_is_male:
        if user_preference == 'males':
            # Мужчина ищет мужчин
            query = query.filter(
                AccountsTable.isMale == True,  # Только мужчины
                or_(
                    AccountsTable.friend_sex == 'males',  # Которые ищут мужчин
                    AccountsTable.friend_sex == 'dont_care'  # Или им всё равно
                ),
                # Скрываем мужчин, которые ищут женщин
                and_(
                    AccountsTable.friend_sex != 'females'
                )
            )
        elif user_preference == 'females':
            # Мужчина ищет женщин
            query = query.filter(
                AccountsTable.isMale == False,  # Только женщины
                or_(
                    AccountsTable.friend_sex == 'males',  # Которые ищут мужчин
                    AccountsTable.friend_sex == 'dont_care'  # Или им всё равно
                ),
                # Скрываем женщин, которые ищут женщин
                and_(
                    AccountsTable.friend_sex != 'females'
                )
            )
        elif user_preference == 'dont_care':
            # Мужчина ищет и мужчин, и женщин
            query = query.filter(
                or_(
                    and_(
                        AccountsTable.isMale == True,  # Мужчины
                        or_(
                            AccountsTable.friend_sex == 'males',  # Ищут мужчин
                            AccountsTable.friend_sex == 'dont_care'  # Им всё равно
                        )
                    ),
                    and_(
                        AccountsTable.isMale == False,  # Женщины
                        or_(
                            AccountsTable.friend_sex == 'males',  # Ищут мужчин
                            AccountsTable.friend_sex == 'dont_care'  # Им всё равно
                        )
                    )
                ),
                # Скрываем мужчин, которые ищут женщин, и женщин, которые ищут женщин
                or_(
                    AccountsTable.isMale == True,
                    and_(
                        AccountsTable.isMale == False,
                        AccountsTable.friend_sex != 'females'
                    )
                )
            )

    # Логика для женщины
    else:
        if user_preference == 'males':
            # Женщина ищет мужчин
            query = query.filter(
                AccountsTable.isMale == True,  # Только мужчины
                or_(
                    AccountsTable.friend_sex == 'females',  # Ищут женщин
                    AccountsTable.friend_sex == 'dont_care'  # Им всё равно
                ),
                # Скрываем мужчин, которые ищут мужчин
                and_(
                    AccountsTable.friend_sex != 'males'
                )
            )
        elif user_preference == 'females':
            # Женщина ищет женщин
            query = query.filter(
                AccountsTable.isMale == False,  # Только женщины
                or_(
                    AccountsTable.friend_sex == 'females',  # Ищут женщин
                    AccountsTable.friend_sex == 'dont_care'  # Им всё равно
                ),
                # Скрываем женщин, которые ищут мужчин
                and_(
                    AccountsTable.friend_sex != 'males'
                )
            )
        elif user_preference == 'dont_care':
            # Женщина ищет и мужчин, и женщин
            query = query.filter(
                or_(
                    and_(
                        AccountsTable.isMale == True,  # Мужчины
                        or_(
                            AccountsTable.friend_sex == 'females',  # Ищут женщин
                            AccountsTable.friend_sex == 'dont_care'  # Им всё равно
                        )
                    ),
                    and_(
                        AccountsTable.isMale == False,  # Женщины
                        or_(
                            AccountsTable.friend_sex == 'females',  # Ищут женщин
                            AccountsTable.friend_sex == 'dont_care'  # Им всё равно
                        )
                    )
                ),
                # Скрываем мужчин, которые ищут мужчин, и женщин, которые ищут мужчин
                or_(
                    AccountsTable.isMale == True,
                    and_(
                        AccountsTable.isMale == False,
                        AccountsTable.friend_sex != 'males'
                    )
                )
            )

    # Выполняем запрос
    result = await accounts_db_session.execute(query)
    return result.scalars().all()


async def get_next_acc(chat_id):
    pass


async def display_acc(call: CallbackQuery, account):
    gender = "Парень" if account.isMale else "Девушка"
    degree = "Бакалавриат" if account.isBaccalaureate else "Магистратура"

    profile_text = (
        f"Имя - {html.escape(account.name)}\n"
        f"Возраст - {account.age}\n"
        f"Пол - {gender}\n"
        f"Факультет - {account.faculty}\n"
        f"Степень - {degree}\n"
        f"Курс - {account.course}\n"
    )
    if account.about:
        profile_text += f"О тебе - {account.about}\n"

    if account.photo:
        photo_path = os.path.abspath(os.path.join("account_photos", str(account.chat_id), account.photo))
        photo = FSInputFile(photo_path)
        await call.message.answer_photo(photo=photo, caption=profile_text, reply_markup=assessment_menu)
    else:
        await call.message.answer(profile_text, reply_markup=assessment_menu)


async def add_liked_account(chat_id, liked_uid):
    async with accounts_db_session() as session:
        pass


@router.callback_query(F.data == "start_search")
async def callback_search(call: CallbackQuery):
    async with accounts_db_session() as session:
        async with session.begin():
            pass


@router.callback_query(F.data == "like")
async def callback_like(call: CallbackQuery):
    pass


@router.callback_query(F.data == "dislike")
async def callback_dislike(call: CallbackQuery):
    pass


@router.callback_query(F.data == "update_search")
async def update_search(event: CallbackQuery):
    user_chat_id = event.message.chat.id
    account = await get_next_acc(user_chat_id)

    if account:
        await event.message.delete()  # Удаляем предыдущее сообщение
        await display_acc(event, account)
    else:
        await event.message.delete()  # Удаляем предыдущее сообщение
        await event.message.answer(
            "Новых анкет нет. Выберите действие:",
            reply_markup=research  # Используем клавиатуру для предложений действий
        )
