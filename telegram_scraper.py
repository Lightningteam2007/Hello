import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
import time
import traceback
import os
import requests
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
            # 1. دریافت محتوای کانال
            url = f"https://t.me/s/{Config.CHANNEL_USERNAME}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            
            response = scraper.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # 2. تجزیه محتوا
            soup = BeautifulSoup(response.text, 'html.parser')
            messages = soup.find_all('div', class_='tgme_widget_message', limit=15)
            
            videos = []
            for message in messages:
                try:
                    # 3. استخراج اطلاعات ویدیو
                    video = message.find('a', class_='tgme_widget_message_video_player')
                    if not video:
                        continue
                        
                    video_url = video['href']
                    date_tag = message.find('time', {'datetime': True})
                    
                    if not date_tag:
                        continue
                        
                    # 4. پردازش تاریخ
                    date_str = date_tag['datetime']
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
                    except ValueError:
                        date = datetime.now()
                    
                    # 5. استخراج توضیحات
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
                
            # 6. انتخاب آخرین ویدیو
            latest = max(videos, key=lambda x: x['date'])
            print(f"✅ آخرین ویدیو: {latest['url']} (تاریخ انتشار: {latest['date']})")
            return latest
            
        except Exception as e:
            print(f"❌ خطا در دریافت محتوا: {str(e)}")
            print(traceback.format_exc())
            return None

    @staticmethod
    def download_video(video_url, output_dir="downloaded_videos"):
        """دانلود ویدیو از تلگرام و ذخیره به صورت محلی"""
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"video_{int(time.time())}.mp4")
        
        try:
            print(f"⬇️ در حال دانلود ویدیو از: {video_url}")
            scraper = cloudscraper.create_scraper()
            response = scraper.get(video_url, stream=True)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ ویدیو با موفقیت دانلود شد: {filename}")
            return filename
        except Exception as e:
            print(f"❌ خطا در دانلود ویدیو: {str(e)}")
            print(traceback.format_exc())
            return None
