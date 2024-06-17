from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
from utils.data import channels
from database.functions import DistrictManager, StreetManager, VoiceManager, PartManager
from sqlalchemy.ext.asyncio import AsyncSession


def show_channel_inlines():
    btns = []
    for channel in channels:
        btns.append([InlineKeyboardButton(text=channel['name'], url=channel['url'])])
    
    btnDoneSubscription = [InlineKeyboardButton(text='Agza boldim', callback_data='subscription_done')]
    btns.append(btnDoneSubscription)

    ikb = InlineKeyboardMarkup(inline_keyboard=btns)
    return ikb


async def show_district_inlines(session: AsyncSession):
    try:
        district_manager = DistrictManager(session)
        districts = await district_manager.get_all_districts()

        btns = []
        for i in range(0, len(districts), 2):
            row = []
            row.append(InlineKeyboardButton(text=districts[i].name, callback_data=f"district/{districts[i].id}"))
            if i + 1 < len(districts):
                row.append(
                    InlineKeyboardButton(text=districts[i + 1].name, callback_data=f"district/{districts[i + 1].id}"))
            btns.append(row)

        ikb = InlineKeyboardMarkup(inline_keyboard=btns)
        return ikb

    except Exception as e:
        print(e)


async def show_street_inlines(session: AsyncSession, district_id):
    try:
        street_manager = StreetManager(session)
        streets = await street_manager.get_streets_by_district_id(int(district_id))

        btns = []
        for i in range(0, len(streets), 2):
            row = []
            row.append(InlineKeyboardButton(text=streets[i].name, callback_data=f"street/{streets[i].id}"))
            if i + 1 < len(streets):
                row.append(
                    InlineKeyboardButton(text=streets[i + 1].name, callback_data=f"street/{streets[i + 1].id}"))
            btns.append(row)

        btns.append([InlineKeyboardButton(text='⬅️⬅️ Qaytıw', callback_data=f"back_from_street")])
        ikb = InlineKeyboardMarkup(inline_keyboard=btns)
        return ikb
    except Exception as e:
        print(e)


def confirm_voice_keyboard():
    voice_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Dawis beruw", callback_data="confirm_voice"),
             InlineKeyboardButton(text="Biykarlaw", callback_data="cancel_voice")]
        ]
    )

    return voice_keyboard


async def show_district_statistic_inlines(session: AsyncSession):
    try:
        part_manager = PartManager(session)
        active_part = await part_manager.get_available_parts()
        voice_manager = VoiceManager(session)
        districts = await voice_manager.get_district_statistics(active_part.id)

        btns = []
        for i in range(0, len(districts), 2):
            row = []
            row.append(InlineKeyboardButton(text=f'{districts[i]["rank"]}. {districts[i]["district_name"]} - {districts[i]["voice_count"]}',
                                            callback_data=f"stat_district/{districts[i]['district_id']}"))
            if i + 1 < len(districts):
                row.append(
                    InlineKeyboardButton(text=f'{districts[i]["rank"]}. {districts[i]["district_name"]} - {districts[i]["voice_count"]}',
                    callback_data=f"stat_district/{districts[i + 1]['district_id']}")
                )
            btns.append(row)

        ikb = InlineKeyboardMarkup(inline_keyboard=btns)
        return ikb

    except Exception as e:
        print(e)


async def show_street_statistic_inlines(session: AsyncSession, district_id: int):
    try:
        part_manager = PartManager(session)
        active_part = await part_manager.get_available_parts()
        voice_manager = VoiceManager(session)
        streets = await voice_manager.get_street_statistics(active_part.id, district_id)

        btns = []
        for i in range(0, len(streets), 2):
            row = []
            row.append(InlineKeyboardButton(text=f'{streets[i]["rank"]}. {streets[i]["street_name"]} - {streets[i]["voice_count"]}',
                                            callback_data=f"111"))
            if i + 1 < len(streets):
                row.append(
                    InlineKeyboardButton(text=f'{streets[i]["rank"]}. {streets[i]["street_name"]} - {streets[i]["voice_count"]}',
                    callback_data=f"111")
                )
            btns.append(row)

        ikb = InlineKeyboardMarkup(inline_keyboard=btns)
        return ikb

    except Exception as e:
        print(e)
