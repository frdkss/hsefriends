from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

first_registration_keyboard = InlineKeyboardMarkup(row_width=1,
                                             inline_keyboard=[
                                                 [InlineKeyboardButton(text='Регистрация', callback_data='first_reg')]
                                             ])

main_menu = InlineKeyboardMarkup(row_width=2,
                            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text='Искать людей!', callback_data='start_search'),
                                    InlineKeyboardButton(text='Мой профиль', callback_data='profile'),
                                    InlineKeyboardButton(text='Настройки', callback_data='settings')
                                ],
                                [
                                    InlineKeyboardButton(text='Помощь', callback_data='help')
                                ]
                            ])

main_settings = InlineKeyboardMarkup(row_width=3,
                                inline_keyboard=[
                                    [
                                        InlineKeyboardButton(text='Изменить профиль', callback_data='edit_profile'),
                                        InlineKeyboardButton(text='Перезаписать профиль',
                                                             callback_data='rewrite_profile'),
                                        InlineKeyboardButton(text='Отключить профиль', callback_data='off_profile'),
                                        InlineKeyboardButton(text='Удалить профиль', callback_data='delete_profile')
                                    ],
                                    [
                                        InlineKeyboardButton(text='Обратная связь', callback_data='feedback')
                                    ]
                                ])

edit_profile = InlineKeyboardMarkup(row_width=3,
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(text='Имя', callback_data='edit_name'),
                                            InlineKeyboardButton(text='Возраст', callback_data='edit_age'),
                                            InlineKeyboardButton(text='Пол', callback_data='edit_sex')
                                        ],
                                        [
                                            InlineKeyboardButton(text='Факультет', callback_data='edit_faculty'),
                                            InlineKeyboardButton(text='Степень', callback_data='edit_degree'),
                                            InlineKeyboardButton(text='Курс', callback_data='edit_course')
                                        ],
                                        [
                                            InlineKeyboardButton(text='Фото', callback_data='edit_photo'),
                                            InlineKeyboardButton(text='"О себе"', callback_data='edit_about'),
                                            InlineKeyboardButton(text='Пол друга', callback_data='edit_friend_sex')
                                        ]
                                    ])



get_back = InlineKeyboardMarkup(row_width=1,
                                inline_keyboard=[
                                    [InlineKeyboardButton(text="back", callback_data="back")]
                                ])
