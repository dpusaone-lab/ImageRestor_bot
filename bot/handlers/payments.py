from aiogram import Router
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(lambda c: c.data == "topup_balance")
async def handle_topup(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer("💳 Оплата скоро появится 🚧")
