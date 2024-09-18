import asyncio
import colorama
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv, find_dotenv
from loguru import logger

from log.logger_cfg import inits_logger
# from callbacks import
# from handlers import
# from states import

colorama.init()

async def main():
    load_dotenv(find_dotenv('src/private/tokens.env'))
    dp = Dispatcher()
    bot = Bot(os.getenv("TEST_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # dp.include_routers(
    # )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Bot started!" + colorama.Fore.RED)
    inits_logger.info('bot successfully started')
    asyncio.run(main())
