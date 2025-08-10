import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    CHANNEL_URL = os.getenv("CHANNEL_URL")
    if not CHANNEL_URL:
        raise ValueError("❌ CHANNEL_URL not set in .env or GitHub Secrets!")

    # YouTube
    YT_UPLOAD_URL = os.getenv("YT_UPLOAD_URL", "https://www.youtube.com/shorts/upload")
    YT_COOKIES = os.getenv("YT_COOKIES")
    if not YT_COOKIES:
        print("⚠️ YT_COOKIES not set - Manual login may be required.")

    # Processing
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "processed_videos")
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
    DELAY_BETWEEN_UPLOADS = int(os.getenv("DELAY_BETWEEN_UPLOADS", 3600 * 8))  # 8 hours

    # Metadata
    DEFAULT_TAGS = os.getenv("DEFAULT_TAGS", "شورت,طنز,میم,سرگرمی,ایرانی").split(",")
    CONTACT_INFO = os.getenv("CONTACT_INFO", "📌 پیج اینستاگرام: @example\n🌐 وبسایت: example.com")
