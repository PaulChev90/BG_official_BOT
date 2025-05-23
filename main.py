import os
import json
from aiogram import Bot, Dispatcher, types, executor

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не установлена")

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Загрузка данных о складах
with open('warehouses.json', 'r', encoding='utf-8') as f:
    warehouses = json.load(f)

warehouse_names = sorted(set(warehouse["name"] for warehouse in warehouses))

# Обработка команды /start
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["📍 Список складов", "📞 Контакты", "ℹ️ О компании"]
    keyboard.add(*buttons)
    await message.answer(
        'Добро пожаловать в официальный бот компании «Би Джи»!\nВыберите нужный раздел:',
        reply_markup=keyboard
    )

# Список складов
@dp.message_handler(lambda message: message.text == "📍 Список складов")
async def list_warehouses(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in warehouse_names:
        keyboard.add(name)
    keyboard.add("⬅️ Назад")
    await message.answer("Выберите склад:", reply_markup=keyboard)

# Информация по складу
@dp.message_handler(lambda message: message.text in warehouse_names)
async def display_warehouse_info(message: types.Message):
    selected = message.text
    matches = [w for w in warehouses if w["name"].lower() == selected.lower()]

    if matches:
        for warehouse in matches:
            lat = warehouse.get("latitude")
            lon = warehouse.get("longitude")
            route_url = f"https://yandex.ru/maps/?rtext=~{lat},{lon}"

            response = (
                f"*Склад {warehouse['name']}*\n"
                f"*Адрес:* {warehouse.get('address', 'Не указано')}\n"
                f"*Телефон:* {warehouse.get('phone', 'Не указано')}\n"
                f"[Показать маршрут]({route_url})"
            )

            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add("⬅️ Назад")
            await message.answer(response, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await message.answer("Склад не найден. Попробуйте снова.")

# Кнопка "Назад"
@dp.message_handler(lambda message: message.text == "⬅️ Назад")
async def go_back(message: types.Message):
    await start_handler(message)

# Контакты
@dp.message_handler(lambda message: message.text == "📞 Контакты")
async def show_contacts(message: types.Message):
    await message.answer(
        'Связаться с нами:\n'
        'Телефон: 8 800 222 24 12\n'
        'Email: info@bglogistic.ru\n'
        '[WhatsApp](https://wa.me/78002222412) | [Telegram](https://t.me/BGLogisticSupport)',
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# О компании
@dp.message_handler(lambda message: message.text == "ℹ️ О компании")
async def about_company(message: types.Message):
    await message.answer(
        'Компания «Би Джи» — мы храним доверие!\n'
        'Сеть современных складов класса A и B в ключевых регионах страны.\n'
        'Сайт: https://bg-logistic.ru/'
    )

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
