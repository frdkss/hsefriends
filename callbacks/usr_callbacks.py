import html
import os

from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.future import select
from sqlalchemy import or_, and_, text, not_, exists

from keyboards.inline_keyboards import main_menu, main_settings, assessment_menu, research, feedback_url, back_to_main, \
    edit_profile, first_registration_keyboard, next_anketa
from keyboards.default_keyboards import confirmation

from database.db_cfg import accounts_db_session, save_like, liked_db_session, engine_like
from database.models import AccountsTable, create_liked_table

router = Router()


async def search_accounts(user_is_male: bool, user_preference: str, user_age: int, user_chat_id: int):
    # Создаем запрос для основной таблицы анкет
    query = select(AccountsTable).filter(AccountsTable.chat_id != user_chat_id)

    # Фильтрация по полу и предпочтениям пользователя
    if user_is_male:
        if user_preference == 'males':
            query = query.filter(
                AccountsTable.isMale == True,
                or_(
                    AccountsTable.friend_sex == 'males',
                    AccountsTable.friend_sex == 'dont_care'
                )
            )
        elif user_preference == 'females':
            query = query.filter(
                AccountsTable.isMale == False,
                or_(
                    AccountsTable.friend_sex == 'males',
                    AccountsTable.friend_sex == 'dont_care'
                )
            )
        elif user_preference == 'dont_care':
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
        # Аналогичная логика для пользователя-женщины
        if user_preference == 'males':
            query = query.filter(
                AccountsTable.isMale == True,
                or_(
                    AccountsTable.friend_sex == 'females',
                    AccountsTable.friend_sex == 'dont_care'
                )
            )
        elif user_preference == 'females':
            query = query.filter(
                AccountsTable.isMale == False,
                or_(
                    AccountsTable.friend_sex == 'females',
                    AccountsTable.friend_sex == 'dont_care'
                )
            )
        elif user_preference == 'dont_care':
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

    # Дополнительная логика фильтрации по isLiked и isDisliked
    async with liked_db_session() as session:
        liked_table = f"liked_{user_chat_id}"
        sql_query = text(f"SELECT chat_id FROM {liked_table} WHERE isLiked = True OR isDisliked = True")
        result = await session.execute(sql_query)

        excluded_chat_ids = [row[0] for row in result.fetchall()]
        if excluded_chat_ids:
            query = query.filter(~AccountsTable.chat_id.in_(excluded_chat_ids))

    result = await accounts_db_session.execute(query)
    return result.scalars().all()


async def get_next_account(chat_id, update_last_uid=True):
    async with accounts_db_session() as session:
        async with session.begin():
            user = await session.execute(
                select(AccountsTable).filter_by(chat_id=chat_id)
            )
            user = user.scalar_one_or_none()

            if user:
                # Получаем список анкет с учётом last_uid
                results = await search_accounts(user.isMale, user.friend_sex, user.age, user.chat_id)

                # Фильтруем анкеты, которые еще не были просмотрены
                next_accounts = [acc for acc in results if acc.uid > user.last_uid]

                if next_accounts:
                    next_account = next_accounts[0]

                    # Обновляем last_uid только если нужно (например, при успешном показе новой анкеты)
                    if update_last_uid:
                        user.last_uid = next_account.uid
                        await session.commit()
                    return next_account
                else:
                    # Если все анкеты просмотрены, сбрасываем last_uid для повторного поиска
                    if update_last_uid:
                        user.last_uid = 0  # Сбрасываем last_uid, чтобы начать просмотр заново
                        await session.commit()
                    return None
            await session.close()
    return None


async def display_account(event: CallbackQuery, account):
    gender = "Парень" if account.isMale else "Девушка"
    degree = "Бакалавриат" if account.isBaccalaureate else "Магистратура"

    # Формируем текст профиля
    profile_text = (
        f"Имя - {html.escape(account.name)}\n"
        f"Возраст - {account.age}\n"
        f"Пол - {gender}\n"
        f"Программа - {account.faculty}\n"
        f"Уровень образования - {degree}\n"
        f"Курс - {account.course}\n"
    )
    if account.about:
        profile_text += f"О себе - {account.about}\n"

    # Удаляем предыдущее сообщение
    await event.message.delete()

    # Если есть фотография, отправляем ее
    if account.photo:
        photo_path = os.path.abspath(os.path.join(account.photo))
        photo = FSInputFile(photo_path)
        await event.message.answer_photo(photo=photo, caption=profile_text, reply_markup=assessment_menu)
    else:
        await event.message.answer(profile_text, reply_markup=assessment_menu)


