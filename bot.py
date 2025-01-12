start
from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram import F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
import asyncio
from datetime import datetime, timedelta
import requests





# Токен бота
TOKEN = "7311925613:AAEozZhlP1th7_X3LRJS_7lo3jsjy4ALHfE"
DB_URI ="postgresql://postgres:CytrXtfYkeOEPafHduRqrWpGbsDyYTRK@postgres.railway.internal:5432/railway"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()
# Ссылки на спонсоров
SPONSORS = [
    "https://t.me/+ZWDMAtOj1c5jN2Jk",
    "https://t.me/+ZWDMAtOj1c5jN2Jk",
    "https://t.me/+ZWDMAtOj1c5jN2Jk",
    "https://t.me/+ZWDMAtOj1c5jN2Jk",
    "https://t.me/+ZWDMAtOj1c5jN2Jk"
]

# Ссылка на вступление в команду
TEAM_LINK = "https://t.me/+UaMfr7uB405mMGNi"

# Ссылка для вывода средств
WITHDRAW_LINK = "https://t.me/c/2350708541/5"

# Создаем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
from flask import Flask
import os

# Создаем приложение Flask
app = Flask(__name__)






# Данные пользователей и статистика
users = {}
stats = {
    "total_users": 0,
    "today_users": 0,
    "total_payouts": 0.0
}

# Кнопки со спонсорами
sponsors_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[ 
        [InlineKeyboardButton(text="☠️ Спонсор 1", url=SPONSORS[0]),
         InlineKeyboardButton(text="☠️ Спонсор 2", url=SPONSORS[1])],
        [InlineKeyboardButton(text="☠️ Спонсор 3", url=SPONSORS[2])],
        [InlineKeyboardButton(text="☠️ Спонсор 4", url=SPONSORS[3]),
         InlineKeyboardButton(text="☠️ Спонсор 5", url=SPONSORS[4])],
        [InlineKeyboardButton(text="Проверить подписку ✅", callback_data="check_subscription")]
    ]
)
@dp.callback_query(F.data == "check_subscription")
async def check_subscription(callback: CallbackQuery):
    """
    Проверяет подписку и позволяет подать заявку на вступление в команду.
    """
    await callback.message.edit_text("⏳ Проверка подписки... Пожалуйста, подождите.")
    await asyncio.sleep(2)  # Задержка для имитации проверки

    is_subscribed = True  # Здесь нужно заменить на реальную проверку подписки, если она доступна

    if is_subscribed:
        # Обновляем текст сообщения и добавляем кнопку "Подать заявку"
        await callback.message.edit_text(
            "✅ Подписка подтверждена! Теперь можете подать заявку на вступление в команду.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Подать заявку", url=TEAM_LINK)],
                [InlineKeyboardButton(text="Я вступил в команду", callback_data="confirm_team_join")]
            ])
        )
    else:
        # Если подписка не подтверждена
        await callback.message.edit_text("❗ Подписка не подтверждена. Пожалуйста, подпишитесь на канал.")
        
@dp.callback_query(F.data == "confirm_team_join")
async def confirm_team_join(callback: CallbackQuery):
    """
    Обработчик кнопки "Я вступил в команду". Подтверждаем, что пользователь присоединился.
    """
    user_id = callback.from_user.id
    user_data = users.get(user_id, {})

    if user_data:
        # Проверяем, не присоединился ли уже пользователь
        if user_data["team_joined"]:
            # Если пользователь уже присоединился, показываем сообщение
            await callback.message.edit_text(
                "🎉 Вы уже вступили в команду!",
                reply_markup=control_panel_menu  # возвращаем основное меню
            )
        else:
            # Обновляем статус пользователя, что он присоединился к команде
            user_data["team_joined"] = True

            # Отправляем сообщение с подтверждением
            await callback.message.edit_text(
                "🎉 Вы успешно вступили в команду!",
                reply_markup=control_panel_menu  # возвращаем основное меню
            )
            
            


