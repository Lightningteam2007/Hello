import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    CHANNEL_URL = "https://t.me/s/sabok_meme"
    
    # YouTube
    YT_UPLOAD_URL = "https://www.youtube.com/shorts/upload"
    YT_COOKIES = os.getenv("YT_COOKIES", "")
    
    # Processing
    OUTPUT_DIR = "processed_videos"
    MAX_RETRIES = 3
    DELAY_BETWEEN_UPLOADS = 3600 * 8  # 8 hours
    
    # Metadata
    DEFAULT_TAGS = ["شورت", "طنز", "میم", "سرگرمی", "ایرانی"]
    CONTACT_INFO = """
📌 پیج اینستاگرام: @example
🌐 وبسایت: example.com
"""
