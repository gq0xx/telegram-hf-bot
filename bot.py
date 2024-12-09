import os
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

load_dotenv()
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

print("Загрузка модели...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_auth_token=HUGGINGFACE_API_KEY)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, use_auth_token=HUGGINGFACE_API_KEY)
print("Модель загружена.")

bot = Bot(token=TELEGRAM_API_KEY)
dp = Dispatcher(bot)

CHANNEL_USERNAME = "@qqq0xx"

subscribe_keyboard = InlineKeyboardMarkup(row_width=1)
subscribe_button = InlineKeyboardButton("Подписаться", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
check_button = InlineKeyboardButton("Проверить подписку", callback_data="check_subscription")
subscribe_keyboard.add(subscribe_button, check_button)

user_subscribed = {}

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply(
        "Привет! Чтобы продолжить работу, подпишись на наш канал.",
        reply_markup=subscribe_keyboard
    )

@dp.callback_query_handler(lambda call: call.data == "check_subscription")
async def check_subscription(call: types.CallbackQuery):
    user_id = call.from_user.id
    chat_member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)

    if chat_member.status in ["member", "administrator", "creator"]:
        user_subscribed[user_id] = True
        await call.message.answer("Спасибо за подписку! Теперь я готов работать. Спроси что-нибудь.")
    else:
        user_subscribed[user_id] = False
        await call.message.answer(
            "Ты ещё не подписался на канал! Подпишись и нажми 'Проверить подписку'.",
            reply_markup=subscribe_keyboard
        )

@dp.message_handler()
async def process_message(message: types.Message):
    user_id = message.from_user.id


    if not user_subscribed.get(user_id, False):
        await message.reply(
            "Чтобы продолжить работу, подпишись на наш канал!",
            reply_markup=subscribe_keyboard
        )
        return

    user_input = message.text
    inputs = tokenizer(user_input, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=150)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    await message.reply(response)


if __name__ == "__main__":
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    executor.start_polling(dp, skip_updates=True)



