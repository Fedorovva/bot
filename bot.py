from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    CallbackQuery,
    BotCommand
)
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime, timedelta
import asyncio
import requests
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Конфигурация бота
TOKEN = os.getenv("BOT_TOKEN", "7651604716:AAHyoyFuCTtHRiX_birOQ2sgo9jOtmKV2tI")  # Используем ваш токен как значение по умолчанию

# Ссылки на спонсоров
SPONSORS = [
    "https://t.me/+ZWDMAtOj1c5jN2Jk",
    "https://t.me/+ZWDMAtOj1c5jN2Jk",
    "https://t.me/+ZWDMAtOj1c5jN2Jk",
    "https://t.me/+ZWDMAtOj1c5jN2Jk",
    "https://t.me/+t2OUM3mp0BphNzVi"
]

# Остальные ссылки
TEAM_LINK = "https://t.me/+UaMfr7uB405mMGNi"
WITHDRAW_LINK = "https://t.me/c/2350708541/5"
SHOP_LINK = "https://t.me/+t2OUM3mp0BphNzVi"
INFO_LINK = "https://t.me/c/2350708541/3"
PAYMENTS_LINK = "https://t.me/c/2350708541/5"
MANUAL_LINK = "https://t.me/c/2350708541/6"
CHAT_LINK = "https://t.me/c/2350708541/43"
TRAINING_LINK = "https://t.me/c/2350708541/48"

# Создаем объекты бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# База данных пользователей (в памяти)
users = {}
stats = {"total_users": 0, "today_users": 0, "total_payouts": 0.0}

# Клавиатуры
sponsors_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="☠️ Спонсор 1", url=SPONSORS[0]),
        InlineKeyboardButton(text="☠️ Спонсор 2", url=SPONSORS[1])
    ],
    [InlineKeyboardButton(text="☠️ Спонсор 3", url=SPONSORS[2])],
    [
        InlineKeyboardButton(text="☠️ Спонсор 4", url=SPONSORS[3]),
        InlineKeyboardButton(text="☠️ Спонсор 5", url=SPONSORS[4])
    ],
    [InlineKeyboardButton(text="Проверить подписку ✅", callback_data="check_subscription")]
])

control_panel_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="💻 Личный кабинет", callback_data="profile"),
        InlineKeyboardButton(text="📚 Магазин", url=SHOP_LINK)
    ],
    [
        InlineKeyboardButton(text="📊 Статистика", callback_data="statistics"),
        InlineKeyboardButton(text="📖 О боте", callback_data="about_bot")
    ]
])

profile_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="👥 Рефералы", callback_data="referrals"),
        InlineKeyboardButton(text="💸 Вывести", url=WITHDRAW_LINK)
    ],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main_menu")]
])

about_bot_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="ℹ️ Информация", url=INFO_LINK),
        InlineKeyboardButton(text="💸 Выплаты", url=PAYMENTS_LINK)
    ],
    [
        InlineKeyboardButton(text="📘 Мануал", url=MANUAL_LINK),
        InlineKeyboardButton(text="💬 Чат", url=CHAT_LINK)
    ],
    [InlineKeyboardButton(text="🎓 Обучение", url=TRAINING_LINK)],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main_menu")]
])

back_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main_menu")]
])

# Вспомогательные функции
def get_user_status(referrals: int) -> str:
    if referrals < 50: return "Возрождённый"
    elif referrals < 100: return "Призрак"
    elif referrals < 250: return "Спектр"
    elif referrals < 500: return "Фантом"
    else: return "Бессмертный"

def get_today() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def get_weekly_referrals(user_id: int) -> int:
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    user_data = users.get(user_id, {})
    referral_stats = user_data.get("referral_stats", {})
    return sum(
        count for date, count in referral_stats.items()
        if week_ago.strftime("%Y-%m-%d") <= date <= today.strftime("%Y-%m-%d")
    )

# ... (весь предыдущий код до обработчика /start остается тем же) ...

