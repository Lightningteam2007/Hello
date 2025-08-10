@staticmethod
def get_latest_video():
    print("🔍 Fetching latest video from Telegram...")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        response = requests.get(Config.CHANNEL_URL, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        videos = []

        for message in soup.find_all('div', class_='tgme_widget_message'):
            # Debug: Print message HTML for inspection
            print(f"Message HTML: {message.prettify()[:200]}...")
            
            video = message.find('a', class_='tgme_widget_message_video_player')
            if not video:
                continue
                
            video_url = video.get("href", "")
            
            # Try alternative ways to find date
            date_tag = (message.find('time', class_='tgme_widget_message_date') or 
                       message.find('time', class_='time') or
                       message.find('time'))
            
            if not date_tag:
                print("⚠️ No date tag found in message")
                continue

            date_str = date_tag.get("datetime", date_tag.get_text(strip=True))
            try:
                date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
            except ValueError:
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    print(f"⚠️ Failed to parse date '{date_str}': {e}")
                    continue

            description = message.find('div', class_='tgme_widget_message_text')
            description_text = description.get_text(strip=True) if description else "No description"
            
            videos.append({
                'url': video_url,
                'date': date,
                'description': description_text
            })

        if not videos:
            print("❌ No valid videos found in the channel!")
            return None

        latest = max(videos, key=lambda x: x['date'])
        print(f"✅ Latest video: {latest['url']} (Published: {latest['date']})")
        return latest

    except Exception as e:
        print(f"❌ Error fetching Telegram: {e}")
        print(traceback.format_exc())
        return None
