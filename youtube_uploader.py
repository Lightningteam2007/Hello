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
    # ... (متدهای load_cookies و check_login بدون تغییر)

    @staticmethod
    def upload_shorts(video_path, title, description):
        for attempt in range(1, Config.MAX_RETRIES + 1):
            print(f"\n🔄 Attempt {attempt}/{Config.MAX_RETRIES}")
            driver = None
            try:
                # تنظیمات Chrome
                options = Options()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--headless=new")
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                options.binary_location = "/usr/bin/chromium-browser"

                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                
                # لاگین و احراز هویت
                if not (YouTubeUploader.load_cookies(driver) and YouTubeUploader.check_login(driver)):
                    raise Exception("Login failed!")

                print("🌐 Navigating to YouTube upload page...")
                driver.get(Config.YT_UPLOAD_URL)
                time.sleep(15)

                # آپلود فایل
                print("📤 Uploading video file...")
                file_input = driver.find_element(By.XPATH, "//input[@type='file']")
                file_input.send_keys(os.path.abspath(video_path))
                print("✅ Video file uploaded.")
                time.sleep(10)

                # تنظیم عنوان (روش بهبود یافته)
                print("✏️ Setting title...")
                try:
                    # روش 1: استفاده از JavaScript برای یافتن عنصر عنوان
                    title_field = driver.execute_script('''
                        return document.querySelector('div[aria-label="Title"]') || 
                               document.querySelector('*[aria-label*="Title"]') ||
                               document.getElementById('title-textarea');
                    ''')
                    
                    if title_field:
                        title_field.click()
                        title_field.clear()
                        driver.execute_script('''
                            arguments[0].value = arguments[1];
                        ''', title_field, title)
                        print("✅ Title set using JavaScript")
                    else:
                        raise Exception("Title field not found")
                except Exception as e:
                    print(f"⚠️ JavaScript method failed: {e}")
                    # روش 2: استفاده از Selenium معمولی
                    try:
                        title_field = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, '//*[contains(@aria-label, "Title")]'))
                        )
                        title_field.click()
                        title_field.clear()
                        title_field.send_keys(title)
                        print("✅ Title set using Selenium")
                    except Exception as e:
                        print(f"⚠️ Selenium method failed: {e}")
                        raise Exception("All title setting methods failed")

                # تنظیم توضیحات
                print("📝 Setting description...")
                try:
                    desc_field = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, '//*[contains(@aria-label, "Description")]'))
                    )
                    desc_field.click()
                    desc_field.clear()
                    desc_field.send_keys(description)
                    print("✅ Description set successfully")
                except Exception as e:
                    print(f"⚠️ Could not set description: {e}")

                # ادامه فرآیند آپلود...
                # ... (کدهای مربوط به دکمه‌های Next و Publish)

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
