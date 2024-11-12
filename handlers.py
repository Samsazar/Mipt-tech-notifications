import asyncio
from datetime import datetime
from operator import index

import aiogram.methods.send_message
from aiogram import Router, types, F
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters.state import State, StatesGroup, StateFilter

from db import add_user, get_user_by_telegram_id, add_notification, delete_notification_by_id, \
    get_notifications_by_user_id
from api import get_last_washing, check_correct_login

router = Router()

class AddNotificationState(StatesGroup):
    datetime_state = State()


class LoginState(StatesGroup):
    login_state = State()
    password_state = State()


class DeleteState(StatesGroup):
    notification_id_state = State()

months = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
          "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"]

@router.message(Command(commands=["start"]))
async def start_command(message: types.Message, state: FSMContext):
    # print(message.chat.id)
    await message.answer("Привет, для начала напиши /instruction и войди в свой аккаунт на mipt.tech")


@router.message(Command(commands=["instruction"]))
async def instruction_command(message: types.Message, state: FSMContext):
    # print(message.chat.id)
    await message.answer("- Для начала необходимо войти через бота в свой аккаунт на mipt.tech."
                         "Для этого введи команду /login\n"
                         "- Далее вы можете обновить информацию о своих предстоящих стирках"
                         " и добавить их в напоминания. Для этого введи команду /update\n"
                         "- Чтобы увидеть свои напоминания, напиши команду /notifications\n"
                         "- Для удаления напоминаний существует команда /delete\n")


@router.message(Command(commands=["login"]))
async def login_command(message: types.Message, state: FSMContext):
    print(await get_user_by_telegram_id(message.chat.id))
    if await get_user_by_telegram_id(message.chat.id):
        await message.answer("Вы уже вошли в свой аккаунт")
        return
    await state.set_state(LoginState.login_state)
    await message.answer("Введите ваш логин от mipt.tech (он рядом со значком студсовета)")


@router.message(StateFilter(LoginState.login_state))
async def login_input_command(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Введите текст, пожалуйста")
        return
    input_login = message.text
    if input_login[0] == "@":
        input_login = input_login[1:]
    await state.update_data(login=input_login)
    await state.set_state(LoginState.password_state)
    await message.answer("Введите ваш пароль от аккаунта на mipt.tech")


@router.message(StateFilter(LoginState.password_state))
async def password_input_command(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Введите текст, пожалуйста")
        return
    data = await state.get_data()
    telegram_id = message.chat.id
    user_name = message.chat.first_name
    login = data["login"]
    password = message.text

    correct = check_correct_login(login, password)
    print(correct)
    if correct:
        await add_user(telegram_id, user_name, login, password)
        await message.answer("Вы вошли! Теперь обновите информацию, чтобы мы добавили напоминание")
    else:
        await message.answer("Данные введены неверно, повторите вход с помощью /login")
    await state.clear()


@router.message(Command(commands=["update"]))
async def update_command(message: types.Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.chat.id)

    if not user:
        await message.answer("Для начала войдите в свой аккаунт через команду /login")
        return

    data = get_last_washing(user.login, user.password)

    records = ""
    for i in range(1, 10):
        start_time = datetime.strptime(data[-i]["start_time"], '%Y-%m-%dT%H:%M:%S+03:00')
        end_time = datetime.strptime(data[-i]["end_time"], '%Y-%m-%dT%H:%M:%S+03:00')
        if not (end_time.timestamp() >= datetime.now().timestamp()):
            break
        records += (f"\n{i}. {start_time.day} {months[start_time.month - 1]} с "
                    f"{start_time.isoformat(timespec='minutes')[-5:]} до "
                    f"{end_time.isoformat(timespec='minutes')[-5:]}")
    if not records:
        await message.answer(f"Ни одна стиралка вами не забронирована")
        return
        # notification_id = await add_notification(user.user_id, start_time, end_time)
    # print(start_time.date())
    # 2024-11-06T22:00:00+03:00
    await state.set_state(AddNotificationState.datetime_state)
    await message.answer(f"Последние брони {records}\n\nВведите номер брони, которую хотите "
                         f"добавить в напоминания или введите \"0\", чтобы отменить добавление")


@router.message(StateFilter(AddNotificationState.datetime_state))
async def add_command(message: types.Message, state: FSMContext):
    if not (message.text and message.text.isdigit()):
        await message.answer("Введите номер необходимой брони")
        return
    user = await get_user_by_telegram_id(message.chat.id)
    data = get_last_washing(user.login, user.password)
    add_notification_id = int(message.text)
    if add_notification_id not in range(0, 6):
        await message.answer("Введите номер из заданного диапазона от 1 до 5, "
                             "чтобы добавить бронь, или 0, чтобы отменить")
        return
    if add_notification_id == 0:
        await message.answer("Отмена добавления напоминания")
        await state.clear()
        return
    start_time = datetime.strptime(data[-add_notification_id]["start_time"],
                                   '%Y-%m-%dT%H:%M:%S+03:00')
    end_time = datetime.strptime(data[-add_notification_id]["end_time"], '%Y-%m-%dT%H:%M:%S+03:00')
    notification_id = await add_notification(user.user_id, start_time, end_time)
    await state.clear()
    await message.answer("Напоминание на данную бронь создано!")


@router.message(Command(commands=["notifications"]))
async def notifications_command(message: types.Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.chat.id)
    if not user:
        await message.answer("Для начала войдите в свой аккаунт через команду /login")
        return

    notifications = await get_notifications_by_user_id(user.user_id)
    if not notifications:
        await message.answer("Напоминания еще не созданы")
        return

    record = ""
    for i in range(len(notifications)):
        start_date = datetime.strptime(notifications[i].start_time, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(notifications[i].end_time, "%Y-%m-%d %H:%M:%S")
        record += (f"\n{i+1}. {start_date.day} {months[start_date.month - 1]} с "
                   f"{start_date.isoformat(timespec='minutes')[-5:]} до "
                   f"{end_date.isoformat(timespec='minutes')[-5:]}")
    await message.answer(f"Ваши стиралки забронированы на: {record}")


@router.message(Command(commands=["delete"]))
async def request_to_delete_notification(message: types.Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer(f"Для начала войдите в свой аккаунт через /login")
        return
    # print()
    if not await get_notifications_by_user_id(user.user_id):
        await message.answer(f"Напоминаний нет. Для создания обновите "
                             f"данные с помощью команды /update")
        return

    await state.set_state(DeleteState.notification_id_state)
    await notifications_command(message, state)
    await asyncio.sleep(0.5)
    await message.answer("Введите номер напоминания, которое вы хотите удалить")


@router.message(StateFilter(DeleteState.notification_id_state))
async def delete_notification(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(f"Напишите число")
        return

    user = await get_user_by_telegram_id(message.chat.id)
    notifications = await get_notifications_by_user_id(user.user_id)

    if not (int(message.text)) in range(1, len(notifications)+1):
        await message.answer(f"Напоминания {message.text} не существует, "
                             f"напишите /delete, чтобы повторить")
    else:
        deleted_notification = await (
            delete_notification_by_id(notifications[int(message.text) - 1].notification_id))
        await message.answer(f"Напоминание {message.text} удалено")
    await state.clear()