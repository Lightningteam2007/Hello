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
        # ... (کد قبلی بدون تغییر)

    @staticmethod
    def check_login(driver):
        # ... (کد قبلی بدون تغییر)

    @staticmethod
    def upload_shorts(video_path, title, description):
        for attempt in range(1, Config.MAX_RETRIES + 1):
            print(f"\n🔄 Attempt {attempt}/{Config.MAX_RETRIES}")
            driver = None
            try:
                # تنظیمات Chrome با پارامترهای اصلاح‌شده
                options = Options()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
                options.add_argument("--remote-debugging-port=9222")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--disable-infobars")
                options.add_argument("--start-maximized")
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option("useAutomationExtension", False)
                
                # پارامترهای مهم برای رفع خطای DevToolsActivePort
                options.add_argument("--remote-debugging-address=0.0.0.0")
                options.add_argument("--remote-debugging-port=9222")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--no-zygote")
                options.add_argument("--single-process")
                
                service = Service(
                    ChromeDriverManager().install(),
                    service_args=['--verbose', '--log-path=chromedriver.log']
                )
                
                try:
                    driver = webdriver.Chrome(service=service, options=options)
                    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                except Exception as e:
                    print(f"⚠️ Failed to start Chrome: {e}")
                    raise

                # ... (ادامه کدهای قبلی برای آپلود ویدیو)

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
