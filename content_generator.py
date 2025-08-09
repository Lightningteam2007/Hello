from config import Config
import random

class ContentGenerator:
    @staticmethod
    def generate_title(description):
        keywords = ["جالب", "خنده دار", "داغ", "ترند", "ویژه"]
        return f"شورت {random.choice(keywords)} | {description[:30]}..." if description else "شورت جدید امروز!"
    
    @staticmethod
    def generate_description(video_info):
        base = f"""
{video_info.get('description', 'ویدیوی جدید روزانه!')}

🔔 سابسکرایب کنید تا ویدیوهای بیشتری ببینید!
👍 لایک کنید اگر دوست داشتید!

{Config.CONTACT_INFO}

"""
        tags = Config.DEFAULT_TAGS.copy()
        if video_info.get('description'):
            tags.extend([word for word in video_info['description'].split() if word.startswith('#') and len(word) > 2])
        
        hashtags = " ".join(set(tags))[:500]  # محدودیت هشتگ
        return base + hashtags
