from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

first_registration_keyboard = InlineKeyboardMarkup(row_width=1,
                                             inline_keyboard=[
                                                 [InlineKeyboardButton(text='Регистрация', callback_data='first_reg')]
                                             ])
