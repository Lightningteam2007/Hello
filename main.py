from telegram_scraper import TelegramScraper
from video_processor import VideoProcessor
from youtube_uploader import YouTubeUploader
from content_generator import ContentGenerator
import time
import os
from config import Config

def main():
    print("🚀 شروع برنامه آپلود خودکار یوتیوب شورت...")
    
    for attempt in range(1, Config.MAX_RETRIES + 1):
        print(f"\n🔹 تلاش {attempt} از {Config.MAX_RETRIES}")
        
        try:
            # 1. دریافت ویدیو از تلگرام
            video_info = TelegramScraper.get_latest_video()
            if not video_info:
                print("❌ ویدیویی یافت نشد. خروج...")
                return
            
            # 2. دانلود ویدیو
            video_path = TelegramScraper.download_video(video_info['url'])
            if not video_path or not os.path.exists(video_path):
                print("❌ دانلود ویدیو ناموفق بود. خروج...")
                continue
            
            # 3. پردازش ویدیو
            processed_path = VideoProcessor.process_for_shorts(video_path)
            if not processed_path or not os.path.exists(processed_path):
                print("❌ پردازش ویدیو ناموفق بود. خروج...")
                continue
            
            # 4. تولید عنوان و توضیحات
            title = ContentGenerator.generate_title(video_info['description'])
            description = ContentGenerator.generate_description(video_info)
            
            # 5. آپلود به یوتیوب
            if YouTubeUploader.upload_shorts(processed_path, title, description):
                print("🎉 ویدیو با موفقیت به یوتیوب آپلود شد!")
                
                # پاکسازی فایل‌های موقت
                try:
                    os.remove(video_path)
                    os.remove(processed_path)
                    print("♻️ فایل‌های موقت پاکسازی شدند.")
                except Exception as e:
                    print(f"⚠️ خطا در پاکسازی فایل‌های موقت: {str(e)}")
                
                break
            else:
                print(f"⚠️ آپلود ناموفق. تلاش مجدد در {Config.DELAY_BETWEEN_ATTEMPTS} ثانیه...")
                time.sleep(Config.DELAY_BETWEEN_ATTEMPTS)
                
        except Exception as e:
            print(f"❌ خطای غیرمنتظره: {str(e)}")
            print(traceback.format_exc())
            time.sleep(Config.DELAY_BETWEEN_ATTEMPTS)
    
    else:
        print("❌ همه تلاش‌ها ناموفق بودند!")

if __name__ == "__main__":
    main()
