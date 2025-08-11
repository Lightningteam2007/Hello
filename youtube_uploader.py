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
            time.sleep(5)
            for cookie in cookies:
                if 'expiry' in cookie:
                    del cookie['expiry']
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    print(f"⚠️ Could not add cookie: {e}")
                    continue
            driver.refresh()
            time.sleep(5)
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
            time.sleep(5)
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

                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(options=options, service=service)
                driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )

                if not (YouTubeUploader.load_cookies(driver) and YouTubeUploader.check_login(driver)):
                    raise Exception("Login failed!")

                print("🌐 Navigating to YouTube upload page...")
                driver.get(Config.YT_UPLOAD_URL)
                time.sleep(20)  # افزایش زمان انتظار

                # دیباگ
                with open(f"upload_page_{attempt}.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                driver.save_screenshot(f"upload_page_{attempt}.png")

                # روش جدید برای آپلود فایل
                print("📤 Uploading video file...")
                try:
                    # روش 1: استفاده از JavaScript برای ایجاد input
                    driver.execute_script('''
                        const input = document.createElement('input');
                        input.type = 'file';
                        input.id = 'custom-file-upload';
                        input.style.display = 'block';
                        input.style.visibility = 'visible';
                        input.style.position = 'absolute';
                        input.style.top = '0';
                        input.style.left = '0';
                        input.style.width = '100%';
                        input.style.height = '100%';
                        document.body.appendChild(input);
                    ''')
                    file_input = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.ID, 'custom-file-upload'))
                    )
                    file_input.send_keys(os.path.abspath(video_path))
                except Exception as e:
                    print(f"⚠️ روش جدید آپلود شکست خورد: {e}")
                    # روش قدیمی به عنوان fallback
                    try:
                        file_input = WebDriverWait(driver, 30).until(
                            EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
                        )
                        file_input.send_keys(os.path.abspath(video_path))
                    except:
                        raise Exception("هیچکدام از روش‌های آپلود کار نکرد")

                print("✅ Video file uploaded.")
                time.sleep(10)

                # تنظیم عنوان
                print("✏️ Setting title...")
                title_field = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@id='textbox' and contains(@aria-label, 'Title')]"))
                )
                title_field.clear()
                title_field.send_keys(title)

                # تنظیم توضیحات
                print("📝 Setting description...")
                description_field = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@id='textbox' and contains(@aria-label, 'Description')]"))
                )
                description_field.clear()
                description_field.send_keys(description)

                # کلیک روی دکمه Next (3 بار)
                for i in range(3):
                    print(f"⏭️ Clicking Next ({i+1}/3)...")
                    next_btn = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[contains(@id, 'next-button')]"))
                    )
                    next_btn.click()
                    time.sleep(5)

                # انتشار ویدیو
                print("🚀 Publishing video...")
                publish_btn = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@id, 'done-button')]"))
                )
                publish_btn.click()
                time.sleep(15)
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
