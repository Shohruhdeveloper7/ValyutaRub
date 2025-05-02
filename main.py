"""
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# --- API sozlamalari ---
TOKEN = '8129968556:AAEhqIxEZKzIZO15ye2UyP8gKpJODak1Qtg'  # <-- BU YERGA O'Z TOKENINGIZNI YOZING
API_BASE = "https://v6.exchangerate-api.com/v6/075da83e108bde274389c814/latest/"
SUPPORTED_DIRECTIONS = ['USD_RUB', 'RUB_USD', 'EUR_RUB']

# --- Bot holatlari ---
SELECT_DIRECTION, GET_AMOUNT = range(2)
user_context = {}

# --- Valyuta kursini olish ---
def get_exchange_rate(base: str, target: str) -> float | None:
    try:
        response = requests.get(f"{API_BASE}{base}", timeout=10)
        data = response.json()
        if data['result'] == 'success':
            return data['conversion_rates'].get(target)
    except:
        return None
    return None

# --- Hisoblash logikasi ---
def convert_currency(amount: float, direction: str) -> str:
    base, target = direction.split("_")
    rate = get_exchange_rate(base, target)

    if rate is None:
        return "❌ Kurslarni olishda xatolik yuz berdi."

    result = round(amount * rate, 2)
    return f"{amount} {base} ≈ {result} {target}"

# --- Klaviatura ---
def get_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("USD <> RUB", callback_data='USD_RUB')],
        [InlineKeyboardButton("RUB <> USD", callback_data='RUB_USD')],
        [InlineKeyboardButton("EUR <> RUB", callback_data='EUR_RUB')],
    ])

# --- /start komandasi ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💱 Valyuta yo‘nalishini tanlang:", reply_markup=get_keyboard())
    return SELECT_DIRECTION

# --- Valyuta yo‘nalishi tanlanganda ---
async def direction_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data not in SUPPORTED_DIRECTIONS:
        await query.edit_message_text("❌ Noto‘g‘ri yo‘nalish tanlandi.")
        return ConversationHandler.END

    user_context[query.from_user.id] = {'direction': query.data}
    await query.edit_message_text("💰 Miqdorni kiriting (faqat son):")
    return GET_AMOUNT

# --- Miqdor kiritinganda ---
async def amount_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    direction = user_context.get(user_id, {}).get('direction')

    try:
        amount = float(update.message.text.replace(",", "."))
    except ValueError:
        await update.message.reply_text("⚠️ Faqat son kiriting. Masalan: 1000")
        return GET_AMOUNT

    result_text = convert_currency(amount, direction)
    await update.message.reply_text(result_text)
    return ConversationHandler.END

# --- /cancel komandasi ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END

# --- Botni ishga tushirish ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_DIRECTION: [CallbackQueryHandler(direction_selected)],
            GET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_entered)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
"""
"""
import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# --- API sozlamalari ---
TOKEN = '8198907146:AAHyB4w-HhVNQsed9PxHSNLFSZHximUj_0U'  # <-- O'z tokeningizni shu yerga yozing
API_BASE = "https://v6.exchangerate-api.com/v6/075da83e108bde274389c814/latest/"

# --- Qo‘llab-quvvatlanadigan yo‘nalishlar ---
SUPPORTED_DIRECTIONS = ['USD_RUB', 'RUB_USD', 'EUR_RUB']
DIRECTION_LABELS = {
    'USD_RUB': '🇺🇸USD ➡️ RUB🇷🇺',
    'RUB_USD': '🇷🇺RUB ➡️ USD',
    'EUR_RUB': '🇪🇺EUR ➡️ RUB🇷🇺',
}

# --- Holatlar ---
SELECT_DIRECTION, GET_AMOUNT = range(2)
user_context = {}

# --- Valyuta kursini olish funksiyasi ---
def get_exchange_rate(base: str, target: str) -> float | None:
    try:
        response = requests.get(f"{API_BASE}{base}", timeout=10)
        data = response.json()
        if data['result'] == 'success':
            return data['conversion_rates'].get(target)
    except:
        return None
    return None

# --- Konvertatsiya qilish ---
def convert_currency(amount: float, direction: str) -> str:
    base, target = direction.split("_")
    rate = get_exchange_rate(base, target)
    if rate is None:
        return "❌ Произошла ошибка при получении курсов."
    result = round(amount * rate, 2)
    return f"{amount} {base} ≈ {result} {target}"

# --- Valyuta tanlash uchun tugmalar ---
def get_direction_keyboard():
    buttons = [[label] for label in DIRECTION_LABELS.values()]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)

# --- /start komandasi ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💱 Выберите направление валюты:",
        reply_markup=get_direction_keyboard()
    )
    return SELECT_DIRECTION

# --- Valyuta yo‘nalishi tanlanganda ---
async def direction_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    label = update.message.text
    direction = next((k for k, v in DIRECTION_LABELS.items() if v == label), None)

    if direction is None:
        await update.message.reply_text("⚠️ Было выбрано неверное направление. Попробуйте еще раз..")
        return SELECT_DIRECTION

    user_context[update.message.from_user.id] = {'direction': direction}
    await update.message.reply_text("💰 Введите количество (только число):", reply_markup=ReplyKeyboardRemove())
    return GET_AMOUNT

# --- Miqdor kiritinganda ---
async def amount_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    direction = user_context.get(user_id, {}).get('direction')

    try:
        amount = float(update.message.text.replace(",", "."))
    except ValueError:
        await update.message.reply_text("⚠️ Просто введите число. Например: 1000")
        return GET_AMOUNT

    result_text = convert_currency(amount, direction)
    await update.message.reply_text(result_text)
    return ConversationHandler.END

# --- /cancel komandasi ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# --- Botni ishga tushirish ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_DIRECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, direction_selected)],
            GET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_entered)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
"""

