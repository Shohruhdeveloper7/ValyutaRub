import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import requests
from decimal import Decimal, InvalidOperation

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
TOKEN = "8198907146:AAHyB4w-HhVNQsed9PxHSNLFSZHximUj_0U"
API_BASE = "https://v6.exchangerate-api.com/v6/075da83e108bde274389c814/latest/"


# Состояния
class CurrencyStates(StatesGroup):
    GET_AMOUNT = State()


# Поддерживаемые направления обмена
EXCHANGE_DIRECTIONS = {
    'USD_RUB': '🇺🇸 USD → RUB 🇷🇺',
    'RUB_USD': '🇷🇺 RUB → USD 🇺🇸',
    'EUR_RUB': '🇪🇺 EUR → RUB 🇷🇺',
}

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher()


# Получение курса валют
async def get_exchange_rate(base: str, target: str) -> Decimal | None:
    try:
        response = requests.get(f"{API_BASE}{base}", timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('result') == 'success':
            rate = data['conversion_rates'].get(target)
            if rate is not None:
                return Decimal(str(rate))
    except Exception as e:
        logger.error(f"Ошибка получения курса: {e}")
    return None


# Конвертация валюты
async def convert_currency(amount: Decimal, direction: str) -> str:
    base, target = direction.split("_")
    rate = await get_exchange_rate(base, target)

    if rate is None:
        return "❌ Ошибка получения курса. Попробуйте позже."

    result = (amount * rate).quantize(Decimal('0.01'))
    return f"🔹 Результат: {amount} {base} ≈ {result} {target}\n🔸 Курс: 1 {base} = {rate} {target}"


# Клавиатура с направлениями обмена
def get_exchange_keyboard():
    keyboard = [
        [KeyboardButton(text=EXCHANGE_DIRECTIONS['USD_RUB'])],
        [KeyboardButton(text=EXCHANGE_DIRECTIONS['RUB_USD'])],
        [KeyboardButton(text=EXCHANGE_DIRECTIONS['EUR_RUB'])]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


# Команда /start - главное меню
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Выберите направление обмена валют:",
        reply_markup=get_exchange_keyboard()
    )


# Обработка выбора направления
@dp.message(F.text.in_(EXCHANGE_DIRECTIONS.values()))
async def direction_selected(message: types.Message, state: FSMContext):
    # Находим код направления по тексту кнопки
    direction_code = next(k for k, v in EXCHANGE_DIRECTIONS.items() if v == message.text)

    await state.update_data(direction=direction_code)
    await message.answer(
        "Введите сумму для конвертации:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(CurrencyStates.GET_AMOUNT)


# Обработка ввода суммы
@dp.message(CurrencyStates.GET_AMOUNT)
async def amount_entered(message: types.Message, state: FSMContext):
    try:
        amount = Decimal(message.text.replace(',', '.').strip())
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
    except (ValueError, InvalidOperation):
        await message.answer("❌ Неверный формат суммы. Введите число (например: 100 или 150.50)")
        return

    data = await state.get_data()
    result = await convert_currency(amount, data['direction'])
    await message.answer(result)
    await state.clear()
    await cmd_start(message)  # Возвращаем в главное меню


# Обработка неизвестных сообщений
@dp.message()
async def unknown_message(message: types.Message):
    await message.answer("Пожалуйста, выберите направление обмена из меню:")
    await cmd_start(message)


# Запуск бота
async def main():
    # Удаляем все обновления, которые могли накопиться пока бот был оффлайн
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем поллинг
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
