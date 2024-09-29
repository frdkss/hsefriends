from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.inline_keyboards import main_menu, main_settings
from keyboards.default_keyboards import confirmation

from states import rewrite_state

from database.db_cfg import accounts_db_session
from database.models import AccountsTable

router = Router()


@router.callback_query(F.data == "menu")
async def callback_menu(event: Message | CallbackQuery):
    user = accounts_db_session.query(AccountsTable).filter_by(chat_id=event.chat.id).first()
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
