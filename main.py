import os
import time
from datetime import datetime
from telegram_scraper import TelegramScraper
from video_processor import VideoProcessor
from youtube_uploader import YouTubeUploader
from content_generator import ContentGenerator
from config import Config

def main():
    print(f"{datetime.now()} - Starting YouTube Shorts Auto-Uploader")
    
    # دریافت آخرین ویدیو از تلگرام
    print("Checking Telegram channel for new videos...")
    video_info = TelegramScraper.get_latest_video()
    
    if not video_info:
        print("No video found in Telegram channel")
        return
    
    print(f"Found video: {video_info['url']}")
    
    # دانلود ویدیو (با youtube-dl)
    print("Downloading video...")
    os.system(f"yt-dlp -o 'temp_video.mp4' {video_info['url']}")
    
    if not os.path.exists("temp_video.mp4"):
        print("Failed to download video")
        return
    
    # پردازش ویدیو برای شورتز
    print("Processing video for Shorts...")
    processed_path = VideoProcessor.process_for_shorts("temp_video.mp4")
    
    if not processed_path or not os.path.exists(processed_path):
        print("Failed to process video")
        return
    
    # تولید محتوا
    print("Generating metadata...")
    title = ContentGenerator.generate_title(video_info['description'])
    description = ContentGenerator.generate_description(video_info)
    
    # آپلود به یوتیوب
    print("Uploading to YouTube Shorts...")
    if YouTubeUploader.upload_shorts(processed_path, title, description):
        print("Upload successful!")
        
        # پاک کردن فایل‌های موقت
        try:
            os.remove("temp_video.mp4")
            os.remove(processed_path)
        except:
            pass
    else:
        print("Upload failed after multiple attempts")

if __name__ == "__main__":
    main()