import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# --- API sozlamalari ---
TOKEN = '8198907146:AAHyB4w-HhVNQsed9PxHSNLFSZHximUj_0U'  # <-- O'z tokeningizni shu yerga yozing
API_BASE = "https://v6.exchangerate-api.com/v6/075da83e108bde274389c814/latest/"

# --- Qo‘llab-quvvatlanadigan yo‘nalishlar ---
SUPPORTED_DIRECTIONS = ['USD_RUB', 'RUB_USD', 'EUR_RUB']
DIRECTION_LABELS = {
    'USD_RUB': '🇺🇸USD ➡️ RUB🇷🇺',
    'RUB_USD': '🇷🇺RUB ➡️ USD',
    'EUR_RUB': '🇪🇺EUR ➡️ RUB🇷🇺',
}

# --- Valyutalar ro‘yxati ---
valyutalar = [
    {'nomi': 'АҚШ доллари', 'kodi': 'USD'},
    {'nomi': 'Евро', 'kodi': 'EUR'},
    {'nomi': 'Буюк Британия фунти', 'kodi': 'GBP'},
    {'nomi': 'Япония иенаси', 'kodi': 'JPY'},
    {'nomi': 'Швейцария франки', 'kodi': 'CHF'},
    {'nomi': 'Хитой юани', 'kodi': 'CNY'},
    {'nomi': 'Австралия доллари', 'kodi': 'AUD'},
    {'nomi': 'Канада доллари', 'kodi': 'CAD'},
    {'nomi': 'Дания кронаси', 'kodi': 'DKK'},
    {'nomi': 'Гонконг доллари', 'kodi': 'HKD'},
    {'nomi': 'Индонезия рупияси', 'kodi': 'IDR'},
    {'nomi': 'Ҳиндистон рупияси', 'kodi': 'INR'},
    {'nomi': 'Исроил янги шекели', 'kodi': 'ILS'},
    {'nomi': 'Корея чонвони', 'kodi': 'KRW'},
    {'nomi': 'Малайзия ринггити', 'kodi': 'MYR'},
    {'nomi': 'Мексика песоси', 'kodi': 'MXN'},
    {'nomi': 'Норвегия кронаси', 'kodi': 'NOK'},
    {'nomi': 'Қозоғистон тенгеси', 'kodi': 'KZT'},
    {'nomi': 'Қатар риёли', 'kodi': 'QAR'},
    {'nomi': 'Ўзбекистон сўми', 'kodi': 'UZS'},
    {'nomi': 'Саудия Арабистони риёли', 'kodi': 'SAR'},
    {'nomi': 'Сингапур доллари', 'kodi': 'SGD'},
    {'nomi': 'Хорватия кунаси', 'kodi': 'HRK'},
    {'nomi': 'Чехия кронаси', 'kodi': 'CZK'},
    {'nomi': 'Эстония песетаси', 'kodi': 'ESP'},
    {'nomi': 'Иордания динори', 'kodi': 'JOD'},
    {'nomi': 'Кения шиллинги', 'kodi': 'KES'},
    {'nomi': 'Куба песоси', 'kodi': 'CUP'},
    {'nomi': 'Марокаш дирҳами', 'kodi': 'MAD'},
    {'nomi': 'Нидерландия гулдени', 'kodi': 'NLG'},
    {'nomi': 'Покистон рупияси', 'kodi': 'PKR'},
    {'nomi': 'Панама балбоаси', 'kodi': 'PAB'},
    {'nomi': 'Перу соли', 'kodi': 'PEN'},
    {'nomi': 'Польша злотийи', 'kodi': 'PLN'},
    {'nomi': 'Руминия лейи', 'kodi': 'RON'},
    {'nomi': 'Судан фунти', 'kodi': 'SDG'},
]

