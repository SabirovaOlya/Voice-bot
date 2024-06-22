import os
import logging
from dotenv import load_dotenv
from aiogram import Bot
from utils.data import channels
from database.functions import UserManager, PartManager, VoiceManager
from sqlalchemy.ext.asyncio import AsyncSession


load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)


async def resolve_chat_id(username: str) -> int:
    try:
        chat = await bot.get_chat(username)
        return chat.id
    except Exception as e:
        logging.error(f"Error resolving chat ID for {username}: {e}")
        return None


async def check_subscription(message, session: AsyncSession) -> bool:
    for channel in channels:
        channel_id = channel['id']
        if channel_id.startswith('@'):
            channel_id = await resolve_chat_id(channel_id)
            if not channel_id:
                logging.error(f"Failed to resolve chat ID for channel: {channel['id']}")
                return False

        try:
            chat_member = await bot.get_chat_member(channel_id, message.from_user.id)
            if chat_member.status == 'left':
                return False
        except Exception as e:
            logging.error(f"Error checking subscription for channel {channel_id}: {e}")
            return False

    user_manager = UserManager(session)
    user = await user_manager.get_user_by_user_id(str(message.from_user.id))
    if not user:
        new_user = await user_manager.add_user(
            full_name=message.from_user.full_name,
            user_id=str(message.from_user.id),
            username=message.from_user.username
        )
    return True


async def check_subscription_by_user_id(user_id: int) -> bool:
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


async def user_voice_having(user_id: str, session: AsyncSession) -> bool:
    part_manager = PartManager(session)
    active_part = await part_manager.get_available_parts()

    if active_part:
        voice_manager = VoiceManager(session)
        user_voice = await voice_manager.get_voice_by_user_id(user_id, active_part.id)
        if not user_voice:
            return False
        return user_voice
    return False


async def user_voice_activate(user_id: str, session: AsyncSession) -> None:
    part_manager = PartManager(session)
    active_part = await part_manager.get_available_parts()

    voice_manager = VoiceManager(session)
    voice = await voice_manager.update_voice_status(user_id, True, active_part.id)


async def check_actual_subscriptions(session: AsyncSession):
    voice_manager = VoiceManager(session)
    voices = await voice_manager.get_all_voices()

    for voice in voices:
        user_id = int(voice.user_id)
        is_subscribed = await check_subscription_by_user_id(user_id)

        if not is_subscribed:
            result = await voice_manager.update_voice_status(voice.user_id, False, voice.part_id)
            print(result)
            await bot.send_message(chat_id=int(user_id),
                text="Сиз каналлардан ўаз кешкенсыз, сол себеплы сиздың даўысыңыз бийкар етилды.\n\n"
                     "Даўысыңызды қайта тиклеў ушын /start ни жумысқа тусырың, каналларға жазылыў болың, "
                     "'Агза болдым' туймесын басыў арқалы жазылыў болғаныңызды тастыйықланг")


def cutting_district_end(name: str):
    if 'районы' in name:
        new_name = name.replace(' районы', '')
        return new_name
    return name

