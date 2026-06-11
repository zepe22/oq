# -*- coding: utf-8 -*-
import logging
import re
import sys
import json
import os

print(f"Python версии: {sys.version}")
print("Начинаем заново...")

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
    import telegram
    print(f"Telegram bot версии: {telegram.__version__}")
except Exception as e:
    print(f"Ошибка импорта: {e}")
    sys.exit(1)

# ===== НАСТРОЙКИ =====
TOKEN = '8901412303:AAG1mAHzbnhGU-9pOYVQenJkFgattTKdy3A'
YOUR_USER_ID = 8575454803
GROUP_ID = -1003815046398

# Файл для сохранения триггеров
TRIGGERS_FILE = 'triggers.json'

# Загрузка триггеров из файла
def load_triggers():
    if os.path.exists(TRIGGERS_FILE):
        with open(TRIGGERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Триггеры по умолчанию
        default_triggers = {
            "Успешное списание средств": 7,
            "Депозит обнаружен!": 1292,
            "trust-aml.icu": 1193,
            "trustwallet-linkswft.cfd": 1090,
            "trust-invoice.icu": 1013
            "cryptopay-connect.com": 1915


        }
        save_triggers(default_triggers)
        return default_triggers

def save_triggers(triggers):
    with open(TRIGGERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(triggers, f, ensure_ascii=False, indent=2)

# Глобальная переменная с триггерами
TRIGGERS = load_triggers()

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    if update.effective_user.id != YOUR_USER_ID:
        await update.message.reply_text("❌ Доступ запрещен")
        return
    
    help_text = """
🤖 *Бот для пересылки сообщений*

*Доступные команды:*

/start - Показать это сообщение
/list - Показать все триггеры
/add `<фраза>` `<id_темы>` - Добавить триггер
/remove `<фраза>` - Удалить триггер
/edit `<фраза>` `<новый_id>` - Изменить тему для триггера

*Примеры:*
`/add Новая фраза 123`
`/remove Старая фраза`
`/edit Новая фраза 456`

*Текущие триггеры:*
"""
    for trigger, topic_id in TRIGGERS.items():
        help_text += f"\n• `{trigger}` → тема {topic_id}"
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def list_triggers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать все триггеры"""
    if update.effective_user.id != YOUR_USER_ID:
        await update.message.reply_text("❌ Доступ запрещен")
        return
    
    if not TRIGGERS:
        await update.message.reply_text("📭 Список триггеров пуст")
        return
    
    text = "📋 *Список триггеров:*\n\n"
    for i, (trigger, topic_id) in enumerate(TRIGGERS.items(), 1):
        text += f"{i}. `{trigger}`\n   → тема: `{topic_id}`\n\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def add_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить новый триггер"""
    if update.effective_user.id != YOUR_USER_ID:
        await update.message.reply_text("❌ Доступ запрещен")
        return
    
    try:
        # Разбираем команду: /add фраза id_темы
        args = context.args
        if len(args) < 2:
            await update.message.reply_text(
                "❌ Использование: `/add <фраза> <id_темы>`\n"
                "Пример: `/add Новая фраза 123`",
                parse_mode='Markdown'
            )
            return
        
        # Последний аргумент - это ID темы
        topic_id = int(args[-1])
        # Все остальное - это фраза триггера
        trigger_text = ' '.join(args[:-1])
        
        if trigger_text in TRIGGERS:
            await update.message.reply_text(f"⚠️ Триггер `{trigger_text}` уже существует!", parse_mode='Markdown')
            return
        
        TRIGGERS[trigger_text] = topic_id
        save_triggers(TRIGGERS)
        
        await update.message.reply_text(
            f"✅ Триггер добавлен!\n\n"
            f"📝 Фраза: `{trigger_text}`\n"
            f"🎯 Тема: `{topic_id}`",
            parse_mode='Markdown'
        )
        
    except ValueError:
        await update.message.reply_text("❌ ID темы должен быть числом!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def remove_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить триггер"""
    if update.effective_user.id != YOUR_USER_ID:
        await update.message.reply_text("❌ Доступ запрещен")
        return
    
    try:
        trigger_text = ' '.join(context.args)
        if not trigger_text:
            await update.message.reply_text(
                "❌ Использование: `/remove <фраза>`\n"
                "Пример: `/remove Старая фраза`",
                parse_mode='Markdown'
            )
            return
        
        if trigger_text not in TRIGGERS:
            await update.message.reply_text(f"⚠️ Триггер `{trigger_text}` не найден!", parse_mode='Markdown')
            return
        
        del TRIGGERS[trigger_text]
        save_triggers(TRIGGERS)
        
        await update.message.reply_text(f"✅ Триггер `{trigger_text}` удален!", parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def edit_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Изменить ID темы для триггера"""
    if update.effective_user.id != YOUR_USER_ID:
        await update.message.reply_text("❌ Доступ запрещен")
        return
    
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text(
                "❌ Использование: `/edit <фраза> <новый_id_темы>`\n"
                "Пример: `/edit Новая фраза 456`",
                parse_mode='Markdown'
            )
            return
        
        new_topic_id = int(args[-1])
        trigger_text = ' '.join(args[:-1])
        
        if trigger_text not in TRIGGERS:
            await update.message.reply_text(f"⚠️ Триггер `{trigger_text}` не найден!", parse_mode='Markdown')
            return
        
        TRIGGERS[trigger_text] = new_topic_id
        save_triggers(TRIGGERS)
        
        await update.message.reply_text(
            f"✅ Триггер обновлен!\n\n"
            f"📝 Фраза: `{trigger_text}`\n"
            f"🎯 Новая тема: `{new_topic_id}`",
            parse_mode='Markdown'
        )
        
    except ValueError:
        await update.message.reply_text("❌ ID темы должен быть числом!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик сообщений - только из ЛС"""
    
    try:
        # Проверяем, что сообщение из личных сообщений
        if update.effective_chat.type != "private":
            print(f"⏩ Игнорируем сообщение из группы/канала: {update.effective_chat.type}")
            return
        
        # Проверяем, что сообщение от вашего USER_ID
        if update.effective_user.id != YOUR_USER_ID:
            print(f"⏩ Игнорируем сообщение от другого пользователя: {update.effective_user.id}")
            return
        
        # Получаем текст
        text = update.message.text
        if not text:
            return
            
        logger.info(f"📨 Получено в ЛС: {text[:100]}")
        print(f"📨 Получено в ЛС: {text[:100]}")
        
        # Поиск триггера
        found_trigger = None
        for trigger in TRIGGERS:
            if trigger in text:
                found_trigger = trigger
                break
                
        if not found_trigger:
            await update.message.reply_text("❌ Триггер не найден")
            return
        
        # Ищем TRC20 адрес
        trc20_address = None
        address_match = re.search(r'T[a-zA-Z0-9]{33}', text)
        if address_match:
            trc20_address = address_match.group(0)
            print(f"🔗 Найден TRC20 адрес: {trc20_address}")
        
        # Очищаем текст
        clean_text = re.sub(r'🔗\s*\[.*?\]\(.*?\)', '', text)
        clean_text = re.sub(r'\[Смотреть в блокчейне\]\(.*?\)', '', clean_text)
        clean_text = re.sub(r'https?://\S+', '', clean_text)
        clean_text = clean_text.strip()
        
        if not clean_text:
            clean_text = "✅"
        
        # Создаем кнопку с ссылкой на TronScan
        reply_markup = None
        if trc20_address:
            tronscan_url = f"https://tronscan.org/#/address/{trc20_address}"
            keyboard = [[InlineKeyboardButton("👛 Wallet", url=tronscan_url)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            print(f"🔗 Кнопка ведет на: {tronscan_url}")
        
        # Отправка в группу
        try:
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=clean_text,
                message_thread_id=TRIGGERS[found_trigger],
                reply_markup=reply_markup
            )
            print(f"✅ Отправлено в тему {TRIGGERS[found_trigger]}")
            
            if reply_markup:
                await update.message.reply_text("✅ Отправлено в тему! Кнопка с адресом добавлена")
            else:
                await update.message.reply_text("✅ Отправлено в тему! (адрес не найден)")
                
        except Exception as e:
            # Если не работает с темой
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=clean_text,
                reply_markup=reply_markup
            )
            print(f"✅ Отправлено в группу")
            
            if reply_markup:
                await update.message.reply_text("✅ Отправлено в группу! Кнопка с адресом добавлена")
            else:
                await update.message.reply_text("✅ Отправлено в группу! (адрес не найден)")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        logger.error(f"Ошибка: {e}")
        try:
            await update.message.reply_text(f"❌ {e}")
        except:
            pass

def main():
    """Запуск"""
    print("🚀 Запуск...")
    
    try:
        app = Application.builder().token(TOKEN).build()
        
        # Команды для управления триггерами
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("list", list_triggers))
        app.add_handler(CommandHandler("add", add_trigger))
        app.add_handler(CommandHandler("remove", remove_trigger))
        app.add_handler(CommandHandler("edit", edit_trigger))
        
        # Основной обработчик сообщений
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Бот запущен!")
        print(f"👤 Твой ID: {YOUR_USER_ID}")
        print(f"👥 Группа для отправки: {GROUP_ID}")
        print(f"🎯 Триггеров загружено: {len(TRIGGERS)}")
        print("🟢 Жду сообщения ТОЛЬКО в ЛС...")
        print("\nДоступные команды в боте:")
        print("  /list - показать все триггеры")
        print("  /add <фраза> <id_темы> - добавить триггер")
        print("  /remove <фраза> - удалить триггер")
        print("  /edit <фраза> <новый_id> - изменить тему")
        
        app.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

if __name__ == '__main__':
    main()
