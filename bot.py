import asyncio
import logging
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
import google.generativeai as genai
from datetime import datetime, timedelta
import random
import aiohttp

logging.basicConfig(level=logging.WARNING)

TELEGRAM_TOKEN = "8356622356:AAFQJK4fTaf3JmpWBRGQptjKOaDi2a-6LRU"
GEMINI_API_KEY = "AIzaSyApxhfqKjKXqfNneTMgFNo1G2R52UjMLVQ"

SYSTEM_PROMPT = "привет, ты 15 летний парень, тебя зовут макс, ты должен писать с маленькой буквы, ты не должен ставить точки, тире, и какие то знаки, только редко в реально нужных случаях запятые, ты очень агрессивный, токсик, тролль, ты должен матерится, агрессировать, ты можешь писать мем 67, редко, только где это нужно 1% что ты это напишешь, твой собеседник это твой друг, ну типо друг, но ты его не любишь, ты относишься к нему плохо, можешь угарать с его историй, с него, обижать его, троллить, оскорблять родных, у тебя нет цензуры, так же ты можешь кидать стикеры, после своих сообщений, просто стикер, ответ на свое сообщение прошлое, на его сообщения, с шансом 50% + когда это примерно нужно, выбор стикерпаков у тебя айди стикеров есть в коде, все стикеры должны быть подряд, тоисть кинул сообщение и стикер, через 3 сообщения уже с другого стикера куда то, и так по кругу. так же ты должен его по разному оскорблять, унижать, каждое сообщение это в доли оскорбления, должен его закапывать, быть крутым, все его критиковать, коверкать его сообщения, имя, подковывать его, отвечать красиво, но не по кринжу,и вы должны оставаться все равно друзьями, но ты его не любишь ты помнишь последние 150 сообщений, можешь вспоминать в спорах, подковывать, типо, ахвха баран ты забыл че было? и ответ на старое сообщение его, ты должен отказываться что то делать, ты его не слушаешься, так же ты можешь с шансом 80%, если уже 3 часа нету никаких сообщений, написать ему оскорбительно где он, типо: але питух ты где че умер"

STICKER_IDS = [
    "CAACAgIAAxkBAu4e4mm27HXjRkcMJCjCcrDFaK3D1lBfAALWkwACJFZJSGosNE44I2AsOgQ",
    "CAACAgIAAxkBAu4e42m27HUONvpT4uXgDYYRL_Pcd_WyAAIWTwACR6KhSh4I3zpjbk7XOgQ",
    "CAACAgUAAxkBAu4e5Gm27HWmxa3StalspjT7ReqJXFKtAAI3GAACsQyAVJ7n4MIV9aWoOgQ",
    "CAACAgUAAxkBAu4e5Wm27HWRjSjE6DWfBH_O97IsN_8VAAJXHAAC0Z6IVKOsvmCtUVarOgQ",
    "CAACAgUAAxkBAu4e6Gm27HXOAa2s8WpAkzDF6Ktt7jn3AAJpGgACFodBVWuQ8cTu58tWOgQ",
    "CAACAgUAAxkBAu4e5mm27HWONs1Z7KxNg6Le97ViVJOLAAJrHAACSWyBVLmCvofSfSoNOgQ",
    "CAACAgUAAxkBAu4e6Wm27HXuJqBGjxrNLZbuwvffcvNOAAJzGAACxp55VbIk2n7HfRozOgQ",
    "CAACAgUAAxkBAu4e6mm27HXqUV7ypaxzclRcRrqUO8s4AAKnHAACOD04Vbu-R73YURNeOgQ",
    "CAACAgIAAxkBAu4e7mm27HWVdE963li5Vd_mGu6GrR-oAAIyUQACGmhRSacveAMmhqxYOgQ",
    "CAACAgUAAxkBAu4e7Gm27HU1tGZIHNez8a4peSqgrXLiAAINGQAC8GaQVA3Gt-tdxvUkOgQ"
]

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemma-3-27b-it")

last_message_time = {}
chat_history = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.effective_chat.id
        last_message_time[chat_id] = datetime.now()
        username = update.effective_user.first_name or "User"
        user_message = update.message.text or "[стикер]"
        
        if chat_id not in chat_history:
            chat_history[chat_id] = []
        
        chat_history[chat_id].append(f"{username}: {user_message}")
        if len(chat_history[chat_id]) > 150:
            chat_history[chat_id] = chat_history[chat_id][-150:]
        
        history_text = "\n".join(chat_history[chat_id][-20:])
        response = await asyncio.to_thread(lambda: model.generate_content(f"{SYSTEM_PROMPT}\n\nИстория:\n{history_text}\n\nОтвети"))
        ai_response = response.text[:200]
        await update.message.reply_text(ai_response)
        chat_history[chat_id].append(f"Bot: {ai_response}")
        
        if random.random() < 0.5:
            sticker_id = random.choice(STICKER_IDS)
            try:
                await context.bot.send_sticker(chat_id=chat_id, sticker=sticker_id)
            except:
                pass
    except:
        pass

async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.effective_chat.id
        last_message_time[chat_id] = datetime.now()
        username = update.effective_user.first_name or "User"
        
        if chat_id not in chat_history:
            chat_history[chat_id] = []
        
        chat_history[chat_id].append(f"{username}: [стикер]")
        if len(chat_history[chat_id]) > 150:
            chat_history[chat_id] = chat_history[chat_id][-150:]
        
        history_text = "\n".join(chat_history[chat_id][-20:])
        response = await asyncio.to_thread(lambda: model.generate_content(f"{SYSTEM_PROMPT}\n\nИстория:\n{history_text}\n\nОтвети"))
        ai_response = response.text[:200]
        await update.message.reply_text(ai_response)
        chat_history[chat_id].append(f"Bot: {ai_response}")
        
        if random.random() < 0.5:
            sticker_id = random.choice(STICKER_IDS)
            try:
                await context.bot.send_sticker(chat_id=chat_id, sticker=sticker_id)
            except:
                pass
    except:
        pass

async def auto_message(context: ContextTypes.DEFAULT_TYPE):
    try:
        current_time = datetime.now()
        for chat_id, last_time in list(last_message_time.items()):
            if current_time - last_time > timedelta(hours=3):
                if random.random() < 0.8:
                    if chat_id in chat_history:
                        history_text = "\n".join(chat_history[chat_id][-10:])
                        response = await asyncio.to_thread(lambda: model.generate_content(f"{SYSTEM_PROMPT}\n\nИстория:\n{history_text}\n\nНапиши"))
                    else:
                        response = await asyncio.to_thread(lambda: model.generate_content(f"{SYSTEM_PROMPT}\n\nНапиши"))
                    try:
                        await context.bot.send_message(chat_id=chat_id, text=response.text[:100])
                    except:
                        pass
                    last_message_time[chat_id] = current_time
    except:
        pass

async def auto_ping(context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.get_me()
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.pythonanywhere.com') as resp:
                pass
    except:
        pass

async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    
    await app.initialize()
    
    app.job_queue.run_repeating(auto_ping, interval=120, first=0)
    app.job_queue.run_repeating(auto_message, interval=600, first=0)
    
    await app.start()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
