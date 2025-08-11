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
        if not Config.YT_COOKIES:
            print("⚠️ No cookies provided in YT_COOKIES!")
            return False

        try:
            cookies = json.loads(Config.YT_COOKIES)
            driver.get("https://www.youtube.com")
            time.sleep(3)  # افزایش زمان انتظار
            for cookie in cookies:
                if 'expiry' in cookie:
                    del cookie['expiry']
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    print(f"⚠️ Could not add cookie: {e}")
                    continue
            driver.refresh()  # رفرش صفحه بعد از اضافه کردن کوکی‌ها
            time.sleep(3)
            print("✅ Cookies loaded successfully.")
            return True
        except Exception as e:
            print(f"❌ Failed to load cookies: {e}")
            print(traceback.format_exc())
            return False

    @staticmethod
    def check_login(driver):
        try:
            driver.get("https://www.youtube.com")
            time.sleep(5)  # افزایش زمان انتظار
            avatar = driver.find_elements(By.CSS_SELECTOR, "img#img")
            if not avatar:
                print("❌ User is NOT logged in!")
                return False
            print("✅ User is logged in.")
            return True
        except Exception as e:
            print(f"❌ Login check failed: {e}")
            print(traceback.format_exc())
            return False

    @staticmethod
    def upload_shorts(video_path, title, description):
        for attempt in range(1, Config.MAX_RETRIES + 1):
            print(f"🔄 Attempt {attempt}/{Config.MAX_RETRIES}")
            driver = None
            try:
                # تنظیمات Chrome
                options = Options()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
                options.add_argument("--disable-extensions")
                options.add_argument("--remote-debugging-port=9222")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--disable-infobars")
                options.add_argument("--start-maximized")
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option("useAutomationExtension", False)
                options.binary_location = "/usr/bin/chromium-browser"

                # استفاده از webdriver-manager
                service = Service(ChromeDriverManager().install())

                # ایجاد درایور
                driver = webdriver.Chrome(options=options, service=service)
                driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )

                # بارگیری کوکی‌ها و بررسی لاگین
                if not (YouTubeUploader.load_cookies(driver) and YouTubeUploader.check_login(driver)):
                    raise Exception("Login failed!")

                # آپلود ویدیو
                print("🌐 Navigating to YouTube upload page...")
                driver.get(Config.YT_UPLOAD_URL)
                time.sleep(15)  # افزایش زمان انتظار

                # دیباگ: ذخیره صفحه و اسکرین‌شات
                with open(f"upload_page_attempt_{attempt}.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                driver.save_screenshot(f"upload_page_attempt_{attempt}.png")

                # آپلود فایل با چندین روش مختلف
                print("📤 Uploading video file...")
                try:
                    # روش اول: استفاده از XPATH استاندارد
                    file_input = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
                    )
                except:
                    try:
                        # روش دوم: استفاده از CSS Selector
                        file_input = WebDriverWait(driver, 30).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                        )
                    except:
                        # روش سوم: استفاده از JavaScript
                        driver.execute_script('''
                            document.querySelector('input[type="file"]').style.display = 'block';
                            document.querySelector('input[type="file"]').style.visibility = 'visible';
                        ''')
                        file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")

                file_input.send_keys(os.path.abspath(video_path))
                print("✅ Video file uploaded.")
                time.sleep(5)  # انتظار برای پردازش ویدیو

                # تنظیم عنوان
                print("✏️ Setting title...")
                title_field = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@id='textbox' and @aria-label='Title']"))
                )
                title_field.clear()
                title_field.send_keys(title)

                # تنظیم توضیحات
                print("📝 Setting description...")
                description_field = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@id='textbox' and @aria-label='Description']"))
                )
                description_field.clear()
                description_field.send_keys(description)

                # کلیک روی دکمه Next (3 بار)
                for i in range(3):
                    print(f"⏭️ Clicking Next ({i+1}/3)...")
                    next_btn = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@id='next-button']"))
                    )
                    next_btn.click()
                    time.sleep(3)

                # انتشار ویدیو
                print("🚀 Publishing video...")
                publish_btn = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@id='done-button']"))
                )
                publish_btn.click()
                time.sleep(10)  # انتظار برای تکمیل آپلود
                print("✅ Video published successfully!")
                return True

            except Exception as e:
                print(f"❌ Attempt {attempt} failed: {e}")
                print(traceback.format_exc())
                if driver:
                    try:
                        driver.save_screenshot(f"error_attempt_{attempt}.png")
                        with open(f"page_source_{attempt}.html", "w", encoding="utf-8") as f:
                            f.write(driver.page_source)
                    except:
                        pass
                time.sleep(Config.DELAY_BETWEEN_ATTEMPTS)

            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass

        print("❌ All upload attempts failed!")
        return False