async def send_profile(event: CallbackQuery, chat_id: int, account):
    """Отправляет анкету пользователя."""
    gender = "Парень" if account.isMale else "Девушка"
    degree = "Бакалавриат" if account.isBaccalaureate else "Магистратура"

    profile_text = (
        f"Имя - {html.escape(account.name)}\n"
        f"Возраст - {account.age}\n"
        f"Пол - {gender}\n"
        f"Программа - {account.faculty}\n"
        f"Уровень образования - {degree}\n"
        f"Курс - {account.course}\n"
    )
    if account.about:
        profile_text += f"О себе - {account.about}\n"

    # Отправляем анкету с фото или без него
    if account.photo:
        photo_path = os.path.abspath(account.photo)
        photo = FSInputFile(photo_path)
        await event.bot.send_photo(chat_id, photo=photo, caption=profile_text)
    else:
        await event.bot.send_message(chat_id, profile_text)


async def send_like_request(event: CallbackQuery, liked_chat_id: int, user_chat_id: int):
    """Отправляет запрос на лайк другому пользователю и показывает его анкету."""

    async with accounts_db_session() as session:
        result = await session.execute(select(AccountsTable).where(AccountsTable.chat_id == user_chat_id))
        user_account = result.scalars().first()

        if not user_account:
            await event.bot.send_message(liked_chat_id, "Ошибка: пользователь не найден.")
            return

        # Формируем текст анкеты
        gender = "Парень" if user_account.isMale else "Девушка"
        degree = "Бакалавриат" if user_account.isBaccalaureate else "Магистратура"

        profile_text = (
            f"Имя - {html.escape(user_account.name)}\n"
            f"Возраст - {user_account.age}\n"
            f"Пол - {gender}\n"
            f"Программа - {user_account.faculty}\n"
            f"Уровень образования - {degree}\n"
            f"Курс - {user_account.course}\n"
        )
        if user_account.about:
            profile_text += f"О себе - {user_account.about}\n"

        # Отправляем анкету с фото или без него
        if user_account.photo:
            photo_path = os.path.abspath(user_account.photo)
            photo = FSInputFile(photo_path)
            await event.bot.send_photo(liked_chat_id, photo=photo, caption=profile_text)
        else:
            await event.bot.send_message(liked_chat_id, profile_text)

        # Отправляем запрос на лайк
        like_request = InlineKeyboardMarkup(row_width=2, inline_keyboard=[
            [
                InlineKeyboardButton(text="Взаимный лайк", callback_data=f"mutual_like_{user_chat_id}"),
                InlineKeyboardButton(text="Отказаться", callback_data="reject_like")
            ],
            [
                InlineKeyboardButton(text="В меню", callback_data="menu")
            ]
        ])
        await event.bot.send_message(
            liked_chat_id,
            "Хотите поставить лайк в ответ?",
            reply_markup=like_request
        )


async def send_mutual_like_notification(event: CallbackQuery, chat_id: int, telegram_username: str):
    """Отправляет уведомление о взаимном лайке."""
    await event.bot.send_message(
        chat_id,
        f"У вас взаимный лайк! @{telegram_username}", reply_markup=next_anketa
    )


async def delete_user_data(user_id: int):
    """Функция для удаления данных пользователя из базы."""
    async with accounts_db_session() as session:  # Используем вашу сессию
        await remove_user_from_db(session, user_id)


async def remove_user_from_db(session: AsyncSession, user_id: int):
    """Удаление пользователя из базы данных."""
    await session.execute(
        AccountsTable.__table__.delete().where(AccountsTable.chat_id == user_id)
    )
    await session.commit()


