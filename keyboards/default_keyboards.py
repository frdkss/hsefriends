from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


user_sex = ReplyKeyboardMarkup(row_width=2,
                               resize_keyboard=True,
                               one_time_keyboard=True,
                               input_field_placeholder='Выберете пункт из меню ',
                               keyboard=[
                                   [
                                       KeyboardButton(text='Мужской'),
                                       KeyboardButton(text='Женский')
                                   ]
                               ])
user_isBaccalaureate = ReplyKeyboardMarkup(row_width=2,
                                           resize_keyboard=True,
                                           one_time_keyboard=True,
                                           input_field_placeholder='Выберете пункт из меню ',
                                           keyboard=[
                                               [
                                                   KeyboardButton(text="Бакалавриат"),
                                                   KeyboardButton(text="Магистратруа")
                                               ]
                                           ])

user_course_bac = ReplyKeyboardMarkup(row_width=4,
                                      resize_keyboard=True,
                                      one_time_keyboard=True,
                                      input_field_placeholder='Выберете пункт из меню ',
                                      keyboard=[
                                          [
                                              KeyboardButton(text="1"),
                                              KeyboardButton(text="2"),
                                              KeyboardButton(text="3"),
                                              KeyboardButton(text="4")
                                          ]
                                      ])
user_course_mag = ReplyKeyboardMarkup(row_width=2,
                                      resize_keyboard=True,
                                      one_time_keyboard=True,
                                      input_field_placeholder='Выберете пункт из меню ',
                                      keyboard=[
                                          [
                                              KeyboardButton(text="1"),
                                              KeyboardButton(text="2")
                                          ]
                                      ])
no_photo = ReplyKeyboardMarkup(row_width=1,
                               resize_keyboard=True,
                               one_time_keyboard=True,
                               input_field_placeholder='Выберете пункт из меню ',
                               keyboard=[
                                       [KeyboardButton(text="Без фото")]
                               ])
no_about = ReplyKeyboardMarkup(row_width=1,
                               resize_keyboard=True,
                               one_time_keyboard=True,
                               input_field_placeholder='Выберете пункт из меню ',
                               keyboard=[
                                       [KeyboardButton(text="Без текста")]
                               ])
user_friend_sex = ReplyKeyboardMarkup(row_width=3,
                                      resize_keyboard=True,
                                      one_time_keyboard=True,
                                      input_field_placeholder='Выберете пункт из меню ',
                                      keyboard=[
                                          [
                                              KeyboardButton(text="Мужчины"),
                                              KeyboardButton(text="Девушки"),
                                              KeyboardButton(text="Без разницы")
                                          ]
                                      ])

# qwe
confirmation = ReplyKeyboardMarkup(row_width=2,
                                   resize_keyboard=True,
                                   one_time_keyboard=True,
                                   input_field_placeholder="Выберете пункт из меню",
                                   keyboard=[
                                       [
                                           KeyboardButton(text="Да"),
                                           KeyboardButton(text="Нет")
                                       ]
                                   ])
