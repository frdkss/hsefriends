import random
import time
from geopy.exc import GeocoderUnavailable
from telebot import *
from telebot.apihelper import ApiTelegramException
from telebot.types import *
import sqlite3
from geopy.geocoders import Nominatim
from random import shuffle, choice
import math
from datetime import datetime, timedelta
from threading import Thread, Lock

# строка из которой мы будем каждый раз составлять уникольный url адрес. Подробнее о нём рассказал в функции send_anket
string = (
        "0 1 2 3 4 5 6 7 8 9 a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z ! # $ % & ' ( ) * + , - . / : ; < = > ? @ [ \ ] ^ _ ` { | } ~" + ' "').split()

# подключаем бота
bot = TeleBot('6921263973:AAG94w0bjhvTvII3NoaQ8HGCFpkImruFRuM')
# подключаемся к базе данных
db = sqlite3.connect('DayVinchick.db', check_same_thread=False)
c = db.cursor()

# этот объект будет блокировать курсор для первого потока, пока его использует другой
lock = Lock()

# сообщаем всем пользователям о том, что бот запущен
try:
    lock.acquire(True)

    c.execute('SELECT id_tg, lang FROM users')
    for i in c.fetchall():
        end_message = {'ru': 'Введите команду /start, чтобы заново активировать бота!',
                       'uk': 'Введіть команду /start, щоб заново активувати бота!',
                       'en': 'Enter the /start command to reactivate the bot!',
                       'id': 'Masukkan perintah /start untuk mengaktifkan kembali bot!'}
        try:
            bot.send_message(i[0], end_message[i[1]], reply_markup=ReplyKeyboardRemove())
        except ApiTelegramException:
            pass
finally:
    lock.release()


# эта функция вызывается когда пользователь хочет активировать свою анкету послё её отключения
def wait_anket(message, after_what):
    id = message.from_user.id
    lang = get_something('lang', message.from_user.id)[0]

    # сообщения, которые пользователь должен отправить на разных языках
    user_wait_anket = {'ru': 'Смотреть анкеты', 'uk': 'Дивитися анкети', 'en': 'View profiles', 'id': 'Lihat profil'}
    # сообщение, которое отправится если пользователь отправил текст не с кнопки
    bot_error = {'ru': 'Нет такого варианта ответа', 'uk': 'Немає такого варіанту відповіді',
                 'en': 'No such option', 'id': 'Tiada jawapan seperti ini'}

    if message.text == user_wait_anket[lang]:
        try:
            lock.acquire(True)
            # активируем анкеты
            c.execute('UPDATE users SET is_search = True WHERE id_tg = ?', (id,))
            db.commit()
        finally:
            lock.release()

        if after_what == 'wait':
            func = lambda message: MyAnket().one_my_anket(message, 'command')
        else:
            func = Menu().after_something

        Lang().one_lang(message, func)
    else:
        send_message = bot.send_message(message.chat.id, bot_error[lang])
        bot.register_next_step_handler(send_message, lambda message: wait_anket(message, after_what))


# функция отправляет анкету. Параметр id указывает чью анкету нужно отправить, а параметр love_anket говорит о том, что в начале сообщения необходимо написать 'Кому-то понравилась твоя анкета'
def send_anket(message, id, markup=None, love_anket=False, my_anket=False):
    text_love_anket = {'ru': 'Кому-то понравилась твоя анкета:\n\n', 'uk': 'Комусь сподобалася твоя анкета:\n\n',
                       'en': 'Someone liked your profile:\n\n', 'id': 'Seseorang seperti profil Anda:\n\n'}
    text_my_anket = {'ru': 'Твой уникальный id, по которому можно найти твой профиль:',
                     'uk': 'Твій унікальний id, за яким можна знайти твій профіль:',
                     'en': 'Your unique id, which can be used to find your profile:',
                     'id': 'ID unik Anda, yang dapat digunakan untuk menemukan profil Anda:'}

    lang = get_something('lang', message.from_user.id)[0]  # получаем язык не по параметру id, а по id пользователя
    name, age, description, photo1, photo2, photo3, video, long, lat, insta = get_something(
        'name, age, description, photo1, photo2, photo3, video, long, lat, instagram', id)
    try:
        # в качестве user_agent каждый раз передаём рандомную строку. Это будет часть url адреса, по которому мы будем взаимодействовать с API. Проблема в том, что на каждый url адрес (я надеюсь что именно на url, а не на ip адрес) наложено ограничение по количеству запросов, и поэтому мы его каждый раз меняем
        geolocator = Nominatim(user_agent=random_str())
        location_address = geolocator.reverse(f"{lat}, {long}", language=lang, zoom=13)
    except GeocoderUnavailable as ge_error:
        print('GeocoderUnavailable ERROR - ' + str(ge_error))
        location_address = ''
    send_text = f"{name}, {age}\n{location_address}"

    if insta:
        send_text += '\n\n' + 'Insta: ' + str(insta)

    if description is not None:
        send_text += '\n\n' + description

    if love_anket:
        send_text = text_love_anket[lang] + send_text

    if my_anket:
        send_text += '\n\n' + text_my_anket[lang]

    if video is not None:
        new_message = bot.send_video(message.chat.id, video, caption=send_text, reply_markup=markup)
    elif photo2 is None and photo1 is not None:
        new_message = bot.send_photo(message.chat.id, photo1, send_text, reply_markup=markup)
    else:
        media = [InputMediaPhoto(photo1, ), InputMediaPhoto(photo2)]

        if photo3 is not None:
            media.append(InputMediaPhoto(photo3))

        bot.send_media_group(message.chat.id, media)
        new_message = bot.send_message(message.chat.id, send_text, reply_markup=markup)

    if my_anket:
        return bot.send_message(message.chat.id, message.from_user.id)

    return new_message


# функция достаёт определённый столбец из таблицы users по определённом айдишнику
def get_something(ctolb, id):
    try:
        lock.acquire(True)
        c.execute(f'SELECT {ctolb} FROM users WHERE id_tg = ?', (str(id),))
    finally:
        lock.release()
    return c.fetchone()


# функция возвращает строку из рандомных символов
def random_str(lenght=8):
    shuffle(string)
    return "".join([choice(string) for i in range(lenght)])


# сортирует список из анкет по количеству рефералов. Я передавал эту функцию в качестве ключа в методе sort
def to_sort(x):
    user_id = get_something('users_id', x[0])[0]

    try:
        lock.acquire(True)

        c.execute('SELECT COUNT(users_id) FROM referrals WHERE users_id = ? GROUP BY users_id',
                  (user_id,))
        count = c.fetchone()
    finally:
        lock.release()

    count = 0 if count is None else count[0]

    return count


# если это не одна из трёх команд, функция возвращает True, а иначе выполняет заданную команду и возвращает False. Я вызываю эту функцию всегда, когда пользователь отправляет мне что-то
def errors(message, self=None, func=None):
    # параметр self я указываю только тогда, когда пользователь смотрит анкеты, а параметр func лишь тогда, когда пользователь заполняет свою анкету. Параметр func передаётся, чтобы функция знала, какую функцию вызвать потом, если пользователь ещё не заполнил свою анкету
    exec(f'global run{message.from_user.id}\nrun{message.from_user.id}=None')

    bot_complaint = {
        'ru': 'Укажите причину жалобы\n\n1. 🔞 Материал для взрослых.\n2. 💊 Пропаганда наркотиков.\n3. 💰 Продажа товаров и услуг.\n4. 🦨 Другое.\n***\n9. Вернуться назад.',
        'uk': 'Вкажіть причину скарги\n\n1. 🔞 Матеріал для дорослих.\n2. 💊 Пропаганда наркотиків.\n3. 💰 Продаж товарів і послуг.\n4. 🦨 Інше.\n***\n9. Повернутись назад.',
        'en': 'Specify the reason for the complaint\n\n1. 🔞 Adult material.\n2. 💊 Drug propaganda.\n3. 💰 Sale of goods and services.\n4. 🦨 Other.\n***\n9. Go back.',
        'id': 'Tentukan alasan pengaduan\n\n1. 🔞 Bahan dewasa.\n2. 💊 Propaganda narkoba.\n3. 💰 Penjualan barang dan jasa.\n4. 🦨 Lainnya.\n***\n9. Kembali.'}
    bot_complaint_error = {'ru': 'Жалобу можно оставить только при просмотре анкеты',
                           'uk': 'Скаргу можна залишити тільки підчас просмотру анкет',
                           'en': 'You can leave a complaint only when viewing the questionnaire',
                           'id': 'Anda dapat meninggalkan keluhan hanya saat melihat kuesioner'}
    bot_not_reg = {"ru": 'Прежде чем использовать эту команду заполните анкету!',
                   'uk': 'Перш ніж використовувати цю команду заповніть анкету!',
                   'en': 'Before using this command, fill out the profile!',
                   'id': 'Sebelum menggunakan perintah ini, isi profil!'}
    user_complaint = {'all': ['1🔞', '2💊', '3💰', '4🦨', '9']}
    user_complaint_back = {'ru': ['Вернуться назад'], 'uk': ['Повернутись назад'], 'en': ['Go back'], 'id': ['Kembali']}

    commands = {'/myprofile': lambda: MyAnket().one_my_anket(message, 'command'),
                '/language': lambda: Lang().one_lang(message, func=lambda message: Menu().after_something(message)),
                '/start': lambda: start_func(message)}
    list_commands = ['/myprofile', '/language', '/start']

    lang = get_something('lang', message.from_user.id)[0]

    text = message.text

    if text in list_commands:
        # проверяем заполнил ли пользователь свою анкету
        reg = get_something('reg', message.from_user.id)[0]
        if reg or text == '/start':
            commands[text]()
            return False

        send_message = bot.send_message(message.chat.id, bot_not_reg[lang])
        bot.register_next_step_handler(send_message, func)
        return False
    elif text == '/complaint':
        # проверяем заполнил ли пользователь свою анкету
        reg = get_something('reg', message.from_user.id)[0]
        if reg:
            if self:
                markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=5)
                markup.add(*user_complaint['all'])

                send_message = bot.send_message(message.chat.id, bot_complaint[self.lang], reply_markup=markup)
                bot.register_next_step_handler(send_message, self.complaint)

                return False

            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*user_complaint_back[lang])

            send_message = bot.send_message(message.chat.id, bot_complaint_error[lang], reply_markup=markup)
            bot.register_next_step_handler(send_message, errors)

            return False

        send_message = bot.send_message(message.chat.id, bot_not_reg[lang])
        bot.register_next_step_handler(send_message, func)
        return False
    elif text in user_complaint_back[lang]:
        ViewsAnket().start(message)
        return False

    return True


# класс благодаря которому можно выбрать или изменить язык
class Lang:
    def __init__(self):
        self.bot_lang = {'ru': 'Язык:', 'uk': 'Мова:', 'en': 'Language:', 'id': 'Bahasa:'}
        self.bot_lang_error = {'ru': 'Нет такого варианта ответа', 'uk': 'Немає такого варіанту відповіді',
                               'en': 'No such option', 'id': 'Tiada jawapan seperti ini'}

        self.user_lang = {'all': ['🇷🇺 Русский', '🇺🇦 Українська', '🇬🇧 English', '🇲🇾 Malay']}

        self.server_lang = {'🇷🇺 Русский': 'ru', '🇺🇦 Українська': 'uk', '🇬🇧 English': 'en', '🇲🇾 Malay': 'id'}

    # функция отправляет сообщение и кнопки для выбора языка
    def one_lang(self, message, func=None):
        self.lang = get_something('lang', message.from_user.id)[0]
        self.func = func
        self.id = message.from_user.id

        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(*self.user_lang['all'])

        send_message = bot.send_message(message.chat.id, self.bot_lang[self.lang], reply_markup=markup)
        bot.register_next_step_handler(send_message, self.two_lang)

    # функция принимает то, что отправил пользователь и изменяет язык
    def two_lang(self, message):
        text = message.text

        if text in self.user_lang['all']:
            try:
                lock.acquire(True)
                c.execute('UPDATE users SET lang = ? WHERE id_tg = ? ', (self.server_lang[text], self.id))
                db.commit()
            finally:
                lock.release()
            if not self.func is None:
                self.func(message)
        else:
            if errors(message, func=self.two_lang):
                send_message = bot.send_message(message.chat.id, self.bot_lang_error[self.lang])
                bot.register_next_step_handler(send_message, self.two_lang)


