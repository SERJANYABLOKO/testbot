import os
import random
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found!")

logging.basicConfig(level=logging.INFO)

group_photos = {}

async def handle_new_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return
    chat_id = update.effective_chat.id
    if update.message and update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
        if chat_id not in group_photos:
            group_photos[chat_id] = []
        if photo_file_id not in group_photos[chat_id]:
            group_photos[chat_id].append(photo_file_id)
            logging.info(f"Saved photo for {chat_id}")

async def sex_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ Works only in groups!")
        return
    
    chat = update.effective_chat
    users = []
    
    try:
        admins = await chat.get_administrators()
        for admin in admins:
            if not admin.user.is_bot:
                users.append(admin.user)
        
        if len(users) < 2:
            async for member in chat.get_members():
                if not member.user.is_bot:
                    users.append(member.user)
                    if len(users) >= 20:
                        break
    except Exception as e:
        await update.message.reply_text("❌ Make me an admin first!")
        return
    
    if len(users) < 2:
        await update.message.reply_text("❌ Not enough users found!")
        return
    
    user1, user2 = random.sample(users, 2)
    
    def get_name(user):
        return f"@{user.username}" if user.username else user.full_name
    
    emojis = ["🍆💦", "🔥", "😈", "🥵", "🍑", "💀", "🤯", "💢"]
    await update.message.reply_text(f"{get_name(user1)} выебал {get_name(user2)} {random.choice(emojis)}")

async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ Works only in groups!")
        return
    
    chat_id = update.effective_chat.id
    msg = await update.message.reply_text("🔍 Searching...")
    
    if chat_id in group_photos and group_photos[chat_id]:
        photo_id = random.choice(group_photos[chat_id])
        await msg.delete()
        await update.message.reply_photo(photo=photo_id, caption=f"🎲 Random photo ({len(group_photos[chat_id])} total)")
    else:
        await msg.edit_text("📭 No photos yet! Send some photos to the group first.")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ Works only in groups!")
        return
    
    chat_id = update.effective_chat.id
    count = len(group_photos.get(chat_id, []))
    await update.message.reply_text(f"📊 Stats:\nPhotos saved: {count}\n\nCommands: /sex | /video | /stats")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Commands:\n"
        "/sex - random pair\n"
        "/video - random photo\n"
        "/stats - statistics\n"
        "/help - this message\n\n"
        "⚠️ Bot needs to be admin for /sex"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("sex", sex_command))
    app.add_handler(CommandHandler("video", video_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("start", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_new_photo))
    
    print("🤖 Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
