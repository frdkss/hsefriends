import os

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from database.db_cfg import accounts_db_session
from keyboards.default_keyboards import user_sex, user_course_bac, no_about, user_friend_sex, no_photo

from database.models import AccountsTable
from .forms.state_forms import RewriteProfile

router = Router()


@router.callback_query(F.data == 'rewrite_profile')
async def state_user_rewrite(event: Message | CallbackQuery, state: FSMContext):
    """Запуск редактирования профиля."""
    chat_id = event.message.chat.id if isinstance(event, CallbackQuery) else event.chat.id

    # Получение текущего профиля пользователя из базы данных
    async with accounts_db_session() as session:
        query = select(AccountsTable).where(AccountsTable.chat_id == chat_id)
        result = await session.execute(query)
        user_profile = result.scalar_one_or_none()

    if not user_profile:
        await event.message.answer("Профиль не найден.")
        return

    # Сохранение текущего состояния для редактирования
    await state.update_data(profile=user_profile)
    await state.set_state(RewriteProfile.name)
    await event.message.answer(f"Ваше текущее имя: {user_profile.name}. Введите новое имя:")


@router.message(RewriteProfile.name)
async def state_edit_name(message: Message, state: FSMContext):
    """Редактирование имени пользователя."""
    await state.update_data(name=message.text)
    await message.answer("Сколько вам лет?")
    await state.set_state(RewriteProfile.age)


@router.message(RewriteProfile.age)
async def state_edit_age(message: Message, state: FSMContext):
    """Редактирование возраста."""
    await state.update_data(age=int(message.text))
    await message.answer("Какой у вас пол?", reply_markup=user_sex)
    await state.set_state(RewriteProfile.isMale)


@router.message(RewriteProfile.isMale)
async def state_edit_gender(message: Message, state: FSMContext):
    """Редактирование пола."""
    if message.text == "Мужской":
        isMale = True
    elif message.text == "Женский":
        isMale = False
    else:
        await message.answer("Пожалуйста, выберите пол из предложенных вариантов: Мужской или Женский.")
        return  # Прекращаем выполнение при некорректном вводе

    await state.update_data(isMale=isMale)
    await message.answer("Введите ваш факультет:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RewriteProfile.faculty)


@router.message(RewriteProfile.faculty)
async def state_edit_faculty(message: Message, state: FSMContext):
    """Редактирование факультета."""
    await state.update_data(faculty=message.text)
    await message.answer("На каком вы курсе?", reply_markup=user_course_bac)
    await state.set_state(RewriteProfile.course)


@router.message(RewriteProfile.course)
async def state_edit_course(message: Message, state: FSMContext):
    """Редактирование курса."""
    await state.update_data(course=int(message.text))
    await message.answer("Отправь свое фото", reply_markup=no_photo)
    await state.set_state(RewriteProfile.photo)


@router.message(RewriteProfile.photo, lambda message: message.photo or message.text)
async def user_photo_inf(message: Message, state: FSMContext):
    if message.text == "Без фото":
        await state.update_data(photo='None')
        await state.set_state(RewriteProfile.about)
    else:
        # Получаем объект бота из message
        bot = message.bot

        # Создаем директорию, если она не существует
        downloads_dir = f'account_photos/{message.chat.id}'
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)

        # Получаем наибольший размер фото
        photo = message.photo[-1]

        # Получаем file_id
        file_id = photo.file_id

        # Загружаем файл по file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path

        # Скачиваем файл
        destination = f"{downloads_dir}/{file_id}.jpg"  # Путь, куда сохранить фото
        await bot.download_file(file_path, destination)

        await message.answer("Фото успешно загружено!")
        # Сбрасываем состояние после получения фото
        await state.update_data(photo=f"{file_id}.jpg")

    await message.answer("Расскажи о себе", reply_markup=no_about)
    await state.set_state(RewriteProfile.about)


@router.message(RewriteProfile.about)
async def user_about_inf(message: Message, state: FSMContext):
    if message.text == "Без текста":
        await state.update_data(about='None')
    else:
        await state.update_data(about=message.text)

    await message.answer('Кого ты хочешь найти?', reply_markup=user_friend_sex)
    await state.set_state(RewriteProfile.friend_sex)


@router.message(RewriteProfile.friend_sex)
async def user_friend_sex_inf(message: Message, state: FSMContext):
    if message.text == "Мужчины":
        await state.update_data(friends_sex="males")
    elif message.text == "Девушки":
        await state.update_data(friends_sex="females")
    elif message.text == "Без разницы":
        await state.update_data(friends_sex="dont_care")
    # Получение обновленных данных и сохранение в базу данных
    data = await state.get_data()
    async with accounts_db_session() as session:
        async with session.begin():
            query = select(AccountsTable).where(AccountsTable.chat_id == data['profile'].chat_id)
            result = await session.execute(query)
            user_profile = result.scalar_one()

            # Обновление данных профиля
            user_profile.name = data['name']
            user_profile.age = data['age']
            user_profile.isMale = data['isMale']
            user_profile.faculty = data['faculty']
            user_profile.course = data['course']

            await session.commit()

    await message.answer("Профиль успешно обновлен!", reply_markup=ReplyKeyboardRemove())
    await state.clear()
