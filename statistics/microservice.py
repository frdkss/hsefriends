import asyncio
import colorama
import os

import statistic_answer

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import load_dotenv, find_dotenv

colorama.init()


async def microservice():
    load_dotenv(find_dotenv('../src/private/tokens.env'))
    dp = Dispatcher()
    bot = Bot(os.getenv("STATISTIC_TOKEN"), parse_mode=ParseMode.HTML)

    dp.include_routers(
        statistic_answer.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("HSE Friends Stat started!" + colorama.Fore.RED)
    asyncio.run(microservice())
