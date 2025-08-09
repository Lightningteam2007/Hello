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
        """بارگذاری کوکی‌ها از Config.YT_COOKIES"""
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
                # تنظیمات کروم
                options = webdriver.ChromeOptions()
                # در صورت تست اولیه، headless رو غیرفعال کن
                # options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                options.add_argument(
                    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36"
                )

                driver = webdriver.Chrome(options=options)
                driver.get("https://www.youtube.com")

                # بارگذاری کوکی‌ها
                if YouTubeUploader.load_cookies(driver):
                    driver.get("https://www.youtube.com")  # رفرش برای فعال شدن کوکی‌ها

                # رفتن به صفحه آپلود
                driver.get(Config.YT_UPLOAD_URL)

                # انتخاب ورودی فایل و آپلود ویدیو
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
                ).send_keys(os.path.abspath(video_path))

                print("⏳ در حال آپلود و پردازش ویدیو...")
                time.sleep(10)

                # تنظیم عنوان
                try:
                    title_field = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((
                            By.CSS_SELECTOR, "div[aria-label='عنوان'], div[aria-label='Title']"
                        ))
                    )
                    title_field.clear()
                    title_field.send_keys(title)
                except Exception:
                    print("⚠️ فیلد عنوان پیدا نشد، احتمالاً زبان یا DOM متفاوت است.")

                # تنظیم توضیحات
                try:
                    description_field = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((
                            By.CSS_SELECTOR, "div[aria-label='توضیحات'], div[aria-label='Description']"
                        ))
                    )
                    description_field.clear()
                    description_field.send_keys(description)
                except Exception:
                    print("⚠️ فیلد توضیحات پیدا نشد، احتمالاً زبان یا DOM متفاوت است.")

                # رد کردن مراحل و انتشار
                for _ in range(3):  # سه بار "بعدی" بزن
                    try:
                        next_btn = WebDriverWait(driver, 30).until(
                            EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='next-button']"))
                        )
                        next_btn.click()
                        time.sleep(1)
                    except:
                        break

                # دکمه انتشار
                publish_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='done-button']"))
                )
                publish_button.click()

                print("✅ ویدیو منتشر شد!")
                time.sleep(5)
                return True

            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")
                time.sleep(10)
            finally:
                try:
                    driver.quit()
                except:
                    pass

        return False
