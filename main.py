import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL", "https://your-bot.onrender.com")  # Render сам создаёт эту переменную
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

with open('warehouses.json', 'r', encoding='utf-8') as f:
    warehouses = json.load(f)

warehouse_names = sorted(set(warehouse["name"] for warehouse in warehouses))

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["📍 Список складов", "📞 Контакты", "ℹ️ О компании"]
    keyboard.add(*buttons)
    await message.answer(
        'Добро пожаловать в официальный бот компании «Би Джи»!\nВыберите нужный раздел:',
        reply_markup=keyboard
    )

@dp.message_handler(lambda message: message.text == "📍 Список складов")
async def list_warehouses(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for warehouse_name in warehouse_names:
        keyboard.add(warehouse_name)
    keyboard.add("⬅️ Назад")
    await message.answer("Выберите склад:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text in warehouse_names)
async def display_warehouse_info(message: types.Message):
    selected_warehouse_name = message.text
    matching_warehouses = [w for w in warehouses if w["name"].lower() == selected_warehouse_name.lower()]

    if matching_warehouses:
        for warehouse in matching_warehouses:
            response = f"**Склад {warehouse['name']}:**\n"
            response += f"**Адрес:** {warehouse.get('address', 'Не указано')}\n"
            response += f"**Телефон:** {warehouse.get('phone', 'Не указано')}\n"
            lat = warehouse['latitude']
            lon = warehouse['longitude']
            route_url = f"https://yandex.ru/maps/?rtext=~{lat},{lon}"
            response += f"**Маршрут:** [Показать маршрут]({route_url})\n"

            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add("⬅️ Назад")

            await message.answer(response, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await message.answer("К сожалению, склад с таким названием не найден. Попробуйте ещё раз.")

@dp.message_handler(lambda message: message.text == "⬅️ Назад")
async def go_back(message: types.Message):
    await start_handler(message)

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

@dp.message_handler(lambda message: message.text == "ℹ️ О компании")
async def about_company(message: types.Message):
    await message.answer(
        'Компания «Би Джи» — мы храним доверие!\n'
        'У нас — сеть современных складов класса A и B в ключевых регионах страны.\n'
        'Больше информации на сайте: https://bg-logistic.ru/'
    )

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )
