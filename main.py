import asyncio
import colorama
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import load_dotenv, find_dotenv

from log.logger_cfg import inits_logger
from database.db_cfg import create_db

from handlers import usr_commands
from callbacks import usr_callbacks
from states import first_registration_state

colorama.init()

async def main():
    load_dotenv(find_dotenv('src/private/tokens.env'))
    dp = Dispatcher()
    bot = Bot(os.getenv("TEST_TOKEN"), parse_mode=ParseMode.HTML)

    dp.include_routers(
        usr_commands.router,
        usr_callbacks.router,
        first_registration_state.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Bot started!" + colorama.Fore.RED)
    inits_logger.info('bot successfully started')
    create_db()
    asyncio.run(main())
