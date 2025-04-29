import os
import json
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook

# Получаем токен бота из переменных окружения (безопасно для деплоя)
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Загружаем информацию о складах
with open('warehouses.json', 'r', encoding='utf-8') as f:
    warehouses = json.load(f)

# Получение списка складов
warehouse_names = sorted(set(warehouse["name"] for warehouse in warehouses))

# Создаем Flask приложение для обработки запросов
app = Flask(__name__)

# URL для webhook
WEBHOOK_URL = f'https://{os.getenv("bg-official-bot.onrender.com")}/{BOT_TOKEN}'

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
async def handle_webhook():
    json_str = await request.get_data(as_text=True)
    update = types.Update(**json.loads(json_str))
    await dp.process_update(update)
    return "OK"


@app.route("/")
def index():
    return "Bot is running!"


# Обработка команды "📍 Список складов"
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["📍 Список складов", "📞 Контакты", "ℹ️ О компании"]
    keyboard.add(*buttons)
    await message.answer(
        'Добро пожаловать в официальный бот компании «Би Джи»!\nВыберите нужный раздел:',
        reply_markup=keyboard
    )

# Обработка команды "📍 Список складов"
@dp.message_handler(lambda message: message.text == "📍 Список складов")
async def list_warehouses(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for warehouse_name in warehouse_names:
        keyboard.add(warehouse_name)
    keyboard.add("⬅️ Назад")
    await message.answer("Выберите склад:", reply_markup=keyboard)

# Обработка выбора склада и отображение информации о складе
@dp.message_handler(lambda message: message.text in warehouse_names)
async def display_warehouse_info(message: types.Message):
    selected_warehouse_name = message.text
    matching_warehouses = [w for w in warehouses if w["name"].lower() == selected_warehouse_name.lower()]

    if matching_warehouses:
        for warehouse in matching_warehouses:
            response = f"**Склад {warehouse['name']}:**\n"
            response += f"**Адрес:** {warehouse.get('address', 'Не указано')}\n"
            response += f"**Телефон:** {warehouse.get('phone', 'Не указано')}\n"
            
            # Формирование ссылок для Яндекс Навигатора с использованием координат
            lat = warehouse['latitude']
            lon = warehouse['longitude']
            
            # Ссылка на маршрут в Яндекс Картах
            route_url = f"https://yandex.ru/maps/?rtext=~{lat},{lon}"
            response += f"**Маршрут:** [Показать маршрут]({route_url})\n"

            # Добавляем кнопку "⬅️ Назад"
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add("⬅️ Назад")

            await message.answer(response, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await message.answer("К сожалению, склад с таким названием не найден. Попробуйте ещё раз.")

# Обработка команды "⬅️ Назад"
@dp.message_handler(lambda message: message.text == "⬅️ Назад")
async def go_back(message: types.Message):
    await start_handler(message)

# Обработка команды "📞 Контакты"
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

# Обработка команды "ℹ️ О компании"
@dp.message_handler(lambda message: message.text == "ℹ️ О компании")
async def about_company(message: types.Message):
    await message.answer(
        'Компания «Би Джи» — мы храним доверие!\n'
        'У нас — сеть современных складов класса A и B в ключевых регионах страны.\n'
        'Больше информации на сайте: https://bg-logistic.ru/'
    )


# Настройка webhook для бота
async def on_start():
    # Настройка webhook
    await bot.set_webhook(WEBHOOK_URL)


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=f'/{BOT_TOKEN}',
        on_startup=on_startup,
        host='0.0.0.0',
        port=10000
    )
