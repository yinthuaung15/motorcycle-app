# bot.py - Telegram Bot for Motorcycle Mini App

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# ==================== LOGGING ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================
# 🔑 ဒီမှာ သင့် Token နဲ့ URL ထည့်ပါ

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"           # @BotFather မှရတဲ့ Token
ADMIN_ID = 123456789                         # သင့် Telegram User ID
GITHUB_PAGES_URL = "https://your-username.github.io/motorcycle-app"  # သင့် GitHub Pages URL

# ==================== START COMMAND ====================

def start(update: Update, context: CallbackContext):
    """Handle /start command"""
    user = update.effective_user
    is_admin = user.id == ADMIN_ID
    
    if is_admin:
        # Admin အတွက် Menu
        keyboard = [
            [InlineKeyboardButton("📊 Admin Panel", web_app=WebAppInfo(url=f"{GITHUB_PAGES_URL}/admin.html"))],
            [InlineKeyboardButton("🏍️ User View", web_app=WebAppInfo(url=f"{GITHUB_PAGES_URL}/index.html"))],
            [InlineKeyboardButton("ℹ️ အကူအညီ", callback_data="help")]
        ]
        text = (
            f"🔑 *Admin Mode*\n\n"
            f"မင်္ဂလာပါ {user.first_name}!\n\n"
            f"• Admin Panel - ဆိုင်ကယ်ဒေတာများ စီမံရန်\n"
            f"• User View - User မြင်ကွင်း ကြည့်ရန်"
        )
    else:
        # User အတွက် Menu
        keyboard = [
            [InlineKeyboardButton("🏍️ ဆိုင်ကယ်များကြည့်ရန်", web_app=WebAppInfo(url=f"{GITHUB_PAGES_URL}/index.html"))],
            [InlineKeyboardButton("ℹ️ အကူအညီ", callback_data="help")]
        ]
        text = (
            f"🏍️ *Motorcycle Price App*\n\n"
            f"မင်္ဂလာပါ {user.first_name}!\n\n"
            f"ဆိုင်ကယ်ဈေးနှုန်းများနှင့် လက်ကျန်များကို ကြည့်ရှုနိုင်ပါသည်။\n\n"
            f"အောက်ပါ ခလုတ်ကို နှိပ်ပါ -"
        )
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


# ==================== HELP CALLBACK ====================

def help_callback(update: Update, context: CallbackContext):
    """Handle help button"""
    query = update.callback_query
    query.answer()
    
    help_text = (
        "🆘 *အကူအညီ*\n\n"
        "*User များအတွက် -*\n"
        "• 🏍️ Mini App ဖွင့်ပြီး ဆိုင်ကယ်များကြည့်နိုင်ပါသည်\n"
        "• 🔍 အမည်/Brand ဖြင့် ရှာဖွေနိုင်ပါသည်\n"
        "• 📂 အမျိုးအစားအလိုက် စစ်ကြည့်နိုင်ပါသည်\n"
        "• 🟢 လက်ကျန်ရှိမရှိ သိနိုင်ပါသည်\n\n"
        "*Admin များအတွက် -*\n"
        "• 📊 Admin Panel မှ ဒေတာများ စီမံနိုင်ပါသည်\n"
        "• ➕ ဆိုင်ကယ်အသစ်ထည့်နိုင်ပါသည်\n"
        "• ✏️ ဈေးနှုန်း/လက်ကျန် ပြင်ဆင်နိုင်ပါသည်\n"
        "• 🗑️ ဆိုင်ကယ်ဖျက်နိုင်ပါသည်\n\n"
        "📞 ဆက်သွယ်ရန်: @YourUsername"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 နောက်သို့", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)


# ==================== BACK CALLBACK ====================

def back_callback(update: Update, context: CallbackContext):
    """Handle back button"""
    query = update.callback_query
    query.answer()
    
    user = query.from_user
    is_admin = user.id == ADMIN_ID
    
    if is_admin:
        keyboard = [
            [InlineKeyboardButton("📊 Admin Panel", web_app=WebAppInfo(url=f"{GITHUB_PAGES_URL}/admin.html"))],
            [InlineKeyboardButton("🏍️ User View", web_app=WebAppInfo(url=f"{GITHUB_PAGES_URL}/index.html"))],
            [InlineKeyboardButton("ℹ️ အကူအညီ", callback_data="help")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🏍️ ဆိုင်ကယ်များကြည့်ရန်", web_app=WebAppInfo(url=f"{GITHUB_PAGES_URL}/index.html"))],
            [InlineKeyboardButton("ℹ️ အကူအညီ", callback_data="help")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        "🏍️ *Motorcycle Price App*\n\nအောက်ပါ Menu မှ ရွေးချယ်ပါ -",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


# ==================== ERROR HANDLER ====================

def error_handler(update: Update, context: CallbackContext):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")


# ==================== MAIN ====================

def main():
    """Main function - Run the bot"""
    
    # Check configuration
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("=" * 50)
        print("❌ BOT_TOKEN ထည့်သွင်းရန် လိုအပ်ပါသည်!")
        print("@BotFather မှ Token ရယူပြီး bot.py ထဲတွင် ထည့်ပါ")
        print("=" * 50)
        return
    
    if GITHUB_PAGES_URL == "https://your-username.github.io/motorcycle-app":
        print("=" * 50)
        print("⚠️ GITHUB_PAGES_URL ထည့်သွင်းရန် အကြံပြုပါသည်")
        print("GitHub Pages URL ကို bot.py ထဲတွင် ထည့်ပါ")
        print("=" * 50)
    
    # Create Updater
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(help_callback, pattern="help"))
    dp.add_handler(CallbackQueryHandler(back_callback, pattern="back"))
    dp.add_error_handler(error_handler)
    
    # Start bot
    print("=" * 50)
    print("✅ Bot is running...")
    print(f"📱 User View: {GITHUB_PAGES_URL}/index.html")
    print(f"🔧 Admin Panel: {GITHUB_PAGES_URL}/admin.html")
    print("Ctrl+C နှိပ်ရင် ရပ်သွားပါမယ်")
    print("=" * 50)
    
    updater.start_polling()
    updater.idle()


# ==================== RUN ====================

if __name__ == '__main__':
    main()
