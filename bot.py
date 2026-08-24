import asyncio
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8907280859:AAEriDRe-qnERxgbCwbkGaOfwwKSBO0UaL4"  # Вставь свой токен

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилище данных
users_data = {}
partners = {}
partner_requests = {}

# Главная клавиатура
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💑 Дни вместе")],
        [KeyboardButton(text="📅 Установить дату")],
        [KeyboardButton(text="⏳ Дней до события")],
        [KeyboardButton(text="👥 Партнёр")],
    ],
    resize_keyboard=True
)

# Клавиатура партнёра
partner_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💑 Наша пара")],
        [KeyboardButton(text="📅 Наша дата")],
        [KeyboardButton(text="💌 Отправить сообщение")],
        [KeyboardButton(text="❌ Отвязать партнёра")],
        [KeyboardButton(text="⬅️ Назад")],
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start(message: types.Message):
    user_name = message.from_user.first_name
    await message.answer(
        f"💖 Привет, {user_name}!\n\n"
        f"Я бот-счётчик для влюблённых!\n\n"
        f"Я умею:\n"
        f"💑 Считать сколько дней вы вместе\n"
        f"📅 Устанавливать важные даты\n"
        f"⏳ Считать дни до событий\n"
        f"👥 Привязывать партнёра\n\n"
        f"Выбери действие:",
        reply_markup=main_kb
    )

# Установить дату начала отношений
@dp.message(F.text == "📅 Установить дату")
async def set_date(message: types.Message):
    await message.answer(
        "Введи дату начала отношений в формате:\n"
        "ДД.ММ.ГГГГ\n\n"
        "Например: 14.02.2024\n\n"
        "Или нажми /отмена для отмены"
    )
    users_data[message.from_user.id] = users_data.get(message.from_user.id, {})
    users_data[message.from_user.id]["waiting_for_date"] = True

# Обработка даты
@dp.message(F.text.regexp(r"^\d{2}\.\d{2}\.\d{4}$"))
async def handle_date(message: types.Message):
    user_id = message.from_user.id
    
    # Проверяем, ждём ли дату
    if users_data.get(user_id, {}).get("waiting_for_date"):
        try:
            date_str = message.text
            date_obj = datetime.strptime(date_str, "%d.%m.%Y")
            
            users_data[user_id]["start_date"] = date_obj
            users_data[user_id]["waiting_for_date"] = False
            
            days = (datetime.now() - date_obj).days
            
            await message.answer(
                f"✅ Дата установлена: {date_str}\n"
                f"💑 Вы вместе: {days} дней!\n\n"
                f"Если у тебя есть партнёр, он тоже увидит эту дату!"
            )
            
            # Если есть партнёр, отправляем ему уведомление
            if user_id in partners:
                partner_id = partners[user_id]
                users_data[partner_id] = users_data.get(partner_id, {})
                users_data[partner_id]["start_date"] = date_obj
                
                await bot.send_message(
                    partner_id,
                    f"🔔 {message.from_user.first_name} установил(а) дату начала отношений: {date_str}\n"
                    f"💑 Вы вместе: {days} дней!"
                )
        except:
            await message.answer("❌ Неверный формат даты!")
    
    # Если ждём дату события
    elif users_data.get(user_id, {}).get("waiting_for_event"):
        try:
            date_str = message.text
            date_obj = datetime.strptime(date_str, "%d.%m.%Y")
            
            users_data[user_id]["waiting_for_event"] = False
            
            days = (date_obj - datetime.now()).days
            
            if days > 0:
                await message.answer(
                    f"⏳ До события осталось: {days} дней!\n"
                    f"📅 Дата: {date_str}"
                )
            elif days == 0:
                await message.answer("🎉 Это сегодня! Поздравляю!")
            else:
                await message.answer(
                    f"📅 Это было {abs(days)} дней назад"
                )
        except:
            await message.answer("❌ Неверный формат даты!")

