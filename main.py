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

cities = sorted(set(warehouse["city"] for warehouse in warehouses))

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["📍 Список складов", "📞 Контакты", "ℹ️ О компании", "💬 FAQ"]
    keyboard.add(*buttons)
    await message.answer(
        'Добро пожаловать в официальный бот компании «Би Джи»!\nВыберите нужный раздел:',
        reply_markup=keyboard
    )

# Обработка команды "📍 Список складов"
@dp.message_handler(lambda message: message.text == "📍 Список складов")
async def list_cities(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for city in cities:
        keyboard.add(city)
    keyboard.add("⬅️ Назад")
    await message.answer("Выберите город:", reply_markup=keyboard)

# Обработка выбора города
@dp.message_handler(lambda message: message.text in cities)
async def list_warehouses(message: types.Message):
    selected_city = message.text
    warehouses_in_city = sorted(set(
        warehouse["name"] for warehouse in warehouses if warehouse["city"].lower() == selected_city.lower()
    ))
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for warehouse_name in warehouses_in_city:
        keyboard.add(warehouse_name)
    keyboard.add("⬅️ Назад")
    await message.answer(f"Выберите склад в городе {selected_city}:", reply_markup=keyboard)

# Обработка выбора склада и отображение информации о складе
@dp.message_handler(lambda message: message.text in [w['name'] for w in warehouses])
async def display_warehouse_info(message: types.Message):
    selected_warehouse_name = message.text
    matching_warehouses = [w for w in warehouses if w["name"].lower() == selected_warehouse_name.lower()]
    
    if matching_warehouses:
        for warehouse in matching_warehouses:
            response = f"**Склад {warehouse['name']} в {warehouse['city']}:**\n"
            response += f"**Адрес:** {warehouse.get('address', 'Не указано')}\n"
            response += f"**Телефон:** {warehouse.get('phone', 'Не указано')}\n"
            response += f"**Схема проезда:** [Ссылка]({warehouse.get('map_link', '')})\n"
            response += f"**Маршрут:** [Ссылка]({warehouse.get('route_link', '')})\n"

            # Добавляем кнопки с быстрыми действиями
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_phone = types.KeyboardButton("📞 Позвонить")
            button_route = types.KeyboardButton("🛣 Построить маршрут")
            keyboard.add(button_phone, button_route)
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

# Обработка команды "💬 FAQ"
@dp.message_handler(lambda message: message.text == "💬 FAQ")
async def faq(message: types.Message):
    await message.answer(
        "Часто задаваемые вопросы:\n"
        "1. Как найти ближайший склад?\n"
        "2. Какие типы складов существуют?\n"
        "3. Как забронировать склад?"
    )

# Обработка быстрого действия "📞 Позвонить"
@dp.message_handler(lambda message: message.text == "📞 Позвонить")
async def call_phone(message: types.Message):
    await message.answer("Позвоните по номеру: +7(800) 222-24-12")

# Обработка быстрого действия "🛣 Построить маршрут"
@dp.message_handler(lambda message: message.text == "🛣 Построить маршрут")
async def build_route(message: types.Message):
    # Для упрощения, просто покажем ссылку на построение маршрута (можно настроить динамически)
    warehouse_name = message.text.strip()
    matching_warehouses = [w for w in warehouses if w['name'] == warehouse_name]
    
    if matching_warehouses:
        warehouse = matching_warehouses[0]
        await message.answer(f"Построить маршрут для склада {warehouse['name']}: {warehouse['route_link']}")
    else:
        await message.answer("Ошибка при построении маршрута. Попробуйте еще раз.")

# Если пользователь ввел данные, которые не соответствуют командам
@dp.message_handler()
async def handle_unrecognized_message(message: types.Message):
    city_name = message.text.strip()
    matching_warehouses = [w for w in warehouses if w["city"].lower() == city_name.lower()]
    
    if matching_warehouses:
        for warehouse in matching_warehouses:
            response = f"**Склад в {warehouse['city']}:**\n"
            response += f"**Адрес:** {warehouse.get('address', 'Не указано')}\n"
            response += f"**Телефон:** {warehouse.get('phone', 'Не указано')}\n"
            response += f"**Схема проезда:** [Ссылка]({warehouse.get('map_link', '')})\n"
            response += f"**Маршрут:** [Ссылка]({warehouse.get('route_link', '')})"
            
            await message.answer(response, parse_mode="Markdown", disable_web_page_preview=True)
    else:
        await message.answer("К сожалению, склад в этом городе не найден. Попробуйте ещё раз.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
