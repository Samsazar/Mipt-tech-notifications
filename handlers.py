from aiogram import Router, types, F
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters.state import State, StatesGroup, StateFilter

# from db import
from api import get_last_washing

router = Router()

class LoginState(StatesGroup):
    login_state = State()
    password_state = State()

@router.message(Command(commands=["start"]))
async def start_command(message: types.Message, state: FSMContext):
    await message.answer("Привет, для начала напиши /login и войди в свой аккаунт на mipt.tech")

@router.message(Command(commands=["login"]))
async def login_command(message: types.Message, state: FSMContext):
    await state.set_state(LoginState.login_state)
    await message.answer("Введите ваш логин")

@router.message(StateFilter(LoginState.login_state))
async def login_input_command(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await state.set_state(LoginState.password_state)
    await message.answer("Введите ваш пароль")


@router.message(StateFilter(LoginState.password_state))
async def password_input_command(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # set_user_login(data["login"], message.text)
    await state.clear()
    await message.answer("Вы вошли! Теперь обновите информацию, чтобы мы добавили напоминание")



@router.message(Command(commands=["update"]))
async def update_command(message: types.Message, state: FSMContext):
    data = get_last_washing("", "")
    await message.answer(f"{data[-1]["id"]}")
