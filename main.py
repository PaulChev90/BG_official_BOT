from aiogram import Bot, Dispatcher, executor, types
import json
import os

# Получаем токен бота из переменных окружения (безопасно для деплоя)
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Загружаем информацию о складах
with open('warehouses.json', 'r', encoding='utf-8') as f:
    warehouses = json.load(f)

# Получение списка федеральных округов
federal_districts = sorted(set(warehouse["federal_district"] for warehouse in warehouses))

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["📍 Список складов", "🔍 Поиск склада", "📞 Контакты", "ℹ️ О компании"]
    keyboard.add(*buttons)
    await message.answer(
        'Добро пожаловать в официальный бот компании «Би Джи»!'
        "Выберите нужный раздел:",
        reply_markup=keyboard
    )

@dp.message_handler(lambda message: message.text == "📍 Список складов")
async def list_districts(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for district in federal_districts:
        keyboard.add(district)
    keyboard.add("⬅️ Назад")
    await message.answer("Выберите федеральный округ:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text in federal_districts)
async def list_cities(message: types.Message):
    selected_district = message.text
    cities = sorted(set(
        warehouse["city"] for warehouse in warehouses if warehouse["federal_district"] == selected_district
    ))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for city in cities:
        keyboard.add(city)
    keyboard.add("⬅️ Назад")
    await message.answer(f"Выберите город в {selected_district}:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "⬅️ Назад")
async def go_back(message: types.Message):
    await start_handler(message)

@dp.message_handler(lambda message: message.text == "🔍 Поиск склада")
async def search_prompt(message: types.Message):
    await message.answer("Введите название города для поиска склада:")

@dp.message_handler(lambda message: message.text == "📞 Контакты")
async def show_contacts(message: types.Message):
    await message.answer(
        'Связаться с нами:'
        'Телефон: 8 800 222 24 12'
        'Email: info@bglogistic.ru'
        '[WhatsApp](https://wa.me/78002222412) | [Telegram](https://t.me/BGLogisticSupport)',
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

@dp.message_handler(lambda message: message.text == "ℹ️ О компании")
async def about_company(message: types.Message):
    await message.answer(
        "Компания «Би Джи» — ведущий оператор складской логистики в России.
"
        "У нас — сеть современных складов класса A и B в ключевых регионах страны.

"
        "Больше информации на сайте: https://bg-logistic.ru/"
    )

@dp.message_handler()
async def handle_city_or_search(message: types.Message):
    city_name = message.text.strip()
    matching_warehouses = [w for w in warehouses if w["city"].lower() == city_name.lower()]
    
    if matching_warehouses:
        for warehouse in matching_warehouses:
            await message.answer(
                f"**Склад в {warehouse['city']}:**

"
                f"**Адрес:** {warehouse['address']}
"
                f"**Телефон:** {warehouse['phone']}
"
                f"**Класс склада:** {warehouse['class']}
"
                f"**Вместимость:** {warehouse['capacity']}
"
                f"**Пропускная способность:** {warehouse['throughput']}
"
                f"**Температурный режим:** {warehouse['temperature']}
"
                f"**Парковка:** {warehouse['parking']}
"
                f"**Ж/д ветка:** {warehouse['railway']}

"
                f"[Схема проезда]({warehouse['map_link']})",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
    else:
        await message.answer("К сожалению, склад в этом городе не найден. Попробуйте ещё раз.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    