# --- Holatlar ---
SELECT_DIRECTION, GET_AMOUNT = range(2)
user_context = {}

# --- Valyuta kursini olish funksiyasi ---
def get_exchange_rate(base: str, target: str) -> float | None:
    try:
        response = requests.get(f"{API_BASE}{base}", timeout=10)
        data = response.json()
        if data['result'] == 'success':
            return data['conversion_rates'].get(target)
    except:
        return None
    return None

# --- Konvertatsiya qilish ---
def convert_currency(amount: float, direction: str) -> str:
    base, target = direction.split("_")
    rate = get_exchange_rate(base, target)
    if rate is None:
        return "❌ Произошла ошибка при получении курсов."
    result = round(amount * rate, 2)
    return f"{amount} {base} ≈ {result} {target}"

# --- Valyuta yo‘nalishini tanlash uchun tugmalar ---
def get_direction_keyboard():
    buttons = [[label] for label in DIRECTION_LABELS.values()]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)

# --- Valyutalar ro‘yxatidan birini tanlash uchun tugmalar ---
def get_currency_keyboard():
    buttons = [[val['nomi']] for val in valyutalar[:5]]
    buttons.append([val['nomi'] for val in valyutalar[5:10]])
    buttons.append([val['nomi'] for val in valyutalar[10:15]])
    buttons.append([val['nomi'] for val in valyutalar[15:20]])
    buttons.append([val['nomi'] for val in valyutalar[20:]])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)

# --- /start komandasi ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💱 Выберите направление валюты:",
        reply_markup=get_direction_keyboard()
    )
    return SELECT_DIRECTION

# --- Valyuta yo‘nalishini tanlaganda ---
async def direction_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    label = update.message.text
    direction = next((k for k, v in DIRECTION_LABELS.items() if v == label), None)

    if direction is None:
        await update.message.reply_text("⚠️ Было выбрано неверное направление. Попробуйте еще раз..")
        return SELECT_DIRECTION

    user_context[update.message.from_user.id] = {'direction': direction}
    await update.message.reply_text("💰 Введите количество (только число):", reply_markup=ReplyKeyboardRemove())
    return GET_AMOUNT

# --- Miqdor kiritinganda ---
async def amount_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    direction = user_context.get(user_id, {}).get('direction')

    try:
        amount = float(update.message.text.replace(",", "."))
    except ValueError:
        await update.message.reply_text("⚠️ Просто введите число. Например: 1000")
        return GET_AMOUNT

    result_text = convert_currency(amount, direction)
    await update.message.reply_text(result_text)
    return ConversationHandler.END

# --- /cancel komandasi ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# --- Botni ishga tushirish ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_DIRECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, direction_selected)],
            GET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_entered)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