# Главное меню
control_panel_menu = InlineKeyboardMarkup(inline_keyboard=[ 
    [InlineKeyboardButton(text="💻 Личный кабинет", callback_data="profile")],
    [InlineKeyboardButton(text="📚 Магазин", callback_data="shop")],
    [InlineKeyboardButton(text="📊 Статистика", callback_data="statistics")],
    [InlineKeyboardButton(text="📖 О боте", callback_data="about_bot")]
])

# Кнопка "Назад"
back_button = InlineKeyboardMarkup(inline_keyboard=[ 
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main_menu")] 
])

# Обработчик кнопки "Назад" для возврата в главное меню
@dp.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Добро пожаловать на панель управления!",
        reply_markup=control_panel_menu
    )

# Личный кабинет с кнопками "Рефералы" и "Вывести" в одном ряду, кнопка "Назад" в другом
profile_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👥 Рефералы", callback_data="referrals"),
     InlineKeyboardButton(text="💸 Вывести", url=WITHDRAW_LINK)],  # Кнопка вывода
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile_menu")]  # Кнопка назад
])

# Кнопка "Назад" для возврата в раздел "Рефералы" из личного кабинета
back_from_referrals_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile_from_referrals")]
])

# Обработчик кнопки "Рефералы"
@dp.callback_query(F.data == "referrals")
async def referrals(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data = users.get(user_id, {})
    if user_data:
        referral_link = user_data["ref_link"]
        referrals_count = user_data["referrals"]
        referral_message = (
            f"🔗 Ваша реферальная ссылка: {referral_link}\n"
            f"👥 Всего рефералов: {referrals_count}"
        )
        # Добавляем кнопку "Назад", чтобы вернуться в Личный кабинет
        await callback.message.edit_text(referral_message, reply_markup=back_from_referrals_button)

# Обработчик кнопки "Назад" для возврата в Личный кабинет
@dp.callback_query(F.data == "back_to_profile_from_referrals")
async def back_to_profile_from_referrals(callback: CallbackQuery):
    # Возвращаемся в личный кабинет
    await profile(callback)

# Обработчик кнопки "Назад" для возврата в Личный кабинет из основного меню
@dp.callback_query(F.data == "back_to_profile_menu")
async def back_to_profile_menu(callback: CallbackQuery):
    # Возвращаемся в Личный кабинет
    await profile(callback)

# Обработчик кнопки "Личный кабинет"
@dp.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data = users.get(user_id, {})

    if user_data:
        # Определяем статус пользователя
        status = get_user_status(user_data["referrals"])

        # Подсчитываем количество рефералов за сегодня и за неделю
        weekly_referrals = get_weekly_referrals(user_id)
        today_referrals = user_data["referral_stats"].get(get_today(), 0)

        # Формируем сообщение
        profile_message = (
            "☠️ 𝐃𝐞𝐚𝐭𝐡𝐥𝐞𝐬𝐬 || 𝐓𝐞𝐚𝐦\n\n"
            "💻—Личный кабинет\n"
            f"┣🆔 Мой ID: {user_id}\n"
            f"┣💰 Баланс: {user_data['balance']}$\n"
            f"┣🏆 Статус: {status}\n"
            f"┣👥 Рефералов сегодня: {today_referrals}\n"
            f"┣📅 Рефералов за неделю: {weekly_referrals}\n"
            f"┣🌟 Всего рефералов: {user_data['referrals']}"
        )

        # Отправляем сообщение с панелью управления
        await callback.message.edit_text(profile_message, reply_markup=profile_keyboard)



# Функция для получения сегодняшней даты
def get_today():
    return datetime.now().strftime("%Y-%m-%d")

# Функция для подсчёта рефералов за неделю
def get_weekly_referrals(user_id):
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    user_data = users.get(user_id, {})
    referral_stats = user_data.get("referral_stats", {})
    return sum(count for date, count in referral_stats.items() if week_ago.strftime("%Y-%m-%d") <= date <= today.strftime("%Y-%m-%d"))

# Обработчик команды /start
@dp.message(F.text.startswith("/start"))
async def send_welcome(message: Message):
    user_id = message.from_user.id
    # Проверяем, передан ли реферальный ID
    referrer_id = None
    if len(message.text.split()) > 1:
        referrer_id = message.text.split()[1]
        try:
            referrer_id = int(referrer_id)
        except ValueError:
            referrer_id = None

    # Если пользователь новый, добавляем его в базу
    if user_id not in users:
        users[user_id] = {
            "balance": 0.0,
            "referrals": 0,
            "referral_earnings": 0.0,
            "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ref_link": f"https://t.me/{(await bot.get_me()).username}?start={user_id}",
            "team_joined": False,
            "referral_stats": {}
        }
        stats["total_users"] += 1
        stats["today_users"] += 1

        # Если есть реферальный ID, увеличиваем счетчик рефералов у пригласившего
        if referrer_id and referrer_id in users:
            users[referrer_id]["referrals"] += 1
            users[referrer_id]["balance"] += 0.5  # Добавляем $0.5 за нового реферала
            users[referrer_id]["referral_earnings"] += 0.5  # Учитываем заработок от рефералов

            # Учитываем рефералы по дате
            today = get_today()
            if today not in users[referrer_id]["referral_stats"]:
                users[referrer_id]["referral_stats"][today] = 0
            users[referrer_id]["referral_stats"][today] += 1

        # Отправляем сообщение только новым пользователям
        await message.answer(
            "✅ Подпишитесь на наших спонсоров, чтобы продолжить!",
            reply_markup=sponsors_keyboard
        )
    else:
        # Если пользователь уже зарегистрирован, отправляем приветственное сообщение без кнопок
        await message.answer(
            "Добро пожаловать обратно! Используйте панель управления для дальнейших действий."
        )

# Функция для определения статуса пользователя
def get_user_status(referrals):
    if referrals < 50:
        return "Возрождённый"
    elif 50 <= referrals < 100:
        return "Призрак"
    elif 100 <= referrals < 250:
        return "Спектр"
    elif 250 <= referrals < 500:
        return "Фантом"
    else:
        return "Бессмертный"

# Личный кабинет с кнопками "Рефералы" и "Вывести" в одном ряду, кнопка "Назад" в другом
profile_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👥 Рефералы", callback_data="referrals"),
     InlineKeyboardButton(text="💸 Вывести", url=WITHDRAW_LINK)],  # Кнопка вывода
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile_menu")]  # Кнопка назад
])

