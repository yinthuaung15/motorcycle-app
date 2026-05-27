import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    BOT_USERNAME = os.getenv('BOT_USERNAME')
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    AI_MODEL = "gpt-3.5-turbo"
    
    # Admin
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    
    # Web App
    WEBAPP_URL = os.getenv('WEBAPP_URL', 'http://localhost:5000')
    PORT = int(os.getenv('PORT', 5000))
    
    # Shop Info
    SHOP_NAME = "မင်းသိင်္ခ Motorcycle Center"
    SHOP_PHONE = "09-123456789"
    SHOP_ADDRESS = "အမှတ်(၁၂၃)၊ ပြည်လမ်း၊ ရန်ကုန်"