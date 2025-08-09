import random
import traceback
from config import Config

class ContentGenerator:
    @staticmethod
    def generate_title(description):
        try:
            keywords = ["جالب", "خنده دار", "داغ", "ترند", "ویژه"]
            if description:
                title = f"شورت {random.choice(keywords)} | {description[:30]}..."
            else:
                title = "شورت جدید امروز!"
            print(f"[INFO] Generated title: {title}")
            return title
        except Exception as e:
            print(f"[ERROR] Failed to generate title: {e}")
            print(traceback.format_exc())
            return "شورت جدید امروز!"

    @staticmethod
    def generate_description(video_info):
        try:
            base = f"""
{video_info.get('description', 'ویدیوی جدید روزانه!')}

🔔 سابسکرایب کنید تا ویدیوهای بیشتری ببینید!
👍 لایک کنید اگر دوست داشتید!

{Config.CONTACT_INFO}

"""
            tags = Config.DEFAULT_TAGS.copy()
            if video_info.get('description'):
                extra_tags = [word for word in video_info['description'].split() if word.startswith('#') and len(word) > 2]
                tags.extend(extra_tags)

            # حذف تکراری‌ها و محدود کردن به 500 کاراکتر
            hashtags = " ".join(set(tags))[:500]

            description = base + hashtags
            print(f"[INFO] Generated description (length {len(description)}): {description[:60]}...")
            return description

        except Exception as e:
            print(f"[ERROR] Failed to generate description: {e}")
            print(traceback.format_exc())
            return "ویدیوی جدید روزانه!"