# Показать дни вместе
@dp.message(F.text == "💑 Дни вместе")
async def days_together(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in users_data or "start_date" not in users_data[user_id]:
        await message.answer(
            "❌ Дата не установлена!\n"
            "Нажми «📅 Установить дату»"
        )
        return
    
    start_date = users_data[user_id]["start_date"]
    days = (datetime.now() - start_date).days
    
    # Красивый вывод
    years = days // 365
    months = (days % 365) // 30
    remaining_days = (days % 365) % 30
    
    await message.answer(
        f"💑 **Вы вместе:**\n\n"
        f"📅 С: {start_date.strftime('%d.%m.%Y')}\n"
        f"⏳ Дней: {days}\n"
        f"🗓 Это: {years} г. {months} мес. {remaining_days} дн.\n\n"
        f"💖 Любите друг друга!"
    )

# Дней до события
@dp.message(F.text == "⏳ Дней до события")
async def days_until(message: types.Message):
    await message.answer(
        "Введи дату события в формате:\n"
        "ДД.ММ.ГГГГ\n\n"
        "Например: 31.12.2024"
    )
    users_data[message.from_user.id] = users_data.get(message.from_user.id, {})
    users_data[message.from_user.id]["waiting_for_event"] = True

# 👥 Партнёр
@dp.message(F.text == "👥 Партнёр")
async def partner_menu(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in partners:
        partner_id = partners[user_id]
        partner_name = users_data.get(partner_id, {}).get("name", "Неизвестно")
        
        await message.answer(
            f"💑 Твой партнёр: {partner_name}\n\n"
            f"Выбери действие:",
            reply_markup=partner_kb
        )
    else:
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Привязать партнёра", callback_data="link_partner")],
            [InlineKeyboardButton(text="ℹ️ Как это работает", callback_data="partner_info")],
        ])
        
        await message.answer(
            "👥 **Партнёр**\n\n"
            "Привяжи свою вторую половинку, чтобы:\n"
            "💑 Считать дни вместе\n"
            "📅 Делиться важными датами\n"
            "💌 Отправлять сообщения\n\n"
            "Выбери действие:",
            reply_markup=inline_kb
        )

# Информация о привязке
@dp.callback_query(F.data == "partner_info")
async def partner_info(callback: types.CallbackQuery):
    await callback.message.answer(
        "ℹ️ **Как привязать партнёра:**\n\n"
        "1️⃣ Нажми «Привязать партнёра»\n"
        "2️⃣ Получи код\n"
        "3️⃣ Отправь код партнёру\n"
        "4️⃣ Партнёр вводит команду:\n"
        "`/connect КОД`\n\n"
        "После этого вы будете связаны!"
    )

