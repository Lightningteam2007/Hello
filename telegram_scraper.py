import requests
from bs4 import BeautifulSoup
from datetime import datetime
import traceback
from config import Config

class TelegramScraper:
    @staticmethod
    def get_latest_video():
        print("[INFO] Starting Telegram channel scrape...")
        try:
            response = requests.get(Config.CHANNEL_URL, timeout=15)
            response.raise_for_status()
            print("[INFO] Telegram channel page fetched successfully.")

            soup = BeautifulSoup(response.text, 'html.parser')
            videos = []

            for message in soup.find_all('div', class_='tgme_widget_message'):
                video = message.find('a', class_='tgme_widget_message_video_player')
                if video:
                    video_url = video.get('href', '')
                    date_tag = message.find('time')
                    if not date_tag:
                        print("[WARN] No date found for a video message, skipping.")
                        continue
                    date_str = date_tag.get('datetime', '')
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
                    except Exception as e:
                        print(f"[WARN] Failed to parse date '{date_str}': {e}")
                        continue

                    text_div = message.find('div', class_='tgme_widget_message_text')
                    description = text_div.get_text(strip=True) if text_div else ""
                    
                    videos.append({
                        'url': video_url,
                        'date': date,
                        'description': description
                    })

            if not videos:
                print("[WARN] No videos found in Telegram channel.")
                return None

            latest = max(videos, key=lambda x: x['date'])
            print(f"[INFO] Latest video found: {latest['url']} published at {latest['date']}")
            return latest

        except requests.Timeout:
            print("[ERROR] Request to Telegram channel timed out.")
        except requests.RequestException as e:
            print(f"[ERROR] Request exception: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error scraping Telegram: {e}")
            print(traceback.format_exc())

        return None
