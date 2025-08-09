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
        """بارگذاری کوکی‌ها از Config.YT_COOKIES"""
        if Config.YT_COOKIES:
            try:
                cookies = json.loads(Config.YT_COOKIES)
                for cookie in cookies:
                    # حذف expiry چون Selenium ممکنه ایراد بگیره
                    if 'expiry' in cookie:
                        del cookie['expiry']
                    driver.add_cookie(cookie)
                print("[INFO] Cookies loaded successfully.")
                return True
            except Exception as e:
                print(f"[ERROR] Loading cookies failed: {e}")
                print(traceback.format_exc())
        else:
            print("[WARN] No YT_COOKIES found in config.")
        return False

    @staticmethod
    def check_login(driver):
        """بررسی اینکه آیا کاربر لاگین شده یا نه"""
        try:
            driver.get("https://www.youtube.com")
            time.sleep(5)  # اجازه بارگذاری کامل صفحه
            page_source = driver.page_source.lower()
            # چند روش برای چک لاگین:
            if "sign in" in page_source or "ورود" in page_source:
                print("[ERROR] User is NOT logged in after loading cookies!")
                return False
            print("[INFO] User logged in successfully.")
            return True
        except Exception as e:
            print(f"[ERROR] Exception during login check: {e}")
            print(traceback.format_exc())
            return False

    @staticmethod
    def upload_shorts(video_path, title, description):
        for attempt in range(Config.MAX_RETRIES):
            driver = None
            try:
                print(f"[INFO] Upload attempt {attempt + 1} started.")
                options = webdriver.ChromeOptions()

                # headless برای دیباگ فعلا غیرفعال باشه
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

                # رفتن به یوتیوب و بارگذاری کوکی
                driver.get("https://www.youtube.com")
                time.sleep(3)
                if YouTubeUploader.load_cookies(driver):
                    driver.refresh()
                    time.sleep(5)
                else:
                    print("[WARN] Continuing without cookies loaded.")

                if not YouTubeUploader.check_login(driver):
                    print("[ERROR] Login failed, aborting upload.")
                    return False

                # رفتن به صفحه آپلود شورتز
                print("[INFO] Navigating to upload page...")
                driver.get(Config.YT_UPLOAD_URL)

                # آپلود فایل ویدیو
                file_input = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
                )
                file_input.send_keys(os.path.abspath(video_path))
                print("[INFO] Video file sent to input element.")
                time.sleep(10)  # زمان برای آپلود اولیه

                # اسکرین‌شات برای دیباگ
                driver.save_screenshot(f"debug_uploaded_{attempt+1}.png")

                # تنظیم عنوان
                try:
                    title_field = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((
                            By.CSS_SELECTOR, "div[aria-label='عنوان'], div[aria-label='Title']"
                        ))
                    )
                    title_field.click()
                    title_field.clear()
                    title_field.send_keys(title)
                    print("[INFO] Title set successfully.")
                except Exception as e:
                    print(f"[WARN] Title field not found or could not be set: {e}")
                    print(traceback.format_exc())

                # تنظیم توضیحات
                try:
                    description_field = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((
                            By.CSS_SELECTOR, "div[aria-label='توضیحات'], div[aria-label='Description']"
                        ))
                    )
                    description_field.click()
                    description_field.clear()
                    description_field.send_keys(description)
                    print("[INFO] Description set successfully.")
                except Exception as e:
                    print(f"[WARN] Description field not found or could not be set: {e}")
                    print(traceback.format_exc())

                # کلیک روی دکمه‌های بعدی (Next) سه بار
                for i in range(3):
                    try:
                        next_btn = WebDriverWait(driver, 30).until(
                            EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='next-button']"))
                        )
                        next_btn.click()
                        print(f"[INFO] Clicked 'Next' button #{i+1}")
                        time.sleep(2)
                    except Exception as e:
                        print(f"[WARN] Could not click 'Next' button #{i+1}: {e}")
                        break

                # کلیک روی دکمه انتشار (Done)
                try:
                    publish_button = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='done-button']"))
                    )
                    publish_button.click()
                    print("[INFO] Publish button clicked.")
                except Exception as e:
                    print(f"[ERROR] Could not click Publish button: {e}")
                    print(traceback.format_exc())
                    return False

                # اسکرین‌شات پس از انتشار برای تایید
                time.sleep(5)
                driver.save_screenshot(f"debug_after_publish_{attempt+1}.png")

                print("✅ Video uploaded and published successfully!")
                return True

            except Exception as e:
                print(f"[ERROR] Attempt {attempt + 1} failed with exception: {e}")
                print(traceback.format_exc())
                time.sleep(10)

            finally:
                if driver:
                    try:
                        driver.quit()
                    except Exception:
                        pass

        print("[ERROR] All upload attempts failed.")
        return False
