import os
import json
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode
from config import Config
from models import motorcycle_db, order_db
from ai_engine import ai_engine

load_dotenv()

# User sessions
sessions = {}

def get_session(user_id):
    if user_id not in sessions:
        sessions[user_id] = {
            'chat_history': [],
            'pending_order': None
        }
    return sessions[user_id]

# ===== KEYBOARDS =====
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🏍️ Motorcycle များကြည့်ရန်", callback_data='bikes')],
        [InlineKeyboardButton("🔍 Brand အလိုက်ရှာရန်", callback_data='brand_menu')],
        [
            InlineKeyboardButton("💰 ဈေးနှုန်းအလိုက်", callback_data='price_menu'),
            InlineKeyboardButton("🏷️ အမျိုးအစား", callback_data='type_menu')
        ],
        [
            InlineKeyboardButton("📝 အရစ်ကျအကြောင်း", callback_data='installment'),
            InlineKeyboardButton("ℹ️ ဆိုင်အကြောင်း", callback_data='about')
        ],
        [InlineKeyboardButton("📞 ဆက်သွယ်ရန်", callback_data='contact')],
        [InlineKeyboardButton("🛒 Mini App ဖွင့်ရန်", web_app=WebAppInfo(url=Config.WEBAPP_URL))],
    ]
    return InlineKeyboardMarkup(keyboard)

