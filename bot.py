import logging
import os
import sqlite3
from datetime import date, timedelta

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

ADMIN_USERNAME = "Nazerati_06"
DB_PATH = "bot_stats.db"

MENU_LINKS = {
    "Зеркало": "https://lkhq.cc/3ddb3d",
}


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_users (
                day TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                PRIMARY KEY (day, user_id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def track_user(user_id: int) -> None:
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO daily_users(day, user_id) VALUES(?, ?)",
            (today, user_id),
        )
        conn.commit()
    finally:
        conn.close()


def count_users(day_value: date) -> int:
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            "SELECT COUNT(*) FROM daily_users WHERE day = ?",
            (day_value.isoformat(),),
        ).fetchone()
        return int(row[0]) if row else 0
    finally:
        conn.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user:
        track_user(update.effective_user.id)

    keyboard = [[item] for item in MENU_LINKS.keys()]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! Выберите, что вам нужно:",
        reply_markup=markup,
    )


async def on_menu_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user:
        track_user(update.effective_user.id)

    choice = (update.message.text or "").strip()
    link = MENU_LINKS.get(choice)

    if link:
        await update.message.reply_text(f"Вот ваша ссылка:\n{link}")
        return

    await update.message.reply_text("Выберите пункт из меню с кнопок.")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user or (user.username or "").lower() != ADMIN_USERNAME.lower():
        await update.message.reply_text("Команда доступна только владельцу бота.")
        return

    today = date.today()
    yesterday = today - timedelta(days=1)
    today_count = count_users(today)
    yesterday_count = count_users(yesterday)

    await update.message.reply_text(
        "Статистика пользователей:\n"
        f"Сегодня ({today.isoformat()}): {today_count}\n"
        f"Вчера ({yesterday.isoformat()}): {yesterday_count}"
    )


def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Не найден BOT_TOKEN. Установите переменную окружения BOT_TOKEN.")

    init_db()

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_menu_click))

    app.run_polling()


if __name__ == "__main__":
    main()