# класс просто отправляет два соощения новым пользователям
class Start:
    def __init__(self):
        self.bot_description = {
            'ru': 'Уже миллионы людей знакомятся в Дайвинчике😍\n\nЯ помогу найти тебе пару или просто друзей👫',
            'uk': 'Вже мільйони людей зустрічаються у Дайвинчике😍\n\nЯ допоможу тобі знайти другу половинку або просто друзів☺',
            'en': 'Already millions of people meet in Daivinchik😍\n\nI will help you find a mate or just friends👫',
            'id': 'Sudah jutaan orang bertemu di Daivinchik😍\n\nSaya akan membantu Anda menemukan jodoh atau hanya teman👫'}
        self.bot_description_error = {'ru': 'Нет такого варианта ответа', 'uk': 'Немає такого варіанту відповіді',
                                      'en': 'No such option', 'id': 'Tiada jawapan seperti ini'}
        self.bot_warning = {
            'ru': '❗Помни, что в интернете люди могут выдавать себя за других. Бот не запрашивает личные данные и не идентифицирует пользователей по паспортным данным. Продолжая ты соглашаешься с использованием бота на свой страх и риск.',
            'uk': '❗Пам\'ятайте, що в Інтернеті люди можуть видавати себе за інших. Бот не запитує персональні дані і не ідентифікує користувачів за будь-якими документами. Продовжуючи, ви погоджуєтеся використовувати бота на свій страх і ризик.',
            'en': '❗Remember that on the Internet people can impersonate others. The bot does not ask personal data and does not identify users by any documents. By continuing, you agree to use of the bot at your own risk.',
            'id': '❗Ingat bahwa di internet orang bisa meniru orang lain. Bot tidak meminta data pribadi dan tidak mengidentifikasi pengguna dengan dokumen apa pun. Dengan melanjutkan, Anda setuju untuk menggunakan bot dengan risiko Anda sendiri.'}
        self.bot_warning_error = {'ru': 'Нет такого варианта ответа', 'uk': 'Немає такого варіанту відповіді',
                                  'en': 'No such option', 'id': 'Tiada jawapan seperti ini'}

        self.user_descpiption = {'ru': ['👌давай начнём'], 'uk': ['👌давайте почнемо'], 'en': ['👌let\'s start'],
                                 'id': ['👌mari kita mulai']}
        self.user_warning = {'ru': ['👌Ok'], 'uk': ['👌Гаразд'], 'en': ['👌Ok'], 'id': ['👌Ok']}

    # отправляет первое сообщение
    def one_start(self, message):
        self.lang = get_something('lang', message.from_user.id)[0]

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*self.user_descpiption[self.lang])

        send_message = bot.send_message(message.chat.id, self.bot_description[self.lang], reply_markup=markup)
        bot.register_next_step_handler(send_message, self.two_start)

    # принимает то, что отправил пользователь в первом сообщении и отправляет второе
    def two_start(self, message):
        text = message.text

        if text in self.user_descpiption[self.lang]:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*self.user_warning[self.lang])

            send_message = bot.send_message(message.chat.id, self.bot_warning[self.lang], reply_markup=markup)
            bot.register_next_step_handler(send_message, self.three_start)
        else:
            if errors(message, func=self.two_start):
                send_message = bot.send_message(message.chat.id, self.bot_description_error[self.lang])
                bot.register_next_step_handler(send_message, self.two_start)

    # принимает то, что отправил пользователь о втором сообщении и вызывает класс, который реализует создание анкеты
    def three_start(self, message):
        text = message.text

        if text in self.user_warning[self.lang]:
            Anket().one_anket(message)
        else:
            if errors(message, func=self.three_start):
                send_message = bot.send_message(message.chat.id, self.bot_warning_error[self.lang])
                bot.register_next_step_handler(send_message, self.three_start)


