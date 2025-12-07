import asyncio
from typing import Optional

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)
from aiogram.filters import CommandStart, Command

from app.config import BOT_TOKEN, BOT_USERNAME, WEBAPP_URL
from app.db import (
    get_user,
    set_user_referred_by,
    add_referral,
    reward_user_for_referral,
)
from app.rating import level_from_xp, rank_name_from_level


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Открыть Traffic Panda",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ]
        ]
    )


async def handle_start(message: Message):
    # /start или /start <ref_id>
    ref_id: Optional[int] = None
    if message.text and " " in message.text:
        try:
            ref_id = int(message.text.split(maxsplit=1)[1])
        except ValueError:
            ref_id = None

    user = await get_user(message.from_user.id, message.from_user.username)

    # Реферальная логика
    if ref_id and ref_id != user.user_id and not user.referred_by:
        await set_user_referred_by(user.user_id, ref_id)
        await add_referral(ref_id, user.user_id)
        await reward_user_for_referral(ref_id)

    text = (
        f"🐼 Привет, {message.from_user.full_name}!\n\n"
        f"Это Traffic Panda — мини-игра и обучение арбитражу трафика.\n\n"
        f"Текущий статус: <b>{user.rank_name}</b>\n"
        f"Уровень: <b>{user.level}</b>\n"
        f"XP: <b>{user.xp}</b>\n"
        f"Баланс: <b>{user.coins}</b> 🪙\n"
        f"Доход в час: <b>{user.hourly_income}</b> 🪙\n\n"
        f"Нажми кнопку ниже, чтобы открыть мини-приложение 👇"
    )

    await message.answer(text, reply_markup=main_menu_kb())


async def handle_menu(message: Message):
    user = await get_user(message.from_user.id, message.from_user.username)
    text = (
        f"🐼 Твой профиль:\n\n"
        f"Статус: <b>{user.rank_name}</b>\n"
        f"Уровень: <b>{user.level}</b>\n"
        f"XP: <b>{user.xp}</b>\n"
        f"Баланс: <b>{user.coins}</b> 🪙\n"
        f"Доход в час: <b>{user.hourly_income}</b> 🪙\n\n"
        f"Открыть мини-игру можно по кнопке:"
    )
    await message.answer(text, reply_markup=main_menu_kb())


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set in .env")

    bot = Bot(
        BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    dp.message.register(handle_start, CommandStart())
    dp.message.register(handle_menu, Command("menu"))

    print("✅ TrafficPanda bot started (polling)")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
