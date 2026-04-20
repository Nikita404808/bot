import logging
import os

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

MENU_LINKS = {
    "Зеркало": "https://lkhq.cc/3ddb3d",
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[item] for item in MENU_LINKS.keys()]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! Выберите, что вам нужно:",
        reply_markup=markup,
    )


async def on_menu_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    choice = (update.message.text or "").strip()
    link = MENU_LINKS.get(choice)

    if link:
        await update.message.reply_text(f"Вот ваша ссылка:\n{link}")
        return

    await update.message.reply_text("Выберите пункт из меню с кнопок.")


def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Не найден BOT_TOKEN. Установите переменную окружения BOT_TOKEN.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_menu_click))

    app.run_polling()


if __name__ == "__main__":
    main()