# класс позволяет создать или изменить анкету
class Anket:
    def __init__(self):
        self.bot_age = {'ru': 'Сколько тебе лет?', 'uk': 'Скільки тобі років?', 'en': 'Your age?',
                        'id': 'Berapa umur anda?'}
        self.bot_age_error = {'ru': 'Укажи правильный возраст, только цифры',
                              'uk': 'Вкажи правильний вік, тільки цифри', 'en': 'Tell me your age, numbers only',
                              'id': 'Sila masukkan umur yang betul, hanya nombor'}
        self.bot_male = {'ru': 'Теперь определимся с полом', 'uk': 'Тепер оберемо стать', 'en': 'Specify your gender',
                         'id': 'Sekarang mari kita menyertakan jantina'}
        self.bot_male_error = {'ru': 'Нет такого варианта ответа', 'uk': 'Немає такого варіанту відповіді',
                               'en': 'No such option', 'id': 'Tiada jawapan seperti ini'}
        self.bot_who_love = {'ru': 'Кто тебе интересен?', 'uk': 'Хто тебе цікавить?', 'en': 'Who are you looking for?',
                             'id': 'Siapa yang menarik minat anda?'}
        self.bot_who_love_error = {'ru': 'Нет такого варианта ответа', 'uk': 'Немає такого варіанту відповіді',
                                   'en': 'No such option', 'id': 'Tiada jawapan seperti ini'}
        self.bot_other_age = {
            'ru': 'Отправьте минимальный и максимальный возраст людей, которых хотите видеть в анкете в следующем формате -\n10/17\nЭто будет значит, что вам будут попадаться анкеты возрастом от 10 до 17 лет.',
            'uk': 'Надішліть мінімальний і максимальний вік людей, яких хочете бачити в анкеті в наступному форматі - \n10/17\nЦе буде означає, що вам будуть потрапляти анкети віком від 10 до 17 років.',
            'en': 'Send the minimum and maximum age of the people you want to see in the questionnaire in the following format - \n10/17\nThis will mean that you will come across questionnaires aged from 10 to 17 years.',
            'id': 'Kirim usia minimum dan maksimum orang yang ingin Anda lihat dalam kuesioner dalam format berikut - \n10/17\nIni berarti Anda akan menemukan kuesioner berusia 10 hingga 17 tahun.'}
        self.bot_other_age_error = {
            'ru': 'Неверный формат. Нужен следующий -\n<число>/<число>\nБез точки в конце! Пример -\n10/17',
            'uk': 'Невірний формат. Потрібен наступний - \n<число>/<число>\n Без крапки в кінці! Приклад - \n10/17',
            'en': 'Invalid format. We need this one - \n<number>/<number>\n Without a dot at the end! Example - \n10/17',
            'id': 'Format tidak valid. Kita membutuhkan yang ini - \n<nomor>/<nomor>\n Tanpa titik di akhir! Contoh- \n10/17'}
        self.bot_other_age_error_age = {
            'ru': 'Слишком большой или маленький возраст. Возраст должен быть от 1 до 110 и первое число должно быть меньше второго!',
            'uk': 'Занадто великий або маленький вік. Вік повинен бути від 1 до 110 і перше число повинно бути менше другого!',
            'en': 'Too old or too young. The age should be from 1 to 110 and the first number should be less than the second!',
            'id': 'Terlalu tua atau terlalu muda. Usia harus dari 1 hingga 110 dan angka pertama harus kurang dari yang kedua!'}
        self.bot_city = {'ru': 'Из какого ты города? Отправь геометку или название города.',
                         'uk': 'З якого ти міста? Відправ геометку або назву міста.',
                         'en': 'What city are you from? Send the geometry or the name of the city.',
                         'id': 'Dari kota mana kamu berasal? Kirim geometri atau nama kota.'}
        self.bot_city_show_adress = {'ru': 'Это твой адрес?\n\n', 'uk': 'Це твоя адреса?\n\n',
                                     'en': 'Is this your address?\n\n', 'id': 'Apakah ini alamat anda?\n\n'}
        self.bot_city_show_adress_error = {'ru': 'Нет такого варианта ответа', 'uk': 'Немає такого варіанту відповіді',
                                           'en': 'No such option', 'id': 'Tiada jawapan seperti ini'}
        self.bot_city_error = {"ru": 'Отправьте геометку, город не найден',
                               'uk': 'Надішліть геометку, місто не знайдено', 'en': 'Send location, city not found',
                               'id': 'Kirim lokasi, kota tidak ditemukan'}
        self.bot_city_error_none = {"ru": 'Вы ещё не отправляли местоположение',
                                    'uk': 'Ви ще не надіслали місцеположення',
                                    'en': 'You haven\'t sent the location yet',
                                    'id': 'Anda belum mengirim lokasi belum'}
        self.bot_name = {'ru': 'Как мне тебя называть?', 'uk': 'Як до тебе звертатись?', 'en': 'What’s your name?',
                         'id': 'Apa aku patut panggil?'}
        self.bot_name_error = {"ru": 'Отправьте имя длинною не более 50 символов',
                               'uk': 'Надішліть ім\'я довжиною не більше 50 символів',
                               'en': 'Send a name no longer than 50 characters',
                               'id': 'Kirim Nama tidak lebih dari 50 karakter'}
        self.bot_instagram = {
            'ru': 'Отправьте ссылку на профиль в инстаграмме или ник с @. Пример: https://www.instagram.com/dava_m или @dava_m',
            'uk': 'Надішліть посилання на профіль в Instagram або нік з @. Приклад: https://www.instagram.com/dava_m або @dave_m',
            'en': 'Send a link to your Instagram profile or a nickname with @. Example: https://www.instagram.com/dava_m or @dave_m',
            'id': 'Kirim tautan ke profil Instagram Anda atau nama panggilan dengan @. Contoh: https://www.instagram.com/dava_m atau @dave_m'}
        self.bot_instagram_error = {'ru': 'Неверный формат ника или несуществующая ссылка',
                                    'uk': 'Невірний формат юзернейма або неіснуюча посилання',
                                    'en': 'Invalid username format or non-existent link',
                                    'id': 'Format nama pengguna tidak valid atau tautan tidak ada'}
        self.bot_descpription = {
            'ru': 'Расскажи о себе и кого хочешь найти, чем предлагаешь заняться. Это поможет лучше подобрать тебе компанию.',
            'uk': 'Розкажи про себе, кого хочеш знайти, чим пропонуєш зайнятись. Це допоможе краще підібрати тобі компанію',
            'en': 'Tell more about yourself. Who are you looking for? What do you want to do? I\'ll find the best matches.',
            'id': 'Beritahu tentang diri anda lebih dan siapa yang anda mahu cari, apa yang anda mahu lakukan. Inilah akan membantu anda mencari seseorang yang baik.'}
        self.bot_descpription_error = {'ru': 'Отправьте текст', 'uk': 'Надішліть текст', 'en': 'Send a text',
                                       'id': 'Mengirim pesan teks'}
        self.bot_photo = {
            'ru': 'Теперь пришли фото или запиши видео 👍 (до 15 сек), его будут видеть другие пользователи',
            'uk': 'Тепер надішли фото чи запиши відео 👍 (до 15 сек), його побачать інші користувачі',
            'en': 'Send your photo or video 👍 (up to 15 sec) for other users to see',
            'id': 'Sekarang sila menghantar foto atau video 👍 (hingga 15 detik), pengguna lain akan melihatnya'}
        self.bot_photo_error = {'ru': 'Пришли фото или видео(до 15 сек)', 'uk': 'Надішли фото чи відео (до 15 сек)',
                                'en': 'Send your photo or video (up to 15 sec)',
                                'id': 'Sila menghantar foto atau video(hingga 15 detik)'}
        self.bot_photo_avatar_error = {'ru': 'Не получилось скачать фото с аватара, отправьте фото или видео!',
                                       'uk': 'Не вийшло завантажити фото з аватара, відправте фото або відео!',
                                       'en': 'I couldn\'t download a photo from the avatar, send a photo or video!',
                                       'id': 'Saya tidak dapat mengunduh foto dari avatar, mengirim foto atau video!'}
        self.bot_photo_error_none = {'ru': 'Вы ещё не отправляли фото', 'uk': 'Ви ще не відправляли фото',
                                     'en': 'You haven\'t sent a photo yet', 'id': 'Anda belum mengirim foto'}
        self.bot_edit_photo = {'ru': 'Пришли фото или запиши видео 👍 (до 15 сек)',
                               'uk': 'Надішли фото чи запиши відео 👍  (до 15 сек)',
                               'en': 'Send your photo/video (up to 15 sec)',
                               'id': 'Sila hantarkan foto atau video 👍 (hingga 15 detik)'}
        self.bot_photo_mane = {
            'ru': 'Фото добавлено - # из 3. Ещё одно?',
            'uk': 'Фото додане – # з 3. Ще одне?',
            'en': 'Photo added  – # from 3. One more?',
            'id': 'Foto ditambah – 1 daripada 3 . Іatu lagi?'
        }

        self.user_male = {'ru': ['Я девушка', 'Я парень'], 'uk': ['Я дівчина', 'Я хлопець'], 'en': ['Female', 'Male'],
                          'id': ['Aku gadis', 'Aku lekaki']}
        self.user_who_love = {'ru': ['Девушки', 'Парни', 'Всё равно'], 'uk': ['Дівчата', 'Хлопці', 'Все одно'],
                              'en': ['Women', 'Men', 'No matter'], 'id': ['Gadis', 'Lekaki', 'Tak peduli']}
        self.user_other_age = {'ru': ['Пропустить', 'Оставить текущий'],
                               'uk': ['Пропустити', 'Лишити поточний'], 'en': ['Skip', 'Leave current age'],
                               'id': ['Langkau', 'Tinggalkan usia saat ini']}
        self.user_city = {'ru': ['Поделиться местоположением', 'Оставить текущее'],
                          'uk': ['Поділитися місцем розташування', 'Лишити так, як є'],
                          'en': ['Share Location', 'Leave current'], 'id': ['Berbagi Lokasi', 'Simpan semasa']}
        self.user_city_show_adress = {'ru': ['Продолжить', 'Изменить адрес'], 'uk': ['Продовжити', 'змінити адресу'],
                                      'en': ['Continue', 'Change Address'], 'id': ['Lanjutkan', 'Ubah Alamat']}
        self.user_instagram = {'ru': ['Пропустить', 'Оставить текущий'],
                               'uk': ['Пропустити', 'Залишити поточний'], 'en': ['Skip', 'Leave the current link'],
                               'id': ['Langkau', 'Tinggalkan tautan saat ini']}
        self.user_descpription = {'ru': ['Пропустить', 'Оставить текущий текст'],
                                  'uk': ['Пропустити', 'Лишити поточний текст'], 'en': ['Skip', 'Leave current text'],
                                  'id': ['Langkau', 'Simpan teks semasa']}
        self.user_photo = {'ru': ['Взять с аватарки', 'Оставить текущее'],
                           'uk': ['Взяти з аватарки', 'Лишити так, як є'],
                           'en': ['Take from the avatar', 'Leave current'],
                           'id': ['Ambil dari avatar', 'Simpan semasa']}
        self.user_photo_mane = {'ru': ['Это все, сохранить фото'], 'uk': ['Це все, зберегти фото'],
                                'en': ['Done, save the photos'], 'id': ['Selesai, simpan foto']}
        self.user_edit = {'ru': ['Вернуться назад'], 'uk': ['Повернутись назад'],
                          'en': ['Go back'], 'id': ['Kembali']}

    # функция создаёт все нужные переменные экземпляра класса и отправляет сообщение с выбором возраста
    def one_anket(self, message):
        self.edit = False
        self.count_photo = 0
        self.photo1 = None
        self.photo2 = None
        self.photo3 = None
        self.do = 'quest'
        self.lang = get_something('lang', message.from_user.id)[0]
        self.id = message.from_user.id

        old_age = get_something('age', self.id)[0]
        if old_age is not None:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(str(old_age))
        else:
            markup = ReplyKeyboardRemove()

        send_message = bot.send_message(message.chat.id, self.bot_age[self.lang], reply_markup=markup)
        bot.register_next_step_handler(send_message, self.two_anket)

    # функция принимает сообщение с возрастом и отправляет сообщение с выбором пола
    def two_anket(self, message):
        text = message.text

        if text.isdigit():
            text = int(text)
            if text <= 110:
                self.age = text

                markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                markup.add(*self.user_male[self.lang])

                send_message = bot.send_message(message.chat.id, self.bot_male[self.lang],
                                                reply_markup=markup)
                bot.register_next_step_handler(send_message, self.three_anket)
            else:
                send_message = bot.send_message(message.chat.id, self.bot_age_error[self.lang])
                bot.register_next_step_handler(send_message, self.two_anket)
        else:
            if errors(message, func=self.two_anket):
                send_message = bot.send_message(message.chat.id, self.bot_age_error[self.lang])
                bot.register_next_step_handler(send_message, self.two_anket)

    # функция принимает сообщение с полом и отправляет сообщение с выбором того, кто нравится пользователю
    def three_anket(self, message):
        text = message.text

        if text in self.user_male[self.lang]:
            if text == self.user_male[self.lang][0]:
                self.male = 'w'
            else:
                self.male = 'm'

            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            markup.add(*self.user_who_love[self.lang])

            send_message = bot.send_message(message.chat.id, self.bot_who_love[self.lang],
                                            reply_markup=markup)
            bot.register_next_step_handler(send_message, self.four_anket)
        else:
            if errors(message, func=self.three_anket):
                send_message = bot.send_message(message.chat.id, self.bot_male_error[self.lang])
                bot.register_next_step_handler(send_message, self.three_anket)

    # функция принимает сообщение, в котором написано, кто нравится пользователю и отправляет сообщение для указания возраста анкет, которых пользователь захочет видеть
    def four_anket(self, message):
        text = message.text

        if text in self.user_who_love[self.lang]:
            if text == self.user_male[self.lang][0]:
                self.love = 'w'
            elif text == self.user_male[self.lang][1]:
                self.love = 'm'
            else:
                self.love = 'n'

            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

            self.old_min_age, self.old_max_age = get_something('min_age, max_age', self.id)

            if self.old_min_age is None or self.old_max_age is None:
                markup.add(self.user_other_age[self.lang][0])
            elif self.old_min_age == int(self.age) - 5 and self.old_max_age == int(self.age) + 5:
                markup.add(self.user_other_age[self.lang][0])
            else:
                markup.add(*self.user_other_age[self.lang])

            send_message = bot.send_message(message.chat.id, self.bot_other_age[self.lang], reply_markup=markup)
            bot.register_next_step_handler(send_message, self.five_anket)
        else:
            if errors(message, func=self.four_anket):
                send_message = bot.send_message(message.chat.id, self.bot_who_love_error[self.lang])
                bot.register_next_step_handler(send_message, self.four_anket)

    # функция принимает сообщение, в котором указано в каком диапозоне возрастов искать анкеты для него и отправляет сообщение с отправкой своего местоположения
    def five_anket(self, message):
        text = message.text

        ages = text.split('/')

        if len(ages) == 2 and ages[0] != '':
            if ages[0].isdigit() and ages[1].isdigit():
                min_age, max_age = list(map(int, ages))
                if (min_age > 0 and max_age <= 110) and (min_age < max_age):
                    self.min_age, self.max_age = min_age, max_age

                    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                    self.is_geo = get_something('long', self.id)[0]
                    if self.is_geo is None:
                        markup.add(KeyboardButton(self.user_city[self.lang][0], request_location=True))
                    else:
                        markup.add(KeyboardButton(self.user_city[self.lang][0], request_location=True),
                                   self.user_city[self.lang][1])

                    send_message = bot.send_message(message.chat.id, self.bot_city[self.lang],
                                                    reply_markup=markup)
                    bot.register_next_step_handler(send_message, self.six_anket)
                else:
                    send_message = bot.send_message(message.chat.id, self.bot_other_age_error_age[self.lang])
                    bot.register_next_step_handler(send_message, self.five_anket)
            else:
                send_message = bot.send_message(message.chat.id, self.bot_other_age_error[self.lang])
                bot.register_next_step_handler(send_message, self.five_anket)
        elif text == self.user_other_age[self.lang][0]:
            self.min_age, self.max_age = int(self.age) - 5, int(self.age) + 5

            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            self.is_geo = get_something('long', self.id)[0]
            if self.is_geo is None:
                markup.add(KeyboardButton(self.user_city[self.lang][0], request_location=True))
            else:
                markup.add(KeyboardButton(self.user_city[self.lang][0], request_location=True),
                           self.user_city[self.lang][1])

            send_message = bot.send_message(message.chat.id, self.bot_city[self.lang],
                                            reply_markup=markup)
            bot.register_next_step_handler(send_message, self.six_anket)
        elif text == self.user_other_age[self.lang][1]:
            self.min_age = self.max_age = 'old'

            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            self.is_geo = get_something('long', self.id)[0]
            if self.is_geo is None:
                markup.add(KeyboardButton(self.user_city[self.lang][0], request_location=True))
            else:
                markup.add(KeyboardButton(self.user_city[self.lang][0], request_location=True),
                           self.user_city[self.lang][1])

            send_message = bot.send_message(message.chat.id, self.bot_city[self.lang],
                                            reply_markup=markup)
            bot.register_next_step_handler(send_message, self.six_anket)
        else:
            if errors(message, func=self.five_anket):
                send_message = bot.send_message(message.chat.id, self.bot_other_age_error[self.lang])
                bot.register_next_step_handler(send_message, self.five_anket)

    # функция принимает сообщение с местоположением и отправляет сообщение с выбором имени
    def six_anket(self, message):
        text = message.text

        if message.location is not None:
            location = message.location

            self.long = location.longitude
            self.lat = location.latitude

            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

            old_name = get_something('name', self.id)[0]

            if old_name is not None and old_name != message.from_user.first_name:
                markup.add(old_name)
            markup.add(message.from_user.first_name)

            send_message = bot.send_message(message.chat.id, self.bot_name[self.lang],
                                            reply_markup=markup)
            bot.register_next_step_handler(send_message, self.seven_anket)
        elif text == self.user_city[self.lang][-1]:
            if self.is_geo is not None:
                self.long = 'old'
                self.lat = 'old'

                markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

                old_name = get_something('name', self.id)[0]
                if old_name is not None and old_name != message.from_user.first_name:
                    markup.add(old_name)

                markup.add(message.from_user.first_name)

                send_message = bot.send_message(message.chat.id, self.bot_name[self.lang],
                                                reply_markup=markup)
                bot.register_next_step_handler(send_message, self.seven_anket)
            else:
                send_message = bot.send_message(message.chat.id, self.bot_city_error_none[self.lang])
                bot.register_next_step_handler(send_message, self.six_anket)
        else:
            if errors(message, func=self.six_anket):
                geolocator = Nominatim(user_agent=random_str())
                location_address = geolocator.geocode(text, language=message.from_user.language_code)
                if location_address is None:
                    send_message = bot.send_message(message.chat.id, self.bot_city_error[self.lang])
                    bot.register_next_step_handler(send_message, self.six_anket)
                else:
                    self.long = location_address.longitude
                    self.lat = location_address.latitude

                    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                    markup.add(*self.user_city_show_adress[self.lang])

                    send_message = bot.send_message(message.chat.id,
                                                    self.bot_city_show_adress[self.lang] + location_address.address,
                                                    reply_markup=markup)
                    bot.register_next_step_handler(send_message, self.show_adress_if_text)

    # эта функция вызывается лишь когда пользователь ввёл свой адрес как текст, чтобы проверить верно ли бот нашёл координаты этого адреса
    def show_adress_if_text(self, message):
        text = message.text

        if text == self.user_city_show_adress[self.lang][0]:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

            old_name = get_something('name', self.id)[0]

            if old_name is not None and old_name != message.from_user.first_name:
                markup.add(old_name)
            markup.add(message.from_user.first_name)

            send_message = bot.send_message(message.chat.id, self.bot_name[self.lang],
                                            reply_markup=markup)
            bot.register_next_step_handler(send_message, self.seven_anket)
        elif text == self.user_city_show_adress[self.lang][1]:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            self.is_geo = get_something('long', self.id)[0]
            if self.is_geo is None:
                markup.add(KeyboardButton(self.user_city[self.lang][0], request_location=True))
            else:
                markup.add(KeyboardButton(self.user_city[self.lang][0], request_location=True),
                           self.user_city[self.lang][1])

            send_message = bot.send_message(message.chat.id, self.bot_city[self.lang],
                                            reply_markup=markup)
            bot.register_next_step_handler(send_message, self.six_anket)
        else:
            if errors(message, func=self.show_adress_if_text):
                send_message = bot.send_message(message.chat.id, self.bot_city_show_adress_error[self.lang])
                bot.register_next_step_handler(send_message, self.show_adress_if_text)

    # функция принимает сообщение с именем и отправляет сообщение для добавления инстаграмма
    def seven_anket(self, message):
        text = message.text

        if text is not None:
            if len(text) < 50 and text not in ['/start', '/myprofile', '/language', '/complaint']:
                self.name = text

                markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

                if get_something('instagram', self.id)[0] is None:
                    markup.add(self.user_instagram[self.lang][0])
                else:
                    markup.add(*self.user_instagram[self.lang])

                send_message = bot.send_message(message.chat.id, self.bot_instagram[self.lang],
                                                reply_markup=markup)
                bot.register_next_step_handler(send_message, self.eight_anket)
            else:
                if errors(message, func=self.seven_anket):
                    send_message = bot.send_message(message.chat.id, self.bot_name_error[self.lang])
                    bot.register_next_step_handler(send_message, self.seven_anket)
        else:
            send_message = bot.send_message(message.chat.id, self.bot_name_error[self.lang])
            bot.register_next_step_handler(send_message, self.seven_anket)

    # функция принимает сообщение с инстаграммом и отправляет сообщение для добавления описания
    def eight_anket(self, message):
        text = message.text

        if text == self.user_instagram[self.lang][0]:
            self.instagram = None

            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

            if get_something('description', self.id)[0] is None:
                markup.add(self.user_descpription[self.lang][0])
            else:
                markup.add(*self.user_descpription[self.lang])

            send_message = bot.send_message(message.chat.id, self.bot_descpription[self.lang],
                                            reply_markup=markup)
            bot.register_next_step_handler(send_message, self.nine_anket)
        elif text == self.user_instagram[self.lang][1]:
            self.instagram = 'old'

            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

            if get_something('description', self.id)[0] is None:
                markup.add(self.user_descpription[self.lang][0])
            else:
                markup.add(*self.user_descpription[self.lang])

            send_message = bot.send_message(message.chat.id, self.bot_descpription[self.lang],
                                            reply_markup=markup)
            bot.register_next_step_handler(send_message, self.nine_anket)
        elif text not in ['/start', '/myprofile', '/language', '/complaint']:
            if text.startswith('@'):
                link = 'https://www.instagram.com/' + text[1:]
            else:
                link = text[:]

            if 'www.instagram.com' in link:
                self.instagram = link

                markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

                if get_something('description', self.id)[0] is None:
                    markup.add(self.user_descpription[self.lang][0])
                else:
                    markup.add(*self.user_descpription[self.lang])

                send_message = bot.send_message(message.chat.id, self.bot_descpription[self.lang],
                                                reply_markup=markup)
                bot.register_next_step_handler(send_message, self.nine_anket)
            else:
                send_message = bot.send_message(message.chat.id, self.bot_instagram_error[self.lang])
                bot.register_next_step_handler(send_message, self.eight_anket)

        else:
            if errors(message, func=self.eight_anket):
                send_message = bot.send_message(message.chat.id, self.bot_name_error[self.lang])
                bot.register_next_step_handler(send_message, self.eight_anket)

    # функция принимает сообщение с описанием анкеты и отправляет сообщение с добавлением фото или видео
    def nine_anket(self, message):
        text = message.text

        if text and text not in ['/start', '/myprofile', '/language', '/complaint']:
            if text == self.user_descpription[self.lang][0]:
                self.description = None
            elif text == self.user_descpription[self.lang][1]:
                self.description = 'old'
            else:
                self.description = text

            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

            self.is_photo = get_something('photo1', self.id)[0]
            self.is_video = get_something('video', self.id)[0]

            if self.is_photo is None:
                markup.add(self.user_photo[self.lang][0])
            else:
                markup.add(*self.user_photo[self.lang])

            send_message = bot.send_message(message.chat.id, self.bot_photo[self.lang], reply_markup=markup)
            bot.register_next_step_handler(send_message, self.ten_anket)
        else:
            if errors(message, func=self.nine_anket):
                send_message = bot.send_message(message.chat.id, self.bot_descpription_error[self.lang])
                bot.register_next_step_handler(send_message, self.nine_anket)

    # функция принимает фото и видео и вызывает класс, который показывает анкету пользователя
    def ten_anket(self, message):
        video = message.video
        photo = message.photo
        text = message.text

        # если пользователь отправил нам фото
        if photo is not None:
            self.count_photo += 1

            # получаем file_id
            exec(f'self.photo{self.count_photo} = photo[-1].file_id')
            # если пользователь уже отправил нам три фото
            if self.count_photo < 3:
                markup = ReplyKeyboardMarkup(resize_keyboard=True)
                if self.edit:
                    markup.add(*self.user_edit[self.lang])
                markup.add(*self.user_photo_mane[self.lang])
                send_message = bot.send_message(message.chat.id,
                                                self.bot_photo_mane[self.lang].replace('#', str(self.count_photo)),
                                                reply_markup=markup)
                bot.register_next_step_handler(send_message, self.ten_anket)
            else:
                try:
                    # если мы заполняем анкету сначала
                    lock.acquire(True)
                    c.execute(
                        f'UPDATE users SET age = ?, male = ?, love = ?, name = ?, photo1 = ?, photo2 = ?, photo3 = ?, video=NULL, reg = ? WHERE id_tg = ?',
                        (self.age, self.male, self.love, self.name, self.photo1, self.photo2, self.photo3, True,
                         self.id))
                    db.commit()

                    self.add_description_or_city()
                except AttributeError:
                    # если мы изменяем только фото или видео
                    c.execute(
                        f'UPDATE users SET photo1 = ?, photo2 = ?, photo3 = ?, video = NULL WHERE id_tg = ?',
                        (self.photo1, self.photo2, self.photo3, self.id))
                    db.commit()
                finally:
                    lock.release()

                MyAnket().one_my_anket(message, self.do)
        # если пользователь отправил нам видео
        elif video is not None:
            # если пользователь прислал нам видео и до этого не присылал нам фото
            if self.photo1 is None:
                # получаем file_id
                save_video = video.file_id
                try:
                    # если мы заполняем анкету сначала
                    lock.acquire(True)
                    c.execute(
                        f'UPDATE users SET age = ?, male = ?, love = ?, name = ?, photo1 = NULL, photo2 = NULL, photo3 = NULL, video = ?, reg = ? WHERE id_tg = ?',
                        (self.age, self.male, self.love, self.name, save_video, True, self.id))
                    db.commit()

                    self.add_description_or_city()
                except AttributeError:
                    # если мы изменяем только фото или видео
                    c.execute(
                        f'UPDATE users SET photo1 = NULL, photo2 = NULL, photo3 = NULL, video = ? WHERE id_tg = ?',
                        (save_video, self.id))
                    db.commit()
                finally:
                    lock.release()
            # но если пользователь уже присылал нам фото и прислал видео, то сохраняем только фото
            else:
                try:
                    lock.acquire(True)

                    c.execute(
                        f'UPDATE users SET age = ?, male = ?, love = ?, name = ?, photo1 = ?, photo2 = ?, photo3 = ?, video=NULL, reg = ? WHERE id_tg = ?',
                        (self.age, self.male, self.love, self.name, self.photo1, self.photo2, self.photo3, True,
                         self.id))
                    db.commit()

                    self.add_description_or_city()
                except AttributeError:
                    c.execute(
                        f'UPDATE users SET photo1 = ?, photo2 = ?, photo3 = ?, video = NULL WHERE id_tg = ?',
                        (self.photo1, self.photo2, self.photo3, self.id))
                    db.commit()
                finally:
                    lock.release()

            MyAnket().one_my_anket(message, self.do)
        # если пользователь нажал на кнопку скачать с аватарки
        elif text == self.user_photo[self.lang][0]:
            try:
                save_photo = bot.get_user_profile_photos(self.id).photos[0][-1].file_id

                try:
                    lock.acquire(True)

                    c.execute(
                        f'UPDATE users SET age = ?, male = ?, love = ?, name = ?, photo1 = ?, photo2 = NULL, photo3 = NULL, video=NULL, reg = ? WHERE id_tg = ?',
                        (self.age, self.male, self.love, self.name, save_photo, True, self.id))
                    db.commit()

                    self.add_description_or_city()
                finally:
                    lock.release()

                MyAnket().one_my_anket(message, self.do)
            except IndexError:
                send_message = bot.send_message(message.chat.id, self.bot_photo_avatar_error[self.lang])
                bot.register_next_step_handler(send_message, self.ten_anket)

        # если пользователь нажал на кнопку оставить текущее
        elif text == self.user_photo[self.lang][1]:
            if self.is_photo is not None or self.is_video is not None:
                try:
                    lock.acquire(True)
                    c.execute(
                        f'UPDATE users SET age = ?, male = ?, love = ?, name = ?, reg = ? WHERE id_tg = ?',
                        (self.age, self.male, self.love, self.name, True, self.id))
                    db.commit()

                    self.add_description_or_city()
                finally:
                    lock.release()

                MyAnket().one_my_anket(message, self.do)
            else:
                send_message = bot.send_message(message.chat.id, self.bot_photo_error_none[self.lang])
                bot.register_next_step_handler(send_message, self.ten_anket)
        # если пользователь нажал вернуться назад
        elif text == self.user_edit[self.lang][0]:
            MyAnket().one_my_anket(message, self.do)
        # если пользователь нажал 'Это всё сохранить фото'
        elif text == self.user_photo_mane[self.lang][0]:
            try:
                lock.acquire(True)

                c.execute(
                    f'UPDATE users SET age = ?, male = ?, love = ?, name = ?, photo1 = ?, photo2 = ?, photo3 = ?, video=NULL, reg = ? WHERE id_tg = ?',
                    (self.age, self.male, self.love, self.name, self.photo1, self.photo2, self.photo3, True, self.id))
                db.commit()

                self.add_description_or_city()
            except AttributeError:
                c.execute(
                    f'UPDATE users SET photo1 = ?, photo2 = ?, photo3 = ?, video = NULL WHERE id_tg = ?',
                    (self.photo1, self.photo2, self.photo3, self.id))
                db.commit()
            finally:
                lock.release()

            MyAnket().one_my_anket(message, self.do)
        else:
            if errors(message, func=self.ten_anket):
                send_message = bot.send_message(message.chat.id, self.bot_photo_error[self.lang])
                bot.register_next_step_handler(send_message, self.ten_anket)

    # функция сохраняет описание и геолокацию если её указали
    def add_description_or_city(self):
        if self.long != 'old':
            c.execute(
                f'UPDATE users SET long = ?, lat = ? WHERE id_tg = ?',
                (self.long, self.lat, self.id))
            db.commit()

        if self.description != 'old':
            c.execute(
                f'UPDATE users SET description = ? WHERE id_tg = ?',
                (self.description, self.id))
            db.commit()

        if self.instagram != 'old':
            c.execute(
                f'UPDATE users SET instagram = ? WHERE id_tg = ?',
                (self.instagram, self.id))
            db.commit()

        if self.max_age != 'old' and self.min_age != 'old':
            c.execute(
                f'UPDATE users SET min_age = ?, max_age = ? WHERE id_tg = ?',
                (self.min_age, self.max_age, self.id))
            db.commit()

    # функция вызывается если мы хотим поменять только фото
    def edit_photo(self, message):
        self.count_photo = 0
        self.do = 'command'
        self.lang = get_something('lang', message.from_user.id)[0]
        self.photo1 = None
        self.photo2 = None
        self.photo3 = None
        self.edit = True
        self.id = message.from_user.id

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*self.user_edit[self.lang])
        send_message = bot.send_message(message.chat.id, self.bot_edit_photo[self.lang], reply_markup=markup)
        bot.register_next_step_handler(send_message, self.ten_anket)

    # функция вызывается если мы хотим поменять описание. Она присылает сообщение о том, что нужно прислать описание
    def edit_description_one(self, message):
        self.lang = get_something('lang', message.from_user.id)[0]
        self.do = 'command'
        self.id = message.from_user.id

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*self.user_edit[self.lang])
        send_message = bot.send_message(message.chat.id, self.bot_descpription[self.lang],
                                        reply_markup=markup)
        bot.register_next_step_handler(send_message, self.edit_description_two)

    # функция принимает сообщение с описанием и сохраняет его. Функция вызывается только когда пользователь пытается изменить только описание
    def edit_description_two(self, message):
        text = message.text

        if text in self.user_edit[self.lang]:
            MyAnket().one_my_anket(message, 'command')
        elif text and text not in ['/start', '/complaint', '/myprofile', '/language']:
            try:
                lock.acquire(True)
                c.execute(
                    f'UPDATE users SET description = ? WHERE id_tg = ?',
                    (text, self.id))
                db.commit()
            finally:
                lock.release()

            MyAnket().one_my_anket(message, 'command')
        else:
            if errors(message):
                send_message = bot.send_message(message.chat.id, self.bot_descpription_error[self.lang])
                bot.register_next_step_handler(send_message, self.edit_description_two)


