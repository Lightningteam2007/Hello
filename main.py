from telegram_scraper import TelegramScraper
from video_processor import VideoProcessor
from youtube_uploader import YouTubeUploader
from content_generator import ContentGenerator
import time
import os
import shutil
import traceback
from config import Config

def cleanup_temp_files():
    """پاکسازی فایل‌های موقت"""
    try:
        if os.path.exists("downloaded_videos"):
            shutil.rmtree("downloaded_videos")
        if os.path.exists(Config.OUTPUT_DIR):
            shutil.rmtree(Config.OUTPUT_DIR)
        # پاکسازی فایل‌های موقت دیگر
        for file in ["chromedriver.log", "webdriver_error.log", "error.log"]:
            if os.path.exists(file):
                os.remove(file)
        print("♻️ فایل‌های موقت با موفقیت پاکسازی شدند")
    except Exception as e:
        print(f"⚠️ خطا در پاکسازی فایل‌های موقت: {e}")
        with open("cleanup_error.log", "w") as f:
            f.write(f"Cleanup error: {str(e)}\n")
            f.write(traceback.format_exc())

def main():
    print("🚀 شروع برنامه آپلود خودکار یوتیوب شورت...")
    
    try:
        for attempt in range(1, Config.MAX_RETRIES + 1):
            print(f"\n🔹 تلاش {attempt} از {Config.MAX_RETRIES}")
            
            try:
                # 1. دریافت ویدیو از تلگرام
                video_info = TelegramScraper.get_latest_video()
                if not video_info:
                    print("❌ ویدیویی یافت نشد. خروج...")
                    return
                
                # 2. دانلود ویدیو
                print(f"📥 در حال دانلود ویدیو از تلگرام...")
                video_path = TelegramScraper.download_video(video_info['url'])
                if not video_path:
                    print("❌ دانلود ویدیو ناموفق بود. خروج...")
                    continue
                
                time.sleep(2)  # تأخیر برای اطمینان از کامل شدن نوشتن فایل
                
                # 3. پردازش ویدیو
                print(f"🔄 در حال پردازش ویدیو...")
                processed_path = VideoProcessor.process_for_shorts(video_path)
                if not processed_path:
                    print("❌ پردازش ویدیو ناموفق بود. خروج...")
                    continue
                
                # 4. تولید عنوان و توضیحات
                print(f"✍️ در حال تولید محتوا...")
                title = ContentGenerator.generate_title(video_info['description'])
                description = ContentGenerator.generate_description(video_info)
                
                # 5. آپلود به یوتیوب
                print(f"📤 در حال آپلود به یوتیوب...")
                if YouTubeUploader.upload_shorts(processed_path, title, description):
                    print("🎉 ویدیو با موفقیت به یوتیوب آپلود شد!")
                    break
                else:
                    print(f"⚠️ آپلود ناموفق. تلاش مجدد در {Config.DELAY_BETWEEN_ATTEMPTS} ثانیه...")
                    time.sleep(Config.DELAY_BETWEEN_ATTEMPTS)
                    
            except Exception as e:
                print(f"❌ خطای غیرمنتظره در تلاش {attempt}: {str(e)}")
                print(traceback.format_exc())
                with open("error.log", "a") as f:
                    f.write(f"Attempt {attempt} error: {str(e)}\n")
                    f.write(traceback.format_exc())
                time.sleep(Config.DELAY_BETWEEN_ATTEMPTS)
        
        else:
            print("❌ همه تلاش‌ها ناموفق بودند!")
            with open("error.log", "a") as f:
                f.write("All attempts failed\n")
    
    except Exception as e:
        print(f"❌ خطای اصلی در اجرای برنامه: {str(e)}")
        print(traceback.format_exc())
        with open("error.log", "w") as f:
            f.write(f"Main error: {str(e)}\n")
            f.write(traceback.format_exc())
    
    finally:
        cleanup_temp_files()

if __name__ == "__main__":
    main()
