import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram channel URL
    CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/s/sabok_meme")

    # YouTube Upload URL and cookies
    YT_UPLOAD_URL = os.getenv("YT_UPLOAD_URL", "https://www.youtube.com/shorts/upload")
    YT_COOKIES = os.getenv("YT_COOKIES", "")

    # Processing parameters
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "processed_videos")
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
    DELAY_BETWEEN_UPLOADS = int(os.getenv("DELAY_BETWEEN_UPLOADS", 3600 * 8))  # seconds

    # Metadata defaults
    DEFAULT_TAGS = os.getenv("DEFAULT_TAGS", "شورت,طنز,میم,سرگرمی,ایرانی").split(",")
    CONTACT_INFO = os.getenv("CONTACT_INFO", """
📌 پیج اینستاگرام: @example
🌐 وبسایت: example.com
""")
