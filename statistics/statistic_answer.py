import asyncio
import os
import aiofiles

from aiogram import Router
from aiogram.types import Message, FSInputFile, InputFile, InputMediaPhoto
from aiogram.filters import Command

from datetime import datetime

router = Router()

@router.message(Command("start"))
async def start_send_stat(message: Message):
    datetime_now = datetime.now().replace(microsecond=0).strftime(format="%d.%m.%Y %H:%M:%S")
    await message.answer(f"Статистика на момент <b>{datetime_now}</b>")
    async def job_builder():
        photo_path_reg1 = os.path.abspath(os.path.join("statistic_png/reg_stat/reg_statistic_from_16.10_for_1_days.png"))
        photo_path_reg2 = os.path.abspath(os.path.join("statistic_png/reg_stat/reg_statistic_from_16.10_for_7_days.png"))
        photo_path_reg3 = os.path.abspath(os.path.join("statistic_png/reg_stat/reg_statistic_from_16.10_for_31_days.png"))
        photo_path_age = os.path.abspath(os.path.join("statistic_png/age_stat/age_statistic.png"))
        photo_path_sex = os.path.abspath(os.path.join("statistic_png/sex_stat/sex_statistic.png"))
        photo_path_user = os.path.abspath(os.path.join("statistic_png/user_stat/users_statistic.png"))

        media = [
            InputMediaPhoto(media=FSInputFile(photo_path_reg1)),
            InputMediaPhoto(media=FSInputFile(photo_path_reg2)),
            InputMediaPhoto(media=FSInputFile(photo_path_reg3)),
        ]

        stat_age = FSInputFile(photo_path_age)
        stat_sex = FSInputFile(photo_path_sex)
        stat_user = FSInputFile(photo_path_user)

        analytics_reg1 = os.path.abspath("statistic_png/reg_stat/reg_for1_day.txt")
        analytics_reg2 = os.path.abspath("statistic_png/reg_stat/reg_for7_days.txt")
        analytics_reg3 = os.path.abspath("statistic_png/reg_stat/reg_for31_days.txt")
        analytics_age = os.path.abspath("statistic_png/age_stat/age_statistic.txt")
        analytics_sex = os.path.abspath("statistic_png/sex_stat/statistics.txt")
        analytics_user = os.path.abspath("statistic_png/user_stat/users_count.txt")

        async def read_file(file_path):
            async with aiofiles.open(file_path, mode='r', encoding='windows-1251', errors='replace') as f:
                return await f.read()

        reg1_text = await read_file(analytics_reg1)
        reg2_text = await read_file(analytics_reg2)
        reg3_text = await read_file(analytics_reg3)
        age_text = await read_file(analytics_age)
        sex_text = await read_file(analytics_sex)
        user_text = await read_file(analytics_user)

        # async with open()
        await message.answer_media_group(media=media)
        await message.answer(f"<b>{datetime_now}</b>\nАналитика по регистрациям:\n{reg1_text}\n{reg2_text}\n{reg3_text}")
        await message.answer_photo(photo=stat_age, caption=f"<b>{datetime_now}</b>\nАналитика по возрастам:\n{age_text}")
        await message.answer_photo(photo=stat_sex, caption=f"<b>{datetime_now}</b>\nАналитика по полам:\n{sex_text}")
        await message.answer_photo(photo=stat_user, caption=f"<b>{datetime_now}</b>\nАналитика по пользователям:\n{user_text}")

    # await job()
    while True:
        await job_builder()
        await asyncio.sleep(7230)

@router.message(Command("send_stat"))
async def send_stat(message: Message):
    from logic.reg_statistic import generate_reg_statistic, write_registration_statistics
    from logic.users_statistic import generate_users_statistic
    from logic.sex_statistic import generate_sex_statistic
    from logic.age_statistic import generate_age_statistic

    db_path = os.path.abspath(r'../database/accounts.db')
    stat_path = "statistic_png/age_stat/"
    generate_reg_statistic(db_path, stat_path,days=2)
    generate_reg_statistic(db_path, stat_path,days=7)
    generate_reg_statistic(db_path, stat_path,days=31)
    write_registration_statistics(db_path,stat_path)
    generate_users_statistic(db_path,stat_path)
    generate_sex_statistic(db_path,stat_path)
    generate_age_statistic(db_path,stat_path)


    datetime_now = datetime.now().replace(microsecond=0).strftime(format="%d.%m.%Y %H:%M:%S")
    await message.answer(f"Статистика на момент <b>{datetime_now}</b>")
    photo_path_reg1 = os.path.abspath(os.path.join("statistic_png/reg_stat/reg_statistic_from_16.10_for_1_days.png"))
    photo_path_reg2 = os.path.abspath(os.path.join("statistic_png/reg_stat/reg_statistic_from_16.10_for_7_days.png"))
    photo_path_reg3 = os.path.abspath(os.path.join("statistic_png/reg_stat/reg_statistic_from_16.10_for_31_days.png"))
    photo_path_age = os.path.abspath(os.path.join("statistic_png/age_stat/age_statistic.png"))
    photo_path_sex = os.path.abspath(os.path.join("statistic_png/sex_stat/sex_statistic.png"))
    photo_path_user = os.path.abspath(os.path.join("statistic_png/user_stat/users_statistic.png"))

    media = [
        InputMediaPhoto(media=FSInputFile(photo_path_reg1)),
        InputMediaPhoto(media=FSInputFile(photo_path_reg2)),
        InputMediaPhoto(media=FSInputFile(photo_path_reg3)),
    ]

    stat_age = FSInputFile(photo_path_age)
    stat_sex = FSInputFile(photo_path_sex)
    stat_user = FSInputFile(photo_path_user)

    analytics_reg1 = os.path.abspath("statistic_png/reg_stat/reg_for1_day.txt")
    analytics_reg2 = os.path.abspath("statistic_png/reg_stat/reg_for7_days.txt")
    analytics_reg3 = os.path.abspath("statistic_png/reg_stat/reg_for31_days.txt")
    analytics_age = os.path.abspath("statistic_png/age_stat/age_statistic.txt")
    analytics_sex = os.path.abspath("statistic_png/sex_stat/statistics.txt")
    analytics_user = os.path.abspath("statistic_png/user_stat/users_count.txt")

    async def read_file(file_path):
        async with aiofiles.open(file_path, mode='r', encoding='windows-1251', errors='replace') as f:
            return await f.read()

    reg1_text = await read_file(analytics_reg1)
    reg2_text = await read_file(analytics_reg2)
    reg3_text = await read_file(analytics_reg3)
    age_text = await read_file(analytics_age)
    sex_text = await read_file(analytics_sex)
    user_text = await read_file(analytics_user)

    # async with open()
    await message.answer_media_group(media=media)
    await message.answer(f"<b>{datetime_now}</b>\nАналитика по регистрациям:\n{reg1_text}\n{reg2_text}\n{reg3_text}")
    await message.answer_photo(photo=stat_age, caption=f"<b>{datetime_now}</b>\nАналитика по возрастам:\n{age_text}")
    await message.answer_photo(photo=stat_sex, caption=f"<b>{datetime_now}</b>\nАналитика по полам:\n{sex_text}")
    await message.answer_photo(photo=stat_user, caption=f"<b>{datetime_now}</b>\nАналитика по пользователям:\n{user_text}")

