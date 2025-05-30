import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

# Telegram bot tokeni environment variable orqali olinadi (Railway uchun qulay)
BOT_TOKEN = os.getenv("7669259973:AAGYMKI8EF39FGA33R-His_gENKcoMWVH54")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN muhit o'zgaruvchisi o'rnatilmagan!")

# Administratorlar ro'yxati (ID formatida)
ADMINS = [7752032178]

# Foydalanuvchilar IDlarini saqlash uchun set
foydalanuvchilar = set()

# Administrator kontakti
ADMIN_CONTACTS = """
📞 +998 94 089-81-19
"""

# /start buyrug‘i handleri
async def start_handler(message: Message):
    foydalanuvchilar.add(message.from_user.id)
    await message.answer(
        "👋 <b>Salom!</b>\n\n"
        "🛍 Kerakli mahsulot yoki xizmat nomini yozing.\n"
        "📨 Biz uni administratorlarga yetkazamiz va ular siz bilan tez orada bog‘lanadi.\n\n"
        "✏️ Marhamat, yozishni boshlang!",
        parse_mode=ParseMode.HTML
    )

# Foydalanuvchidan kelgan xabarni adminlarga yuborish
async def text_handler(message: Message, bot: Bot):
    foydalanuvchilar.add(message.from_user.id)

    user_identifier = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else f"id: <a href='tg://user?id={message.from_user.id}'>{message.from_user.id}</a>"
    )

    user_info = (
        f"💬 <b>Yangi so‘rov!</b>\n\n"
        f"👤 <b>Foydalanuvchi:</b> {user_identifier}\n"
        f"{ADMIN_CONTACTS}\n"
        f"📩 <b>Xabar:</b> <i>{message.text}</i>"
    )

    for admin_id in ADMINS:
        try:
            await bot.send_message(admin_id, user_info, parse_mode=ParseMode.HTML)
        except Exception as e:
            logging.warning(f"Admin xabarga yuborishda xatolik: {e}")

    await message.answer(
        "🆗 <b>So‘rovingiz yuborildi!</b>\n"
        "📞 So‘rovingiz bo‘yicha adminlar bilan bog'laning.\n"
        "Spam bo‘lsa ham adminlar siz bilan bog‘lanadi.",
        parse_mode=ParseMode.HTML
    )

# /reklama buyrug‘i — faqat adminlar uchun, barcha foydalanuvchilarga reklama yuboradi
async def reklama_handler(message: Message, bot: Bot):
    if message.from_user.id not in ADMINS:
        return await message.answer("🚫 Siz bu buyruqdan foydalana olmaysiz.")

    matn = message.text.replace("/reklama", "").strip()
    if not matn:
        return await message.answer("❗ Iltimos, reklama matnini yozing.\nMasalan:\n/reklama 🎉 Yangi aksiyalar boshlandi!")

    reklama_xabar = (
        "📢 <b>YANGI REKLAMA!</b>\n\n"
        f"{matn}\n\n"
        "🔔 Bizni kuzatib boring!"
    )

    count = 0
    for user_id in foydalanuvchilar:
        try:
            await bot.send_message(user_id, reklama_xabar, parse_mode=ParseMode.HTML)
            count += 1
        except Exception as e:
            logging.warning(f"Reklama yuborishda xatolik: {e}")

    await message.answer(f"✅ Reklama {count} ta foydalanuvchiga yuborildi!")

# /foydalanuvchilar buyrug‘i — adminlarga botdan foydalanganlar sonini ko‘rsatadi
async def foydalanuvchilar_handler(message: Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("🚫 Bu buyruq faqat administratorlar uchun.")

    await message.answer(
        f"👥 Botdan hozirgacha <b>{len(foydalanuvchilar)}</b> ta foydalanuvchi foydalangan.",
        parse_mode=ParseMode.HTML
    )

# Botni ishga tushirish uchun main funksiyasi
async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.message.register(start_handler, Command("start"))
    dp.message.register(reklama_handler, F.text.startswith("/reklama"))
    dp.message.register(foydalanuvchilar_handler, Command("foydalanuvchilar"))
    dp.message.register(text_handler)

    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