# класс показывает анкету пользователя
class MyAnket:
    def __init__(self):
        self.bot_your_anket = {'ru': 'Так выглядит твоя анкета:', 'uk': 'Так виглядає твоя анкета:',
                               'en': 'Your profile:',
                               'id': 'Begini rupa seni profil anda:'}
        self.bot_command = {
            'ru': '1. Заполнить анкету заново.\n2. Изменить фото/видео.\n3. Изменить текст анкеты.\n4. Смотреть анкеты.',
            'uk': '1. Заповнити анкету наново.\n2. Змінити фото/відео.\n3. Змінити текст анкети.\n4. Дивитися анкети.',
            'en': '1. Edit my profile.\n2. Change my photo/video.\n3. Change profile text.\n4. View profiles.',
            'id': '1. Isi profil sekali lagi.\n2. Ubah foto/video.\n3. Ubah teks dari profil.\n4. Lihat profil.'}
        self.bot_error = {'ru': 'Нет такого варианта ответа', 'uk': 'Немає такого варіанту відповіді',
                          'en': 'No such option', 'id': 'Tiada jawapan seperti ini'}
        self.bot_quest = {"ru": 'Всё верно?', 'uk': 'Все правильно?', 'en': 'Correct?', 'id': 'Apa itu benar?'}

        self.user_command = {'all': ['1', '2', '3', '4 🚀']}
        self.user_quest = {'ru': ['Да', 'Изменить анкету'], 'uk': ['Так', 'Змінити анкету'],
                           'en': ['Yes', 'Edit my profile'], 'id': ['Ya', 'Ubah profil']}

    # функция отпраляет анкету, и если пользователь только что заполнял её с начала, то потом отправляет сообщение с вопросом, а в любом другом случае менюшку.
    def one_my_anket(self, message, do):
        self.lang = get_something('lang', message.from_user.id)[0]
        self.id = message.from_user.id

        bot.send_message(message.chat.id, self.bot_your_anket[self.lang], reply_markup=ReplyKeyboardRemove())

        send_anket(message, self.id, my_anket=True)
        # если мы только что заполняли анкету сначала
        if do == 'quest':
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add(*self.user_quest[self.lang])

            send_message = bot.send_message(message.chat.id, self.bot_quest[self.lang], reply_markup=markup)
            bot.register_next_step_handler(send_message, self.two_quest_my_anket)
        # иначе
        elif do == 'command':
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
            markup.add(*self.user_command['all'])

            send_message = bot.send_message(message.chat.id, self.bot_command[self.lang], reply_markup=markup)
            bot.register_next_step_handler(send_message, self.three_command_my_anket)

            # останавливаем проверку того, лайкнули тебя или нет
            exec(f'global run{self.id}\nrun{self.id}=message')

    # функция вызывается только если перед этим было сообщение с вопросом. Если пользователь нажимает да, то начинается просмотр анкет, а инчае отправляет сообщение с менюшкой.
    def two_quest_my_anket(self, message):
        text = message.text

        if text == self.user_quest[self.lang][0]:
            ViewsAnket().start(message)
        elif text == self.user_quest[self.lang][1]:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
            markup.add(*self.user_command['all'])

            send_message = bot.send_message(message.chat.id, self.bot_command[self.lang], reply_markup=markup)
            bot.register_next_step_handler(send_message, self.three_command_my_anket)

            # запускаем проверку того, лакнули ли тебя или нет
            exec(f'global run{self.id}\nrun{self.id}=message')
        else:
            if errors(message):
                send_message = bot.send_message(message.chat.id, self.bot_error[self.lang])
                bot.register_next_step_handler(send_message, self.two_quest_my_anket)

    # функция принимает то, что выбрал пользователь в менюшке
    def three_command_my_anket(self, message):
        # останавливаем проверку того, лайкнули тебя или нет
        exec(f'global run{self.id}\nrun{self.id}=None')

        text = message.text

        if text == self.user_command['all'][0]:
            Anket().one_anket(message)
        elif text == self.user_command['all'][1]:
            Anket().edit_photo(message)
        elif text == self.user_command['all'][2]:
            Anket().edit_description_one(message)
        elif text == self.user_command['all'][3]:
            ViewsAnket().start(message)
        else:
            if errors(message):
                send_message = bot.send_message(message.chat.id, self.bot_error[self.lang])
                bot.register_next_step_handler(send_message, self.three_command_my_anket)


