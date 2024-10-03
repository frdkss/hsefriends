from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from keyboards.inline_keyboards import main_menu, main_settings
from keyboards.default_keyboards import confirmation

from states import rewrite_state

from database.db_cfg import accounts_db_session
from database.models import AccountsTable

router = Router()


async def search_accounts(user_is_male: bool, user_preference: str, user_age: int, user_chat_id: int):
    if user_preference not in ['males', 'females', 'dont_care']:
        return []  # Если предпочтение указано неправильно

    async with accounts_db_session:
        query = select(AccountsTable).filter(AccountsTable.chat_id != user_chat_id)  # Исключаем одинаковые chat_id

        if user_is_male:
            # Пользователь - мужчина
            if user_preference == 'males':
                # Ищет мужчин
                query = query.filter(
                    AccountsTable.isMale == True,
                    or_(
                        AccountsTable.friend_sex == 'males',
                        AccountsTable.friend_sex == 'dont_care'
                    ),
                    AccountsTable.age.between(user_age - 3, user_age + 3)
                )
            elif user_preference == 'females':
                # Ищет женщин
                query = query.filter(
                    AccountsTable.isMale == False,
                    or_(
                        AccountsTable.friend_sex == 'males',
                        AccountsTable.friend_sex == 'dont_care'
                    ),
                    AccountsTable.age.between(user_age - 3, user_age + 3)
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
                    ),
                    AccountsTable.age.between(user_age - 3, user_age + 3)
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
                    ),
                    AccountsTable.age.between(user_age - 3, user_age + 3)
                )
            elif user_preference == 'females':
                # Ищет женщин
                query = query.filter(
                    AccountsTable.isMale == False,
                    or_(
                        AccountsTable.friend_sex == 'females',
                        AccountsTable.friend_sex == 'dont_care'
                    ),
                    AccountsTable.age.between(user_age - 3, user_age + 3)
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
                    ),
                    AccountsTable.age.between(user_age - 3, user_age + 3)
                )

        result = await accounts_db_session.execute(query)
        return result.scalars().all()


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
                await event.answer(f"{greeting} {user.name}! Добро пожаловать в меню", reply_markup=main_menu)
            elif isinstance(event, CallbackQuery):
                await event.message.answer(f"{greeting} {user.name}! Добро пожаловать в меню", reply_markup=main_menu)


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
async def callback_find_people(event: Message | CallbackQuery):
    if isinstance(event, CallbackQuery):
        async with accounts_db_session() as session:  # Use async context manager
            async with session.begin():  # Optional: use a transaction
                # Use the asynchronous query method
                user = await session.execute(
                    select(AccountsTable).filter_by(chat_id=event.message.chat.id)
                )
                user = user.scalar_one_or_none()  # Get the first result or None

                if user:
                    results = await search_accounts(user.isMale, user.friend_sex, user.age, user.chat_id)

                    print(f"Найдено {len(results)} анкет:")
                    for account in results:
                        print(account.name, account.age, account.isMale, account.friend_sex)


@router.callback_query(F.data == "like")
async def callback_like(event: Message | CallbackQuery):
    pass


@router.callback_query(F.data == "dislike")
async def callback_dislike(event: Message | CallbackQuery):
    pass


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
