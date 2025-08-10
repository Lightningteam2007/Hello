import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # فقط نام کاربری کانال بدون @
    if not CHANNEL_USERNAME:
        raise ValueError("❌ CHANNEL_USERNAME not set in .env")
    
    # YouTube
    YT_UPLOAD_URL = os.getenv("YT_UPLOAD_URL", "https://www.youtube.com/shorts/upload")
    YT_COOKIES = os.getenv("YT_COOKIES")  # اختیاری
    
    # Processing
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "processed_videos")
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
    DELAY_BETWEEN_ATTEMPTS = int(os.getenv("DELAY_BETWEEN_ATTEMPTS", 10))  # 10 ثانیه
    
    # Metadata
    DEFAULT_TAGS = os.getenv("DEFAULT_TAGS", "شورت,طنز,میم,سرگرمی,ایرانی").split(",")
    CONTACT_INFO = os.getenv("CONTACT_INFO", "📌 پیج اینستاگرام: @example\n🌐 وبسایت: example.com")
