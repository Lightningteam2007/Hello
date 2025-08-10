import requests
from bs4 import BeautifulSoup
from datetime import datetime
import traceback
from config import Config

class TelegramScraper:
    @staticmethod
    def get_latest_video():
        print("🔍 Fetching latest video from Telegram...")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }
            response = requests.get(Config.CHANNEL_URL, headers=headers, timeout=15)
            response.raise_for_status()  # Fail if status != 200

            soup = BeautifulSoup(response.text, 'html.parser')
            videos = []

            for message in soup.find_all('div', class_='tgme_widget_message'):
                video = message.find('a', class_='tgme_widget_message_video_player')
                if video:
                    video_url = video.get("href", "")  # ✅ اصلاح: استفاده از " به جای '
                    date_tag = message.find('time')
                    if not date_tag:
                        print("⚠️ No date found for video, skipping.")
                        continue

                    date_str = date_tag.get("datetime", "")  # ✅ اصلاح: استفاده از " به جای '
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
                    except Exception as e:
                        print(f"⚠️ Failed to parse date: {e}")
                        continue

                    description = message.find('div', class_='tgme_widget_message_text').get_text(strip=True) if message.find('div', class_='tgme_widget_message_text') else "No description"
                    
                    videos.append({'url': video_url, 'date': date, 'description': description})

            if not videos:
                print("❌ No videos found in the channel!")
                return None

            latest = max(videos, key=lambda x: x['date'])
            print(f"✅ Latest video: {latest['url']} (Published: {latest['date']})")
            return latest

        except requests.Timeout:
            print("❌ Telegram request timed out!")
        except requests.RequestException as e:
            print(f"❌ Failed to fetch Telegram: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print(traceback.format_exc())

        return None
