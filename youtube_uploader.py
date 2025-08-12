from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
import traceback
from config import Config

class YouTubeUploader:
    @staticmethod
    def load_cookies(driver):
        """بارگذاری کوکی‌های یوتیوب"""
        try:
            cookies = json.loads(Config.YT_COOKIES)
            driver.get("https://www.youtube.com")
            time.sleep(3)
            
            # حذف کوکی‌های قبلی
            driver.delete_all_cookies()
            time.sleep(2)
            
            # اضافه کردن کوکی‌های جدید
            for cookie in cookies:
                if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                    cookie['sameSite'] = 'Lax'
                driver.add_cookie(cookie)
            
            driver.refresh()
            time.sleep(5)
            return True
        except Exception as e:
            print(f"خطا در بارگذاری کوکی‌ها: {str(e)}")
            return False

    @staticmethod
    def check_login(driver):
        """بررسی وضعیت ورود به سیستم"""
        try:
            driver.get("https://www.youtube.com")
            time.sleep(5)
            avatar = driver.find_elements(By.CSS_SELECTOR, "img#img")
            return len(avatar) > 0
        except:
            return False

    @staticmethod
    def upload_shorts(video_path, title, description):
        """آپلود خودکار ویدیو به یوتیوب شورت"""
        for attempt in range(1, Config.MAX_RETRIES + 1):
            print(f"\n🔄 تلاش {attempt} از {Config.MAX_RETRIES}")
            driver = None
            
            try:
                # تنظیمات کروم
                options = Options()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--headless=new")
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option("useAutomationExtension", False)
                
                # راه‌اندازی درایور
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                driver.implicitly_wait(30)
                
                # ورود به سیستم
                if not YouTubeUploader.load_cookies(driver):
                    raise Exception("ورود به یوتیوب ناموفق بود")
                
                if not YouTubeUploader.check_login(driver):
                    raise Exception("احراز هویت ناموفق")
                
                print("🔵 در حال رفتن به صفحه آپلود...")
                driver.get("https://studio.youtube.com")
                time.sleep(10)
                
                # کلیک روی دکمه ایجاد
                WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//ytcp-button[@id="create-icon"]'))
                ).click()
                time.sleep(3)
                
                # انتخاب گزینه آپلود ویدیو
                WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//ytcp-text-menu-item[@test-id="upload-beta"]'))
                ).click()
                time.sleep(10)
                
                # آپلود فایل
                print("📤 در حال آپلود ویدیو...")
                file_input = driver.find_element(By.XPATH, '//input[@type="file"]')
                file_input.send_keys(os.path.abspath(video_path))
                time.sleep(15)
                
                # تنظیم عنوان (3 روش مختلف)
                print("✏️ در حال تنظیم عنوان...")
                try:
                    title_field = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, '//div[@id="title-textarea"]//textarea'))
                    )
                    title_field.clear()
                    title_field.send_keys(title)
                except:
                    title_field = driver.find_element(By.NAME, "title")
                    title_field.send_keys(title)
                
                # تنظیم توضیحات
                print("📝 در حال تنظیم توضیحات...")
                desc_field = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@id="description-textarea"]//textarea'))
                )
                desc_field.send_keys(description)
                time.sleep(3)
                
                # کلیک روی دکمه‌های بعدی
                for _ in range(3):
                    WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, '//ytcp-button[@id="next-button"]'))
                    ).click()
                    time.sleep(5)
                
                # انتشار ویدیو
                print("🚀 در حال انتشار ویدیو...")
                WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//ytcp-button[@id="done-button"]'))
                ).click()
                time.sleep(15)
                
                print("✅ ویدیو با موفقیت آپلود شد!")
                return True
                
            except Exception as e:
                print(f"❌ خطا در تلاش {attempt}: {str(e)}")
                if driver:
                    driver.save_screenshot(f"error_attempt_{attempt}.png")
                time.sleep(Config.DELAY_BETWEEN_ATTEMPTS)
                
            finally:
                if driver:
                    driver.quit()
        
        print("❌ تمام تلاش‌ها ناموفق بودند")
        return False
