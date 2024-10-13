import os
import html

from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from keyboards.inline_keyboards import main_menu, main_settings, assessment_menu, research
from keyboards.default_keyboards import confirmation

from states import rewrite_state

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


async def get_next_account(chat_id):
    async with accounts_db_session() as session:
        user = await session.execute(
            select(AccountsTable).filter_by(chat_id=chat_id)
        )
        user = user.scalar_one_or_none()

        if user:
            # Получаем анкеты, исключая те, на которые пользователь нажал "like"
            liked_accounts = await session.execute(
                select(LikedAccountsTable).filter_by(chat_id=chat_id)
            )
            liked_uids = [acc.uid for acc in liked_accounts.scalars().all()]

            results = await search_accounts(user.isMale, user.friend_sex, user.age, user.chat_id)

            # Фильтруем анкеты, исключая те, которые пользователь лайкнул
            next_accounts = [acc for acc in results if acc.uid > user.last_uid and acc.uid not in liked_uids]
            if next_accounts:
                next_account = next_accounts[0]
                user.last_uid = next_account.uid  # Обновляем last_uid
                await session.commit()  # Коммитим изменения last_uid
                return next_account
    return None


async def display_account(event: CallbackQuery, account):
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
        await event.message.answer_photo(photo=photo, caption=profile_text, reply_markup=assessment_menu)
    else:
        await event.message.answer(profile_text, reply_markup=assessment_menu)


async def add_liked_account(chat_id, liked_uid):
    async with accounts_db_session() as session:
        liked_entry = LikedAccountsTable(chat_id=chat_id, liked_uid=liked_uid)
        session.add(liked_entry)
        await session.commit()


@router.callback_query(F.data == "menu")
async def callback_menu(event: Message | CallbackQuery):
    async with accounts_db_session() as session:  # Use async context manager
        async with session.begin():  # Optional: use a transaction
            # Use the asynchronous query method
            user_result = await session.execute(
                select(AccountsTable).filter_by(chat_id=event.chat.id)
            )
            user = user_result.scalar_one_or_none()  # Get the first result or None

            hour = datetime.now().hour

            greetings = {
                (6, 12): "Доброе утро",
                (12, 18): "Добрый день",
                (18, 24): "Добрый вечер",
                (0, 6): "Доброй ночи",
            }
            greeting = next((msg for (start, end), msg in greetings.items() if start <= hour < end), "Привет")

            if isinstance(event, Message):
                await event.answer(f"{greeting} {html.escape(user.name)}! Добро пожаловать в меню", reply_markup=main_menu)
            elif isinstance(event, CallbackQuery):
                await event.message.delete()
                await event.message.answer(f"{greeting} {html.escape(user.name)}! Добро пожаловать в меню", reply_markup=main_menu)
            await session.close()


@router.callback_query(F.data == "profile")
async def callback_profile(event: Message | CallbackQuery):
    async with accounts_db_session() as session:
        async with session.begin():
            user_result = await session.execute(
                select(AccountsTable).filter_by(chat_id=event.message.chat.id)
            )
            user = user_result.scalar_one_or_none()

            gender = "Парень" if user.isMale else "Девушка"
            degree = "Бакалавриат" if user.isBaccalaureate else "Магистратура"
            friend_sex = {
                "males": "Парней",
                "females": "Девушек",
                "dont_care": "И парней и девушек"
            }.get(user.friend_sex, "Не указано")

            profile_text = (
                f"Ваш профиль:\n"
                f"Имя - {html.escape(user.name)}\n"
                f"Возраст - {user.age}\n"
                f"Пол - {gender}\n"
                f"Факультет - {user.faculty}\n"
                f"Степень - {degree}\n"
                f"Курс - {user.course}\n"
            )

            if user.about:
                profile_text += f"О тебе - {user.about}\n"

            profile_text += f"Ты ищешь - {friend_sex}"

            if isinstance(event, CallbackQuery):
                if user.photo:
                    # Загружаем фото как InputFile
                    photo_path = os.path.abspath(os.path.join("account_photos", str(user.chat_id), user.photo))
                    photo = FSInputFile(photo_path)
                    await event.message.answer_photo(
                        photo=photo,
                        caption=profile_text
                    )
                else:
                    await event.message.answer(profile_text)
            await session.close()


@router.callback_query(F.data == "settings")
async def callback_settings(event: Message | CallbackQuery):
    if isinstance(event, Message):
        await event.answer("Настройки:", reply_markup=main_settings)
    elif isinstance(event, CallbackQuery):
        await event.message.delete()
        await event.message.answer("Настройки:", reply_markup=main_settings)


@router.callback_query(F.data == "rewrite_profile")
async def callback_rewrite_profile(call: CallbackQuery, state: FSMContext):
    await rewrite_state.user_rewrite(call, state)


