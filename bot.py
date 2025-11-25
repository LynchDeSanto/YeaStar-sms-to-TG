from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from sms_api import send_sms

PORT, PHONE, MESSAGE = range(3)

async def start_send_sms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите порт GSM-шлюза:")
    return PORT

async def get_port(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['port'] = update.message.text
    await update.message.reply_text("Введите номер телефона получателя:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone_number'] = update.message.text
    await update.message.reply_text("Введите текст SMS:")
    return MESSAGE

async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    port = context.user_data['port']
    phone = context.user_data['phone_number']
    msg = update.message.text

    success, response_text = send_sms(port, phone, msg)
    await update.message.reply_text(response_text)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправка SMS отменена.")
    return ConversationHandler.END

def run_telegram_bot(token):
    app = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('send_sms', start_send_sms)],
        states={
            PORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_port)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_message)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)
    print("[+] Telegram-бот запущен. Ожидание команды /send_sms ...")
    app.run_polling()