# Обработчик кнопки "Личный кабинет"
@dp.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data = users.get(user_id, {})

    if user_data:
        # Определяем статус пользователя
        status = get_user_status(user_data["referrals"])

        # Подсчитываем количество рефералов за сегодня и за неделю
        weekly_referrals = get_weekly_referrals(user_id)
        today_referrals = user_data["referral_stats"].get(get_today(), 0)

        # Формируем сообщение
        profile_message = (
            "☠️ 𝐃𝐞𝐚𝐭𝐡𝐥𝐞𝐬𝐬 || 𝐓𝐞𝐚𝐦\n\n"
            "💻—Личный кабинет\n"
            f"┣🆔 Мой ID: {user_id}\n"
            f"┣💰 Баланс: {user_data['balance']}$\n"
            f"┣🏆 Статус: {status}\n"
            f"┣👥 Рефералов сегодня: {today_referrals}\n"
            f"┣📅 Рефералов за неделю: {weekly_referrals}\n"
            f"┣🌟 Всего рефералов: {user_data['referrals']}"
        )

        # Отправляем сообщение с панелью управления
        await callback.message.edit_text(profile_message, reply_markup=profile_keyboard)

# Обработчик кнопки "Назад" для возврата в Личный кабинет
@dp.callback_query(F.data == "back_to_profile_menu")
async def back_to_profile_menu(callback: CallbackQuery):
    # Повторно отображаем Личный кабинет
    await profile(callback)  # Переиспользуем обработчик для личного кабинета