@router.callback_query(F.data == "menu")
async def callback_menu(event: Message | CallbackQuery):
    async with accounts_db_session() as session:  # Use async context manager
        async with session.begin():  # Optional: use a transaction
            # Use the asynchronous query method
            user_result = await session.execute(
                select(AccountsTable).filter_by(chat_id=event.chat.id if isinstance(event, Message) else event.message.chat.id)
            )
            user = user_result.scalar_one_or_none()  # Get the first result or None

            hour = datetime.now().hour

            greetings = {
                (6, 12): "Доброе утро,",
                (12, 18): "Добрый день,",
                (18, 24): "Добрый вечер,",
                (0, 6): "Доброй ночи,",
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
    async with accounts_db_session() as session:  # Use async context manager
        async with session.begin():  # Optional: use a transaction
            # Use the asynchronous query method
            user_result = await session.execute(
                select(AccountsTable).filter_by(chat_id=event.message.chat.id)
            )
            user = user_result.scalar_one_or_none()

            if isinstance(event, CallbackQuery):
                gender = "Парень" if user.isMale else "Девушка"
                degree = "Бакалавриат" if user.isBaccalaureate else "Магистратура"

                if user.friend_sex == "males":
                    sex_preference = "Мужчин"
                elif user.friend_sex == "females":
                    sex_preference = "Девушек"
                elif user.friend_sex == "dont_care":
                    sex_preference = "И девушек и мужчин"
                else:
                    sex_preference = "Не указано"

                # Формируем текст профиля
                profile_text = (
                    f"Имя - {html.escape(user.name)}\n"
                    f"Возраст - {user.age}\n"
                    f"Пол - {gender}\n"
                    f"Программа - {user.faculty}\n"
                    f"Уровень образования - {degree}\n"
                    f"Курс - {user.course}\n"
                    f"Ты ищешь - {sex_preference}\n"
                )
                if user.about:
                    profile_text += f"О тебе - {user.about}\n"

                # Удаляем предыдущее сообщение
                await event.message.delete()

                # Если есть фотография, отправляем ее
                if user.photo:
                    photo_path = os.path.abspath(os.path.join(user.photo))
                    photo = FSInputFile(photo_path)
                    await event.message.answer_photo(photo=photo, caption=profile_text, reply_markup=back_to_main)
                else:
                    await event.message.answer(profile_text, reply_markup=back_to_main)
                await session.close()


@router.callback_query(F.data == "settings")
async def callback_settings(event: Message | CallbackQuery):
    if isinstance(event, Message):
        await event.answer("Настройки:", reply_markup=main_settings)
    elif isinstance(event, CallbackQuery):
        await event.message.delete()
        await event.message.answer("Настройки:", reply_markup=main_settings)


@router.callback_query(F.data == "delete_profile")
async def callback_delete_account(event: Message | CallbackQuery):
    if isinstance(event, Message):
        await event.answer("Вы уверенны?", reply_markup=confirmation)
    elif isinstance(event, CallbackQuery):
        await event.message.answer("Вы уверенны?", reply_markup=confirmation)

    @router.message(F.text.in_(["Да", "Нет"]))
    async def handle_confirmation(message: Message):
        if message.text.lower() == "да":
            await delete_user_data(message.from_user.id)
            await message.answer(
                "Ваш профиль удалён. Для продолжения используйте /start.",
                reply_markup=ReplyKeyboardRemove()
            )
        elif message.text.lower() == "нет":
            await callback_settings(message)


@router.callback_query(F.data == "start_search")
async def callback_find_people(event: CallbackQuery):
    async with accounts_db_session() as session:
        async with session.begin():
            user = await session.execute(
                select(AccountsTable).filter_by(chat_id=event.message.chat.id)
            )
            user = user.scalar_one_or_none()

            if user:
                # Создаем таблицы для статистики и liked перед поиском
                await create_liked_table(user.chat_id, engine_like)

                results = await search_accounts(user.isMale, user.friend_sex, user.age, user.chat_id)
                print(results)
                print(f"Найдено {len(results)} анкет:")

                for account in results:
                    print(account.name, account.age, account.isMale, account.friend_sex)

                if results:
                    first_account = results[0]  # Берем первую анкету
                    await display_account(event, first_account)  # Отправляем анкету с фото или текстом
                else:
                    await event.message.edit_text("Анкеты не найдены.")
            await session.close()

@router.callback_query(F.data == "like")
async def callback_like(event: CallbackQuery):
    user_chat_id = event.message.chat.id
    liked_account = await get_next_account(user_chat_id, update_last_uid=True)

    if liked_account:
        await save_like(user_chat_id, liked_account.chat_id)

        # Устанавливаем isLiked = True в таблице liked_{user_chat_id}
        async with liked_db_session() as session:
            liked_table = f"liked_{user_chat_id}"
            await session.execute(
                text(f"UPDATE {liked_table} SET isLiked = True WHERE chat_id = :chat_id"),
                {"chat_id": liked_account.chat_id}
            )
            await session.commit()

        await send_like_request(event, liked_account.chat_id, user_chat_id)

        next_account = await get_next_account(user_chat_id, update_last_uid=False)
        if next_account:
            await display_account(event, next_account)
        else:
            await event.message.delete()
            await event.message.answer(
                "Анкеты закончились. Выберите действие:",
                reply_markup=research
            )
    else:
        await event.message.delete()
        await event.message.answer(
            "Анкеты закончились. Выберите действие:",
            reply_markup=research
        )


@router.callback_query(F.data == "dislike")
async def callback_dislike(event: CallbackQuery):
    user_chat_id = event.message.chat.id
    next_account = await get_next_account(user_chat_id)

    if next_account:
        # Устанавливаем isDisliked = True в таблице liked_{user_chat_id}
        async with liked_db_session() as session:
            liked_table = f"liked_{user_chat_id}"
            await session.execute(
                text(f"UPDATE {liked_table} SET isDisliked = True WHERE chat_id = :chat_id"),
                {"chat_id": next_account.chat_id}
            )
            await session.commit()

        await display_account(event, next_account)
    else:
        await event.message.delete()
        await event.message.answer(
            "Анкеты закончились. Выберите действие:",
            reply_markup=research
        )


@router.callback_query(F.data.startswith("mutual_like_"))
async def handle_mutual_like(event: CallbackQuery):
    user_chat_id = event.message.chat.id
    liked_chat_id = int(event.data.split("_")[-1])

    async with accounts_db_session() as session:
        async with session.begin():
            # Получаем данные анкет обоих пользователей
            liked_tg_id = await session.execute(select(AccountsTable).filter_by(chat_id=liked_chat_id))
            user_tg_id = await session.execute(select(AccountsTable).filter_by(chat_id=user_chat_id))
            acc = liked_tg_id.scalar_one_or_none()
            user = user_tg_id.scalar_one_or_none()

            if not acc or not user:
                await event.answer("Ошибка: один из пользователей не найден.")
                return

            # Отправляем анкеты пользователям
            await send_profile(event, user_chat_id, acc)
            await send_profile(event, liked_chat_id, user)

            # Отправляем уведомления о взаимном лайке
            await send_mutual_like_notification(event, user_chat_id, acc.tg_id)
            await send_mutual_like_notification(event, liked_chat_id, user.tg_id)

            await event.answer("Взаимный лайк! Вам отправлены анкеты пользователей.")
            await session.close()


@router.callback_query(F.data == "reject_like")
async def callback_reject_like(event: CallbackQuery):
    """Обработчик для отказа от взаимного лайка."""
    await event.answer("Вы отказались от взаимного лайка.", show_alert=True)
    await event.message.delete()  # Удаляем сообщение с запросом на взаимный лайк


@router.callback_query(F.data == "restart_search")
async def restart_search(callback: CallbackQuery):
    table_name = f"liked_{callback.message.chat.id}"  # Определяем название таблицы
    async with liked_db_session() as session:
        # Удаляем таблицу для сброса лайков
        await session.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
        await session.commit()

    # Уведомляем пользователя о начале нового поиска
    await callback.message.edit_text("Поиск начат заново.", reply_markup=assessment_menu)

    # Запускаем новый поиск
    await callback_find_people(callback)


@router.callback_query(F.data == "feedback")
async def callback_feedback(event: Message | CallbackQuery):
    if isinstance(event, CallbackQuery):
        await event.message.answer("Вы можете связаться с нашим разработчиком лично, чтобы сообщить о баге или недоработке. \nЗа спам, флуд, оскорбления вы можете быть заблокированы", reply_markup=feedback_url)


@router.callback_query(F.data == "feedback_account")
async def callback_send_feedback(call: CallbackQuery):
    pass  # сделать тут лог


@router.callback_query(F.data == "edit_profile")
async def callback_edit_profile(event: Message | CallbackQuery):
    await event.message.answer("Выберете что мы будем изменять:", reply_markup=edit_profile) if isinstance(event, CallbackQuery) else event.answer(
        "Выберете что мы будем изменять:", reply_markup=edit_profile)

