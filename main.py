import os
import asyncio
import logging
import sys

from dotenv import load_dotenv
from aiogram import Dispatcher, Bot
from routes import router as main_router

load_dotenv()

from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker


TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_routers(main_router,)


async def on_startup():
    run_param = False
    if run_param:
        await drop_db()

    await create_db()


async def on_shutdown():
    print('Bot is shutting down')
    await bot.close()


async def main() -> None:
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

#contabo, regru, timeweb, zomro, aws, digitalocean
