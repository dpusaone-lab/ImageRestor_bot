from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏠 Меню"), KeyboardButton(text="💳 Баланс")],
        [KeyboardButton(text="👨‍💻 О разработчике"), KeyboardButton(text="🖼 Примеры")],
    ],
    resize_keyboard=True,
)
