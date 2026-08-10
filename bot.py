import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

QUESTIONS = [
    ("Seni xursand qiladigan narsa qaysi?", ["Mehrli so'z", "Birga vaqt", "Sovg'a", "Yordam"]),
    ("Xafa bo'lganingda nimani xohlaysan?", ["Gaplashishni", "Yolg'iz qolishni", "Quchoqlashni", "Chalg'ishni"]),
    ("Munosabatda eng muhim narsa nima?", ["Ishonch", "Mehr", "Sadoqat", "Tushunish"]),
    ("Sevgan insoning senga mehrini qanday ko'rsatgani yoqadi?", ["So'z bilan", "Harakat bilan", "Vaqt ajratib", "Kutilmagan e'tibor bilan"]),
    ("Ideal uchrashuv sen uchun qanday?", ["Sayr", "Kino", "Birga ovqatlanish", "Uyda suhbat"]),
]

user_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("❤️ Roziman, boshlaymiz", callback_data="start_test")]]
    text = (
        "❤️ Munosabat testi\n\n"
        "Bu test bir-biringizni yaxshiroq tushunishga yordam beradi.\n\n"
        "⚠️ Muhim: testdagi javoblaringiz bot egasiga yuboriladi.\n"
        "Davom etish uchun roziligingizni tasdiqlang."
    )
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data == "start_test":
        user_data[user_id] = {"index": 0, "answers": []}
        await send_question(query.message, user_id)
        return

    if data.startswith("answer_"):
        answer = data.replace("answer_", "", 1)
        user_data[user_id]["answers"].append(answer)
        user_data[user_id]["index"] += 1

        if user_data[user_id]["index"] >= len(QUESTIONS):
            await finish_test(query.message, query.from_user)
        else:
            await send_question(query.message, user_id)


async def send_question(message, user_id):
    index = user_data[user_id]["index"]
    question, options = QUESTIONS[index]

    keyboard = []
    for i, option in enumerate(options):
        keyboard.append([
            InlineKeyboardButton(
                option,
                callback_data=f"answer_{i+1}"
            )
        ])

    await message.reply_text(
        f"❤️ Savol {index + 1}/{len(QUESTIONS)}\n\n{question}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def finish_test(message, user):
    answers = user_data[user.id]["answers"]

    result = (
        f"❤️ TEST YAKUNLANDI\n\n"
        f"Foydalanuvchi: {user.first_name}\n"
        f"Telegram ID: {user.id}\n\n"
        f"Javoblar:\n"
    )

    for i, answer in enumerate(answers):
        result += f"{i + 1}. {answer}\n"

    await message.reply_text(
        "❤️ Test tugadi!\n\n"
        "Javoblaringiz qabul qilindi. Rahmat 😊"
    )

    if ADMIN_ID:
        await message.get_bot().send_message(
            chat_id=ADMIN_ID,
            text=result
        )


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN topilmadi")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()


if __name__ == "__main__":
    main()
