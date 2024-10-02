import os

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from log.logger_cfg import inline_kb_logger

from keyboards.default_keyboards import user_sex, user_isBaccalaureate, user_course_bac, user_course_mag, no_photo, \
    no_about, user_friend_sex

from callbacks import usr_callbacks
from handlers import usr_commands

from database.db_cfg import accounts_db_session
from database.models import AccountsTable
from .forms.state_forms import FirstRegistration

router = Router()


@router.callback_query(F.data == 'first_reg')
async def user_first_reg(event: Message | CallbackQuery, state: FSMContext):
    print(event.message.chat.id)
    if isinstance(event, Message):
        inline_kb_logger.info('start reg')
        await state.set_state(FirstRegistration.username)
        user_username = event.from_user.username
        await state.set_state(FirstRegistration.chat_id)

        await state.update_data(username=user_username)
        user_chat_id = event.chat.id
        # await state.set_state(FirstRegistration.isActive)

        await state.update_data(chat_id=user_chat_id)
        await state.set_state(FirstRegistration.name)

#         await state.update_data(isActive = True)
        await event.answer("Давай начнем, если ты хочешь отменить, напиши \"/cancel\"! Напиши свое имя которое будет отображаться в профиле.")
    elif isinstance(event, CallbackQuery):
        await event.message.delete()
        inline_kb_logger.info('start reg')
        await state.set_state(FirstRegistration.username)
        user_username = event.from_user.username
        await state.set_state(FirstRegistration.chat_id)

        await state.update_data(username=user_username)
        user_chat_id = event.message.chat.id
        await state.set_state(FirstRegistration.name)

        await state.update_data(chat_id=user_chat_id)
        await event.message.answer("Давай начнем! Напиши свое имя которое будет отображаться в профиле.")

@router.message(Command('cancel'))
async def cancel_reg(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Регистрация отменена')

    await usr_commands.command_start(message)

@router.message(FirstRegistration.name)
async def user_name_inf(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(FirstRegistration.age)


@router.message(FirstRegistration.age)
async def user_age_inf(message: Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await message.answer("Какой у тебя пол?", reply_markup=user_sex)
    await state.set_state(FirstRegistration.isMale)


@router.message(FirstRegistration.isMale)
async def user_sex_inf(message: Message, state: FSMContext):
    if message.text == "Мужской":
        await state.update_data(isMale=True)
    elif message.text == "Женский":
        await state.update_data(isMale=False)
    await message.answer("Отлично! Теперь скажи, на каком факультете ты учишься?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(FirstRegistration.faculty)


@router.message(FirstRegistration.faculty)
async def user_faculty_inf(message: Message, state: FSMContext):
    await state.update_data(faculty=message.text)
    await message.answer("Ты учишься на бакалавриате или магистратуре?", reply_markup=user_isBaccalaureate)
    await state.set_state(FirstRegistration.isBaccalaureate)


@router.message(FirstRegistration.isBaccalaureate)
async def user_degree_inf(message: Message, state: FSMContext):
    if message.text == "Бакалавриат":
        await state.update_data(isBaccalaureate=True)
        await message.answer("На каком ты курсе?", reply_markup=user_course_bac)
    elif message.text == "Магистратруа":
        await state.update_data(isBaccalaureate=False)
        await message.answer("На каком ты курсе?", reply_markup=user_course_mag)

    await state.set_state(FirstRegistration.course)


@router.message(FirstRegistration.course)
async def user_course_inf(message: Message, state: FSMContext):
    await state.update_data(course=message.text)
    await message.answer("Отправь свое фото", reply_markup=no_photo)

    await state.set_state(FirstRegistration.photo)


@router.message(FirstRegistration.photo, lambda message: message.photo or message.text)
async def user_photo_inf(message: Message, state: FSMContext):
    if message.text == "Без фото":
        await state.update_data(photo='None')
        await state.set_state(FirstRegistration.about)
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
        await state.update_data(photo=destination)

    await message.answer("Расскажи о себе", reply_markup=no_about)
    await state.set_state(FirstRegistration.about)


@router.message(FirstRegistration.about)
async def user_about_inf(message: Message, state: FSMContext):
    if message.text == "Без текста":
        await state.update_data(about='None')
    else:
        await state.update_data(about=message.text)

    await message.answer('Кого ты хочешь найти?', reply_markup=user_friend_sex)
    await state.set_state(FirstRegistration.friend_sex)


@router.message(FirstRegistration.friend_sex)
async def user_friend_sex_inf(message: Message, state: FSMContext):
    if message.text == "Мужчины":
        await state.update_data(friends_sex="males")
    elif message.text == "Девушки":
        await state.update_data(friends_sex="females")
    elif message.text == "Без разницы":
        await state.update_data(friends_sex="dont_care")

    data = await state.get_data()
    print(data)
    accounts_table = AccountsTable(
        chat_id=data['chat_id'],
        tg_id=data['username'],
        isActive=True,
        name=data['name'],
        age=data['age'],
        isMale=data['isMale'],
        faculty=data['faculty'],
        isBaccalaureate=data['isBaccalaureate'],
        course=data['course'],
        photo=data['photo'],
        about=data['about'],
        friend_sex=data['friends_sex']
    )
    accounts_db_session.add(accounts_table)
    accounts_db_session.commit()

    await message.answer(f"Регистраниця завершена!", reply_markup=ReplyKeyboardRemove())
    await usr_callbacks.callback_menu(message)
