import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
    if not CHANNEL_USERNAME:
        raise ValueError("❌ CHANNEL_USERNAME not set in .env")
    
    # YouTube
    YT_UPLOAD_URL = os.getenv("YT_UPLOAD_URL", "https://studio.youtube.com")
    YT_COOKIES = os.getenv("YT_COOKIES")
    if not YT_COOKIES:
        raise ValueError("❌ YT_COOKIES not set in .env")
    
    # Processing
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "processed_videos")
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 5))  # افزایش تعداد تلاش‌ها
    DELAY_BETWEEN_ATTEMPTS = int(os.getenv("DELAY_BETWEEN_ATTEMPTS", 30))  # افزایش زمان انتظار
    
    # Video Processing
    TARGET_HEIGHT = int(os.getenv("TARGET_HEIGHT", 1920))
    TARGET_FPS = int(os.getenv("TARGET_FPS", 60))
    BITRATE = os.getenv("BITRATE", "8000k")
    
    # Metadata
    DEFAULT_TAGS = os.getenv("DEFAULT_TAGS", "شورت,طنز,میم,سرگرمی,ایرانی").split(",")
    CONTACT_INFO = os.getenv("CONTACT_INFO", "📌 پیج اینستاگرام: @example\n🌐 وبسایت: example.com")
    
    # Selenium Settings
    WEBDRIVER_TIMEOUT = int(os.getenv("WEBDRIVER_TIMEOUT", 45))
    PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", 60))
