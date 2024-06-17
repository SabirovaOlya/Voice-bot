from aiogram.utils.keyboard import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton


def send_contact_keyboard():
    contact_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Telefon nomer jiberiw", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    return contact_keyboard