@dp.message(F.text.startswith("/start"))
async def start_command(message: Message):
    user_id = message.from_user.id
    referrer_id = None

    if len(message.text.split()) > 1:
        try:
            referrer_id = int(message.text.split()[1])
        except ValueError:
            referrer_id = None

    if user_id not in users:
        users[user_id] = {
            "balance": 0.0,
            "referrals": 0,
            "referral_earnings": 0.0,
            "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ref_link": f"https://t.me/{(await bot.get_me()).username}?start={user_id}",
            "team_joined": False,
            "referral_stats": {},
            "referrer_id": referrer_id,  # Сохраняем ID пригласившего пользователя
            "subscription_checked": False  # Флаг для отслеживания прохождения подписки
        }
        stats["total_users"] += 1
        stats["today_users"] += 1

        await message.answer(
            "✅ Подпишитесь на наших спонсоров, чтобы продолжить!",
            reply_markup=sponsors_keyboard
        )
    else:
        await message.answer(
            "Добро пожаловать обратно! Используйте панель управления для дальнейших действий.",
            reply_markup=control_panel_menu
        )

@dp.callback_query(F.data == "check_subscription")
async def check_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data = users.get(user_id, {})

    await callback.message.edit_text(
        "⏳ Проверка подписки... Пожалуйста, подождите."
    )
    await asyncio.sleep(2)

    # Если пользователь новый и еще не проходил проверку подписки
    if user_data and not user_data.get("subscription_checked"):
        referrer_id = user_data.get("referrer_id")

        # Отмечаем, что пользователь прошел проверку подписки
        user_data["subscription_checked"] = True

        # Обновляем статистику реферера и отправляем ему уведомление
        if referrer_id and referrer_id in users:
            users[referrer_id]["referrals"] += 1
            users[referrer_id]["balance"] += 0.5
            users[referrer_id]["referral_earnings"] += 0.5

            today = get_today()
            if today not in users[referrer_id]["referral_stats"]:
                users[referrer_id]["referral_stats"][today] = 0
            users[referrer_id]["referral_stats"][today] += 1

            # Отправляем уведомление рефереру
            try:
                await bot.send_message(
                    referrer_id,
                    f"🎉 По вашей реферальной ссылке зарегистрировался новый пользователь!\n"
                    f"💰 Ваш баланс пополнен на 0.5$\n"
                    f"📊 Всего рефералов: {users[referrer_id]['referrals']}"
                )
            except Exception as e:
                print(f"Не удалось отправить уведомление пользователю {referrer_id}: {e}")

    await callback.message.edit_text(
        "✅ Подписка подтверждена! Теперь можете подать заявку на вступление в команду.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подать заявку", url=TEAM_LINK)],
            [InlineKeyboardButton(text="Я вступил в команду", callback_data="confirm_team_join")]
        ])
    )

@dp.callback_query(F.data == "confirm_team_join")
async def confirm_team_join(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data = users.get(user_id, {})

    if user_data:
        if user_data.get("team_joined"):
            await callback.message.edit_text(
                "🎉 Вы уже вступили в команду!",
                reply_markup=control_panel_menu
            )
        else:
            user_data["team_joined"] = True

            # Отправляем уведомление рефереру о полном прохождении регистрации
            referrer_id = user_data.get("referrer_id")
            if referrer_id and referrer_id in users:
                try:
                    await bot.send_message(
                        referrer_id,
                        "🎯 Ваш реферал успешно присоединился к команде!"
                    )
                except Exception as e:
                    print(f"Не удалось отправить уведомление пользователю {referrer_id}: {e}")

            await callback.message.edit_text(
                "🎉 Вы успешно вступили в команду!",
                reply_markup=control_panel_menu
            )

# ... (остальной код остается тем же) ...

# Обработчики команд и callback-запросов
@dp.message(F.text.startswith("/start"))
async def start_command(message: Message):
    user_id = message.from_user.id
    referrer_id = None

    if len(message.text.split()) > 1:
        try:
            referrer_id = int(message.text.split()[1])
        except ValueError:
            referrer_id = None

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

        if referrer_id and referrer_id in users:
            users[referrer_id]["referrals"] += 1
            users[referrer_id]["balance"] += 0.5
            users[referrer_id]["referral_earnings"] += 0.5

            today = get_today()
            if today not in users[referrer_id]["referral_stats"]:
                users[referrer_id]["referral_stats"][today] = 0
            users[referrer_id]["referral_stats"][today] += 1

        await message.answer(
            "✅ Подпишитесь на наших спонсоров, чтобы продолжить!",
            reply_markup=sponsors_keyboard
        )
    else:
        await message.answer(
            "Добро пожаловать обратно! Используйте панель управления для дальнейших действий.",
            reply_markup=control_panel_menu
        )

@dp.callback_query(F.data == "check_subscription")
async def check_subscription(callback: CallbackQuery):
    await callback.message.edit_text(
        "⏳ Проверка подписки... Пожалуйста, подождите."
    )
    await asyncio.sleep(2)

    await callback.message.edit_text(
        "✅ Подписка подтверждена! Теперь можете подать заявку на вступление в команду.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подать заявку", url=TEAM_LINK)],
            [InlineKeyboardButton(text="Я вступил в команду", callback_data="confirm_team_join")]
        ])
    )