# класс позволяет просматривать другие анкеты
class ViewsAnket:
    def __init__(self):
        self.bot_find = {'all': '✨🔍'}
        self.bot_phone = {
            'ru': 'У вас нет username. Если хотите, чтобы ваши лайки увидели, отправьте номер или создайте username.',
            'uk': 'У вас немає username. Якщо хочете, щоб ваші лайки побачили, відправте номер або створіть username.',
            'en': 'You don\'t have a username. If you want your likes to be seen, send a number or create a username.',
            'id': 'Anda tidak memiliki nama pengguna. Jika Anda ingin suka dilihat, kirim nomor atau buat nama pengguna.'}
        self.bot_phone_error = {'ru': 'Вы не создали имя пользователя!', 'uk': 'Ви не створили ім\'я користувача!',
                                'en': 'You didn\'t create a username!', 'id': 'Anda tidak membuat nama pengguna!'}
        self.bot_empty = {'ru': 'Упс... Анкеты закончились. Нажмите на кнопку чтобы начать смотреть анкеты с начала',
                          'uk': 'Упс... Анкети закінчилися. Натисніть на кнопку щоб почати дивитися анкети спочатку',
                          'en': 'Oops... Profiles are over. Click on the button to start looking at the profiles from the beginning',
                          'id': 'UPS... Profil sudah berakhir. Klik tombol untuk mulai melihat kuesioner dari awal'}
        self.bot_find_anket = {'ru': 'Смотреть анкеты или найти её по ID?',
                               'uk': 'Дивитися анкети або знайти її по ID?', 'en': 'View profiles or find it by ID?',
                               'id': 'Lihat profil atau menemukannya dengan ID?'}
        self.bot_find_id = {'ru': 'Пришлите ID пользователя', 'uk': 'Надішліть ID користувача',
                            'en': 'Send the user ID', 'id': 'Kirim ID pengguna'}
        self.bot_find_id_error = {'ru': 'Недействительный ID. Отправьте заново!',
                                  'uk': 'Недійсний ID. Відправте заново!', 'en': 'Invalid ID. Send it again!',
                                  'id': 'ID tidak valid. Kirim lagi!'}
        self.bot_find_id_you_error = {'ru': 'Нельзя присылать свой ID', 'uk': 'Не можна надсилати свій ID',
                                      'en': 'You cannot send your ID', 'id': 'Anda tidak dapat mengirim ID anda'}
        self.bot_send = {
            'ru': 'Напиши сообщение для этого пользователя, отправь фото или запиши короткое видео (до 15 сек)',
            'uk': 'Напиши повідомлення для цього користувача, відправ фото або запиши коротке відео (до 15 сек)',
            'en': 'Write a message for this user, send a photo or record a short video (up to 15 seconds)',
            'id': 'Tulis pesan untuk pengguna ini, kirim foto atau rekam video pendek (hingga 15 detik)'}
        self.bot_send_error = {'ru': 'Можно отправить только текст или видео. Введите сообщение заново.',
                               'uk': 'Можна надіслати лише текст або відео. Напиши повідомлення знову.',
                               'en': 'Only text or video can be sent. Re-enter, please.',
                               'id': 'Hanya teks atau video yang boleh dihantar. Masukkan semula mesej anda.'}
        self.after_send = {'ru': 'Лайк отправлен, ждем ответа.', 'uk': 'Лайк надіслано, чекаємо на відповідь.',
                           'en': 'Like sent, waiting for a response.', 'id': 'Suka dihantar, menunggu jawapan.'}
        self.bot_true_complaint = {'ru': 'Жалоба будет обработана в ближайшее время.',
                                   'uk': 'Скарга буде опрацьована найближчим часом.',
                                   'en': 'Your complaint will be processed soon.', 'id': 'Aduan kemudiannya diproses.'}
        self.bot_error = {'ru': 'Нет такого варианта ответа', 'uk': 'Немає такого варіанту відповіді',
                          'en': 'No such option', 'id': 'Tiada jawapan seperti ini'}

        self.user_phone = {'ru': ['Отправить телефон', 'Я создал имя пользователя'],
                           'uk': ['Надіслати телефон', 'Я створив ім\'я користувача'],
                           'en': ['Send phone', 'I created a username'],
                           'id': ['Kirim telepon', 'Saya telah membuat nama pengguna']}
        self.user_find_anket = {'ru': ['Смотреть анкеты', 'Найти анкету по ID'],
                                'uk': ['Дивитися анкети', 'Знайти анкету по ID'],
                                'en': ['View profiles', 'Find profile by ID'],
                                'id': ['Lihat profil', 'Cari profil dengan ID']}
        self.user_find_id = {'ru': ['Отмена'], 'uk': ['Скасування'], 'en': ['Cancel'], 'id': ['Batal']}
        self.user_rate = {'all': ['❤', '💌 / 📹', '👎', '💤']}
        self.user_send = {'ru': ['Вернуться назад'], 'uk': ['Повернутись назад'], 'en': ['Go back'], 'id': ['Kembali']}
        self.user_empty = {'ru': ['Смотреть анкеты с начала'], 'uk': ['Дивитися анкети з початку'],
                           'en': ['View profiles from the beginning'],
                           'id': ['Lihat profil dari awal']}

        self.server_in_complaint = ['1🔞', '2💊', '3💰', '4🦨', '9']
        self.server_complaint = {'1🔞': '🔞 Материал для взрослых', '2💊': ' 💊Пропаганда наркотиков',
                                 '3💰': '💰 Продажа товаров и услуг', '4🦨': '🦨 Другое'}

    # функция вызывается только один раз, в начала просмота анкет
    def start(self, message):
        self.id = message.from_user.id
        self.lang = get_something('lang', message.from_user.id)[0]
        self.username = message.from_user.username
        self.user_anket = None

        self.user_love, self.user_age, self.user_long, self.user_lat, self.user_lang_code, self.user_index, self.user_male, self.phone, self.firstname, self.min_age, self.max_age = get_something(
            'love, age, long, lat, lang_code, ind, male, phone, name, min_age, max_age', self.id)

        # получаем анкеты, которые подходят нашему пользователю
        try:
            lock.acquire(True)

            if self.user_love == 'n':
                c.execute(
                    'SELECT id_tg FROM users WHERE (age BETWEEN ? AND ?) AND ((long BETWEEN ? AND ?) AND (lat BETWEEN ? and ?)) AND lang_code = ? AND id_tg <> ? AND is_search = 1',
                    (self.min_age, self.max_age,
                     self.user_long - 1 / ((math.cos(53.85 * math.pi / 180) * 40000 / 360) / 20),
                     self.user_long + 1 / ((math.cos(53.85 * math.pi / 180) * 40000 / 360) / 20),
                     self.user_lat - 0.2702702702702703, self.user_lat + 0.2702702702702703, self.user_lang_code,
                     self.id))
            else:
                c.execute(
                    'SELECT id_tg FROM users WHERE male = ? AND (age BETWEEN ? AND ?) AND ((long BETWEEN ? AND ?) AND (lat BETWEEN ? and ?)) AND lang_code = ? AND id_tg <> ? AND is_search = 1',
                    (self.user_love, self.user_age - 5, self.user_age + 5,
                     self.user_long - 1 / ((math.cos(53.85 * math.pi / 180) * 40000 / 360) / 20),
                     self.user_long + 1 / ((math.cos(53.85 * math.pi / 180) * 40000 / 360) / 20),
                     self.user_lat - 0.2702702702702703, self.user_lat + 0.2702702702702703, self.user_lang_code,
                     self.id))

            self.ankets_id = c.fetchall()
        finally:
            lock.release()

        # сортируем их
        self.ankets_id.sort(key=to_sort, reverse=True)

        # если у пользователя нет username, и он не давал нам его телефон, то сообщаем ему об этом
        if self.username is None and self.phone is None:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add(KeyboardButton(self.user_phone[self.lang][0], request_contact=True),
                       KeyboardButton(self.user_phone[self.lang][1]))
            send_message = bot.send_message(message.chat.id, self.bot_phone[self.lang], reply_markup=markup)
            bot.register_next_step_handler(send_message, self.add_phone)
        # и иначе пытаемся начать просмотр анкет
        else:
            # если есть анкеты
            if self.ankets_id:
                bot.send_message(message.chat.id, self.bot_find['all'], reply_markup=ReplyKeyboardRemove())
                markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                markup.add(*self.user_find_anket[self.lang])

                send_message = bot.send_message(message.chat.id, self.bot_find_anket[self.lang], reply_markup=markup)
                bot.register_next_step_handler(send_message, self.find_anket)
            else:
                bot.send_message(message.chat.id, self.bot_empty[self.lang], reply_markup=ReplyKeyboardRemove())
                MyAnket().one_my_anket(message, 'command')

    # функция вызывается, когда у пользователя нет username, и он не указал номер телефона. Эта функция принимает то, что он отправил
    def add_phone(self, message):
        text = message.text
        contact = message.contact

        if contact:
            try:
                lock.acquire(True)

                c.execute('UPDATE users SET phone = ? WHERE id_tg = ?',
                          (contact.phone_number, contact.user_id))
                db.commit()
            finally:
                lock.release()

            self.phone = contact.phone_number

            bot.send_message(message.chat.id, self.bot_find['all'])

            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            markup.add(*self.user_find_anket[self.lang])

            send_message = bot.send_message(message.chat.id, self.bot_find_anket[self.lang], reply_markup=markup)
            bot.register_next_step_handler(send_message, self.find_anket)
        elif text == self.user_phone[self.lang][1]:
            if message.from_user.username:
                self.username = message.from_user.username

                bot.send_message(message.chat.id, self.bot_find['all'])

                markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                markup.add(*self.user_find_anket[self.lang])

                send_message = bot.send_message(message.chat.id, self.bot_find_anket[self.lang], reply_markup=markup)
                bot.register_next_step_handler(send_message, self.find_anket)
            else:
                send_message = bot.send_message(message.chat.id, self.bot_phone_error[self.lang])
                bot.register_next_step_handler(send_message, self.add_phone)
        else:
            if errors(message):
                send_message = bot.send_message(message.chat.id, self.bot_error[self.lang])
                bot.register_next_step_handler(send_message, self.add_phone)

    def find_anket(self, message):
        text = message.text

        if text == self.user_find_anket[self.lang][0]:
            self.get_anket(message)
        elif text == self.user_find_anket[self.lang][1]:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*self.user_find_id[self.lang])

            send_messsage = bot.send_message(message.chat.id, self.bot_find_id[self.lang],
                                             reply_markup=markup)
            bot.register_next_step_handler(send_messsage, self.get_anket_id)
        else:
            if errors(message):
                send_message = bot.send_message(message.chat.id, self.bot_error[self.lang])
                bot.register_next_step_handler(send_message, self.add_phone)

    def get_anket_id(self, message):
        text = message.text

        if text == str(message.from_user.id):
            send_message = bot.send_message(message.chat.id, self.bot_find_id_you_error[self.lang])
            bot.register_next_step_handler(send_message, self.get_anket_id)
        else:
            if text in self.user_find_id[self.lang]:
                self.get_anket(message)
            elif text in ['/myprofile', '/complaint', '/start', '/language']:
                errors(message)
            else:
                self.user_anket = get_something('id_tg', text)
                if self.user_anket is None:
                    send_message = bot.send_message(message.chat.id, self.bot_find_id_error[self.lang])
                    bot.register_next_step_handler(send_message, self.get_anket_id)
                else:
                    self.user_anket = self.user_anket[0]
                    self.get_anket(message)

    # функция отправляет анкету
    def get_anket(self, message):
        if self.user_index >= len(self.ankets_id):
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*self.user_empty[self.lang])

            send_message = bot.send_message(message.chat.id, self.bot_empty[self.lang], reply_markup=markup)
            bot.register_next_step_handler(send_message, self.reset_index)

            exec(f'global run{self.id}\nrun{self.id}=message')
        else:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
            markup.add(*self.user_rate['all'])
            if self.user_anket:
                send_message = send_anket(message, self.user_anket, markup)
            else:
                send_message = send_anket(message, self.ankets_id[self.user_index][0], markup)
            bot.register_next_step_handler(send_message, self.rate)

    # функция принимает то, что пользователь поставил анкете (лайк, дизлайк и т.д)
    def rate(self, message):
        text = message.text

        if text == self.user_rate['all'][0]:
            try:
                lock.acquire(True)

                if self.user_anket:
                    if self.username:
                        c.execute('INSERT INTO love(from_user, to_user, from_username, from_male) VALUES(?, ?, ?, ?)',
                                  (self.id, self.user_anket, self.username, self.user_male))
                        db.commit()
                    else:
                        c.execute(
                            'INSERT INTO love(from_user, to_user, from_male, from_phone, from_first_name) VALUES(?, ?, ?, ?, ?)',
                            (self.id, self.user_anket, self.user_male, self.phone,
                             self.firstname))
                        db.commit()

                    self.user_anket = None
                else:
                    if self.username:
                        c.execute('INSERT INTO love(from_user, to_user, from_username, from_male) VALUES(?, ?, ?, ?)',
                                  (self.id, self.ankets_id[self.user_index][0], self.username, self.user_male))
                        db.commit()
                    else:
                        c.execute(
                            'INSERT INTO love(from_user, to_user, from_male, from_phone, from_first_name) VALUES(?, ?, ?, ?, ?)',
                            (self.id, self.ankets_id[self.user_index][0], self.user_male, self.phone,
                             self.firstname))
                        db.commit()
                    self.user_index += 1
                    c.execute('UPDATE users SET ind = ? WHERE id_tg = ?', (self.user_index, self.id))
                    db.commit()
            finally:
                lock.release()

            self.get_anket(message)
        elif text == self.user_rate['all'][1]:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*self.user_send[self.lang])

            send_message = bot.send_message(message.chat.id, self.bot_send[self.lang], reply_markup=markup)
            bot.register_next_step_handler(send_message, self.send_text_or_video)
        elif text == self.user_rate['all'][2]:
            if self.user_anket:
                self.user_anket = None
            else:
                self.user_index += 1
                try:
                    lock.acquire(True)
                    c.execute('UPDATE users SET ind = ? WHERE id_tg = ?', (self.user_index, self.id))
                    db.commit()
                finally:
                    lock.release()

            self.get_anket(message)
        elif text == self.user_rate['all'][3]:
            Menu().one_menu1(message)
        else:
            if errors(message, self):
                send_message = bot.send_message(message.chat.id, self.bot_error[self.lang])
                bot.register_next_step_handler(send_message, self.rate)

    # функция позволяет отправить фото или видео
    def send_text_or_video(self, message):
        text = message.text
        video = message.video
        photo = message.photo

        if text == self.user_send[self.lang][0]:
            if errors(message):
                self.get_anket(message)
        elif video:
            save_video = video.file_id

            try:
                lock.acquire(True)

                if self.user_anket:
                    if self.phone:
                        c.execute(
                            'INSERT INTO love(from_user, to_user, from_male, from_phone, from_first_name, video) VALUES(?, ?, ?, ?, ?, ?)',
                            (self.id, self.user_anket, self.user_male, self.phone,
                             self.firstname, save_video))
                        db.commit()
                    else:
                        c.execute(
                            'INSERT INTO love(from_user, to_user, from_username, from_male, video) VALUES(?, ?, ?, ?, ?)',
                            (self.id, self.user_anket, self.username, self.user_male, save_video))
                        db.commit()

                    self.user_anket = None
                else:
                    if self.phone:
                        c.execute(
                            'INSERT INTO love(from_user, to_user, from_male, from_phone, from_first_name, video) VALUES(?, ?, ?, ?, ?, ?)',
                            (self.id, self.ankets_id[self.user_index][0], self.user_male, self.phone,
                             self.firstname, save_video))
                        db.commit()
                    else:
                        c.execute(
                            'INSERT INTO love(from_user, to_user, from_username, from_male, video) VALUES(?, ?, ?, ?, ?)',
                            (self.id, self.ankets_id[self.user_index][0], self.username, self.user_male, save_video))
                        db.commit()

                    self.user_index += 1
                    c.execute('UPDATE users SET ind = ? WHERE id_tg = ?', (self.user_index, self.id))
                    db.commit()
            finally:
                lock.release()

            bot.send_message(message.chat.id, self.after_send[self.lang])
            self.get_anket(message)
        elif text:
            try:
                lock.acquire()

                if self.user_anket:
                    if self.phone:
                        c.execute(
                            'INSERT INTO love(from_user, to_user, from_male, from_phone, from_first_name, text) VALUES(?, ?, ?, ?, ?, ?)',
                            (self.id, self.user_anket, self.user_male, self.phone,
                             self.firstname, text))
                        db.commit()
                    else:
                        c.execute(
                            'INSERT INTO love(from_user, to_user, from_username, from_male, text) VALUES(?, ?, ?, ?, ?)',
                            (self.id, self.user_anket, self.username, self.user_male, text))
                        db.commit()

                    self.user_anket = None
                else:
                    if self.phone:
                        c.execute(
                            'INSERT INTO love(from_user, to_user, from_male, from_phone, from_first_name, text) VALUES(?, ?, ?, ?, ?, ?)',
                            (self.id, self.ankets_id[self.user_index][0], self.user_male, self.phone,
                             self.firstname, text))
                        db.commit()
                    else:
                        c.execute(
                            'INSERT INTO love(from_user, to_user, from_username, from_male, text) VALUES(?, ?, ?, ?, ?)',
                            (self.id, self.ankets_id[self.user_index][0], self.username, self.user_male, text))
                        db.commit()

                    self.user_index += 1
                    c.execute('UPDATE users SET ind = ? WHERE id_tg = ?', (self.user_index, self.id))
                    db.commit()
            finally:
                lock.release()

            bot.send_message(message.chat.id, self.after_send[self.lang])
            self.get_anket(message)
        elif photo:
            save_photo = photo[-1].file_id

            try:
                lock.acquire(True)

                if self.user_anket:
                    if self.phone:
                        c.execute(
                            'INSERT INTO love(from_user, to_user, from_male, from_phone, from_first_name, photo) VALUES(?, ?, ?, ?, ?, ?)',
                            (self.id, self.user_anket, self.user_male, self.phone,
                             self.firstname, save_photo))
                        db.commit()
                    else:
                        c.execute(
                            'INSERT INTO love(from_user, to_user, from_username, from_male, [photo]) VALUES(?, ?, ?, ?, ?)',
                            (self.id, self.user_anket, self.username, self.user_male, save_photo))
                        db.commit()

                    self.user_anket = None
                else:
                    if self.phone:
                        c.execute(
                            'INSERT INTO love(from_user, to_user, from_male, from_phone, from_first_name, photo) VALUES(?, ?, ?, ?, ?, ?)',
                            (self.id, self.ankets_id[self.user_index][0], self.user_male, self.phone,
                             self.firstname, save_photo))
                        db.commit()
                    else:
                        c.execute(
                            'INSERT INTO love(from_user, to_user, from_username, from_male, [photo]) VALUES(?, ?, ?, ?, ?)',
                            (self.id, self.ankets_id[self.user_index][0], self.username, self.user_male, save_photo))
                        db.commit()

                    self.user_index += 1
                    c.execute('UPDATE users SET ind = ? WHERE id_tg = ?', (self.user_index, self.id))
                    db.commit()
            finally:
                lock.release()

            bot.send_message(message.chat.id, self.after_send[self.lang])
            self.get_anket(message)
        else:
            if errors(message):
                send_message = bot.send_message(message.chat.id, self.bot_send_error[self.lang])
                bot.register_next_step_handler(send_message, self.send_text_or_video)

    # эта функция вызывается если пользователь нажал на кнопку смотреть анкеты сначала
    def reset_index(self, message):
        exec(f'global run{self.id}\nrun{self.id}=None')

        text = message.text

        if text in self.user_empty[self.lang]:
            try:
                lock.acquire()

                self.user_index = 0
                c.execute('UPDATE users SET ind = ? WHERE id_tg = ?', (self.user_index, self.id))
                db.commit()
            finally:
                lock.release()

            self.get_anket(message)
        else:
            if errors(message):
                send_message = bot.send_message(message.chat.id, self.bot_error[self.lang])
                bot.register_next_step_handler(send_message, self.reset_index)

    # функция вызывается если пользователь ввёл команду /complaint
    def complaint(self, message):
        text = message.text

        if text in self.server_in_complaint:
            if text != '9':
                bot.send_message(message.chat.id, self.bot_true_complaint[self.lang])

                try:
                    lock.acquire(True)

                    c.execute('INSERT INTO complaint(from_user, to_user, type) VALUES(?, ?, ?)',
                              (self.id, self.ankets_id[self.user_index][0], self.server_complaint[text]))
                    db.commit()

                    self.user_index += 1
                    c.execute('UPDATE users SET ind = ? WHERE id_tg = ?', (self.user_index, self.id))
                    db.commit()
                finally:
                    lock.release()

            self.get_anket(message)
        else:
            if errors(message):
                send_message = bot.send_message(message.chat.id, self.bot_error[self.lang])
                bot.register_next_step_handler(send_message, self.complaint)


