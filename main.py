from telegram_scraper import TelegramScraper
from video_processor import VideoProcessor
from youtube_uploader import YouTubeUploader
from content_generator import ContentGenerator
import os
import time
from config import Config

def main():
    print("🚀 Starting YouTube Shorts Auto-Uploader...")
    
    # Step 1: Fetch latest video from Telegram
    video_info = TelegramScraper.get_latest_video()
    if not video_info:
        print("❌ No video found. Exiting.")
        return

    # Step 2: Process video for Shorts
    processed_video = VideoProcessor.process_for_shorts(video_info['url'])
    if not processed_video:
        print("❌ Video processing failed. Exiting.")
        return

    # Step 3: Generate title & description
    title = ContentGenerator.generate_title(video_info['description'])
    description = ContentGenerator.generate_description(video_info)

    # Step 4: Upload to YouTube
    if not YouTubeUploader.upload_shorts(processed_video, title, description):
        print("❌ Upload failed after all retries.")
    else:
        print("🎉 Successfully uploaded video to YouTube!")

if __name__ == "__main__":
    main()