# Обработчик кнопки "Статистика"
@dp.callback_query(F.data == "statistics")
async def statistics(callback: CallbackQuery):
    # Получаем данные статистики
    total_users = stats["total_users"]
    today_users = stats["today_users"]
    total_payouts = stats["total_payouts"]
    
    

    # Формируем сообщение для статистики
    statistics_message = (
        "☠️ 𝐃𝐞𝐚𝐭𝐡𝐥𝐞𝐬𝐬 || 𝐓𝐞𝐚𝐦\n\n"
        "📊—Статистика:\n"
        f"┣Всего пользователей в боте: {total_users}\n"
        f"┗За сегодня в бота зашло: {today_users}\n"
    )

    # Кнопка "Назад" для возврата в главное меню
    back_button = InlineKeyboardMarkup(inline_keyboard=[ 
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main_menu")] 
    ])

    # Отправляем сообщение с статистикой
    await callback.message.edit_text(statistics_message, reply_markup=back_button)
    
    # Ссылка на магазин
SHOP_LINK = "https://t.me/+t2OUM3mp0BphNzVi"

# Главное меню с кнопкой "Магазин"
control_panel_menu = InlineKeyboardMarkup(inline_keyboard=[ 
    [InlineKeyboardButton(text="💻 Личный кабинет", callback_data="profile")],
    [InlineKeyboardButton(text="📚 Магазин", url=SHOP_LINK)],  # Кнопка с ссылкой на магазин
    [InlineKeyboardButton(text="📊 Статистика", callback_data="statistics")],
    [InlineKeyboardButton(text="📖 О боте", callback_data="about_bot")]
])

# Ссылки для кнопок в разделе "О боте"
INFO_LINK = "https://t.me/c/2350708541/3"
PAYMENTS_LINK = "https://t.me/c/2350708541/5"
MANUAL_LINK = "https://t.me/c/2350708541/6"
CHAT_LINK = "https://t.me/c/2350708541/43"
TRAINING_LINK = "https://t.me/c/2350708541/48"

# Кнопки для "О боте"
about_bot_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="ℹ️ Информация", url=INFO_LINK)],
    [InlineKeyboardButton(text="💸 Выплаты", url=PAYMENTS_LINK)],
    [InlineKeyboardButton(text="📘 Мануал", url=MANUAL_LINK)],
    [InlineKeyboardButton(text="💬 Чат", url=CHAT_LINK)],
    [InlineKeyboardButton(text="🎓 Обучение", url=TRAINING_LINK)],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main_menu")]
])

# Обработчик кнопки "О боте"
@dp.callback_query(F.data == "about_bot")
async def about_bot(callback: CallbackQuery):
    await callback.message.edit_text(
        "☠️ 𝐃𝐞𝐚𝐭𝐡𝐥𝐞𝐬𝐬 || 𝐓𝐞𝐚𝐦 \n\n 📚 Информация о 𝐃𝐞𝐚𝐭𝐡𝐥𝐞𝐬𝐬 || 𝐓𝐞𝐚𝐦",
        reply_markup=about_bot_keyboard
    )
# Главное меню с кнопками по два в ряду
control_panel_menu = InlineKeyboardMarkup(inline_keyboard=[ 
    [InlineKeyboardButton(text="💻 Личный кабинет", callback_data="profile"),
     InlineKeyboardButton(text="📚 Магазин", url=SHOP_LINK)],  # Кнопка с ссылкой на магазин
    [InlineKeyboardButton(text="📊 Статистика", callback_data="statistics"),
     InlineKeyboardButton(text="📖 О боте", callback_data="about_bot")]
])

# Личный кабинет с кнопками "Рефералы" и "Вывести" в одном ряду, кнопка "Назад" в другом
profile_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👥 Рефералы", callback_data="referrals"),
     InlineKeyboardButton(text="💸 Вывести", url=WITHDRAW_LINK)],  # Кнопка вывода
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main_menu")]  # Кнопка назад
])