# класс реализует вторую менюшку
class Menu:
    def __init__(self):
        self.bot_menu1 = {'ru': 'Подождем пока кто-то увидит твою анкету',
                          'uk': 'Почекай поки хтось побачить твою анкету', 'en': 'Wait until someone sees you.',
                          'id': 'Mari tunggu sehingga seseorang melihat profil anda'}
        self.bot_menu2 = {
            'ru': '1. Смотреть анкеты.\n2. Моя анкета.\n3. Я больше не хочу никого искать.\n***\n4. Пригласи друзей - получи больше лайков 😎.',
            'uk': '1. Дивитися анкети.\n2. Моя анкета.\n3. Я більше не хочу нікого шукати.\n***\n4. Запроси друзів - отримай більше лайків 😎.',
            'en': '1. View profiles.\n2. My profile.\n3. Not searching anymore.\n***\n4. Invite friends to get more likes 😎.',
            'id': '1. Lihat profil.\n2. Profil aku.\n3. Aku tak mahu lagi cari seseorang.\n***\n4. Jemput kawan-kawan - bawa lebih banyak like 😎.'}
        self.bot_sleep = {
            'ru': 'Так ты не узнаешь, что кому-то нравишься... Точно хочешь отключить свою анкету?\n\n1. Да, отключить анкету.\n2. Нет, вернуться назад.',
            'uk': 'Так ти не дізнаєшся, що комусь подобаєшся... Точно хочеш відключити свою анкету?\n\n1. Так, відключити анкету.\n2. Ні, повернутись назад.',
            'en': 'You won\'t know who likes you then... Sure about deactivating?\n1. Yes, deactivate my profile please.\n2. No, I want to see my matches.',
            'id': 'Dengan ini anda tidak akan mengetahui bahawa seseorang menyukai anda... Adakah anda pasti mahu nyahaktifkan profil anda?\n\n1. Ya, nyahaktifkan profil.\n2. Tak, kembali.'}
        self.bot_wait_anket = {
            'ru': 'Надеюсь ты нашел кого-то благодаря мне! Рад был с тобой пообщаться, будет скучно – пиши, обязательно найдем тебе кого-нибудь\n\n1. Смотреть анкеты',
            'uk': 'Сподіваюсь ти когось знайшов з моєю допомогою! \nРадий був поспілкуватися, якщо буде нудно – пиши, обов\'язково знайдем тобі когось\n\n1. Дивитися анкети',
            'en': 'Hope you met someone with my help!\nAlways happy to chat. If bored, text me -  I\'ll find someone special for you.\n\n1. View profiles',
            'id': 'Aku harap anda menjumpai seseorang kerana aku! Aku gembira dapat bercakap dengan anda, jika ianya akan membosankan - tulis, kita pasti mencarikan anda seseorang\n\n1. Lihat profil'}
        self.bot_boost1 = {
            'ru': 'Пригласи друзей и получи больше лайков!\n\nТвоя статистика\nПришло за 14 дней: №\nБонус к силе анкеты: #%\nПерешли друзьям или размести в своих соцсетях.\nВот твоя личная ссылка 👇',
            'uk': 'Запроси друзів і отримай більше лайків!\n\nТвоя статистика\nПрийшло за 14 днів: №\nБонус до сили анкети: #%\n\nНадішли друзям або пошир у своїх соцмережах.\nТвоє персональне посилання 👇',
            'en': 'Invite friends to get more likes!\n\nMy stats\nJoined in 14 days: №\nA bonus to your profile: #%\n\nShare it with your friends/on your social media!\nYour personal link👇',
            'id': 'Jemput kawan-kawan dan bawa lebih banyak like!\n\nStatistik awak\nBergabung selama 14 hari: №\nBonus ke kuasa profil: #%\n\nKirim ke kawan atau letak link di social media anda. \nIni lah link peribadi anda👇'}
        self.bot_boost2 = {'ru': 'Бот знакомств Дайвинчик🍷 в Telegram! Найдет друзей или даже половинку 👫\n👉 ',
                           'uk': 'Бот знайомств Дайвінчик🍷 у Telegram! Знайде друзів або навіть другу половинку 👫\n👉 ',
                           'en': 'Dating Bot – Leomatchbot🍷 is on Telegram! Find new friends or even a lover 👫\n👉 ',
                           'id': 'Bot temu janji Leomatchbot 🍷di Telegram! Cari kawan atau cinta anda 👫\n👉 '}
        self.bot_error = {'ru': 'Нет такого варианта ответа', 'uk': 'Немає такого варіанту відповіді',
                          'en': 'No such option', 'id': 'Tiada jawapan seperti ini'}

        self.user_menu2 = {'all': ['1 🚀', '2', '3', '4']}
        self.user_sleep = {'all': ['1', '2']}
        self.user_wait_anket = {'ru': ['Смотреть анкеты'], 'uk': ['Дивитися анкети'], 'en': ['View profiles'],
                                'id': ['Lihat profil']}
        self.user_boost = {'ru': ['Назад'], 'uk': ['Назад'], 'en': ['Go back'], 'id': ['Kembali']}

    # создаёт необходимые переменные экземпляра класса и отправляет текст 'Подождём пока кто-то увидит твою анкету'
    def one_menu1(self, message):
        self.lang = get_something('lang', message.from_user.id)[0]
        self.id = message.from_user.id

        bot.send_message(message.chat.id, self.bot_menu1[self.lang], reply_markup=ReplyKeyboardRemove())
        self.one_menu2(message)

    # функция отправляет саму менюшку
    def one_menu2(self, message):
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
        markup.add(*self.user_menu2['all'])

        send_message = bot.send_message(message.chat.id, self.bot_menu2[self.lang], reply_markup=markup)
        bot.register_next_step_handler(send_message, self.two_menu)

        exec(f'global run{self.id}\nrun{self.id}=message')

    # функция принимает то, что выбрал пользователь во второй менюшке
    def two_menu(self, message):
        exec(f'global run{self.id}\nrun{self.id}=None')

        text = message.text

        if text == self.user_menu2['all'][0]:
            ViewsAnket().start(message)
        elif text == self.user_menu2['all'][1]:
            MyAnket().one_my_anket(message, 'command')
        elif text == self.user_menu2['all'][2]:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add(*self.user_sleep['all'])

            send_message = bot.send_message(message.chat.id, self.bot_sleep[self.lang], reply_markup=markup)
            bot.register_next_step_handler(send_message, self.sleep_menu)
        elif text == self.user_menu2['all'][3]:
            user_id = get_something('users_id', self.id)[0]

            try:
                lock.acquire(True)

                c.execute('SELECT COUNT(users_id) FROM referrals WHERE users_id = ? GROUP BY users_id',
                          (user_id,))
                count = c.fetchone()
                count = '0' if count is None else str(count[0])

                c.execute(
                    'SELECT COUNT(users_id) FROM referrals WHERE users_id = ? AND date_created > ? GROUP BY users_id',
                    (user_id, datetime.strftime(datetime.now() - timedelta(days=14), '%Y-%m-%d %H:%M:%S')))
                count_14 = c.fetchone()
                count_14 = '0' if count_14 is None else str(count_14[0])
            finally:
                lock.release()

            bot.send_message(message.chat.id,
                             self.bot_boost1[self.lang].replace('#', count).replace('№', count_14))

            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*self.user_boost[self.lang])

            send_message = bot.send_message(message.chat.id, self.bot_boost2[
                self.lang] + f'https://t.me/leomatchprogabot?start={self.id}', reply_markup=markup,
                                            disable_web_page_preview=True)
            bot.register_next_step_handler(send_message, self.boost)
        else:
            if errors(message):
                send_message = bot.send_message(message.chat.id, self.bot_error[self.lang])
                bot.register_next_step_handler(send_message, self.two_menu)

    # функция вызывается тогда, когда пользователь нажал на кнопку отключить свою анкету
    def sleep_menu(self, message):
        text = message.text

        if text == self.user_sleep['all'][0]:
            try:
                lock.acquire(True)

                c.execute('UPDATE users SET is_search = False WHERE id_tg = ?', (self.id,))
                db.commit()
            finally:
                lock.release()

            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*self.user_wait_anket[self.lang])

            send_message = bot.send_message(message.chat.id, self.bot_wait_anket[self.lang],
                                            reply_markup=markup)

            bot.register_next_step_handler(send_message, lambda message: wait_anket(message, 'menu'))
        elif text == self.user_sleep['all'][1]:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*self.user_menu2['all'])

            send_message = bot.send_message(message.chat.id, self.bot_menu2[self.lang], reply_markup=markup)
            bot.register_next_step_handler(send_message, self.two_menu)

            exec(f'global run{self.id}\nrun{self.id}=message')
        else:
            if errors(message):
                send_message = bot.send_message(message.chat.id, self.bot_error[self.lang])
                bot.register_next_step_handler(send_message, self.sleep_menu)

    # функция обратно возвращает менюшку, если пользователь нажал на кнопку назад, которая появляется когда пользователь хочет получить реферальную ссылку
    def boost(self, message):
        text = message.text

        if text == self.user_boost[self.lang][0]:
            self.one_menu2(message)
        else:
            if errors(message):
                send_message = bot.send_message(message.chat.id, self.bot_error[self.lang])
                bot.register_next_step_handler(send_message, self.boost)

    # функция создаёт необходимые переменные и вызывает функцию one_menu2 . Она нужна когда нужно отослать пользователю меню, но не отсылать первое сообщение - 'ПОдождём пока кто-то увидет твою анкету'
    def after_something(self, message):
        self.lang = get_something('lang', message.from_user.id)[0]
        self.id = message.from_user.id

        self.one_menu2(message)


