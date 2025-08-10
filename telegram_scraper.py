import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
import time
import os
import traceback
import subprocess
from config import Config

class TelegramScraper:
    @staticmethod
    def get_latest_video():
        print("🔍 در حال دریافت آخرین ویدیو از تلگرام...")
        
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        try:
            url = f"https://t.me/s/{Config.CHANNEL_USERNAME}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            
            response = scraper.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            messages = soup.find_all('div', class_='tgme_widget_message', limit=15)
            
            videos = []
            for message in messages:
                try:
                    video = message.find('a', class_='tgme_widget_message_video_player')
                    if not video:
                        continue
                        
                    video_url = video['href']
                    date_tag = message.find('time', {'datetime': True})
                    
                    if not date_tag:
                        continue
                        
                    date_str = date_tag['datetime']
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
                    except ValueError:
                        date = datetime.now()
                    
                    desc = message.find('div', class_='tgme_widget_message_text')
                    description = desc.get_text(strip=True) if desc else "بدون توضیحات"
                    
                    videos.append({
                        'url': video_url,
                        'date': date,
                        'description': description
                    })
                    
                except Exception as e:
                    print(f"⚠️ خطا در پردازش پیام: {str(e)}")
                    continue
            
            if not videos:
                print("❌ هیچ ویدیویی در کانال یافت نشد!")
                return None
                
            latest = max(videos, key=lambda x: x['date'])
            print(f"✅ آخرین ویدیو: {latest['url']} (تاریخ انتشار: {latest['date']})")
            return latest
            
        except Exception as e:
            print(f"❌ خطا در دریافت محتوا: {str(e)}")
            print(traceback.format_exc())
            return None

    @staticmethod
    def download_video(video_url, output_dir="downloaded_videos"):
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"video_{int(time.time())}.mp4")
        
        try:
            print(f"⬇️ در حال دانلود ویدیو از: {video_url}")
            
            # استفاده از ffmpeg برای دانلود مستقیم با کنترل کیفیت
            cmd = [
                'ffmpeg',
                '-i', video_url,
                '-c', 'copy',
                '-movflags', 'faststart',
                filename
            ]
            
            result = subprocess.run(
                cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"خطای FFmpeg: {result.stderr}")
            
            # بررسی صحت فایل
            if not os.path.exists(filename) or os.path.getsize(filename) == 0:
                raise ValueError("فایل دانلود شده نامعتبر است!")
            
            print(f"✅ ویدیو با موفقیت دانلود شد: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ خطا در دانلود ویدیو: {str(e)}")
            if os.path.exists(filename):
                os.remove(filename)
            return None