@dp.callback_query(F.data == "confirm_team_join")
async def confirm_team_join(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data = users.get(user_id, {})

    if user_data:
        if user_data.get("team_joined"):
            await callback.message.edit_text(
                "🎉 Вы уже вступили в команду!",
                reply_markup=control_panel_menu
            )
        else:
            user_data["team_joined"] = True
            await callback.message.edit_text(
                "🎉 Вы успешно вступили в команду!",
                reply_markup=control_panel_menu
            )

@dp.callback_query(F.data == "profile")
async def profile_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data = users.get(user_id, {})

    if user_data:
        status = get_user_status(user_data["referrals"])
        weekly_referrals = get_weekly_referrals(user_id)
        today_referrals = user_data["referral_stats"].get(get_today(), 0)

        message_text = (
            "☠️ 𝐃𝐞𝐚𝐭𝐡𝐥𝐞𝐬𝐬 𝐓𝐞𝐚𝐦\n\n"
            "💻—Личный кабинет\n"
            f"┣🆔 Мой ID: {user_id}\n"
            f"┣💰 Баланс: {user_data['balance']}$\n"
            f"┣🏆 Статус: {status}\n"
            f"┣👥 Рефералов сегодня: {today_referrals}\n"
            f"┣📅 Рефералов за неделю: {weekly_referrals}\n"
            f"┣🌟 Всего рефералов: {user_data['referrals']}"
        )
        await callback.message.edit_text(message_text, reply_markup=profile_keyboard)

@dp.callback_query(F.data == "referrals")
async def referrals_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data = users.get(user_id, {})

    if user_data:
        referral_link = user_data["ref_link"]
        referrals_count = user_data["referrals"]
        message_text = (
            f"🔗 Ваша реферальная ссылка: {referral_link}\n"
            f"👥 Всего рефералов: {referrals_count}"
        )
        await callback.message.edit_text(message_text, reply_markup=back_button)

@dp.callback_query(F.data == "statistics")
async def statistics_handler(callback: CallbackQuery):
    message_text = (
        "☠️ 𝐃𝐞𝐚𝐭𝐡𝐥𝐞𝐬𝐬 𝐓𝐞𝐚𝐦\n\n"
        "📊—Статистика:\n"
        f"┣Всего пользователей: {stats['total_users']}\n"
        f"┗За сегодня: {stats['today_users']}"
    )
    await callback.message.edit_text(message_text, reply_markup=back_button)

@dp.callback_query(F.data == "about_bot")
async def about_bot_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "☠️ 𝐃𝐞𝐚𝐭𝐡𝐥𝐞𝐬𝐬 𝐓𝐞𝐚𝐦\n\n📚 Информация о 𝐃𝐞𝐚𝐭𝐡𝐥𝐞𝐬𝐬 || 𝐓𝐞𝐚𝐦",
        reply_markup=about_bot_keyboard
    )

@dp.callback_query(F.data == "back_to_main_menu")
async def back_to_main_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "Главное меню",
        reply_markup=control_panel_menu
    )

# Запуск бота
async def main():
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота")
    ])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
