from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from log.logger_cfg import inline_kb_logger

# from database.db_cfg import accounts_db_session
from database.models import AccountsTable
from .forms.state_forms import FirstRegistration

router = Router()


@router.callback_query(F.data == 'rewrite_profile')
def user_rewrite(event: Message | CallbackQuery, state: FSMContext):
    pass
