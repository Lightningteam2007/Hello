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
        try:
            cookies = json.loads(Config.YT_COOKIES)
            driver.get("https://www.youtube.com")
            time.sleep(5)
            
            # Clear existing cookies
            driver.delete_all_cookies()
            time.sleep(2)
            
            for cookie in cookies:
                if 'expiry' in cookie:
                    del cookie['expiry']
                driver.add_cookie(cookie)
            
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
            
            # Multiple ways to check login status
            logged_in = False
            try:
                if driver.find_elements(By.CSS_SELECTOR, "img#img"):
                    logged_in = True
            except:
                pass
                
            if not logged_in:
                try:
                    if driver.find_elements(By.XPATH, "//a[contains(@href, 'account')]"):
                        logged_in = True
                except:
                    pass
            
            if logged_in:
                print("✅ User is logged in.")
                return True
            else:
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
                # Chrome options setup
                options = Options()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument(f"--window-size={Config.TARGET_HEIGHT},1080")
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
                options.add_argument("--remote-debugging-port=9222")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--disable-infobars")
                options.add_argument("--start-maximized")
                options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{Config.CHROME_VERSION} Safari/537.36")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option("useAutomationExtension", False)
                options.binary_location = "/usr/bin/chromium-browser"

                # Initialize driver
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)

                # Authentication
                if not (YouTubeUploader.load_cookies(driver) and YouTubeUploader.check_login(driver)):
                    raise Exception("Login failed!")

                print("🌐 Navigating to YouTube upload page...")
                driver.get(Config.YT_UPLOAD_URL)
                time.sleep(15)

                # Debug: Save page source
                with open(f"upload_page_{attempt}.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                driver.save_screenshot(f"upload_page_{attempt}.png")

                # File upload with multiple methods
                print("📤 Uploading video file...")
                uploaded = False
                try:
                    # Method 1: Create input element with JavaScript
                    driver.execute_script('''
                        const input = document.createElement('input');
                        input.type = 'file';
                        input.id = 'custom-upload-input';
                        input.style.display = 'block';
                        input.style.visibility = 'visible';
                        input.style.position = 'absolute';
                        input.style.top = '0';
                        input.style.left = '0';
                        input.style.width = '100%';
                        input.style.height = '100%';
                        document.body.appendChild(input);
                    ''')
                    file_input = WebDriverWait(driver, Config.WEBDRIVER_TIMEOUT).until(
                        EC.presence_of_element_located((By.ID, 'custom-upload-input'))
                    )
                    file_input.send_keys(os.path.abspath(video_path))
                    uploaded = True
                except Exception as e:
                    print(f"⚠️ JavaScript upload method failed: {e}")
                    try:
                        # Method 2: Standard file input
                        file_input = WebDriverWait(driver, Config.WEBDRIVER_TIMEOUT).until(
                            EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
                        )
                        file_input.send_keys(os.path.abspath(video_path))
                        uploaded = True
                    except Exception as e:
                        print(f"⚠️ Standard upload method failed: {e}")
                        raise Exception("All upload methods failed")

                if uploaded:
                    print("✅ Video file uploaded.")
                    time.sleep(10)

                    # Set title
                    print("✏️ Setting title...")
                    try:
                        title_field = WebDriverWait(driver, Config.WEBDRIVER_TIMEOUT).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[contains(@aria-label, "Title")]'))
                        )
                        title_field.clear()
                        title_field.send_keys(title)
                        print("✅ Title set successfully")
                    except Exception as e:
                        print(f"⚠️ Could not set title: {e}")
                        raise

                    # Set description
                    print("📝 Setting description...")
                    try:
                        desc_field = WebDriverWait(driver, Config.WEBDRIVER_TIMEOUT).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[contains(@aria-label, "Description")]'))
                        )
                        desc_field.clear()
                        desc_field.send_keys(description)
                        print("✅ Description set successfully")
                    except Exception as e:
                        print(f"⚠️ Could not set description: {e}")

                    # Click Next buttons (3 times)
                    for i in range(3):
                        print(f"⏭️ Clicking Next ({i+1}/3)...")
                        try:
                            next_btn = WebDriverWait(driver, Config.WEBDRIVER_TIMEOUT).until(
                                EC.element_to_be_clickable((By.XPATH, "//div[contains(@id, 'next-button')]"))
                            )
                            next_btn.click()
                            time.sleep(5)
                        except Exception as e:
                            print(f"⚠️ Could not click Next button ({i+1}/3): {e}")
                            raise

                    # Publish video
                    print("🚀 Publishing video...")
                    try:
                        publish_btn = WebDriverWait(driver, Config.WEBDRIVER_TIMEOUT).until(
                            EC.element_to_be_clickable((By.XPATH, "//div[contains(@id, 'done-button')]"))
                        )
                        publish_btn.click()
                        time.sleep(15)
                        print("✅ Video published successfully!")
                        return True
                    except Exception as e:
                        print(f"❌ Could not publish video: {e}")
                        raise

            except Exception as e:
                print(f"❌ Attempt {attempt} failed: {e}")
                print(traceback.format_exc())
                if driver:
                    try:
                        driver.save_screenshot(f"error_attempt_{attempt}.png")
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
