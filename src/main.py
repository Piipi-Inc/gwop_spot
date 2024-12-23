from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, ApplicationBuilder

from config import config
from rag import rag

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Привет! Я ваш Финансовый Помощник. 🚀\n"
        "Я помогу вам разобраться с инвестициями, финансами и аналитикой.\n\n"
        "Напишите /help, чтобы узнать, что я могу!"
    )

async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "💡 Вот что я могу:\n"
        "- отвечу на вопросы про инвестициям.\n"
        "- укажу в какие акции вкладываться.\n"
        "- помогу в построении финансового плана.\n\n"
        "Напишите сообщение, чтобы узнать что-то конкретное!"
    )

async def handle_text(update: Update, context: CallbackContext) -> None:
    res = rag.final_rag_chain.invoke({"question": update.message.text})
    await update.message.reply_text(
        res
    )


def main():

    app = ApplicationBuilder().token(config.token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.ALL, handle_text))

    app.run_polling()


if __name__ == "__main__":
    main()