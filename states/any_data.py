import os

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from callbacks.usr_callbacks import callback_menu
from database.db_cfg import accounts_db_session
from keyboards.default_keyboards import user_sex, user_course_bac, no_about, user_friend_sex, no_photo

from database.models import AccountsTable
from .forms.state_forms import RewriteProfile, NewMessageState, NewPhotoState

router = Router()


@router.callback_query(F.data == "edit_name")
async def callback_edit_name(event: Message | CallbackQuery, state: FSMContext):
    chat_id = event.from_user.id  # Получаем chat_id пользователя
    await event.answer("Введите новое имя:") if isinstance(event, Message) else event.message.answer("Введите новое имя:")

    # Устанавливаем состояние ожидания нового имени
    await NewMessageState.waiting_for_new_message.set()
    await state.update_data(chat_id=chat_id)


@router.message(NewMessageState.waiting_for_new_message)
async def process_new_name(event: Message | CallbackQuery, state: FSMContext):
    new_name = event.text.strip() if isinstance(event, Message) else event.message.text.strip()  # Извлекаем текст нового имени
    data = await state.get_data()
    chat_id = data.get('chat_id')

    async with accounts_db_session() as session:
        async with session.begin():
            # Находим пользователя по chat_id
            stmt = select(AccountsTable).where(AccountsTable.chat_id == chat_id)
            try:
                user = await session.execute(stmt)
                user = user.scalars().one()  # Получаем первую (и единственную) запись

                # Обновляем имя пользователя
                user.name = new_name

                # Сохраняем изменения
                await session.commit()

                await event.answer(f"Ваше имя успешно изменено на: {new_name}") if isinstance(event, Message) else event.message.answer(
                    f"Ваше имя успешно изменено на: {new_name}")
            except Exception:
                await event.answer("Пользователь не найден.") if isinstance(event, Message) else event.message.answer("Пользователь не найден.")

    # Сбрасываем состояние после получения нового имени
    await state.finish()


@router.callback_query(F.data == "edit_age")
async def callback_edit_age(event: Message | CallbackQuery, state: FSMContext):
    chat_id = event.from_user.id  # Получаем chat_id пользователя
    await event.answer("Введите новый возраст:") if isinstance(event, Message) else event.message.answer("Введите новый возраст:")

    # Устанавливаем состояние ожидания нового имени
    await NewMessageState.waiting_for_new_message.set()
    await state.update_data(chat_id=chat_id)


@router.message(NewMessageState.waiting_for_new_message)
async def process_new_name(event: Message | CallbackQuery, state: FSMContext):
    new_name = event.text.strip() if isinstance(event, Message) else event.message.text.strip()  # Извлекаем текст нового имени
    data = await state.get_data()
    chat_id = data.get('chat_id')

    async with accounts_db_session() as session:
        async with session.begin():
            # Находим пользователя по chat_id
            stmt = select(AccountsTable).where(AccountsTable.chat_id == chat_id)
            try:
                user = await session.execute(stmt)
                user = user.scalars().one()  # Получаем первую (и единственную) запись

                # Обновляем имя пользователя
                user.name = new_name

                # Сохраняем изменения
                await session.commit()

                await event.answer(f"Ваше имя успешно изменено на: {new_name}") if isinstance(event, Message) else event.message.answer(
                    f"Ваше имя успешно изменено на: {new_name}")
            except Exception:
                await event.answer("Пользователь не найден.") if isinstance(event, Message) else event.message.answer("Пользователь не найден.")

    # Сбрасываем состояние после получения нового имени
    await state.finish()


@router.callback_query(F.data == "edit_sex")
async def callback_edit_sex(event: Message | CallbackQuery, state: FSMContext):
    chat_id = event.from_user.id  # Получаем chat_id пользователя
    await event.answer("Введите новый пол:") if isinstance(event, Message) else event.message.answer("Введите новый пол:")

    # Устанавливаем состояние ожидания нового имени
    await NewMessageState.waiting_for_new_message.set()
    await state.update_data(chat_id=chat_id)


@router.message(NewMessageState.waiting_for_new_message)
async def process_new_name(event: Message | CallbackQuery, state: FSMContext):
    new_name = event.text.strip() if isinstance(event, Message) else event.message.text.strip()  # Извлекаем текст нового имени
    data = await state.get_data()
    chat_id = data.get('chat_id')

    async with accounts_db_session() as session:
        async with session.begin():
            # Находим пользователя по chat_id
            stmt = select(AccountsTable).where(AccountsTable.chat_id == chat_id)
            try:
                user = await session.execute(stmt)
                user = user.scalars().one()  # Получаем первую (и единственную) запись

                # Обновляем имя пользователя
                user.name = new_name

                # Сохраняем изменения
                await session.commit()

                await event.answer(f"Ваше имя успешно изменено на: {new_name}") if isinstance(event, Message) else event.message.answer(
                    f"Ваше имя успешно изменено на: {new_name}")
            except Exception:
                await event.answer("Пользователь не найден.") if isinstance(event, Message) else event.message.answer("Пользователь не найден.")

    # Сбрасываем состояние после получения нового имени
    await state.finish()


