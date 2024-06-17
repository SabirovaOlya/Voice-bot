import os
import asyncio
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from sqlalchemy.future import select
from utils.data import channels
from database.engine import session_maker
from database.models import Voice
from database.functions import VoiceManager


load_dotenv()

TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)


async def resolve_chat_id(username: str) -> int | None:
    try:
        chat = await bot.get_chat(username)
        return chat.id
    except Exception as e:
        print(e)
        return None


async def check_subscription(user_id: int) -> bool:
    for channel in channels:
        channel_id = channel['id']
        if channel_id.startswith('@'):
            channel_id = await resolve_chat_id(channel_id)
            if not channel_id:
                return False

        try:
            chat_member = await bot.get_chat_member(channel_id, user_id)
            if chat_member.status == 'left':
                return False
        except Exception as e:
            print(e)
            return False
    return True


async def check_actual_subscriptions() -> None:
    async with session_maker() as session:
        async with session.begin():
            result = await session.execute(select(Voice).filter_by(is_active=True))
            voices = result.scalars().all()

            for voice in voices:
                user_id = int(voice.user_id)
                is_subscribed = await check_subscription(user_id)

                if not is_subscribed:
                    voice_manager = VoiceManager(session)
                    result = await voice_manager.update_voice_status(voice.user_id, False, voice.part_id)
                    print(result)
                    await bot.send_message(chat_id=int(user_id),
                        text="Siz kanallardan waz keshkensiz, sol sebepli sizdiń dawısıńız biykar etildi.\n\n"
                             "Dawısıńızdı qayta tiklew ushın /start ni jumısqa tusiriń, kanallarǵa jazılıw bolıń, "
                             "'Agza boldım' tuymesin basıw arqalı jazılıw bolǵanıńızdı tastıyıqlang")
            await session.commit()


def schedule_daily_check():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_actual_subscriptions, 'interval', minutes=1)
    scheduler.start()

    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        scheduler.shutdown()


if __name__ == '__main__':
    schedule_daily_check()