# класс позволяет получить уведомление о том, что тебя кто-то лайкнул
class Love:
    def __init__(self):
        self.bot_love = {'ru1': 'Ты &#? \n1. Показать.\n2. Не хочу больше никого смотреть.',
                         'ru2': '1. Показать # я нравлюсь.\n2. Моя анкета.\n3. Я больше не хочу никого искать.',
                         'uk1': 'Ти &#? \n1. Показавши.\n2. Не хочу більше нікого дивитися.',
                         'uk2': '1. Показати # я подобаюся.\n2. Моя анкета.\n3. Я більше не хочу нікого шукати.',
                         'en1': '# liked &. Have a look? \n1. Show.\n2. Not searching anymore',
                         'en2': '1. Show # me.\n2. My profile.\n3. I don\'t want to look for anyone else.',
                         'id1': '# menyukai &. Coba lihat? \n1. Tunjukkan.\n2. Tidak mencari lagi',
                         'id2': '1. Tampilkan # yang menyukai saya.\n2. Profil saya.\n3. Saya tidak ingin mencari orang lain.'
                         }
        self.bot_love_user_1 = {'ru': {'w': 'понравилась ', 'm': 'понравился '},
                                'uk': {"w": 'сподобалася ', 'm': 'сподобався '},
                                'en': {'w': 'you', 'm': 'you'},
                                'id': {'w ': 'Anda', 'm': 'Anda'}}
        self.bot_love_user_2 = {
            'ru1': {'ma': 'людям. Показать их?', 'w': 'девушке. Показать её?', 'm': 'парню. Показать его?',
                    'wm': 'девушкам. Показать их?', 'mm': 'парням. Показать их?'},
            'uk1': {'ma': 'людина. Показати їх?', 'w': 'дівчина. Показати її?', 'm': 'хлопець. Показати його?',
                    'wm': 'дівчатам. Показати їх?', 'mm': 'хлопцям. Показати їх?'},
            'en1': {'ma': 'people', 'w': 'woman', 'm': 'man', 'wm': 'women', 'mm': 'men'},
            'id1': {'ma': 'orang ', 'w': 'wanita', 'm': 'pria', 'wm': 'wanita', 'mm': 'pria'},
            'ru2': {"ma": 'людей, которым', 'w': 'девушку, которой', 'm': 'парня, которому', 'wm': 'девушек, которым',
                    'mm': 'парней, которым'},
            'uk2': {"ma": 'людей, яким', 'w': 'дівчину, якій', 'm': 'хлопця, якому', 'wm': 'дівчат, яким',
                    'mm': 'хлопців, яким'},
            'en2': {'ma': 'people who like', 'w': 'girl who likes', 'm': 'guy who likes', 'wm': 'girls who like',
                    'mm': 'guys who like'},
            'id2': {'ma': 'orang', 'w': 'gadis', 'm': 'pria', 'wm': 'cewek yang suka', 'mm': 'cowok yang suka'}}
        self.bot_link = {'ru': 'Отлично! Надеюсь хорошо проведете время ;) Начинай общаться #',
                         'uk': 'Відмінно! Сподіваюся добре проведете час;) починай спілкуватися #',
                         'en': 'Matched! Start chatting #', 'id': 'Cocok! Mulai chatting #'}
        self.bot_complaint = {
            'ru': 'Укажите причину жалобы\n\n1. 🔞 Материал для взрослых.\n2. 💊 Пропаганда наркотиков.\n3. 💰 Продажа товаров и услуг.\n4. 🦨 Другое.\n***\n9. Вернуться назад.',
            'uk': 'Вкажіть причину скарги\n\n1. 🔞 Матеріал для дорослих.\n2. 💊 Пропаганда наркотиків.\n3. 💰 Продаж товарів і послуг.\n4. 🦨 Інше.\n***\n9. Повернутись назад.',
            'en': 'Specify the reason for the complaint\n\n1. 🔞 Adult material.\n2. 💊 Drug propaganda.\n3. 💰 Sale of goods and services.\n4. 🦨 Other.\n***\n9. Go back.',
            'id': 'Tentukan alasan pengaduan\n\n1. 🔞 Bahan dewasa.\n2. 💊 Propaganda narkoba.\n3. 💰 Penjualan barang dan jasa.\n4. 🦨 Lainnya.\n***\n9. Kembali.'}
        self.bot_true_complaint = {'ru': 'Жалоба будет обработана в ближайшее время.',
                                   'uk': 'Скарга буде опрацьована найближчим часом.',
                                   'en': 'Your complaint will be processed soon.', 'id': 'Aduan kemudiannya diproses.'}
        self.bot_sleep = {
            'ru': 'Так ты не узнаешь, что кому-то нравишься... Точно хочешь отключить свою анкету?\n\n1. Да, отключить анкету.\n2. Нет, вернуться назад.',
            'uk': 'Так ти не дізнаєшся, що комусь подобаєшся... Точно хочеш відключити свою анкету?\n\n1. Так, відключити анкету.\n2. Ні, повернутись назад.',
            'en': 'You won\'t know who likes you then... Sure about deactivating?\n1. Yes, deactivate my profile please.\n2. No, I want to see my matches.',
            'id': 'Dengan ini anda tidak akan mengetahui bahawa seseorang menyukai anda... Adakah anda pasti mahu nyahaktifkan profil anda?\n\n1. Ya, nyahaktifkan profil.\n2. Tak, kembali.'}
        self.bot_wait_anket = {
            'ru': 'Надеюсь ты нашел кого-то благодаря мне! Рад был с тобой пообщаться, будет скучно – пиши, обязательно найдем тебе кого-нибудь\n\n1. Смотреть анкеты',
            'uk': 'Сподіваюсь ти когось знайшов з моєю допомогою! \nРадий був поспілкуватися, якщо буде нудно – пиши, обов\'язково знайдем тобі когось\n\n1. Дивитися анкети',
            'en': 'Hope you met someone with my help!\nAlways happy to chat. If bored, text me -  I\'ll find someone special for you.\n\n1. View profiles',
            'id': 'Aku harap anda menjumpai seseorang kerana aku! Aku gembira dapat bercakap dengan anda, jika ianya akan membosankan - tulis, kita pasti mencarikan anda seseorang\n\n1. Lihat profil'}
        self.bot_continue = {'ru': '#, подпишись на телеграмм канал создателя этого бота 👉 @pythonproga',
                             'uk': '#, підпишись на телеграм канал творця цього бота 👉 @pythonproga',
                             'en': '#, subscribe to the telegram channel of the creator of this bot 👉 @pythonproga',
                             'id': '# , berlangganan saluran telegram dari pencipta bot ini 👉 @pythonproga'}
        self.bot_text = {'ru': '# для тебя текст:\n\n', 'uk': '# для тебе текст:\n\n', 'en': '# text for you:\n\n',
                         'id': '# teks untuk Anda:\n\n'}
        self.bot_video = {'ru': '# для тебя видео 👆', 'uk': '# для тебе відео 👆', 'en': '# video for you 👆',
                          'id': '# video untuk Anda 👆'}
        self.bot_photo = {'ru': '# для тебя фото 👆', 'uk': '# для тебе фото 👆', 'en': '# photo for you 👆',
                          'id': '# foto untuk Anda 👆'}
        self.bot_send = {'ru': {'w': 'Она отправила', 'm': 'Он отправил'},
                         'uk': {"w": 'Вона відправила', 'm': 'Він відправив'},
                         'en': {'w': 'She sent', 'm': 'He sent'},
                         'id': {'w': 'Dia mengirim', 'm': 'Dia mengirim'}}
        self.bot_error = {'ru': 'Нет такого варианта ответа', 'uk': 'Немає такого варіанту відповіді',
                          'en': 'No such option', 'id': 'Tiada jawapan seperti ini'}

        self.user_love = {'all1': ['❤', '💤'], 'all2': ['1🚀', '2', '3']}
        self.user_anket = {'ru': ['❤', '👎', 'жалоба', '💤'], 'uk': ['❤', '👎', 'скарга', '💤'],
                           'en': ['❤', '👎', 'complaint', '💤'], 'id': ['❤', '👎', 'keluhan', '💤']}
        self.user_link = {'ru': ['⚠ Пожаловаться'], 'uk': ['⚠ Поскаржитися'], 'en': ['⚠ Complain'],
                          'id': ['⚠ Mengeluh']}
        self.user_link_complaint = {
            'ru': ['🔞 Материал для взрослых', '💰 Продажа товаров и услуг', '😴 Не отвечает', '🦨 Другое', '✖ Отмена'],
            'uk': ['🔞 Матеріал для дорослих', '💰 Продаж товарів і послуг', '😴 Не відповідає', '🦨 Інше',
                   '✖ Скасування'],
            'en': ['🔞 Adult material', '💰 Sale of goods and services', '😴 Not responding', '🦨 Other', '✖ Cancel'],
            'id': ['🔞 Bahan dewasa', '💰 Penjualan barang dan jasa', '😴 Tidak menanggapi', '🦨 Lainnya', '✖ Batal']}
        self.user_true_complaint = {'ru': ['✅ Жалоба отправлена'], 'uk': ['✅ Скарга відправлена'],
                                    'en': ['✅ The complaint has been sent'], 'id': ['✅ Keluhan telah dikirim']}
        self.user_complaint = {'all': ['1🔞', '2💊', '3💰', '4🦨', '9']}
        self.user_sleep = {'all': ['1', '2']}
        self.user_wait_anket = {'ru': ['Смотреть анкеты'], 'uk': ['Дивитися анкети'], 'en': ['View profiles'],
                                'id': ['Lihat profil']}

        self.server_complaint = {'1🔞': '🔞 Материал для взрослых', '2💊': ' 💊Пропаганда наркотиков',
                                 '3💰': '💰 Продажа товаров и услуг', '4🦨': '🦨 Другое'}

    # функция каждые 60 секунд проверяет лайкнул ли пользователя кто-то или нет
    def one_love(self, message, ankets):
        self.id = message.from_user.id

        self.user_love_anket = ankets

        self.ind = 0
        self.count_love_anket = len(self.user_love_anket)

        bot.clear_step_handler(message)

        self.lang, self.male = get_something('lang, male', self.id)

        random_chisl = random.randint(1, 2)
        key = f'{self.lang}{random_chisl}'
        send_message_text = self.bot_love[key]

        if random_chisl == 1:
            send_message_text = send_message_text.replace('&',
                                                          self.bot_love_user_1[self.lang][self.male])
        if self.count_love_anket > 1:
            all_women = True
            for i in self.user_love_anket:
                if i[4] == 'm':
                    all_women = False

            all_man = True
            for i in self.user_love_anket:
                if i[4] == 'w':
                    all_man = False

            if all_man:
                send_message_text = send_message_text.replace('#', str(self.count_love_anket) + ' ' +
                                                              self.bot_love_user_2[key]['mm'])
            elif all_women:
                send_message_text = send_message_text.replace('#', str(self.count_love_anket) + ' ' +
                                                              self.bot_love_user_2[key]['wm'])
            else:
                send_message_text = send_message_text.replace('#', str(self.count_love_anket) + ' ' +
                                                              self.bot_love_user_2[key]['ma'])
        else:
            send_message_text = send_message_text.replace('#', str(self.count_love_anket) + ' ' +
                                                          self.bot_love_user_2[key][
                                                              self.user_love_anket[self.ind][4]])

        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(*self.user_love[f'all{random_chisl}'])

        send_message = bot.send_message(message.chat.id, send_message_text, reply_markup=markup)
        bot.register_next_step_handler(send_message, self.two_love)

    # функция вызывается когда пользователя кто-то лайкнул, и принимает то, что ответил пользователь на сообщение по типу - 'Показать 1 девушку, которой я нравлюсь. 1. ДА 2. НЕТ'
    def two_love(self, message, many_anket=False):
        # мы выходим из менюшки, и это значит, что пока чтог нельзя сообщать о лайках анкеты
        exec(f'global run{self.id}\nrun{self.id}=None')

        try:
            lock.acquire(True)

            # так, как пользователь увидел, что его лайкнули, то обнуляем счётчик лайков
            c.execute('UPDATE users SET count_of_send_message = 0 WHERE id_tg = ?', (self.id,))
            db.commit()
        finally:
            lock.release()

        text = message.text

        if (text == self.user_love[f'all1'][0] or text == self.user_love['all2'][0]) or many_anket:
            if self.ind < self.count_love_anket:
                markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
                markup.add(*self.user_anket[self.lang])

                send_message = send_anket(message, self.user_love_anket[self.ind][1], markup, True)
                if self.user_love_anket[self.ind][7]:
                    send_message = bot.send_message(message.chat.id,
                                                    self.bot_text[self.lang].replace('#', self.bot_send[self.lang][
                                                        self.user_love_anket[self.ind][4]]) +
                                                    self.user_love_anket[self.ind][7])
                elif self.user_love_anket[self.ind][8]:
                    send_message = bot.send_video(message.chat.id, self.user_love_anket[self.ind][8], 15,
                                                  caption=self.bot_video[self.lang].replace('#',
                                                                                            self.bot_send[
                                                                                                self.lang][
                                                                                                self.user_love_anket[
                                                                                                    self.ind][4]]))
                elif self.user_love_anket[self.ind][9]:
                    send_message = bot.send_photo(chat_id=message.chat.id, photo=self.user_love_anket[self.ind][9],
                                                  caption=self.bot_photo[self.lang].replace('#',
                                                                                            self.bot_send[self.lang][
                                                                                                self.user_love_anket[
                                                                                                    self.ind][4]]))

                bot.register_next_step_handler(send_message, self.three_love)
            else:
                Menu().after_something(message)
        elif text == self.user_love['all1'][1]:
            Menu().after_something(message)
        elif text == self.user_love['all2'][2]:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add(*self.user_sleep['all'])

            send_message = bot.send_message(message.chat.id, self.bot_sleep[self.lang], reply_markup=markup)
            bot.register_next_step_handler(send_message, self.sleep_love)
        elif text == self.user_love['all2'][1]:
            MyAnket().one_my_anket(message, 'command')
        else:
            if errors(message):
                send_message = bot.send_message(message.chat.id, self.bot_error[self.lang])
                bot.register_next_step_handler(send_message, self.two_love)

    # функция принимает то, что поставил (лайк, дизлайк, жалоба и т.д.) пользователь другому пользователю, если он его лайкнул
    def three_love(self, message):
        text = message.text
        if text == self.user_anket[self.lang][0]:
            markup = InlineKeyboardMarkup(row_width=1)
            complaint = InlineKeyboardButton(self.user_link[self.lang][0],
                                             callback_data=f'complaint_{self.user_love_anket[self.ind][0]}')
            markup.add(complaint)

            if self.user_love_anket[self.ind][3] is None:
                bot.send_contact(message.chat.id, phone_number=self.user_love_anket[self.ind][5],
                                 first_name=self.user_love_anket[self.ind][6], )
                bot.send_message(message.chat.id, self.bot_link[self.lang].replace('#', ''), reply_markup=markup)
            else:
                bot.send_message(message.chat.id,
                                 self.bot_link[self.lang].replace('#', f'👉 @{self.user_love_anket[self.ind][3]}'),
                                 reply_markup=markup)

            try:
                lock.acquire(True)

                c.execute('UPDATE love SET active = 0 WHERE from_user = ? AND to_user = ?',
                          (self.user_love_anket[self.ind][1], self.user_love_anket[self.ind][2]))
                db.commit()
            finally:
                lock.release()

            self.ind += 1

            self.two_love(message, True)
        elif text == self.user_anket[self.lang][1]:
            try:
                lock.acquire(True)

                c.execute('UPDATE love SET active = 0 WHERE from_user = ? AND to_user = ?',
                          (self.user_love_anket[self.ind][1], self.user_love_anket[self.ind][2]))
                db.commit()
            finally:
                lock.release()

            self.ind += 1

            self.two_love(message, True)
        elif text == self.user_anket[self.lang][2]:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=5)
            markup.add(*self.user_complaint['all'])

            send_message = bot.send_message(message.chat.id, self.bot_complaint[self.lang], reply_markup=markup)
            bot.register_next_step_handler(send_message, self.complaint)
        elif text == self.user_anket[self.lang][3]:
            Menu().after_something(message)
        else:
            if errors(message, self):
                send_message = bot.send_message(message.chat.id, self.bot_error[self.lang])
                bot.register_next_step_handler(send_message, self.two_love)

    def complaint(self, message):
        text = message.text

        if text in self.user_complaint['all']:
            if text != '9':
                bot.send_message(message.chat.id, self.bot_true_complaint[self.lang])

                try:
                    lock.acquire(True)

                    c.execute('INSERT INTO complaint(from_user, to_user, type) VALUES(?, ?, ?)',
                              (self.id, self.user_love_anket[self.ind][1], self.server_complaint[text]))
                    db.commit()

                    c.execute('UPDATE love SET active = 0 WHERE from_user = ? AND to_user = ?',
                              (self.user_love_anket[self.ind][1], self.user_love_anket[self.ind][2]))
                    db.commit()
                finally:
                    lock.release()

                self.ind += 1
            self.two_love(message, True)
        else:
            if errors(message):
                send_message = bot.send_message(message.chat.id, self.bot_error[self.lang])
                bot.register_next_step_handler(send_message, self.complaint)

    # функция вызывается тогда, когда пользователь захотел отключить свою анкету
    def sleep_love(self, message):
        text = message.text

        if text == self.user_sleep['all'][0]:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*self.user_wait_anket[self.lang])

            send_message = bot.send_message(message.chat.id, self.bot_wait_anket[self.lang], reply_markup=markup)

            try:
                lock.acquire(True)

                c.execute('UPDATE users SET is_search = False WHERE id_tg = ?', (self.id,))
                db.commit()
            finally:
                lock.release()

            bot.register_next_step_handler(send_message, lambda message: wait_anket(message, 'wait'))
        elif text == self.user_sleep['all'][1]:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
            markup.add(*self.user_anket[self.lang])

            send_message = send_anket(message, self.user_love_anket[self.ind][1], markup, True)
            bot.register_next_step_handler(send_message, self.three_love)
        else:
            if errors(message):
                send_message = bot.send_message(message.chat.id, self.bot_error[self.lang])
                bot.register_next_step_handler(send_message, self.sleep_love)