@router.callback_query(F.data == "edit_faculty")
async def callback_edit_faculty(event: Message | CallbackQuery, state: FSMContext):
    chat_id = event.from_user.id  # Получаем chat_id пользователя
    await event.answer("Введите новый факультет:") if isinstance(event, Message) else event.message.answer("Введите новый факультет:")

    # Устанавливаем состояние ожидания нового имени
    await NewMessageState.waiting_for_new_message.set()
    await state.update_data(chat_id=chat_id)


@router.message(NewMessageState.waiting_for_new_message)
async def process_new_name(event: Message | CallbackQuery, state: FSMContext):
    new_name = event.text.strip() if isinstance(event, Message) else event.message.text.strip()  # Извлекаем текст нового имени
    data = await state.get_data()
    chat_id = data.get('chat_id')

    async with accounts_db_session() as session:
        async with session.begin():
            # Находим пользователя по chat_id
            stmt = select(AccountsTable).where(AccountsTable.chat_id == chat_id)
            try:
                user = await session.execute(stmt)
                user = user.scalars().one()  # Получаем первую (и единственную) запись

                # Обновляем имя пользователя
                user.name = new_name

                # Сохраняем изменения
                await session.commit()

                await event.answer(f"Ваше имя успешно изменено на: {new_name}") if isinstance(event, Message) else event.message.answer(
                    f"Ваше имя успешно изменено на: {new_name}")
            except Exception:
                await event.answer("Пользователь не найден.") if isinstance(event, Message) else event.message.answer("Пользователь не найден.")

    # Сбрасываем состояние после получения нового имени
    await state.finish()


@router.callback_query(F.data == "edit_degree")
async def callback_edit_degree(event: Message | CallbackQuery, state: FSMContext):
    chat_id = event.from_user.id  # Получаем chat_id пользователя
    await event.answer("Введите новую степень:") if isinstance(event, Message) else event.message.answer("Введите новую степень:")

    # Устанавливаем состояние ожидания нового имени
    await NewMessageState.waiting_for_new_message.set()
    await state.update_data(chat_id=chat_id)


@router.message(NewMessageState.waiting_for_new_message)
async def process_new_name(event: Message | CallbackQuery, state: FSMContext):
    new_name = event.text.strip() if isinstance(event, Message) else event.message.text.strip()  # Извлекаем текст нового имени
    data = await state.get_data()
    chat_id = data.get('chat_id')

    async with accounts_db_session() as session:
        async with session.begin():
            # Находим пользователя по chat_id
            stmt = select(AccountsTable).where(AccountsTable.chat_id == chat_id)
            try:
                user = await session.execute(stmt)
                user = user.scalars().one()  # Получаем первую (и единственную) запись

                # Обновляем имя пользователя
                user.name = new_name

                # Сохраняем изменения
                await session.commit()

                await event.answer(f"Ваше имя успешно изменено на: {new_name}") if isinstance(event, Message) else event.message.answer(
                    f"Ваше имя успешно изменено на: {new_name}")
            except Exception:
                await event.answer("Пользователь не найден.") if isinstance(event, Message) else event.message.answer("Пользователь не найден.")

    # Сбрасываем состояние после получения нового имени
    await state.finish()


@router.callback_query(F.data == "edit_course")
async def callback_edit_course(event: Message | CallbackQuery, state: FSMContext):
    chat_id = event.from_user.id  # Получаем chat_id пользователя
    await event.answer("Введите новый курс:") if isinstance(event, Message) else event.message.answer("Введите новый курс:")

    # Устанавливаем состояние ожидания нового имени
    await NewMessageState.waiting_for_new_message.set()
    await state.update_data(chat_id=chat_id)


@router.message(NewMessageState.waiting_for_new_message)
async def process_new_name(event: Message | CallbackQuery, state: FSMContext):
    new_name = event.text.strip() if isinstance(event, Message) else event.message.text.strip()  # Извлекаем текст нового имени
    data = await state.get_data()
    chat_id = data.get('chat_id')

    async with accounts_db_session() as session:
        async with session.begin():
            # Находим пользователя по chat_id
            stmt = select(AccountsTable).where(AccountsTable.chat_id == chat_id)
            try:
                user = await session.execute(stmt)
                user = user.scalars().one()  # Получаем первую (и единственную) запись

                # Обновляем имя пользователя
                user.name = new_name

                # Сохраняем изменения
                await session.commit()

                await event.answer(f"Ваше имя успешно изменено на: {new_name}") if isinstance(event, Message) else event.message.answer(
                    f"Ваше имя успешно изменено на: {new_name}")
            except Exception:
                await event.answer("Пользователь не найден.") if isinstance(event, Message) else event.message.answer("Пользователь не найден.")

    # Сбрасываем состояние после получения нового имени
    await state.finish()


