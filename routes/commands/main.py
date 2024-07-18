import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from utils.functions import check_subscription, user_voice_having, user_voice_activate, check_actual_subscriptions
from utils.messages import NOT_SUB_MESSAGE
from components.inlinekeyboards import (show_district_inlines, show_street_inlines,
                                        confirm_voice_keyboard, show_channel_inlines, show_district_statistic_inlines,
                                        show_street_statistic_inlines, statistics_part_select)
from database.functions import PartManager, StreetManager, VoiceManager, UserManager, DistrictManager
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()
logging.basicConfig(level=logging.INFO)


class Form(StatesGroup):
    selected_street = State()
    phone_number = State()


class AdminForm(StatesGroup):
    username = State()


@router.message(CommandStart())
async def start_handler(message: Message, session: AsyncSession):
    voice_manager = VoiceManager(session)
    part_manager = PartManager(session)
    active_part = await part_manager.get_available_parts()
    if active_part:
        if await check_subscription(message, session):
            user_voice = await user_voice_having(str(message.from_user.id), session)
            print(str(message.from_user.id), 'start\n\n')
            print(user_voice)
            if user_voice:
                statistic = await voice_manager.get_voice_statistics(str(message.from_user.id), active_part.id)

                message_text = (
                    f'Ассалаўма әлейкум {message.from_user.full_name}, Сиз алдын даўыс бердиңиз!!!\n\n'
                    f'Район: {user_voice["district_name"]} ({statistic["district_rank"]} орын)\n'
                    f'Mәҳәлле: {user_voice["street_name"]} ({statistic["street_rank"]} орын)\n'
                    f'Бөлим: {user_voice["part_name"]}\n'
               )
                await message.answer(message_text)
            else:
                text = (
                    f"Ассалаўма әлейкум {message.from_user.full_name}!!!\n\nЕң белсенди “Мәҳәлле жетилиги”не даўыс бериў ботына хош келипсиз!"
                    f"\n\n{active_part.name}")
                await message.answer(text=text)
                await message.answer(text='Районды сайлаң:', reply_markup=await show_district_inlines(session))
        else:
            await message.answer(text=NOT_SUB_MESSAGE, reply_markup=show_channel_inlines())
    else:
        await message.answer(text=f'Ассалаўма әлейкум {message.from_user.full_name}!!!'
                                  '\n\nMәҳәллелерге даўыс бериў тоқтатылды')


@router.callback_query(F.data == 'subscription_done')
async def subscription_done_handler(callback: CallbackQuery, session: AsyncSession):
    if await check_subscription(callback, session):
        user_voice = await user_voice_having(str(callback.from_user.id), session)
        print(user_voice)
        if user_voice and user_voice["is_active"] is False:
            await user_voice_activate(str(callback.from_user.id), session)
            message_text = (
                f'Даўысыңыз тикленди!!!\n\n'
                f'Район: {user_voice["district_name"]}\n'
                f'Mәҳәлле: {user_voice["street_name"]}\n'
                f'Бөлим: {user_voice["part_name"]}\n'
            )
            await callback.message.answer(message_text)
        else:
            await callback.message.answer(text='Районды сайлаң:', reply_markup=await show_district_inlines(session))
    else:
        text = NOT_SUB_MESSAGE + '\n\n Қайтадан тексериң!!!'
        await callback.message.answer(text=text)


@router.callback_query(F.data.startswith('district/'))
async def district_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    district_id = callback.data.split('/')[-1]
    await state.set_state(Form.selected_street)
    await callback.message.answer(text='Mәҳәллены тәңлаң:',
                                  reply_markup=await show_street_inlines(session, district_id))


@router.callback_query(F.data.startswith('street/'), Form.selected_street)
async def street_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    try:
        street_id = callback.data.split('/')[-1]
        street_manager = StreetManager(session)
        selected_street = await street_manager.get_street_by_id(int(street_id))
        await state.update_data(selected_street={"id": selected_street.id, "name": selected_street.name})
        data = await state.get_data()
        await callback.message.answer(
            text=f"\n\nСайлаған мәҳәллеңиз: {data['selected_street']['name']}",
            reply_markup=confirm_voice_keyboard()
        )
    except Exception as e:
        await callback.message.answer(text=f"Кәте: {str(e)}")
    finally:
        await session.close()