# функция всё время просматирвает все лайки анкет
def like_ankets_search():
    while True:
        try:
            lock.acquire(True)

            # получаем все лайки
            c.execute(
                'SELECT love_id, from_user, to_user, from_username, from_male, from_phone, from_first_name, text, video, photo FROM love WHERE active = 1 GROUP BY from_user, to_user, from_phone')
            user_love_ankets = c.fetchall()
        finally:
            lock.release()

        # получаем все id, которые лайкнули
        users_id = set([i[2] for i in user_love_ankets])

        for id in users_id:
            # если пользователь находится в меню, то в переменной у нас будет находиться объект telebot.Message, а иначе None
            message = globals().get(f'run{id}', None)

            if message:
                # получаем лайки, предназначенные для какого-то одного пользователя
                send_ankets = [i for i in user_love_ankets if i[2] == id]

                try:
                    lock.acquire(True)

                    c.execute('SELECT count_of_send_message FROM users WHERE id_tg = ?', (id,))
                    # узнаём сколько людей лайкнули пользователя
                    count_of_send_message = c.fetchone()[0]

                    # и если мы видим, что добавились ещё лайке к анкете, то сообщаем об этом, а также, записываем, сколько лайков
                    if len(send_ankets) > count_of_send_message:
                        c.execute('UPDATE users SET count_of_send_message = ? WHERE id_tg = ?', (len(send_ankets), id))
                        db.commit()
                finally:
                    lock.release()

                if send_ankets and len(send_ankets) > count_of_send_message:
                    Love().one_love(message, send_ankets)


# запускаем поток в фоне
Thread(target=like_ankets_search).start()


# функция, которая реагирует на команду start
@bot.message_handler(commands=['start', 'help'])
def start_func(message):
    # это нужно, чтобы если пользователь несколько раз быстро нажал на команду /start, сообщение не отсылались по несколько раз
    if globals().get(f'start_time_{message.from_user.id}', 0) < time.time():
        exec(f'global start_time_{message.from_user.id}\nstart_time_{message.from_user.id} = time.time()+5')

        try:
            lock.acquire(True)

            c.execute('SELECT reg FROM users WHERE id_tg = ?', (message.from_user.id,))
            cf = c.fetchone()
        finally:
            lock.release()

        # проверяем перешёл ли по реферальной ссылке он или нет
        if " " in message.text:
            referrer_candidate = message.text.split()[1]

            try:
                lock.acquire(True)
                c.execute('SELECT users_id FROM users WHERE id_tg = ?', (referrer_candidate,))
                users_id = c.fetchone()

                if users_id and str(message.from_user.id) != referrer_candidate and cf is None:
                    c.execute('SELECT referrals_id FROM referrals WHERE tg_id = ?', (message.from_user.id,))

                    if c.fetchone() is None:
                        c.execute('INSERT INTO referrals(tg_id, date_created, users_id) VALUES(?, ?, ?)',
                                  (message.from_user.id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), users_id[0]))
                        db.commit()
            finally:
                lock.release()

        # если пользователь первый раз пользуется ботом
        if cf is None:
            try:
                lock.acquire(True)
                c.execute('INSERT INTO users(id_tg, lang_code, reg) VALUES(?, ?, ?)',
                          (message.from_user.id, message.from_user.language_code, 0))
                db.commit()
            finally:
                lock.release()

            Lang().one_lang(message, Start().one_start)
        # если пользователь ещё не до конца создал анкету
        elif cf[0] == 0:
            Lang().one_lang(message, Start().one_start)
        # в любом другом случае
        else:
            Lang().one_lang(message, lambda message: MyAnket().one_my_anket(message, 'command'))


# функция изменяет callback-inline кнопки, которые позволяют пожаловаться, если пользователь лайкнул в ответ другого пользователя
@bot.callback_query_handler(lambda callback: callback.data)
def complaint_callback(callback):
    user_link = {'ru': ['⚠ Пожаловаться'], 'uk': ['⚠ Поскаржитися'], 'en': ['⚠ Complain'],
                 'id': ['⚠ Mengeluh']}
    user_link_complaint = {
        'ru': ['🔞 Материал для взрослых', '💰 Продажа товаров и услуг', '😴 Не отвечает', '🦨 Другое', '✖ Отмена'],
        'uk': ['🔞 Матеріал для дорослих', '💰 Продаж товарів і послуг', '😴 Не відповідає', '🦨 Інше',
               '✖ Скасування'],
        'en': ['🔞 Adult material', '💰 Sale of goods and services', '😴 Not responding', '🦨 Other', '✖ Cancel'],
        'id': ['🔞 Bahan dewasa', '💰 Penjualan barang dan jasa', '😴 Tidak menanggapi', '🦨 Lainnya', '✖ Batal']}
    user_true_complaint = {'ru': ['✅ Жалоба отправлена'], 'uk': ['✅ Скарга відправлена'],
                           'en': ['✅ The complaint has been sent'], 'id': ['✅ Keluhan telah dikirim']}
    user_true_true_complaint = {'ru': 'Вы уже отправили жалобу!', 'uk': 'Ви вже надіслали скаргу!',
                                'en': 'You have already sent a complaint!', 'id': 'Anda sudah mengirim keluhan!'}

    server_complaint = {'porno': '🔞 Материал для взрослых', 'sale': '💰 Продажа товаров и услуг',
                        'not responding': '😴 Не отвечает', 'other': '🦨 Другое'}

    id = callback.from_user.id
    lang = get_something('lang', id)[0]
    data, love_id = callback.data.split('_')

    if data == 'complaint':
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton(user_link_complaint[lang][0], callback_data=f'porno_{love_id}'),
                   InlineKeyboardButton(user_link_complaint[lang][1], callback_data=f'sale_{love_id}'),
                   InlineKeyboardButton(user_link_complaint[lang][2], callback_data=f'not responding_{love_id}'),
                   InlineKeyboardButton(user_link_complaint[lang][3], callback_data=f'other_{love_id}'),
                   InlineKeyboardButton(user_link_complaint[lang][4], callback_data=f'cancel_{love_id}'), )

        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                              text=callback.message.text, reply_markup=markup)
    elif data == 'cancel':
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton(user_link[lang][0], callback_data=f'complaint_{love_id}'))

        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                              text=callback.message.text, reply_markup=markup)
    elif data == 'true complaint':
        bot.answer_callback_query(callback_query_id=callback.id, text=user_true_true_complaint[lang])
    else:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton(user_true_complaint[lang][0], callback_data=f'true complaint_{love_id}'))

        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                              text=callback.message.text, reply_markup=markup)

        try:
            lock.acquire(True)

            c.execute('SELECT from_user FROM love WHERE love_id = ?', (love_id,))
            from_user = c.fetchone()

            c.execute('DELETE FROM love WHERE love_id = ?', (love_id,))
            db.commit()

            c.execute('INSERT INTO complaint(from_user, to_user, type) VALUES(?, ?, ?)',
                      (id, from_user[0], server_complaint[data]))
            db.commit()
        finally:
            lock.release()


bot.polling(none_stop=True)

# закрываем базу данных
if db:
    db.close()

