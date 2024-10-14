from aiogram.fsm.state import State, StatesGroup


class FirstRegistration(StatesGroup):
    # auto
    username = State()
    chat_id = State()
    isActive = State()

    # user info
    name = State()
    age = State()
    isMale = State()
    faculty = State()
    isBaccalaureate = State()
    course = State()
    photo = State()
    about = State()
    friend_sex = State()


class RewriteProfile(StatesGroup):
    # user info
    name = State()
    age = State()
    isMale = State()
    faculty = State()
    isBaccalaureate = State()
    course = State()
    photo = State()
    about = State()
    friend_sex = State()


class MenuState:
    MAIN = "main_menu"
    SETTINGS = "main_settings"
    HELP = "help_menu"
