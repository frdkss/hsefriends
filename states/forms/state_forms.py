from aiogram.fsm.state import State, StatesGroup

class FirstRegistration(StatesGroup):
    # auto
    username = State()
    chat_id = State()

    # user info
    name = State()
    age = State()
    isMale = State()
    faculty = State()
    isBaccalaureate = State()
    course = State()
    photo = State()
    about = State()

    # friend
    friend_sex = State()
