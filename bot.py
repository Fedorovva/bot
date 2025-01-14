from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
from dataclasses import dataclass
from decimal import Decimal
import aiohttp
from collections import defaultdict

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Конфигурация бота
class Config:
    TOKEN = "7651604716:AAHyoyFuCTtHRiX_birOQ2sgo9jOtmKV2tI"
    SPONSORS = [
        "https://t.me/+ZWDMAtOj1c5jN2Jk", "https://t.me/+ZWDMAtOj1c5jN2Jk",
        "https://t.me/+ZWDMAtOj1c5jN2Jk", "https://t.me/+ZWDMAtOj1c5jN2Jk",
        "https://t.me/+t2OUM3mp0BphNzVi"
    ]
    TEAM_LINK = "https://t.me/+UaMfr7uB405mMGNi"
    WITHDRAW_LINK = "https://t.me/c/2350708541/5"
    SHOP_LINK = "https://t.me/+t2OUM3mp0BphNGNi"
    INFO_LINK = "https://t.me/c/2350708541/3"
    PAYMENTS_LINK = "https://t.me/c/2350708541/5"
    MANUAL_LINK = "https://t.me/c/2350708541/6"
    CHAT_LINK = "https://t.me/c/2350708541/43"
    TRAINING_LINK = "https://t.me/c/2350708541/48"


@dataclass
class UserStats:
    balance: Decimal = Decimal("0")
    referrals: int = 0
    referral_earnings: Decimal = Decimal("0")
    joined_at: datetime = None
    team_joined: bool = False
    referral_stats: Dict[str, int] = None
    ref_link: str = ""

    def __post_init__(self):
        if self.joined_at is None:
            self.joined_at = datetime.now()
        if self.referral_stats is None:
            self.referral_stats = defaultdict(int)


class Stats:

    def __init__(self):
        self.total_users = 0
        self.today_users = 0
        self.total_payouts = Decimal("0")


from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
# ... (остальные импорты остаются теми же)


