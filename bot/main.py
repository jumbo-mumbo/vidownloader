import logging
import asyncio

from aiogram import Dispatcher, Bot, Router, types

from config import API_TOKEN
from handlers import main_handlers


async def main():
    bot = Bot(API_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(main_handlers.router)

    logging.basicConfig(level=logging.INFO)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())