@router.callback_query(F.data == "off_profile")
async def callback_disconnect_account(event: Message | CallbackQuery):
    if isinstance(event, Message):
        await event.answer("Вы уверенны?", reply_markup=confirmation)
    elif isinstance(event, CallbackQuery):
        await event.message.delete()
        await event.message.answer("Вы уверенны?", reply_markup=confirmation)

    @router.message(F.text.in_(["Да", "Нет"]))
    async def handle_confirmation(message: Message):
        if message.text.lower() == "да":
            pass
        elif message.text.lower() == "нет":
            await callback_settings(message)


@router.callback_query(F.data == "delete_profile")
async def callback_delete_account(event: Message | CallbackQuery):
    if isinstance(event, Message):
        await event.answer("Вы уверенны?", reply_markup=confirmation)
    elif isinstance(event, CallbackQuery):
        await event.message.answer("Вы уверенны?", reply_markup=confirmation)

    @router.message(F.text.in_(["Да", "Нет"]))
    async def handle_confirmation(message: Message):
        if message.text.lower() == "да":
            pass
        elif message.text.lower() == "нет":
            await callback_settings(message)


@router.callback_query(F.data == "start_search")
async def callback_find_people(event: CallbackQuery):
    async with accounts_db_session() as session:
        user = await session.execute(
            select(AccountsTable).filter_by(chat_id=event.message.chat.id)
        )
        user = user.scalar_one_or_none()

        if user:
            # Получаем следующую анкету с last_uid
            next_account = await get_next_account(user.chat_id)

            if next_account:
                await display_account(event, next_account)  # Отправляем новую анкету
            else:
                await event.message.answer(
                    "Анкеты закончились. Выберите действие:",
                    reply_markup=research  # Используем клавиатуру research
                )


@router.callback_query(F.data == "like")
async def callback_like(event: CallbackQuery):
    user_chat_id = event.message.chat.id

    # Получаем следующую анкету
    account = await get_next_account(user_chat_id)

    if account:
        await display_account(event, account)
    else:
        await event.message.delete()  # Удаляем предыдущее сообщение
        await event.message.answer(
            "Анкеты закончились. Выберите действие:",
            reply_markup=research  # Используем клавиатуру research
        )


@router.callback_query(F.data == "dislike")
async def callback_dislike(event: CallbackQuery):
    user_chat_id = event.message.chat.id

    # Получаем следующую анкету
    account = await get_next_account(user_chat_id)

    if account:
        await display_account(event, account)
    else:
        await event.message.delete()  # Удаляем предыдущее сообщение
        await event.message.answer(
            "Анкеты закончились. Выберите действие:",
            reply_markup=research  # Используем клавиатуру research
        )


@router.callback_query(F.data == "restart_search")
async def restart_search(event: CallbackQuery):
    user_chat_id = event.message.chat.id

    async with accounts_db_session() as session:
        user = await session.execute(
            select(AccountsTable).filter_by(chat_id=user_chat_id)
        )
        user = user.scalar_one_or_none()

        if user:
            user.last_uid = 0  # Сбрасываем last_uid для начала нового поиска
            await session.commit()

    account = await get_next_account(user_chat_id)
    if account:
        await event.message.delete()  # Удаляем предыдущее сообщение
        await display_account(event, account)
    else:
        await event.message.delete()  # Удаляем предыдущее сообщение
        await event.message.answer("Анкеты не найдены.")


@router.callback_query(F.data == "update_search")
async def update_search(event: CallbackQuery):
    user_chat_id = event.message.chat.id
    account = await get_next_account(user_chat_id)

    if account:
        await event.message.delete()  # Удаляем предыдущее сообщение
        await display_account(event, account)
    else:
        await event.message.delete()  # Удаляем предыдущее сообщение
        await event.message.answer(
            "Новых анкет нет. Выберите действие:",
            reply_markup=research  # Используем клавиатуру для предложений действий
        )


@router.callback_query(F.data == "feedback")
async def callback_feedback(event: Message | CallbackQuery):
    pass


@router.callback_query(F.data == "edit_profile")
async def callback_edit_profile(event: Message | CallbackQuery):
    pass


@router.callback_query(F.data == "edit_name")
async def callback_edit_name(event: Message | CallbackQuery):
    pass


@router.callback_query(F.data == "edit_age")
async def callback_edit_age(event: Message | CallbackQuery):
    pass


@router.callback_query(F.data == "edit_sex")
async def callback_edit_sex(event: Message | CallbackQuery):
    pass


@router.callback_query(F.data == "edit_faculty")
async def callback_edit_faculty(event: Message | CallbackQuery):
    pass


@router.callback_query(F.data == "edit_degree")
async def callback_edit_degree(event: Message | CallbackQuery):
    pass


@router.callback_query(F.data == "edit_course")
async def callback_edit_course(event: Message | CallbackQuery):
    pass


@router.callback_query(F.data == "edit_photo")
async def callback_edit_photo(event: Message | CallbackQuery):
    pass


@router.callback_query(F.data == "edit_about")
async def callback_edit_about(event: Message | CallbackQuery):
    pass


@router.callback_query(F.data == "edit_friend_sex")
async def callback_edit_friend_sex(event: Message | CallbackQuery):
    pass
