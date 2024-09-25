from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from keyboards.inline_keyboards import first_registration_keyboard
from log.logger_cfg import command_logger

router = Router()


@router.message(Command("start"))
async def start_msg(message: Message):
    command_logger.info("user used /start command")
    if message.from_user.last_name is None:
        await message.answer(f"Привет <b><a href=\"t.me/{message.from_user.username}\">"
                             f"{message.from_user.first_name}</a></b>! "
                             f"Давай начнем регистрацию твоего аккаунта в HSE Friends",
                             disable_web_page_preview=True,
                             reply_markup=first_registration_keyboard)
        command_logger.info(f"user: {message.from_user.username}, haven't last name")
    else:
        await message.answer(f"Привет <b><a href=\"t.me/{message.from_user.username}\">"
                             f"{message.from_user.first_name} {message.from_user.last_name}</a></b>! "
                             f"Давай начнем регистрацию твоего аккаунта в HSE Friends",
                             disable_web_page_preview=True,
                             reply_markup=first_registration_keyboard)
        command_logger.info(f"user: {message.from_user.username}, have last name")
