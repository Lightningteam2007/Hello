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
            
            # روش اول: استفاده از yt-dlp (اولویت اصلی)
            try:
                import yt_dlp
                ydl_opts = {
                    'outtmpl': filename,
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'retries': 3,
                    'quiet': True,
                    'no_warnings': True
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                
                # بررسی صحت فایل دانلود شده
                if not os.path.exists(filename) or os.path.getsize(filename) == 0:
                    raise ValueError("فایل دانلود شده نامعتبر است!")
                
                # بررسی با FFprobe
                cmd = ['ffprobe', '-v', 'error', '-i', filename]
                result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                if result.returncode != 0:
                    raise ValueError(f"فایل ویدیو معتبر نیست: {result.stderr.decode()}")
                
                print(f"✅ ویدیو با yt-dlp دانلود شد: {filename}")
                return filename
                
            except Exception as e:
                print(f"⚠️ خطا در دانلود با yt-dlp: {e}")
                if os.path.exists(filename):
                    os.remove(filename)
                
                # روش دوم: استفاده از cloudscraper (رزرو)
                try:
                    scraper = cloudscraper.create_scraper()
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Referer': 'https://t.me/',
                        'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5'
                    }
                    
                    with scraper.get(video_url, headers=headers, stream=True, timeout=30) as response:
                        response.raise_for_status()
                        
                        with open(filename, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                    
                    # بررسی مضاعف فایل
                    if os.path.getsize(filename) == 0:
                        raise ValueError("فایل دانلود شده خالی است!")
                        
                    print(f"✅ ویدیو با cloudscraper دانلود شد: {filename}")
                    return filename
                    
                except Exception as e:
                    print(f"⚠️ خطا در روش دوم دانلود: {e}")
                    if os.path.exists(filename):
                        os.remove(filename)
                    raise
                    
        except Exception as e:
            print(f"❌ خطا در دانلود ویدیو: {str(e)}")
            if os.path.exists(filename):
                os.remove(filename)
            return None