@router.callback_query(F.data == "edit_photo")
async def callback_edit_photo(event: Message | CallbackQuery, state: FSMContext):
    chat_id = event.from_user.id  # Получаем chat_id пользователя
    await event.answer("Отправьте новую фотографию:") if isinstance(event, Message) else event.message.answer("Отправьте новую фотографию:")

    # Устанавливаем состояние ожидания нового имени
    await NewPhotoState.waiting_for_new_photo.set()
    await state.update_data(chat_id=chat_id)


@router.message(NewMessageState.waiting_for_new_message)
async def process_new_name(event: Message | CallbackQuery, state: FSMContext):
    new_name = event.text.strip() if isinstance(event, Message) else event.message.text.strip()  # Извлекаем текст нового имени
    data = await state.get_data()
    chat_id = data.get('chat_id')

    async with accounts_db_session() as session:
        async with session.begin():
            # Находим пользователя по chat_id
            stmt = select(AccountsTable).where(AccountsTable.chat_id == chat_id)
            try:
                user = await session.execute(stmt)
                user = user.scalars().one()  # Получаем первую (и единственную) запись

                # Обновляем имя пользователя
                user.name = new_name

                # Сохраняем изменения
                await session.commit()

                await event.answer(f"Ваше имя успешно изменено на: {new_name}") if isinstance(event, Message) else event.message.answer(
                    f"Ваше имя успешно изменено на: {new_name}")
            except Exception:
                await event.answer("Пользователь не найден.") if isinstance(event, Message) else event.message.answer("Пользователь не найден.")

    # Сбрасываем состояние после получения нового имени
    await state.finish()


@router.callback_query(F.data == "edit_about")
async def callback_edit_about(event: Message | CallbackQuery, state: FSMContext):
    chat_id = event.from_user.id  # Получаем chat_id пользователя
    await event.answer("Введите новый текст \"О себе\":") if isinstance(event, Message) else event.message.answer("Введите новый текст \"О себе\":")

    # Устанавливаем состояние ожидания нового имени
    await NewMessageState.waiting_for_new_message.set()
    await state.update_data(chat_id=chat_id)


@router.message(NewMessageState.waiting_for_new_message)
async def process_new_name(event: Message | CallbackQuery, state: FSMContext):
    new_name = event.text.strip() if isinstance(event, Message) else event.message.text.strip()  # Извлекаем текст нового имени
    data = await state.get_data()
    chat_id = data.get('chat_id')

    async with accounts_db_session() as session:
        async with session.begin():
            # Находим пользователя по chat_id
            stmt = select(AccountsTable).where(AccountsTable.chat_id == chat_id)
            try:
                user = await session.execute(stmt)
                user = user.scalars().one()  # Получаем первую (и единственную) запись

                # Обновляем имя пользователя
                user.name = new_name

                # Сохраняем изменения
                await session.commit()

                await event.answer(f"Ваше имя успешно изменено на: {new_name}") if isinstance(event, Message) else event.message.answer(
                    f"Ваше имя успешно изменено на: {new_name}")
            except Exception:
                await event.answer("Пользователь не найден.") if isinstance(event, Message) else event.message.answer("Пользователь не найден.")

    # Сбрасываем состояние после получения нового имени
    await state.finish()


@router.callback_query(F.data == "edit_friend_sex")
async def callback_edit_friend_sex(event: Message | CallbackQuery, state: FSMContext):
    chat_id = event.from_user.id  # Получаем chat_id пользователя
    await event.answer("Введите новый пол:") if isinstance(event, Message) else event.message.answer("Введите новый пол:")

    event_text = event.text if isinstance(event, Message) else event.message.text

    if event_text == "Мужчины":
        await state.update_data(friends_sex="males")
    elif event_text == "Девушки":
        await state.update_data(friends_sex="females")
    elif event_text == "Без разницы":
        await state.update_data(friends_sex="dont_care")

    # Устанавливаем состояние ожидания нового имени
    await NewMessageState.waiting_for_new_message.set()
    await state.update_data(chat_id=chat_id)


@router.message(NewMessageState.waiting_for_new_message)
async def process_new_name(event: Message | CallbackQuery, state: FSMContext):
    new_name = event.text.strip() if isinstance(event, Message) else event.message.text.strip()  # Извлекаем текст нового имени
    data = await state.get_data()
    chat_id = data.get('chat_id')

    async with accounts_db_session() as session:
        async with session.begin():
            # Находим пользователя по chat_id
            stmt = select(AccountsTable).where(AccountsTable.chat_id == chat_id)
            try:
                user = await session.execute(stmt)
                user = user.scalars().one()  # Получаем первую (и единственную) запись

                # Обновляем имя пользователя
                user.name = new_name

                # Сохраняем изменения
                await session.commit()

                await event.answer(f"Ваше имя успешно изменено на: {new_name}") if isinstance(event, Message) else event.message.answer(
                    f"Ваше имя успешно изменено на: {new_name}")
            except Exception:
                await event.answer("Пользователь не найден.") if isinstance(event, Message) else event.message.answer("Пользователь не найден.")

    # Сбрасываем состояние после получения нового имени
    await state.finish()
