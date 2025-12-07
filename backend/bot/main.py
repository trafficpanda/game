import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.config import BOT_TOKEN

async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    print("✅ Bot started (polling skeleton)")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
