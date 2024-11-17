"""
Главный файл проекта
"""
from src import db

import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from src.handlers import router

import os
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)


async def set_commands(bot: Bot):
    """
    Объявление команд бота
    """
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/instruction", description="Узнать о работе бота"),
        BotCommand(command="/login", description="Войти"),
        BotCommand(command="/update", description="Обновить информацию"),
        BotCommand(command="/notifications", description="Напоминания"),
        BotCommand(command="/delete", description="Удалить напоминание"),
    ]
    await bot.set_my_commands(commands)

async def main():
    """
    Запуск бота
    """
    bot = Bot(token=API_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    await db.init_db()
    await set_commands(bot)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.close()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
