from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
            for cookie in cookies:
                if 'expiry' in cookie:
                    del cookie['expiry']
                driver.add_cookie(cookie)
            print("✅ Cookies loaded successfully.")
            return True
        except Exception as e:
            print(f"❌ Failed to load cookies: {e}")
            return False

    @staticmethod
    def check_login(driver):
        try:
            driver.get("https://www.youtube.com")
            time.sleep(3)
            if "sign in" in driver.page_source.lower():
                print("❌ User is NOT logged in!")
                return False
            print("✅ User is logged in.")
            return True
        except Exception as e:
            print(f"❌ Login check failed: {e}")
            return False

    @staticmethod
    def upload_shorts(video_path, title, description):
        for attempt in range(1, Config.MAX_RETRIES + 1):
            print(f"🔄 Attempt {attempt}/{Config.MAX_RETRIES}")
            driver = None
            try:
                options = webdriver.ChromeOptions()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--window-size=1920,1080")
                driver = webdriver.Chrome(options=options)

                # Load cookies & check login
                driver.get("https://www.youtube.com")
                if not (YouTubeUploader.load_cookies(driver) and YouTubeUploader.check_login(driver)):
                    raise Exception("Login failed!")

                # Upload video
                driver.get(Config.YT_UPLOAD_URL)
                file_input = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
                )
                file_input.send_keys(os.path.abspath(video_path))
                print("📤 Video file uploaded.")

                # Set title & description
                title_field = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Title']"))
                )
                title_field.clear()
                title_field.send_keys(title)

                description_field = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Description']"))
                )
                description_field.clear()
                description_field.send_keys(description)

                # Click Next (3 times)
                for _ in range(3):
                    next_btn = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='next-button']"))
                    )
                    next_btn.click()
                    time.sleep(2)

                # Publish
                publish_btn = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='done-button']"))
                )
                publish_btn.click()
                print("✅ Video published successfully!")
                return True

            except Exception as e:
                print(f"❌ Attempt {attempt} failed: {e}")
                if driver:
                    driver.save_screenshot(f"error_attempt_{attempt}.png")
                time.sleep(10)

            finally:
                if driver:
                    driver.quit()

        print("❌ All upload attempts failed!")
        return False
