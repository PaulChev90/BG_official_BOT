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
        'Добро пожаловать в официальный бот компании «Би Джи»! Выберите нужный раздел:',
        reply_markup=keyboard
    )

# Обработка команды "📍 Список складов"
@dp.message_handler(lambda message: message.text == "📍 Список складов")
async def list_districts(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for district in federal_districts:
        keyboard.add(district)
    keyboard.add("⬅️ Назад")
    await message.answer("Выберите федеральный округ:", reply_markup=keyboard)

# Обработка выбора федерального округа
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

# Обработка выбора города
@dp.message_handler(lambda message: message.text in [w['city'] for w in warehouses])
async def display_warehouse_info(message: types.Message):
    selected_city = message.text
    matching_warehouses = [w for w in warehouses if w["city"].lower() == selected_city.lower()]
    
    if matching_warehouses:
        for warehouse in matching_warehouses:
            await message.answer(
                f"**Склад в {warehouse['city']}:**\n"
                f"**Адрес:** {warehouse['address']}\n"
                f"**Телефон:** {warehouse['phone']}\n"
                f"**Класс склада:** {warehouse['class']}\n"
                f"**Вместимость:** {warehouse['capacity']}\n"
                f"**Пропускная способность:** {warehouse['throughput']}\n"
                f"**Температурный режим:** {warehouse['temperature']}\n"
                f"**Парковка:** {warehouse['parking']}\n"
                f"**Ж/д ветка:** {warehouse['railway']}\n"
                f"[Схема проезда]({warehouse['map_link']})",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
    else:
        await message.answer("К сожалению, склад в этом городе не найден. Попробуйте ещё раз.")

# Обработка команды "⬅️ Назад"
@dp.message_handler(lambda message: message.text == "⬅️ Назад")
async def go_back(message: types.Message):
    await start_handler(message)

# Обработка команды "🔍 Поиск склада"
@dp.message_handler(lambda message: message.text == "🔍 Поиск склада")
async def search_prompt(message: types.Message):
    await message.answer("Введите название города для поиска склада:")

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

# Если пользователь ввел данные, которые не соответствуют командам
@dp.message_handler()
async def handle_unrecognized_message(message: types.Message):
    # Проверим, является ли введенный текст названием города
    city_name = message.text.strip()
    matching_warehouses = [w for w in warehouses if w["city"].lower() == city_name.lower()]
    
    if matching_warehouses:
        for warehouse in matching_warehouses:
            await message.answer(
                f"**Склад в {warehouse['city']}:**\n"
                f"**Адрес:** {warehouse['address']}\n"
                f"**Телефон:** {warehouse['phone']}\n"
                f"**Класс склада:** {warehouse['class']}\n"
                f"**Вместимость:** {warehouse['capacity']}\n"
                f"**Пропускная способность:** {warehouse['throughput']}\n"
                f"**Температурный режим:** {warehouse['temperature']}\n"
                f"**Парковка:** {warehouse['parking']}\n"
                f"**Ж/д ветка:** {warehouse['railway']}\n"
                f"[Схема проезда]({warehouse['map_link']})",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
    else:
        await message.answer("К сожалению, склад в этом городе не найден. Попробуйте ещё раз.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
