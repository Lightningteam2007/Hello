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
            
            # پاک کردن کوکی‌های قبلی
            driver.delete_all_cookies()
            time.sleep(2)
            
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
            
            # روش‌های مختلف برای بررسی لاگین
            try:
                avatar = driver.find_element(By.CSS_SELECTOR, "img#img")
                if avatar:
                    print("✅ User is logged in.")
                    return True
            except:
                pass
                
            try:
                account_button = driver.find_element(By.XPATH, "//a[contains(@href, 'account')]")
                if account_button:
                    print("✅ User is logged in.")
                    return True
            except:
                pass
                
            print("❌ User is NOT logged in!")
            return False
            
        except Exception as e:
            print(f"❌ Login check failed: {e}")
            print(traceback.format_exc())
            return False

    @staticmethod
    def upload_shorts(video_path, title, description):
        for attempt in range(1, Config.MAX_RETRIES + 1):
            print(f"\n🔄 Attempt {attempt}/{Config.MAX_RETRIES}")
            driver = None
            try:
                # تنظیمات پیشرفته Chrome
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
                options.binary_location = "/usr/bin/chromium-browser"

                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(options=options, service=service)
                
                # مخفی کردن شناسایی اتوماسیون
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                # لاگین و احراز هویت
                if not (YouTubeUploader.load_cookies(driver) and YouTubeUploader.check_login(driver)):
                    raise Exception("Login failed!")

                print("🌐 Navigating to YouTube upload page...")
                driver.get(Config.YT_UPLOAD_URL)
                time.sleep(15)

                # ذخیره صفحه برای دیباگ
                with open(f"upload_page_{attempt}.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                driver.save_screenshot(f"upload_page_{attempt}.png")

                # آپلود فایل ویدیویی
                print("📤 Uploading video file...")
                try:
                    # ایجاد المان آپلود دینامیک
                    driver.execute_script('''
                        const input = document.createElement('input');
                        input.type = 'file';
                        input.id = 'dynamic-upload-input';
                        input.accept = 'video/*';
                        input.style.position = 'fixed';
                        input.style.top = '0';
                        input.style.left = '0';
                        input.style.width = '100%';
                        input.style.height = '100%';
                        input.style.opacity = '0';
                        document.body.appendChild(input);
                    ''')
                    
                    file_input = WebDriverWait(driver, 45).until(
                        EC.presence_of_element_located((By.ID, 'dynamic-upload-input'))
                    )
                    file_input.send_keys(os.path.abspath(video_path))
                    print("✅ Video file uploaded.")
                    time.sleep(10)
                except Exception as e:
                    print(f"⚠️ روش دینامیک آپلود شکست خورد: {e}")
                    raise

                # تنظیم عنوان با روش‌های مختلف
                print("✏️ Setting title...")
                title_set = False
                title_selectors = [
                    ("XPATH", "//div[@id='textbox' and contains(@aria-label, 'Title')]"),
                    ("CSS", "div[aria-label='Title']"),
                    ("ID", "title-textarea"),
                    ("XPATH", "//*[contains(@aria-label, 'Title')]")
                ]
                
                for selector_type, selector in title_selectors:
                    try:
                        title_field = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.__getattribute__(selector_type), selector))
                        )
                        title_field.clear()
                        for char in title:
                            title_field.send_keys(char)
                            time.sleep(0.05)
                        title_set = True
                        print(f"✅ Title set using {selector_type}: {selector}")
                        break
                    except Exception as e:
                        print(f"⚠️ Failed to set title with {selector_type} {selector}: {e}")

                if not title_set:
                    raise Exception("All title setting methods failed")

                # تنظیم توضیحات
                print("📝 Setting description...")
                try:
                    desc_selectors = [
                        ("XPATH", "//div[@id='textbox' and contains(@aria-label, 'Description')]"),
                        ("CSS", "div[aria-label='Description']"),
                        ("ID", "description-textarea")
                    ]
                    
                    for selector_type, selector in desc_selectors:
                        try:
                            desc_field = WebDriverWait(driver, 15).until(
                                EC.element_to_be_clickable((By.__getattribute__(selector_type), selector))
                            )
                            desc_field.clear()
                            desc_field.send_keys(description)
                            print(f"✅ Description set using {selector_type}")
                            break
                        except Exception as e:
                            print(f"⚠️ Failed to set description with {selector_type}: {e}")
                except Exception as e:
                    print(f"⚠️ Could not set description: {e}")

                # کلیک روی دکمه‌های بعدی
                print("⏭️ Clicking Next buttons...")
                for i in range(3):
                    try:
                        next_buttons = [
                            ("XPATH", "//div[contains(@id, 'next-button')]"),
                            ("CSS", "div.next-button"),
                            ("XPATH", "//*[contains(text(), 'Next')]")
                        ]
                        
                        clicked = False
                        for selector_type, selector in next_buttons:
                            try:
                                next_btn = WebDriverWait(driver, 15).until(
                                    EC.element_to_be_clickable((By.__getattribute__(selector_type), selector))
                                )
                                next_btn.click()
                                print(f"✅ Clicked Next ({i+1}/3) using {selector_type}")
                                time.sleep(5)
                                clicked = True
                                break
                            except Exception as e:
                                print(f"⚠️ Failed to click Next with {selector_type}: {e}")
                        
                        if not clicked:
                            raise Exception(f"Could not click Next button ({i+1}/3)")
                            
                    except Exception as e:
                        print(f"⚠️ Error in Next button {i+1}: {e}")
                        raise

                # انتشار ویدیو
                print("🚀 Publishing video...")
                try:
                    publish_buttons = [
                        ("XPATH", "//div[contains(@id, 'done-button')]"),
                        ("CSS", "div.done-button"),
                        ("XPATH", "//*[contains(text(), 'Publish')]")
                    ]
                    
                    published = False
                    for selector_type, selector in publish_buttons:
                        try:
                            publish_btn = WebDriverWait(driver, 20).until(
                                EC.element_to_be_clickable((By.__getattribute__(selector_type), selector))
                            )
                            publish_btn.click()
                            print(f"✅ Published using {selector_type}")
                            time.sleep(15)
                            published = True
                            break
                        except Exception as e:
                            print(f"⚠️ Failed to publish with {selector_type}: {e}")
                    
                    if not published:
                        raise Exception("All publish methods failed")
                        
                    print("✅ Video published successfully!")
                    return True
                    
                except Exception as e:
                    print(f"❌ Failed to publish: {e}")
                    raise

            except Exception as e:
                print(f"❌ Attempt {attempt} failed: {e}")
                print(traceback.format_exc())
                if driver:
                    try:
                        driver.save_screenshot(f"error_attempt_{attempt}.png")
                        with open(f"page_source_{attempt}.html", "w", encoding="utf-8") as f:
                            f.write(driver.page_source)
                    except Exception as e:
                        print(f"⚠️ Could not save debug info: {e}")
                time.sleep(Config.DELAY_BETWEEN_ATTEMPTS)

            finally:
                if driver:
                    try:
                        driver.quit()
                    except Exception as e:
                        print(f"⚠️ Error closing driver: {e}")

        print("❌ All upload attempts failed!")
        return False
