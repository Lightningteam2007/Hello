import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from config import Config

class TelegramScraper:
    @staticmethod
    def get_latest_video():
        try:
            response = requests.get(Config.CHANNEL_URL, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            videos = []
            
            for message in soup.find_all('div', class_='tgme_widget_message'):
                if video := message.find('a', class_='tgme_widget_message_video_player'):
                    video_url = video['href']
                    date_str = message.find('time')['datetime']
                    date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
                    text = message.find('div', class_='tgme_widget_message_text')
                    description = text.get_text(strip=True) if text else ""
                    
                    videos.append({
                        'url': video_url,
                        'date': date,
                        'description': description
                    })
            
            if videos:
                latest = max(videos, key=lambda x: x['date'])
                return latest
                
        except Exception as e:
            print(f"Error scraping Telegram: {e}")
        
        return None
