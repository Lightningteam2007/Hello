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
            },
            delay=10,
            interpreter='nodejs'
        )
        
        try:
            url = f"https://t.me/s/{Config.CHANNEL_USERNAME}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://t.me/',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
            
            # 3 تلاش برای دریافت محتوا
            for attempt in range(1, 4):
                print(f"🔄 تلاش {attempt} از 3 برای دریافت محتوا")
                try:
                    response = scraper.get(url, headers=headers, timeout=60)
                    response.raise_for_status()
                    
                    # دیباگ: ذخیره پاسخ HTML
                    debug_filename = f"telegram_debug_{int(time.time())}.html"
                    with open(debug_filename, "w", encoding="utf-8") as f:
                        f.write(response.text)
                    print(f"💾 پاسخ HTML ذخیره شد: {debug_filename}")
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # روش‌های مختلف برای یافتن ویدیوها
                    video_elements = []
                    
                    # روش 1: پیام‌های دارای پلیر ویدیو
                    video_wrappers = soup.find_all('div', class_='tgme_widget_message_video_wrap')
                    video_elements.extend(video_wrappers)
                    
                    # روش 2: لینک‌های ویدیو
                    video_links = soup.find_all('a', href=lambda x: x and any(k in x for k in ['video', '.mp4', '.mov']))
                    video_elements.extend(video_links)
                    
                    # روش 3: تگ‌های ویدیو
                    video_tags = soup.find_all('video')
                    video_elements.extend(video_tags)
                    
                    # روش 4: پیام‌های معمولی با محتوای ویدیویی
                    messages = soup.find_all('div', class_='tgme_widget_message', limit=20)
                    
                    videos = []
                    for element in video_elements + messages:
                        try:
                            video_data = {}
                            
                            # استخراج URL ویدیو
                            if element.name == 'a':
                                video_url = element['href']
                            elif element.name == 'video':
                                video_url = element.find('source')['src'] if element.find('source') else None
                            elif 'tgme_widget_message_video_wrap' in element.get('class', []):
                                video_url = element.find('a')['href'] if element.find('a') else None
                            else:
                                video = element.find('a', class_='tgme_widget_message_video_player')
                                video_url = video['href'] if video else None
                            
                            if not video_url:
                                continue
                                
                            # استخراج تاریخ
                            date_tag = element.find('time', {'datetime': True}) or \
                                      element.find_parent('div', class_='tgme_widget_message').find('time', {'datetime': True})
                            if date_tag:
                                try:
                                    date = datetime.strptime(date_tag['datetime'], '%Y-%m-%dT%H:%M:%S%z')
                                except ValueError:
                                    date = datetime.now()
                            else:
                                date = datetime.now()
                            
                            # استخراج توضیحات
                            desc = element.find('div', class_='tgme_widget_message_text') or \
                                   element.find_parent('div', class_='tgme_widget_message').find('div', class_='tgme_widget_message_text')
                            description = desc.get_text(strip=True) if desc else "بدون توضیحات"
                            
                            videos.append({
                                'url': video_url,
                                'date': date,
                                'description': description,
                                'source': element.name
                            })
                            
                        except Exception as e:
                            print(f"⚠️ خطا در پردازش عنصر ویدیو: {str(e)}")
                            continue
                    
                    if not videos:
                        print("❌ هیچ ویدیویی در کانال یافت نشد! ساختارهای بررسی شده:")
                        print("1. div.tgme_widget_message_video_wrap")
                        print("2. a[href*='video']")
                        print("3. video tags")
                        print("4. div.tgme_widget_message")
                        return None
                        
                    # انتخاب جدیدترین ویدیو
                    latest = max(videos, key=lambda x: x['date'])
                    print(f"✅ آخرین ویدیو یافت شد (از {latest['source']}):")
                    print(f"📅 تاریخ: {latest['date']}")
                    print(f"🔗 لینک: {latest['url']}")
                    print(f"📝 توضیحات: {latest['description'][:50]}...")
                    return latest
                    
                except Exception as e:
                    print(f"⚠️ خطا در دریافت محتوا (تلاش {attempt}): {str(e)}")
                    if attempt < 3:
                        time.sleep(15)
                    continue
                    
            raise Exception("پس از 3 تلاش، دریافت ویدیو ناموفق بود")
            
        except Exception as e:
            print(f"❌ خطای کلی در دریافت محتوا: {str(e)}")
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
                    'no_warnings': True,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Referer': 'https://t.me/'
                    }
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
                    
                    with scraper.get(video_url, headers=headers, stream=True, timeout=60) as response:
                        response.raise_for_status()
                        
                        with open(filename, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
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
