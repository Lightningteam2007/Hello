from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager  # اضافه شده
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
            time.sleep(2)
            for cookie in cookies:
                if 'expiry' in cookie:
                    del cookie['expiry']
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    print(f"⚠️ Could not add cookie: {e}")
                    continue
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
            time.sleep(3)
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
                options.binary_location = "/usr/bin/chromium-browser"

                # استفاده از webdriver-manager برای مدیریت Chromedriver
                service = Service(ChromeDriverManager().install())

                # ایجاد درایور
                try:
                    driver = webdriver.Chrome(options=options, service=service)
                    driver.execute_script(
                        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                    )
                except Exception as e:
                    print(f"❌ Failed to initialize Chrome: {str(e)}")
                    with open("webdriver_error.log", "w") as f:
                        f.write(f"Driver init error: {str(e)}\n")
                    raise

                driver.maximize_window()

                # بارگیری کوکی‌ها و بررسی لاگین
                if not (YouTubeUploader.load_cookies(driver) and YouTubeUploader.check_login(driver)):
                    raise Exception("Login failed!")

                # آپلود ویدیو
                print("🌐 Navigating to YouTube upload page...")
                driver.get(Config.YT_UPLOAD_URL)
                time.sleep(3)

                # آپلود فایل
                print("📤 Uploading video file...")
                file_input = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
                )
                file_input.send_keys(os.path.abspath(video_path))
                print("✅ Video file uploaded.")

                # تنظیم عنوان
                print("✏️ Setting title...")
                title_field = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Title']"))
                )
                title_field.clear()
                title_field.send_keys(title)

                # تنظیم توضیحات
                print("📝 Setting description...")
                description_field = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Description']"))
                )
                description_field.clear()
                description_field.send_keys(description)

                # کلیک روی دکمه Next (3 بار)
                for i in range(3):
                    print(f"⏭️ Clicking Next ({i+1}/3)...")
                    next_btn = WebDriverWait(driver, 60).until(
                        EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='next-button']"))
                    )
                    next_btn.click()
                    time.sleep(2)

                # انتشار ویدیو
                print("🚀 Publishing video...")
                publish_btn = WebDriverWait(driver, 60).until(
                    EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='done-button']"))
                )
                publish_btn.click()
                print("✅ Video published successfully!")
                return True

            except Exception as e:
                print(f"❌ Attempt {attempt} failed: {e}")
                print(traceback.format_exc())
                if driver:
                    try:
                        driver.save_screenshot(f"error_attempt_{attempt}.png")
                    except:
                        pass
                time.sleep(10)

            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass

        print("❌ All upload attempts failed!")
        return False
