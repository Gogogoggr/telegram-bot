import time
time.sleep(10)  # Пауза для инициализации
print("🟢 Бот запущен и работает!")
import logging
import time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext
)
from telegram.error import TelegramError
from telegram.constants import ParseMode

# Ваши настройки
BOT_TOKEN = "8142368589:AAFdxP0kXOxZYTt3bB-kI-W3woJJ6fG7L-U"
ADMIN_CHAT_ID = 1017061285
SOURCE_CHANNEL_ID = -1002569423833
DESTINATION_CHANNEL_IDS = [
    -1002840637729, -1002897564090, -1002601899784,
    -1002759975602, -1002685685567, -1002792624987,
    -1002355454394
]

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log'  # Логи будут сохраняться в файл
)
logger = logging.getLogger(__name__)

# Глобальная переменная состояния
bot_active = False

def get_keyboard():
    """Клавиатура с кнопками управления"""
    return ReplyKeyboardMarkup([
        ["🚀 Запустить бота", "🛑 Остановить бота"],
        ["♻️ Перезапустить", "📊 Статус"]
    ], resize_keyboard=True)

async def start(update: Update, context: CallbackContext):
    """Обработчик команды /start"""
    if update.effective_chat.id != ADMIN_CHAT_ID:
        return
    
    await update.message.reply_text(
        "🤖 Бот для пересылки сообщений\nВыберите действие:",
        reply_markup=get_keyboard()
    )

async def start_bot(update: Update, context: CallbackContext):
    """Запуск бота"""
    global bot_active
    bot_active = True
    await update.message.reply_text("🟢 Бот запущен!", reply_markup=get_keyboard())

async def stop_bot(update: Update, context: CallbackContext):
    """Остановка бота"""
    global bot_active
    bot_active = False
    await update.message.reply_text("🔴 Бот остановлен!", reply_markup=get_keyboard())

async def restart_bot(update: Update, context: CallbackContext):
    """Перезапуск бота"""
    global bot_active
    bot_active = False
    await update.message.reply_text("🔄 Перезапускаю...")
    bot_active = True
    await update.message.reply_text("🟢 Бот перезапущен!", reply_markup=get_keyboard())

async def show_status(update: Update, context: CallbackContext):
    """Проверка статуса"""
    status = "🟢 АКТИВЕН" if bot_active else "🔴 НЕАКТИВЕН"
    await update.message.reply_text(
        f"📊 Статус: {status}\n"
        f"Канал-источник: {SOURCE_CHANNEL_ID}\n"
        f"Получателей: {len(DESTINATION_CHANNEL_IDS)}",
        reply_markup=get_keyboard()
    )

async def forward_post(update: Update, context: CallbackContext):
    """Пересылка сообщений"""
    global bot_active
    if not bot_active or not update.channel_post:
        return
    
    message = update.channel_post
    for dest_id in DESTINATION_CHANNEL_IDS:
        try:
            if message.photo:
                await message.copy(dest_id)
            elif message.text:
                await context.bot.send_message(
                    chat_id=dest_id,
                    text=message.text,
                    parse_mode=ParseMode.HTML if message.entities else None
                )
            logger.info(f"Сообщение переслано в {dest_id}")
        except Exception as e:
            logger.error(f"Ошибка: {str(e)}")

def setup_application():
    """Настройка обработчиков"""
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^🚀 Запустить бота$"), start_bot))
    application.add_handler(MessageHandler(filters.Regex("^🛑 Остановить бота$"), stop_bot))
    application.add_handler(MessageHandler(filters.Regex("^♻️ Перезапустить$"), restart_bot))
    application.add_handler(MessageHandler(filters.Regex("^📊 Статус$"), show_status))
    application.add_handler(
        MessageHandler(
            filters.Chat(SOURCE_CHANNEL_ID) & 
            (filters.PHOTO | filters.TEXT),
            forward_post
        )
    )
    return application

def run_bot():
    """Основной цикл работы"""
    while True:
        try:
            logger.info("Запуск бота...")
            application = setup_application()
            application.run_polling()
        except Exception as e:
            logger.error(f"Критическая ошибка: {str(e)}")
            time.sleep(60)  # Пауза перед перезапуском

if __name__ == '__main__':
    run_bot()