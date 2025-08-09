import os
import time
from datetime import datetime
from telegram_scraper import TelegramScraper
from video_processor import VideoProcessor
from youtube_uploader import YouTubeUploader
from content_generator import ContentGenerator
from config import Config
import traceback

def main():
    print(f"{datetime.now()} - Starting YouTube Shorts Auto-Uploader")

    try:
        # دریافت آخرین ویدیو از تلگرام
        print("[INFO] Checking Telegram channel for new videos...")
        video_info = TelegramScraper.get_latest_video()

        if not video_info:
            print("[WARN] No new video found in Telegram channel.")
            return

        print(f"[INFO] Found video URL: {video_info['url']}")

        # دانلود ویدیو با yt-dlp
        video_filename = "temp_video.mp4"
        print("[INFO] Downloading video...")
        ret_code = os.system(f"yt-dlp -o {video_filename} {video_info['url']}")

        if ret_code != 0 or not os.path.exists(video_filename):
            print("[ERROR] Failed to download video.")
            return

        # پردازش ویدیو برای شورتز
        print("[INFO] Processing video for Shorts...")
        processed_path = VideoProcessor.process_for_shorts(video_filename)

        if not processed_path or not os.path.exists(processed_path):
            print("[ERROR] Failed to process video.")
            return

        # تولید محتوا
        print("[INFO] Generating metadata...")
        title = ContentGenerator.generate_title(video_info['description'])
        description = ContentGenerator.generate_description(video_info)

        # آپلود به یوتیوب
        print("[INFO] Uploading to YouTube Shorts...")
        success = YouTubeUploader.upload_shorts(processed_path, title, description)

        if success:
            print("[SUCCESS] Upload successful!")
            # پاک کردن فایل‌های موقت
            try:
                os.remove(video_filename)
                os.remove(processed_path)
                print("[INFO] Temporary files cleaned up.")
            except Exception as e:
                print(f"[WARN] Failed to clean temporary files: {e}")
        else:
            print("[ERROR] Upload failed after multiple attempts.")

    except Exception as e:
        print(f"[ERROR] Unexpected error in main process: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
