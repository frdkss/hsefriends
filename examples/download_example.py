from aiogram import Router, Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
import os
import asyncio


# Определяем состояния FSM
class PhotoStates(StatesGroup):
    waiting_for_photo = State()


# Инициализация роутера
photo_router = Router()


# Хендлер для команды /photo
@photo_router.message(Command("photo"))
async def ask_for_photo(message: Message, state: FSMContext):
    await message.answer("Отправь мне фото!")
    # Устанавливаем состояние ожидания фотографии
    await state.set_state(PhotoStates.waiting_for_photo)


# Хендлер для получения фото
@photo_router.message(PhotoStates.waiting_for_photo, lambda message: message.photo)
async def download_photo(message: Message, state: FSMContext):
    # Получаем объект бота из message
    bot = message.bot

    # Создаем директорию, если она не существует
    downloads_dir = 'downloads'
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
    await state.clear()


# Основной код для запуска бота
async def main():
    # Инициализация бота и диспетчера с памятью FSM
    bot = Bot(token="YOUR_BOT_TOKEN")
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем маршрутизатор
    dp.include_router(photo_router)

    # Запускаем polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
