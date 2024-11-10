from aiogram import Router, types, F
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
# from db import
from aiogram.filters.state import State, StatesGroup, StateFilter


router = Router()

@router.message(Command(commands=["start"]))
async def start_command(message: types.Message, state: FSMContext):
    await message.answer("Привет! Добро пожаловать в нашего бота с тестами! Вы согласны на сохранение данных?")