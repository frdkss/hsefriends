import html
import os

from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from sqlalchemy.future import select
from sqlalchemy import or_, and_

from keyboards.inline_keyboards import main_menu, main_settings, assessment_menu, research, feedback_url
from keyboards.default_keyboards import confirmation

from database.db_cfg import accounts_db_session, check_mutual_like, save_like
from database.models import AccountsTable

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
    return None




async def display_account(event: CallbackQuery, account):
    gender = "Парень" if account.isMale else "Девушка"
    degree = "Бакалавриат" if account.isBaccalaureate else "Магистратура"

    # Формируем текст профиля
    profile_text = (
        f"Имя - {html.escape(account.name)}\n"
        f"Возраст - {account.age}\n"
        f"Пол - {gender}\n"
        f"Факультет - {account.faculty}\n"
        f"Степень - {degree}\n"
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


async def send_like_request(event: CallbackQuery, liked_chat_id: int, user_chat_id: int):
    """Отправляет запрос на лайк другому пользователю."""
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Взаимный лайк", callback_data=f"mutual_like_{user_chat_id}"),
         InlineKeyboardButton(text="Отказаться", callback_data="reject_like")]
    ])

    await event.bot.send_message(
        liked_chat_id,
        f"Вас лайкнули! Хотите поставить лайк в ответ?",
        reply_markup=markup
    )


async def send_mutual_like_notification(event: CallbackQuery, chat_id: int, telegram_username: str):
    """Отправляет уведомление о взаимном лайке."""
    await event.bot.send_message(
        chat_id,
        f"У вас взаимный лайк! Вот tg_id: {telegram_username}"
    )


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
                    f"Факультет - {user.faculty}\n"
                    f"Степень - {degree}\n"
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
                    await event.message.answer_photo(photo=photo, caption=profile_text)
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
        async with session.begin():
            user = await session.execute(
                select(AccountsTable).filter_by(chat_id=event.message.chat.id)
            )
            user = user.scalar_one_or_none()

            if user:
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


@router.callback_query(F.data == "restart_search")
async def restart_search(callback: CallbackQuery):
    async with accounts_db_session() as session:
        user = await session.get(AccountsTable, callback.message.chat.id)
        user.last_uid = 0  # Сбрасываем last_uid
        await session.commit()
        await callback.message.edit_text("Поиск начат заново.", reply_markup=assessment_menu)

@router.callback_query(F.data == "like")
async def callback_like(event: CallbackQuery):
    user_chat_id = event.message.chat.id
    liked_account = await get_next_account(user_chat_id, update_last_uid=True)  # Обновляем last_uid при лайке

    if liked_account:
        # Сохраняем лайк в базу данных
        await save_like(user_chat_id, liked_account.chat_id)

        # Отправляем запрос на взаимный лайк
        await send_like_request(event, liked_account.chat_id, user_chat_id)

        # После успешного отправления запроса на лайк, отображаем следующую анкету
        next_account = await get_next_account(user_chat_id, update_last_uid=False)  # Не обновляем last_uid повторно
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
            liked_tg_id = await session.execute(select(AccountsTable).filter_by(chat_id=liked_chat_id))
            user_tg_id = await session.execute(select(AccountsTable).filter_by(chat_id=user_chat_id))
            acc = liked_tg_id.scalar_one_or_none()
            user = user_tg_id.scalar_one_or_none()

    # Отправляем tg_id друг другу при взаимном лайке
            await send_mutual_like_notification(event, user_chat_id, acc.tg_id)
            await send_mutual_like_notification(event, liked_chat_id, user.tg_id)

            await event.answer("Взаимный лайк! Вам отправлено tg_id пользователя.")


@router.callback_query(F.data == "reject_like")
async def callback_reject_like(event: CallbackQuery):
    """Обработчик для отказа от взаимного лайка."""
    await event.answer("Вы отказались от взаимного лайка.", show_alert=True)
    await event.message.delete()  # Удаляем сообщение с запросом на взаимный лайк


@router.callback_query(F.data == "update_search")
async def update_search(callback: CallbackQuery):
    async with accounts_db_session() as session:
        user = await session.get(AccountsTable, callback.message.chat.id)
        accounts = await search_accounts(user.isMale, user.friend_sex, user.age, user.chat_id)

        if accounts:
            next_account = accounts[0]
            user.last_uid = next_account.id
            await session.commit()

            gender = "Парень" if next_account.isMale else "Девушка"
            degree = "Бакалавриат" if next_account.isBaccalaureate else "Магистратура"
            profile_text = (
                f"Имя - {html.escape(next_account.name)}\n"
                f"Возраст - {next_account.age}\n"
                f"Пол - {gender}\n"
                f"Факультет - {next_account.faculty}\n"
                f"Степень - {degree}\n"
                f"Курс - {next_account.course}\n"
            )
            if next_account.about:
                profile_text += f"О тебе - {next_account.about}\n"

            await callback.message.edit_text(profile_text, reply_markup=assessment_menu)
        else:
            await callback.message.edit_text(
                "Новых анкет нет. Хотите начать поиск заново?",
                reply_markup=research
            )


@router.callback_query(F.data == "feedback")
async def callback_feedback(event: Message | CallbackQuery):
    if isinstance(event, CallbackQuery):
        await event.message.answer("Вы можете связаться с нашим разработчиком лично, бла бла бла", reply_markup=feedback_url)


@router.callback_query(F.data == "edit_profile")
async def callback_edit_profile(call: CallbackQuery):
    pass  # открыть меню с изменениями


@router.callback_query(F.data == "feedback_account")
async def callback_send_feedback(call: CallbackQuery):
    pass  # сделать тут лог


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