def bikes_keyboard(bikes):
    keyboard = []
    for bike in bikes:
        stock_icon = "✅" if bike['stock'] > 0 else "❌"
        stock_text = f"{bike['stock']} စီး" if bike['stock'] > 0 else "ကုန်ပြီ"
        keyboard.append([
            InlineKeyboardButton(
                f"{stock_icon} {bike['brand']} {bike['model']} - {bike['price']:,} Ks ({stock_text})",
                callback_data=f"bike_{bike['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton("◀️ ပင်မစာမျက်နှာ", callback_data='main')])
    return InlineKeyboardMarkup(keyboard)

def brand_keyboard():
    brands = list(set(b['brand'] for b in motorcycle_db.get_all()))
    keyboard = [[InlineKeyboardButton(brand, callback_data=f"brand_{brand}")] for brand in brands]
    keyboard.append([InlineKeyboardButton("◀️ နောက်သို့", callback_data='main')])
    return InlineKeyboardMarkup(keyboard)

def type_keyboard():
    types = list(set(b['bike_type'] for b in motorcycle_db.get_all()))
    keyboard = [[InlineKeyboardButton(t, callback_data=f"type_{t}")] for t in types]
    keyboard.append([InlineKeyboardButton("◀️ နောက်သို့", callback_data='main')])
    return InlineKeyboardMarkup(keyboard)

def bike_detail_keyboard(bike_id):
    bike = motorcycle_db.get_by_id(bike_id)
    keyboard = []
    if bike and bike['stock'] > 0:
        keyboard.append([InlineKeyboardButton("🛒 ဒီမော်ဒယ်ဝယ်မယ်", callback_data=f"buy_{bike_id}")])
    else:
        keyboard.append([InlineKeyboardButton("📝 ကြိုတင်မှာယူမယ်", callback_data=f"preorder_{bike_id}")])
    keyboard.append([InlineKeyboardButton("💬 မေးမယ်", callback_data=f"ask_{bike_id}")])
    keyboard.append([InlineKeyboardButton("◀️ Motorcycle စာရင်း", callback_data='bikes')])
    return InlineKeyboardMarkup(keyboard)

# ===== COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    session = get_session(user.id)
    session['chat_history'] = []
    
    welcome = f"""
🏍️ **{Config.SHOP_NAME}** မှ ကြိုဆိုပါတယ် {user.first_name} ခင်ဗျာ!

✅ **ကျွန်တော်တို့ဆိုင်ရဲ့ အားသာချက်များ**
• Brand စုံ - Honda, Yamaha, Suzuki, CFMoto
• ဈေးနှုန်းသက်သာ
• အရစ်ကျစနစ်ဖြင့် ဝယ်ယူနိုင်
• Showroom လာရောက်စမ်းမောင်းနိုင်သည်
• After Sales Service အပြည့်အဝ

💡 **ဘယ်လိုသုံးမလဲ?**
• Menu မှ ရွေးချယ်နိုင်ပါတယ်
• စာရိုက်ပြီး တိုက်ရိုက်မေးနိုင်ပါတယ်
• AI က သင့်အတွက် အကောင်းဆုံးမော်ဒယ်ကို ညွှန်းပေးပါမယ်

🛒 Mini App မှာလည်း ဝယ်ယူနိုင်ပါတယ်!
    """
    
    await update.message.reply_text(
        welcome,
        reply_markup=main_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle customer messages"""
    user_message = update.message.text
    user = update.effective_user
    chat_id = update.effective_chat.id
    session = get_session(user.id)
    
    # Check order confirmation
    if user_message.upper() in ['YES', 'အတည်ပြုပါတယ်', 'ဟုတ်ကဲ့', 'OK'] and session.get('pending_order'):
        return await confirm_order(update, context)
    
    # Show typing
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    # Get AI reply
    ai_reply = ai_engine.generate_reply(user_message, session['chat_history'], user.first_name)
    
    # Save history
    session['chat_history'].append({"role": "user", "content": user_message})
    session['chat_history'].append({"role": "assistant", "content": ai_reply})
    
    if len(session['chat_history']) > 20:
        session['chat_history'] = session['chat_history'][-20:]
    
    # Check if AI is confirming an order
    if 'အတည်ပြုချက်' in ai_reply or 'YES' in ai_reply:
        # Try to extract order info
        import re
        brand_match = re.search(r'🏍️\s*(.+?)(?:\n|$)', ai_reply)
        if brand_match:
            bike_name = brand_match.group(1).strip()
            bike = motorcycle_db.search(bike_name.split()[0] if bike_name.split() else bike_name)
            if bike:
                session['pending_order'] = {
                    'bike_id': bike[0]['id'],
                    'brand': bike[0]['brand'],
                    'model': bike[0]['model'],
                    'price': bike[0]['price']
                }
    
    await update.message.reply_text(ai_reply, reply_markup=main_menu())

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and save order"""
    user = update.effective_user
    session = get_session(user.id)
    order = session['pending_order']
    
    bike = motorcycle_db.get_by_id(order['bike_id'])
    
    if not bike or bike['stock'] <= 0:
        await update.message.reply_text(
            "စိတ်မကောင်းပါဘူးခင်ဗျာ... လက်ရှိလက်ကျန်မရှိတော့ပါ 😔",
            reply_markup=main_menu()
        )
        session['pending_order'] = None
        return
    
    # Reduce stock
    motorcycle_db.update_stock(order['bike_id'], 1, 'remove')
    
    # Save order
    order_record = {
        'user_id': user.id,
        'user_name': user.full_name,
        'username': user.username or '',
        'bike_id': bike['id'],
        'brand': bike['brand'],
        'model': bike['model'],
        'price': bike['price'],
        'quantity': 1,
        'total': bike['price'],
        'payment_method': 'Cash',
        'customer_name': user.full_name,
        'phone': '',
        'address': '',
        'status': 'confirmed'
    }
    order_db.add(order_record)
    
    # Notify admin
    admin_id = os.getenv('ADMIN_IDS', '').split(',')[0]
    if admin_id:
        try:
            await context.bot.send_message(
                int(admin_id),
                f"🔔 **အော်ဒါအသစ်!**\n\n"
                f"👤 {user.full_name} (@{user.username})\n"
                f"🏍️ {bike['brand']} {bike['model']}\n"
                f"💰 {bike['price']:,} Ks\n"
                f"📅 {order_record['created_at']}",
                parse_mode=ParseMode.MARKDOWN
            )
        except:
            pass
    
    await update.message.reply_text(
        f"✅ **အော်ဒါအတည်ပြုပြီးပါပြီ!**\n\n"
        f"🏍️ {bike['brand']} {bike['model']}\n"
        f"💰 {bike['price']:,} Ks\n\n"
        f"📞 {Config.SHOP_PHONE} သို့ ဆက်သွယ်ပါ\n"
        f"📍 {Config.SHOP_ADDRESS}\n\n"
        f"ကျေးဇူးတင်ပါတယ်ခင်ဗျာ! 🙏",
        reply_markup=main_menu(),
        parse_mode=ParseMode.MARKDOWN
    )
    
    session['pending_order'] = None

# ===== CALLBACKS =====
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == 'main':
        await query.edit_message_text(
            "🏍️ **Menu**\nအောက်မှ ရွေးချယ်ပါ 👇",
            reply_markup=main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == 'bikes':
        bikes = motorcycle_db.get_available()
        if not bikes:
            await query.edit_message_text(
                "လက်ရှိလက်ကျန်မရှိသေးပါ 😔\nမကြာခင်ပြန်ဖြည့်ပါမည်",
                reply_markup=main_menu()
            )
        else:
            await query.edit_message_text(
                "🏍️ **လက်ကျန်ရှိသော Motorcycle များ**",
                reply_markup=bikes_keyboard(bikes),
                parse_mode=ParseMode.MARKDOWN
            )
    
    elif data.startswith('bike_'):
        bike_id = int(data.split('_')[1])
        bike = motorcycle_db.get_by_id(bike_id)
        
        if bike:
            stock_status = f"✅ {bike['stock']} စီးကျန်" if bike['stock'] > 0 else "❌ ကုန်သွားပါပြီ"
            
            detail = f"""
🏍️ **{bike['brand']} {bike['model']}** ({bike['year']})

📋 **အသေးစိတ်**
• အမျိုးအစား: {bike['bike_type']}
• အင်ဂျင်: {bike['engine']}
• အရောင်: {bike['color']}
• အာမခံ: {bike['warranty']}

⭐ **ထူးခြားချက်များ**
{chr(10).join(['• ' + f for f in bike['features']])}

💰 **ဈေးနှုန်း**
• Cash: **{bike['price']:,} Ks**
• စရံ: {bike['installment_down']:,} Ks
• လစဉ်: {bike['installment_monthly']:,} Ks × {bike['installment_period']}လ

📊 **လက်ကျန်**: {stock_status}

📝 {bike['description']}
            """
            await query.edit_message_text(
                detail,
                reply_markup=bike_detail_keyboard(bike_id),
                parse_mode=ParseMode.MARKDOWN
            )
    
    elif data.startswith('buy_'):
        bike_id = int(data.split('_')[1])
        bike = motorcycle_db.get_by_id(bike_id)
        
        if not bike or bike['stock'] <= 0:
            await query.answer("စိတ်မကောင်းပါဘူး... ကုန်သွားပါပြီ 😔", show_alert=True)
            return
        
        user_id = update.effective_user.id
        sessions[user_id] = sessions.get(user_id, {'chat_history': [], 'pending_order': None})
        sessions[user_id]['pending_order'] = {
            'bike_id': bike_id,
            'brand': bike['brand'],
            'model': bike['model'],
            'price': bike['price']
        }
        
        await query.edit_message_text(
            f"🛒 **{bike['brand']} {bike['model']}** ဝယ်ယူရန်\n\n"
            f"💰 ဈေးနှုန်း: **{bike['price']:,} Ks**\n\n"
            f"အတည်ပြုရန် **YES** ဟုရိုက်ထည့်ပါ",
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == 'brand_menu':
        await query.edit_message_text("🏍️ **Brand ရွေးပါ**", reply_markup=brand_keyboard())
    
    elif data.startswith('brand_'):
        brand = data.split('_')[1]
        bikes = [b for b in motorcycle_db.get_all() if b['brand'].lower() == brand.lower()]
        await query.edit_message_text(f"🏍️ **{brand}**", reply_markup=bikes_keyboard(bikes))
    
    elif data == 'type_menu':
        await query.edit_message_text("🏍️ **အမျိုးအစားရွေးပါ**", reply_markup=type_keyboard())
    
    elif data.startswith('type_'):
        bike_type = data.split('_', 1)[1]
        bikes = [b for b in motorcycle_db.get_all() if bike_type.lower() in b['bike_type'].lower()]
        await query.edit_message_text(f"🏍️ **{bike_type}**", reply_markup=bikes_keyboard(bikes))
    
    elif data == 'installment':
        await query.edit_message_text(
            "📝 **အရစ်ကျစနစ်**\n\n"
            "• စရံ ၂၀-၃၀% ပေးသွင်းရုံဖြင့် ရယူနိုင်ပါတယ်\n"
            "• ၁၂လ၊ ၁၈လ၊ ၂၄လ ပေးသွင်းနိုင်ပါတယ်\n"
            "• အတိုးနှုန်းသက်သာပါတယ်\n\n"
            "**လိုအပ်သောစာရွက်စာတမ်းများ**\n"
            "• မှတ်ပုံတင်မိတ္တူ\n• အိမ်ထောင်စုစာရင်းမိတ္တူ\n• ဝင်ငွေအထောက်အထား\n\n"
            f"📞 {Config.SHOP_PHONE}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ နောက်သို့", callback_data='main')]]),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == 'about':
        await query.edit_message_text(
            f"ℹ️ **{Config.SHOP_NAME}**\n\n"
            f"📍 {Config.SHOP_ADDRESS}\n"
            f"📞 {Config.SHOP_PHONE}\n"
            f"🕐 မနက် ၉ မှ ညနေ ၅ နာရီ\n\n"
            "• Showroom လာကြည့်နိုင်ပါတယ်\n"
            "• Test Ride စမ်းမောင်းနိုင်ပါတယ်\n"
            "• Service Center ရှိပါတယ်",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ နောက်သို့", callback_data='main')]]),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == 'contact':
        await query.edit_message_text(
            "📞 **ဆက်သွယ်ရန်**\n\n"
            f"• ဖုန်း: {Config.SHOP_PHONE}\n"
            f"• Telegram: @{Config.BOT_USERNAME}\n"
            f"• လိပ်စာ: {Config.SHOP_ADDRESS}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ နောက်သို့", callback_data='main')]]),
            parse_mode=ParseMode.MARKDOWN
        )

# ===== MAIN =====
def main():
    app = Application.builder().token(Config.BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    print("🏍️ Motorcycle Sales Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()