class BotManager:

    def __init__(self):
        self.bot = Bot(token=Config.TOKEN)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.users: Dict[int, UserStats] = {}
        self.stats = Stats()
        self.setup_keyboards()
        self.register_handlers()

    def setup_keyboards(self):
        """Настройка всех клавиатур"""
        # Клавиатура со спонсорами
        self.sponsors_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="☠️ Спонсор 1",
                                     url=Config.SPONSORS[0]),
                InlineKeyboardButton(text="☠️ Спонсор 2",
                                     url=Config.SPONSORS[1])
            ],
            [
                InlineKeyboardButton(text="☠️ Спонсор 3",
                                     url=Config.SPONSORS[2])
            ],
            [
                InlineKeyboardButton(text="☠️ Спонсор 4",
                                     url=Config.SPONSORS[3]),
                InlineKeyboardButton(text="☠️ Спонсор 5",
                                     url=Config.SPONSORS[4])
            ],
            [
                InlineKeyboardButton(text="Проверить подписку ✅",
                                     callback_data="check_subscription")
            ]
        ])

        # Основное меню
        self.control_panel_menu = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💻 Личный кабинет",
                                     callback_data="profile"),
                InlineKeyboardButton(text="📚 Магазин", url=Config.SHOP_LINK)
            ],
            [
                InlineKeyboardButton(text="📊 Статистика",
                                     callback_data="statistics"),
                InlineKeyboardButton(text="📖 О боте",
                                     callback_data="about_bot")
            ]
        ])

        # Меню профиля
        self.profile_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="👥 Рефералы",
                                     callback_data="referrals"),
                InlineKeyboardButton(text="💸 Вывести",
                                     url=Config.WITHDRAW_LINK)
            ],
                             [
                                 InlineKeyboardButton(
                                     text="🔙 Назад",
                                     callback_data="back_to_main_menu")
                             ]])

        # О боте
        self.about_bot_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="ℹ️ Информация",
                                     url=Config.INFO_LINK),
                InlineKeyboardButton(text="💸 Выплаты",
                                     url=Config.PAYMENTS_LINK)
            ],
            [
                InlineKeyboardButton(text="📘 Мануал", url=Config.MANUAL_LINK),
                InlineKeyboardButton(text="💬 Чат", url=Config.CHAT_LINK)
            ],
            [
                InlineKeyboardButton(text="🎓 Обучение",
                                     url=Config.TRAINING_LINK)
            ],
            [
                InlineKeyboardButton(text="🔙 Назад",
                                     callback_data="back_to_main_menu")
            ]
        ])

    def register_handlers(self):
        """Регистрация всех обработчиков"""
        self.dp.callback_query.register(self.check_subscription,
                                        F.data == "check_subscription")
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.callback_query.register(self.profile, F.data == "profile")

    async def check_subscription(self, callback: CallbackQuery):
        """Обработчик проверки подписки"""
        try:
            await callback.message.edit_text(
                "⏳ Проверка подписки... Пожалуйста, подождите.")
            await asyncio.sleep(2)  # Имитация проверки

            is_subscribed = await self.check_subscription_actual(
                callback.from_user.id)

            if not is_subscribed:
                await callback.message.edit_text(
                    "❗ Подписка не подтверждена. Пожалуйста, подпишитесь на ВСЕХ спонсоров.",
                    reply_markup=self.sponsors_keyboard)
                return

            await callback.message.edit_text(
                "✅ Подписка подтверждена! Теперь можете подать заявку на вступление в команду.",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[
                        InlineKeyboardButton(text="Подать заявку",
                                             url=Config.TEAM_LINK)
                    ],
                                     [
                                         InlineKeyboardButton(
                                             text="Я вступил в команду",
                                             callback_data="confirm_team_join")
                                     ]]))

        except Exception as e:
            logger.error(f"Error in check_subscription: {e}")
            await callback.message.edit_text(
                "Произошла ошибка при проверке подписки. Попробуйте позже.",
                reply_markup=self.sponsors_keyboard)

    async def check_subscription_actual(self, user_id: int) -> bool:
        """Проверка подписки только на последний канал"""
        try:
            last_sponsor = Config.SPONSORS[-1]
            chat_id = last_sponsor.split('/')[-1]

            async with aiohttp.ClientSession() as session:
                async with session.get(
                        f"https://api.telegram.org/bot{Config.TOKEN}/getChatMember",
                        params={
                            "chat_id": chat_id,
                            "user_id": user_id
                        }) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["result"]["status"] in [
                            "member", "administrator", "creator"
                        ]
                    return False
        except Exception as e:
            logger.error(f"Error checking subscription: {e}")
            return False

    async def cmd_start(self, message: Message):
        """Обработчик команды /start"""
        user_id = message.from_user.id

        try:
            args = message.text.split()
            if len(args) > 1:
                try:
                    referrer_id = int(args[1])
                    if referrer_id in self.users and referrer_id != user_id:
                        await self.process_referral(referrer_id, user_id)
                except ValueError:
                    pass

            if user_id not in self.users:
                self.users[user_id] = UserStats(
                    ref_link=
                    f"https://t.me/{(await self.bot.get_me()).username}?start={user_id}"
                )
                self.stats.total_users += 1
                self.stats.today_users += 1

                await message.answer(
                    "✅ Подпишитесь на наших спонсоров, чтобы продолжить!",
                    reply_markup=self.sponsors_keyboard)
            else:
                await message.answer(
                    "Добро пожаловать обратно! Используйте панель управления для дальнейших действий.",
                    reply_markup=self.control_panel_menu)

        except Exception as e:
            logger.error(f"Error in cmd_start: {e}")
            await message.answer("Произошла ошибка. Попробуйте позже.")

    async def profile(self, callback: CallbackQuery):
        """Обработчик кнопки Личный кабинет"""
        user_id = callback.from_user.id
        user_data = self.users.get(user_id)

        if user_data:
            status = self.get_user_status(user_data.referrals)
            weekly_referrals = self.get_weekly_referrals(user_id)
            today_referrals = user_data.referral_stats.get(self.get_today(), 0)

            profile_message = ("☠️ 𝐃𝐞𝐚𝐭𝐡𝐥𝐞𝐬𝐬 || 𝐓𝐞𝐚𝐦\n\n"
                               "💻—Личный кабинет\n"
                               f"┣🆔 Мой ID: {user_id}\n"
                               f"┣💰 Баланс: {user_data.balance}$\n"
                               f"┣🏆 Статус: {status}\n"
                               f"┣👥 Рефералов сегодня: {today_referrals}\n"
                               f"┣📅 Рефералов за неделю: {weekly_referrals}\n"
                               f"┣🌟 Всего рефералов: {user_data.referrals}")

            await callback.message.edit_text(
                profile_message, reply_markup=self.profile_keyboard)

    def get_user_status(self, referrals: int) -> str:
        """Определение статуса пользователя"""
        if referrals >= 500:
            return "Бессмертный"
        elif referrals >= 250:
            return "Фантом"
        elif referrals >= 100:
            return "Спектр"
        elif referrals >= 50:
            return "Призрак"
        return "Возрождённый"

    def get_today(self):
        """Получение текущей даты"""
        return datetime.now().strftime("%Y-%m-%d")

    def get_weekly_referrals(self, user_id: int) -> int:
        """Подсчёт рефералов за неделю"""
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        user_data = self.users.get(user_id, {})
        return sum(count for date, count in user_data.referral_stats.items()
                   if week_ago.strftime("%Y-%m-%d") <= date <= today.strftime(
                       "%Y-%m-%d"))

    async def run(self):
        """Запуск бота"""
        try:
            commands = [
                BotCommand(command="/start", description="Начать работу"),
                BotCommand(command="/profile", description="Личный кабинет"),
                BotCommand(command="/help", description="Помощь")
            ]
            await self.bot.set_my_commands(commands)
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise


if __name__ == "__main__":
    bot_manager = BotManager()
    try:
        asyncio.run(bot_manager.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
