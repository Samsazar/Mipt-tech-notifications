"""
Создание и использование базы данных
"""
from datetime import datetime

import aiosqlite


class User:
    """
    Класс пользователя, с которым удобно взаимодействовать благодаря полям
    """
    def __init__(self, user_id: int, telegram_id: int, user_name: str, login: str, password: str):
        self.user_id = user_id
        self.telegram_id = telegram_id
        self.user_name = user_name
        self.login = login
        self.password = password


class Notification:
    """
    Класс пользователя, с которым удобно взаимодействовать благодаря полям
    """
    def __init__(self, notification_id: int, user_id: int, start_time: datetime, end_time: datetime):
        self.notification_id = notification_id
        self.user_id = user_id
        self.start_time = start_time
        self.end_time = end_time


async def init_db():
    """
    Инициализация базы данных
    """
    async with aiosqlite.connect('notifications_bot.db') as conn:
        # Создаем курсор для выполнения SQL-запросов
        cursor = await conn.cursor()

        await cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            user_name TEXT NOT NULL,
            login TEXT NOT NULL,
            password TEXT NOT NULL
        )
        ''')

        await cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (            
            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            start_time DATETIME,
            end_time DATETIME
        )
        ''')
        # Сохраняем изменения
        await conn.commit()


async def add_user(telegram_id: int, user_name: str, login: str, password: str) -> int:
    """
    Добавление пользователя
    Возвращает присвоенный пользователю id
    """
    async with aiosqlite.connect('notifications_bot.db') as conn:
        cursor = await conn.cursor()

        # Выполняем SQL-запрос для добавления нового ответа
        await cursor.execute('''
        INSERT INTO users (telegram_id, user_name, login, password)
        VALUES (?, ?, ?, ?)
        ''', (telegram_id, user_name, login, password))

        # Сохраняем изменения
        await conn.commit()

        user_id = cursor.lastrowid

    print("Пользователь успешно добавлен.")
    return user_id


async def add_notification(user_id: int, start_time: datetime, end_time: datetime) -> int:
    """
    Добавляет уведомление
    """
    async with aiosqlite.connect('notifications_bot.db') as conn:
        cursor = await conn.cursor()

        # Выполняем SQL-запрос для добавления нового ответа
        await cursor.execute('''
        INSERT INTO notifications (user_id, start_time, end_time)
        VALUES (?, ?, ?)
        ''', (user_id, start_time, end_time))

        # Сохраняем изменения
        await conn.commit()

        notification_id = cursor.lastrowid

    print("Напоминание успешно добавлено.")
    return notification_id


async def get_user_by_telegram_id(telegram_id: int) -> User:
    """
    Возвращает объект User по telegram_id
    """
    async with aiosqlite.connect('notifications_bot.db') as conn:
        cursor = await conn.cursor()

        # Выполняем SQL-запрос для получения опроса по названию
        await cursor.execute('''
        SELECT user_id, user_name, login, password
        FROM users
        WHERE telegram_id = ?
        ''', (telegram_id,))

        # Получаем результат запроса
        raw_user = await cursor.fetchone()
    if not raw_user:
        return False
    user = User(raw_user[0], telegram_id, raw_user[1], raw_user[2], raw_user[3])
    return user


async def get_notifications_by_user_id(user_id: int) -> list:
    """
    Возвращает объект Notification по user_id
    """
    async with aiosqlite.connect('notifications_bot.db') as conn:
        cursor = await conn.cursor()

        # Выполняем SQL-запрос для получения опроса по названию
        await cursor.execute('''
        SELECT notification_id, start_time, end_time
        FROM notifications
        WHERE user_id = ?
        ''', (user_id,))

        # Получаем результат запроса
        raw_notifications = await cursor.fetchall()
    notifications = []
    for elem in raw_notifications:
        notifications.append(Notification(elem[0], user_id, elem[1], elem[2]))
    return notifications


async def delete_notification_by_id(notification_id: int) -> list:
    """
    Удаляет запись уведомления по его id
    """
    async with aiosqlite.connect('notifications_bot.db') as conn:
        cursor = await conn.cursor()

        # Выполняем SQL-запрос для получения опроса по названию
        await cursor.execute('''
        DELETE
        FROM notifications
        WHERE notification_id = ?
        ''', (notification_id,))

        # Сохраняем изменения
        await conn.commit()

        # Получаем результат запроса
        data = await cursor.fetchone()

    return data