# Ссылки для кнопок в разделе "О боте"
INFO_LINK = "https://t.me/c/2350708541/3"
PAYMENTS_LINK = "https://t.me/c/2350708541/5"
MANUAL_LINK = "https://t.me/c/2350708541/6"
CHAT_LINK = "https://t.me/c/2350708541/43"
TRAINING_LINK = "https://t.me/c/2350708541/48"

# Кнопки для "О боте", расставленные по три в ряду
about_bot_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="ℹ️ Информация", url=INFO_LINK),
     InlineKeyboardButton(text="💸 Выплаты", url=PAYMENTS_LINK)],  # Информация и Выплаты в одном ряду
    [InlineKeyboardButton(text="📘 Мануал", url=MANUAL_LINK),
     InlineKeyboardButton(text="💬 Чат", url=CHAT_LINK)],  # Мануал и Чат во втором ряду
    [InlineKeyboardButton(text="🎓 Обучение", url=TRAINING_LINK)],  # Обучение в третьем ряду
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main_menu")]  # Кнопка назад
])

# Обработчик кнопки "О боте"
@dp.callback_query(F.data == "about_bot")
async def about_bot(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔧 Информация о боте:\n\nВыберите нужный раздел.",
        reply_markup=about_bot_keyboard
    )

    import requests

# Установите вебхук
def set_webhook():
    url = f'https://api.telegram.org/bot<7311925613:AAEozZhlP1th7_X3LRJS_7lo3jsjy4ALHfE>/setWebhook?url=https://your-server.com/your-webhook-endpoint'
    response = requests.get(url)
    print(response.json())

# Функция для обработки сообщений от Telegram
def handle_updates(update):
    # Здесь код обработки обновлений (например, сообщений пользователей)
    pass

# Вызовите функцию для настройки вебхука
set_webhook()

# Обработчик вывода средств
@dp.callback_query(F.data == "withdraw")
async def withdraw(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data = users.get(user_id, {})

    if user_data:
        balance = user_data['balance']
        
        if balance > 0:
            # Логика вывода средств
            # Предположим, что пользователь получает свои деньги, и теперь нужно обновить статистику
            user_data['balance'] = 0.0  # Сбрасываем баланс пользователя после вывода

            # Обновляем общую статистику выплат
            stats["total_payouts"] += balance  # Добавляем выплаченные средства к общей статистике
            stats["today_users"] -= 1  # Обновляем количество пользователей, сделавших вывод сегодня

            # Отправляем сообщение о выводе
            await callback.message.edit_text(f"💸 Ваш вывод на сумму {balance}$ успешно обработан! Ваш новый баланс: 0$")
        else:
            # Если баланс 0
            await callback.message.edit_text("❗ У вас недостаточно средств для вывода.")
    else:
        await callback.message.edit_text("❗ Пользователь не найден.")

        
# Запуск бота
async def main():
    await bot.set_my_commands([ 
        BotCommand(command="/start", description="Начать работу")
    ])
    await dp.start_polling(bot)


from psycopg2 import OperationalError

try:
    db_connection = psycopg2.connect(DB_URI, sslmode="require")
    db_object = db_connection.cursor()
except OperationalError as e:
    print(f"Ошибка подключения к базе данных: {e}")
    exit()

@dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    if message.chat.type == "private":
        try:
            # Проверяем, есть ли пользователь в базе данных
            db_object.execute(f"SELECT id FROM users WHERE id = {user_id}")
            result = db_object.fetchone()

            if not result:
                # Добавляем нового пользователя
                db_object.execute("INSERT INTO users(id, username) VALUES (%s, %s)", (user_id, username))
                db_connection.commit()
                await bot.send_message(message.chat.id, f"Добро пожаловать, {username}!\nВы получили 2 бесплатных балла.", reply_markup=await gen_main_markup())
            else:
                await bot.send_message(message.chat.id, f"Добро пожаловать обратно, {username}!", reply_markup=await gen_main_markup())
        except Exception as e:
            await bot.send_message(message.chat.id, "Произошла ошибка при работе с базой данных.")
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())