# Начать привязку
@dp.callback_query(F.data == "link_partner")
async def link_partner_start(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    code = random.randint(100000, 999999)
    partner_requests[user_id] = {
        "code": code,
        "timestamp": datetime.now()
    }
    
    await callback.message.answer(
        f"🔗 **Привязка партнёра**\n\n"
        f"1️⃣ Отправь партнёру этот код: `{code}`\n"
        f"2️⃣ Партнёр должен ввести:\n"
        f"`/connect {code}`\n\n"
        f"⏰ Код действителен 10 минут!"
    )

# Подключение по коду
@dp.message(Command("connect"))
async def connect_partner(message: types.Message):
    user_id = message.from_user.id
    
    try:
        code = int(message.text.split()[1])
        
        for partner_id, data in partner_requests.items():
            if data["code"] == code:
                time_diff = datetime.now() - data["timestamp"]
                if time_diff.seconds > 600:
                    await message.answer("❌ Код истёк! Попроси новый.")
                    return
                
                # Привязываем партнёров
                partners[user_id] = partner_id
                partners[partner_id] = user_id
                
                # Сохраняем имена
                users_data[user_id] = users_data.get(user_id, {})
                users_data[user_id]["name"] = message.from_user.first_name
                
                users_data[partner_id] = users_data.get(partner_id, {})
                users_data[partner_id]["name"] = users_data.get(partner_id, {}).get("name", "Партнёр")
                
                # Если у кого-то уже установлена дата, синхронизируем
                if "start_date" in users_data[user_id]:
                    users_data[partner_id]["start_date"] = users_data[user_id]["start_date"]
                elif "start_date" in users_data[partner_id]:
                    users_data[user_id]["start_date"] = users_data[partner_id]["start_date"]
                
                del partner_requests[partner_id]
                
                await message.answer(
                    f"✅ Вы успешно привязаны!\n"
                    f"💑 Теперь вы пара!",
                    reply_markup=partner_kb
                )
                
                await bot.send_message(
                    partner_id,
                    f"💑 {message.from_user.first_name} привязался(ась) к тебе!\n"
                    f"Теперь вы пара!",
                    reply_markup=partner_kb
                )
                
                return
        
        await message.answer("❌ Неверный код или он уже использован!")
    
    except:
        await message.answer(
            "❌ Используй формат:\n"
            "`/connect КОД`\n\n"
            "Например: `/connect 123456`"
        )

# 💑 Наша пара
@dp.message(F.text == "💑 Наша пара")
async def our_pair(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in partners:
        await message.answer("❌ У тебя нет партнёра!")
        return
    
    partner_id = partners[user_id]
    partner_name = users_data.get(partner_id, {}).get("name", "Неизвестно")
    
    # Если есть дата, показываем дни
    if "start_date" in users_data.get(user_id, {}):
        start_date = users_data[user_id]["start_date"]
        days = (datetime.now() - start_date).days
        
        years = days // 365
        months = (days % 365) // 30
        remaining_days = (days % 365) % 30
        
        await message.answer(
            f"💑 **Ваша пара**\n\n"
            f"👤 Ты: {message.from_user.first_name}\n"
            f"👤 Партнёр: {partner_name}\n"
            f"📅 Вместе с: {start_date.strftime('%d.%m.%Y')}\n"
            f"⏳ Дней вместе: {days}\n"
            f"🗓 Это: {years} г. {months} мес. {remaining_days} дн.\n\n"
            f"💖 Любовь — это прекрасно!"
        )
    else:
        await message.answer(
            f"💑 **Ваша пара**\n\n"
            f"👤 Ты: {message.from_user.first_name}\n"
            f"👤 Партнёр: {partner_name}\n\n"
            f"Установите дату начала отношений!\n"
            f"Нажми «📅 Установить дату»"
        )

# 📅 Наша дата
@dp.message(F.text == "📅 Наша дата")
async def our_date(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in partners:
        await message.answer("❌ У тебя нет партнёра!")
        return
    
    if "start_date" in users_data.get(user_id, {}):
        start_date = users_data[user_id]["start_date"]
        days = (datetime.now() - start_date).days
        
        await message.answer(
            f"📅 **Дата начала отношений:**\n\n"
            f"📅 День: {start_date.strftime('%d.%m.%Y')}\n"
            f"⏳ Прошло дней: {days}\n\n"
            f"Следующая годовщина:\n"
            f"🎉 Через {365 - (days % 365)} дней!"
        )
    else:
        await message.answer(
            "❌ Дата не установлена!\n"
            "Нажми «📅 Установить дату»"
        )

# 💌 Отправить сообщение партнёру
@dp.message(F.text == "💌 Отправить сообщение")
async def send_message_to_partner(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in partners:
        await message.answer("❌ У тебя нет партнёра!")
        return
    
    await message.answer(
        "💌 Напиши сообщение для партнёра:\n"
        "(просто отправь текст следующим сообщением)"
    )
    
    users_data[user_id]["waiting_for_partner_message"] = True

# Обработка сообщений партнёру
@dp.message(F.text)
async def handle_messages(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    
    # Если ждём сообщение для партнёра
    if users_data.get(user_id, {}).get("waiting_for_partner_message"):
        partner_id = partners.get(user_id)
        
        if partner_id:
            await bot.send_message(
                partner_id,
                f"💌 **Сообщение от партнёра:**\n\n"
                f"«{text}»\n\n"
                f"— {message.from_user.first_name}"
            )
            
            await message.answer("✅ Сообщение отправлено партнёру!")
            users_data[user_id]["waiting_for_partner_message"] = False
            return

# ❌ Отвязать партнёра
@dp.message(F.text == "❌ Отвязать партнёра")
async def unlink_partner(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in partners:
        await message.answer("❌ У тебя нет партнёра!")
        return
    
    partner_id = partners[user_id]
    
    del partners[user_id]
    del partners[partner_id]
    
    await message.answer("❌ Вы отвязаны от партнёра.", reply_markup=main_kb)
    
    await bot.send_message(
        partner_id,
        "❌ Твой партнёр отвязался. Вы больше не пара.",
        reply_markup=main_kb
    )

# ⬅️ Назад
@dp.message(F.text == "⬅️ Назад")
async def back_to_main(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_kb)

# Отмена
@dp.message(Command("отмена"))
async def cancel(message: types.Message):
    user_id = message.from_user.id
    if user_id in users_data:
        users_data[user_id]["waiting_for_date"] = False
        users_data[user_id]["waiting_for_event"] = False
        users_data[user_id]["waiting_for_partner_message"] = False
    await message.answer("✅ Действие отменено", reply_markup=main_kb)

async def main():
    print("🤖 Бот-счётчик запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
