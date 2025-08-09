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
        print("[INFO] Loading YouTube cookies...")
        if Config.YT_COOKIES:
            try:
                cookies = json.loads(Config.YT_COOKIES)
                for cookie in cookies:
                    if 'expiry' in cookie:
                        del cookie['expiry']
                    driver.add_cookie(cookie)
                print("[INFO] Cookies loaded successfully.")
                return True
            except Exception as e:
                print(f"[ERROR] Error loading cookies: {e}")
                print(traceback.format_exc())
        else:
            print("[WARN] No cookies found in Config.YT_COOKIES.")
        return False

    @staticmethod
    def take_screenshot(driver, name="error_screenshot.png"):
        try:
            driver.save_screenshot(name)
            print(f"[INFO] Screenshot saved: {name}")
        except Exception as e:
            print(f"[WARN] Failed to take screenshot: {e}")

    @staticmethod
    def upload_shorts(video_path, title, description):
        for attempt in range(1, Config.MAX_RETRIES + 1):
            print(f"[INFO] Upload attempt {attempt} of {Config.MAX_RETRIES}")
            driver = None
            try:
                options = webdriver.ChromeOptions()
                # options.add_argument("--headless=new")  # برای دیباگ غیرفعال کن
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
                print("[INFO] YouTube main page loaded.")

                if YouTubeUploader.load_cookies(driver):
                    driver.get("https://www.youtube.com")  # Refresh to activate cookies
                    time.sleep(3)
                else:
                    print("[WARN] Continuing without cookies; may require manual login.")

                driver.get(Config.YT_UPLOAD_URL)
                print(f"[INFO] Navigated to upload page: {Config.YT_UPLOAD_URL}")

                # آپلود فایل
                file_input = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
                )
                abs_video_path = os.path.abspath(video_path)
                print(f"[INFO] Uploading video file: {abs_video_path}")
                file_input.send_keys(abs_video_path)

                print("[INFO] Waiting for video processing to start...")
                time.sleep(10)  # زمان برای شروع آپلود

                # تنظیم عنوان
                try:
                    title_field = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((
                            By.CSS_SELECTOR, "div[aria-label='عنوان'], div[aria-label='Title']"
                        ))
                    )
                    title_field.clear()
                    title_field.send_keys(title)
                    print(f"[INFO] Title set: {title}")
                except Exception as e:
                    print(f"[WARN] Title field not found or settable: {e}")

                # تنظیم توضیحات
                try:
                    description_field = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((
                            By.CSS_SELECTOR, "div[aria-label='توضیحات'], div[aria-label='Description']"
                        ))
                    )
                    description_field.clear()
                    description_field.send_keys(description)
                    print("[INFO] Description set.")
                except Exception as e:
                    print(f"[WARN] Description field not found or settable: {e}")

                # کلیک روی دکمه "بعدی" سه بار
                for i in range(3):
                    try:
                        next_btn = WebDriverWait(driver, 30).until(
                            EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='next-button']"))
                        )
                        next_btn.click()
                        print(f"[INFO] Clicked 'Next' button {i + 1}/3")
                        time.sleep(2)
                    except Exception as e:
                        print(f"[WARN] Could not click 'Next' button at step {i+1}: {e}")
                        break

                # دکمه انتشار
                try:
                    publish_button = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='done-button']"))
                    )
                    publish_button.click()
                    print("[INFO] Clicked 'Publish' button.")
                except Exception as e:
                    print(f"[ERROR] Publish button not clickable: {e}")
                    YouTubeUploader.take_screenshot(driver, f"publish_error_{attempt}.png")
                    raise

                print("[SUCCESS] Video published successfully!")
                time.sleep(5)  # صبر برای اطمینان از ثبت نهایی
                return True

            except Exception as e:
                print(f"[ERROR] Upload attempt {attempt} failed: {e}")
                print(traceback.format_exc())
                if driver:
                    YouTubeUploader.take_screenshot(driver, f"upload_error_{attempt}.png")

                time.sleep(10)  # زمان استراحت قبل از تلاش مجدد

            finally:
                if driver:
                    try:
                        driver.quit()
                        print("[INFO] Browser closed.")
                    except Exception as e:
                        print(f"[WARN] Failed to close browser: {e}")

        print("[ERROR] All upload attempts failed.")
        return False
