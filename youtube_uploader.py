from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os
from config import Config

class YouTubeUploader:
    @staticmethod
    def load_cookies(driver):
        if Config.YT_COOKIES:
            try:
                cookies = json.loads(Config.YT_COOKIES)
                for cookie in cookies:
                    if 'expiry' in cookie:
                        del cookie['expiry']
                    driver.add_cookie(cookie)
                return True
            except Exception as e:
                print(f"Error loading cookies: {e}")
        return False

    @staticmethod
    def upload_shorts(video_path, title, description):
        for attempt in range(Config.MAX_RETRIES):
            try:
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
                
                driver = webdriver.Chrome(options=options)
                driver.get("https://www.youtube.com")
                
                # بارگذاری کوکی‌ها
                YouTubeUploader.load_cookies(driver)
                
                # رفتن به صفحه آپلود
                driver.get(Config.YT_UPLOAD_URL)
                
                # آپلود فایل
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
                ).send_keys(os.path.abspath(video_path))
                
                # انتظار برای پردازش
                time.sleep(10)
                
                # تنظیم عنوان
                title_field = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='عنوان']"))
                title_field.clear()
                title_field.send_keys(title)
                
                # تنظیم توضیحات
                description_field = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='توضیحات']"))
                description_field.clear()
                description_field.send_keys(description)
                
                # انتشار
                publish_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'انتشار')]")))
                publish_button.click()
                
                # انتظار برای تأیید آپلود
                time.sleep(15)
                return True
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(10)
            finally:
                try:
                    driver.quit()
                except:
                    pass
                
        return False