@router.callback_query(F.data == 'confirm_voice')
async def subscription_done_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    if data.get('selected_street')['id']:
        part_manager = PartManager(session)
        active_part = await part_manager.get_available_parts()
        voice_manager = VoiceManager(session)
        print(str(callback.from_user.id), '\n\n')
        user_voice = await voice_manager.get_voice_by_user_id(str(callback.from_user.id), active_part.id)
        if user_voice:
            message_text = (
                'Сиз алдын даўыс бердиңиз!!!\n\n'
                f'Район: {user_voice["district_name"]}\n'
                f'Mәҳәлле: {user_voice["street_name"]}\n'
                f'Бөлим: {user_voice["part_name"]}\n'
            )
            await callback.message.answer(message_text)
        else:
            try:
                result = await voice_manager.add_voice(str(callback.from_user.id),
                                                   int(data.get('selected_street')['id']),
                                                   active_part.id)
                user_voice = await voice_manager.get_voice_by_user_id(str(callback.from_user.id), active_part.id)
                statistic = await voice_manager.get_voice_statistics(str(callback.from_user.id), active_part.id)
                await callback.message.answer(f"{callback.from_user.full_name}, Даўыс бергениңиз ушын рахмет!!!\n\n"
                                            f'Район: {user_voice["district_name"]} ({statistic["district_rank"]} орын)\n'
                                            f'Mәҳәлле: {user_voice["street_name"]} ({statistic["street_rank"]} орын)\n'
                                            f'Бөлим: {user_voice["part_name"]}\n')
            except Exception as e:
                print(e)
    else:
        await callback.answer(text='Mәҳәллены тәңлаң!!!', show_alert=True)


@router.callback_query(F.data == 'cancel_voice')
async def subscription_done_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.clear()
    await callback.message.answer(text='Районды сайлаң:', reply_markup=await show_district_inlines(session))


@router.callback_query(F.data == 'back_from_street')
async def subscription_done_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.clear()
    await callback.message.answer(text='Районды сайлаң:', reply_markup=await show_district_inlines(session))


@router.message(Command('dawis_tekseriw'))
async def check_sub(message: Message, session: AsyncSession):
    user_manager = UserManager(session)
    is_admin_status = await user_manager.is_admin(str(message.from_user.id))
    if is_admin_status:
        await check_actual_subscriptions(session)
    else:
        await message.answer("Бундай команда жоқ")


@router.message(Command('statistika'))
async def show_statistics(message: Message, session: AsyncSession):
    user_manager = UserManager(session)
    is_admin_status = await user_manager.is_admin(str(message.from_user.id))
    if is_admin_status:
        await message.answer(text="Бөлим:", reply_markup=statistics_part_select())
    else:
        await message.answer("Бундай команда жоқ")


@router.callback_query(F.data.startswith('stat_part/'))
async def show_statistics_parts(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    part_id = callback.data.split('/')[-1]

    await state.set_state(Form.selected_street)
    await callback.message.answer(text=f'Статистика (бөлим - {part_id}):',
                                  reply_markup=await show_district_statistic_inlines(session, part_id))


@router.callback_query(F.data.startswith('stat_district/'))
async def district_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    url_data = callback.data.split('/')[-1]
    part_id = url_data.split('&')[0]
    district_id = url_data.split('&')[-1]

    district_manager = DistrictManager(session)
    selected_district = await district_manager.get_district_by_id(int(district_id))

    await state.set_state(Form.selected_street)
    await callback.message.answer(text=f'Статистика ({selected_district.name}):',
                                  reply_markup=await show_street_statistic_inlines(session, int(district_id), part_id))


@router.message(Command('change_role'))
async def make_admin(message: Message, state: FSMContext, session: AsyncSession):
    user_manager = UserManager(session)
    is_admin_status = await user_manager.is_admin(str(message.from_user.id))
    if is_admin_status:
        await state.set_state(AdminForm.username)
        await message.answer(text="Username киритынг:")
    else:
        await message.answer("Бундай команда жоқ")


@router.message(AdminForm.username)
async def make_admin(message: Message, state: FSMContext, session: AsyncSession):
    user_manager = UserManager(session)
    is_admin_status = await user_manager.is_admin(str(message.from_user.id))
    if is_admin_status:
        await state.update_data(username=message.text)
        user = await user_manager.get_user_by_username(message.text)
        if user:
            if user.role.value == 'admin':
                updated_user = await user_manager.update_user_role(user.user_id, 'user')
                if updated_user:
                    await message.answer('Роль пайдалануйшыга озгерди')
                else:
                    await message.answer('Кәте шикты')
            else:
                updated_user = await user_manager.update_user_role(user.user_id, 'admin')
                if updated_user:
                    await message.answer('Роль админга озгерди')
                else:
                    await message.answer('Кәте шикты')
        else:
            await message.answer("Бундай пайдалануйшы таулмады")
    else:
        await message.answer("Бундай команда жоқ")


# @router.message(F.content_type == 'contact')
# async def contact_handler(message: Message, state: FSMContext):
#     contact = message.contact
#     await state.update_data(phone_number=contact.phone_number)
#
#     data = await state.get_data()
#     await message.answer(f"{message.from_user.full_name}, Dawis bergen ushun rahmet!!!"
#                          f"\n\nTelefon nomer: {data.get('phone_number')}"
#                          f"\nTanlagan mektep: {data.get('selected_street')['name']}")

