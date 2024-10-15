import html

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.db_cfg import statistics_db_session
# from database.models import StatTable
from keyboards.inline_keyboards import first_registration_keyboard
from log.logger_cfg import command_logger

from callbacks import usr_callbacks
from states import first_registration_state, rewrite_state

from sqlalchemy.future import select

router = Router()


@router.message(Command("start"))
async def command_start(message: Message):
    command_logger.info("user used /start command")
    usr_first_name = html.escape(message.from_user.first_name)
    usr_last_name = html.escape(message.from_user.last_name) if message.from_user.last_name else None
    if usr_last_name is None:
        await message.answer(f"Добро пожаловать в HSE Friends!, <b><a href=\"t.me/{message.from_user.username}\">"
                             f"{usr_first_name}</a></b>! ",
                             disable_web_page_preview=True,
                             reply_markup=first_registration_keyboard)
        command_logger.info(f"user: {message.from_user.username}, haven't last name")
    else:
        await message.answer(f"Добро пожаловать в HSE Friends!, <b><a href=\"t.me/{message.from_user.username}\">"
                             f"{usr_first_name} {usr_last_name}</a></b>!",
                             disable_web_page_preview=True,
                             reply_markup=first_registration_keyboard)
        command_logger.info(f"user: {message.from_user.username}, have last name")


@router.message(Command("reg"))
async def command_first_registration(message: Message, state: FSMContext):
    await first_registration_state.user_first_reg(message, state)


@router.message(Command("menu"))
async def command_menu(message: Message):
    await usr_callbacks.callback_menu(message)


@router.message(Command("settings"))
async def command_settings(message: Message):
    await usr_callbacks.callback_settings(message)


@router.message(Command("rewrite"))
async def command_rewrite_profile(message: Message, state: FSMContext):
    await rewrite_state.user_rewrite(message, state)


@router.message(Command("disconnect_account"))
async def command_disconnect_account(message: Message):
    await usr_callbacks.callback_disconnect_account(message)


@router.message(Command("delete_account"))
async def command_delete_account(message: Message):
    await usr_callbacks.callback_delete_account(message)


@router.message(Command("feedback"))
async def command_feedback(message: Message):
    await usr_callbacks.callback_feedback(message)


@router.message(Command("edit_profile"))
async def command_edit_profile(message: Message):
    await usr_callbacks.callback_edit_profile(message)


@router.message(Command("edit_name"))
async def command_edit_name(message: Message):
    await usr_callbacks.callback_edit_name(message)


@router.message(Command("edit_age"))
async def command_edit_age(message: Message):
    await usr_callbacks.callback_edit_age(message)


@router.message(Command("edit_sex"))
async def command_edit_sex(message: Message):
    await usr_callbacks.callback_edit_sex(message)


@router.message(Command("edit_faculty"))
async def command_edit_faculty(message: Message):
    await usr_callbacks.callback_edit_faculty(message)


@router.message(Command("edit_degree"))
async def command_edit_degree(message: Message):
    await usr_callbacks.callback_edit_degree(message)


@router.message(Command("edit_course"))
async def command_edit_course(message: Message):
    await usr_callbacks.callback_edit_course(message)


@router.message(Command("edit_photo"))
async def command_edit_photo(message: Message):
    await usr_callbacks.callback_edit_photo(message)


@router.message(Command("edit_about"))
async def command_edit_about(message: Message):
    await usr_callbacks.callback_edit_about(message)


@router.message(Command("edit_friend_sex"))
async def command_edit_friend_sex(message: Message):
    await usr_callbacks.callback_edit_friend_sex(message)

# @router.message(Command("test"))
# async def command_test(message:Message):
#     async with statistics_db_session() as session:
#         async with session.begin():
#             qwe = await session.execute(select(StatTable))
#             ewq = qwe.scalar_one_or_none()
#             if qwe:
#                 if ewq:
#                     print(ewq.account_id)
#                 else:
#                     print("None")
