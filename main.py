from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
import re
from datetime import datetime

import time
import json
import os

class CourseScraper:
    def __init__(self):
        self.MAX_WAIT_TIME = 4
        self.MIN_WAIT_TIME = 3
        self.DEBUG_MODE = True

        self.base_download_dir = os.path.abspath("downloads")
        self.log_file = os.path.join(self.base_download_dir, "log.txt")
        
        # Create downloads directory if it doesn't exist
        os.makedirs(self.base_download_dir, exist_ok=True)
        
        # Initialize log file
        self._init_log_file()

        chrome_options = Options()
        chrome_options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": self.base_download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
        )

        self.driver = webdriver.Chrome(options=chrome_options)
        self.cookies_file = "cookies.json"
        
        self.log("="*80)
        self.log("System started")
        self.log("="*80)

    def _init_log_file(self):
        """Initialize log file with session header"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n\n{'='*80}\n")
            f.write(f"NEW SESSION - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"{'='*80}\n\n")

    def log(self, message, exception=None, level="INFO"):
        """
        Log messages with timestamp
        
        Args:
            message: Message to log
            exception: Exception object (optional)
            level: Log level (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Define prefix based on level
        prefix_map = {
            "INFO": "->",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "SUCCESS": "✓"
        }
        prefix = prefix_map.get(level, "->")
        
        # Format message
        if exception:
            log_message = f"[{timestamp}] {prefix} {message} | Exception: {str(exception)}"
        else:
            log_message = f"[{timestamp}] {prefix} {message}"
        
        # Display in console if DEBUG_MODE is active
        if self.DEBUG_MODE:
            print(log_message)
        
        # Save to file
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
        except Exception as e:
            print(f"Error saving log: {e}")

    def load_login_data(self, credentials_file='credentials.json'):
        """Load email and password from JSON file"""
        with open(credentials_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.email = data["email"]
            self.password = data["password"]

    def save_cookies(self):
        """Store cookies to JSON file"""
        with open(self.cookies_file, 'w', encoding='utf-8') as file:
            json.dump(self.driver.get_cookies(), file)
        self.log("Cookies saved successfully", level="SUCCESS")

    def load_cookies(self):
        """Load cookies from file and add them to driver"""
        if not os.path.exists(self.cookies_file):
            self.log("Cookies file not found", level="WARNING")
            return False
        
        with open(self.cookies_file, 'r', encoding='utf-8') as file:
            cookies = json.load(file)

        for cookie in cookies:
            self.driver.add_cookie(cookie)

        self.log("Cookies loaded successfully", level="SUCCESS")
        return True

    def login(self, login_url):
        """Perform login using cookies or manual credentials"""
        self.log(f"Starting login process at: {login_url}")
        self.load_login_data()

        self.driver.get(login_url)
        self.driver.maximize_window()

        # Try login using cookies (if valid)
        if self.load_cookies():
            self.driver.get(login_url)
            time.sleep(3)
            if "entrar" not in self.driver.current_url.lower():
                self.log("Logged in using saved cookies", level="SUCCESS")
                return
            else:
                self.log("Cookies invalid. Performing manual login", level="WARNING")

        # Manual login
        self.log("Filling login credentials")
        email_input = WebDriverWait(self.driver, self.MAX_WAIT_TIME).until(
            EC.presence_of_element_located((By.ID, "inputEmail"))
        )
        email_input.send_keys(self.email)

        password_input = WebDriverWait(self.driver, self.MAX_WAIT_TIME).until(
            EC.presence_of_element_located((By.ID, "inputPassword"))
        )
        password_input.send_keys(self.password + Keys.ENTER)

        time.sleep(5)

        # Save cookies after successful login
        self.save_cookies()
        self.log("Manual login completed successfully", level="SUCCESS")

    def download_class_audio(self):
        """Download audio file from class"""
        try:
            self.log("Searching for audio button")
            WebDriverWait(self.driver, self.MAX_WAIT_TIME).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Áudio da')]"))
            )
            audio_button = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Áudio da')]")
            audio_button.click()
            self.log("Audio download started", level="SUCCESS")
        except Exception as e:
            self.log('Could not find audio button', e, level="ERROR")

    def sanitize_filename(self, filename):
        """Remove invalid characters from filename"""
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = filename.strip()
        return filename[:200]  # Limit filename length

    def download_class_summary(self):
        """Extract and save class text content to .txt file"""
        try:
            self.log("Starting class text extraction")
            
            # Wait for lesson-content__text div to load
            WebDriverWait(self.driver, self.MAX_WAIT_TIME).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'lesson-content__text'))
            )
            
            self.log("Class content loaded, processing HTML")
            
            # Get page HTML
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find lesson-content__text div
            lesson_content = soup.find('div', class_='lesson-content__text')
            
            if not lesson_content:
                self.log('Could not find lesson-content__text div', level="ERROR")
                return
            
            # Extract lesson title
            title_element = lesson_content.find('h2', class_='lesson-text__title')
            title = title_element.get_text(strip=True) if title_element else 'untitled_lesson'
            self.log(f"Extracted title: {title}")
            
            # Extract theme
            theme_element = lesson_content.find('span', class_='lesson-text__theme')
            theme = theme_element.get_text(strip=True) if theme_element else ''
            
            # Extract description
            description_element = lesson_content.find('div', class_='lesson-text__description')
            description = description_element.get_text(strip=True) if description_element else ''
            
            # Extract article content
            article = lesson_content.find('article', class_='editor')
            
            if not article:
                self.log('Could not find article content', level="ERROR")
                return
            
            # Remove scripts and styles
            for script in article(['script', 'style']):
                script.decompose()
            
            # Get all text formatted
            paragraphs = article.find_all('p')
            content_text = '\n\n'.join([p.get_text(strip=True) for p in paragraphs])
            
            self.log(f"Text extracted: {len(content_text)} characters, {len(paragraphs)} paragraphs")
            
            # Build final text
            full_text = f"{theme}\n\n"
            full_text += f"{title}\n"
            full_text += "=" * len(title) + "\n\n"
            
            if description:
                full_text += f"{description}\n\n"
                full_text += "-" * 80 + "\n\n"
            
            full_text += content_text
            
            # Create filename
            filename = self.sanitize_filename(f"{title}.txt")
            filepath = os.path.join(self.base_download_dir, filename)
            
            # Save file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            self.log(f'Text saved successfully to: {filename}', level="SUCCESS")
            
        except Exception as e:
            self.log('Error downloading class summary', e, level="ERROR")

    def get_class_material(self, class_url, first_time=False):
        """Navigate to class URL and download materials"""
        self.log(f"Accessing class URL: {class_url}")
        self.driver.get(class_url)

        if first_time:
            try:
                review_button = WebDriverWait(self.driver, self.MIN_WAIT_TIME).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".course-review__ask-later"))
                )
                review_button.click()
                self.log("Review popup closed")
            except:
                pass

        # self.download_class_audio()
        self.download_class_summary()

    def get_all_classes_links(self, course_url):
        """Get all class URLs from a course"""
        self.log(f"Getting class list from course: {course_url}")
        self.driver.get(course_url)

        # Wait until lessons load
        WebDriverWait(self.driver, self.MAX_WAIT_TIME).until(
            EC.presence_of_all_elements_located((By.ID, "course-classes"))
        )

        links = self.driver.find_elements(By.CSS_SELECTOR, "a.class")
        urls = [link.get_attribute("href") for link in links]
        self.log(f"Found {len(urls)} classes in course", level="SUCCESS")
        return urls
    
    def download_course(self, course_url: str):
        """Download all materials from a course"""
        course_name = course_url.split('/')[-1]
        course_dir = os.path.join(self.base_download_dir, course_name)
        os.makedirs(course_dir, exist_ok=True)

        self.log(f"Starting course download: {course_name}")
        self.log(f"Destination directory: {course_dir}")

        # Change Chrome download folder at runtime
        self.driver.execute_cdp_cmd(
            "Page.setDownloadBehavior",
            {
                "behavior": "allow",
                "downloadPath": course_dir
            }
        )

        class_urls = self.get_all_classes_links(course_url)

        for index, url in enumerate(class_urls, start=1):
            self.log(f"Processing class {index}/{len(class_urls)}")
            self.get_class_material(url, first_time=(index == 1))
            time.sleep(1)
        
        self.log(f"Course download completed: {course_name}", level="SUCCESS")

    def get_all_courses_links(self, courses_url):
        """Get all course URLs from courses page"""
        self.log(f"Getting courses list from: {courses_url}")
        self.driver.get(courses_url)

        # Wait until courses load
        WebDriverWait(self.driver, self.MAX_WAIT_TIME).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "course-card"))
        )

        links = self.driver.find_elements(By.CLASS_NAME, "course-card")
        urls = [link.get_attribute("href") for link in links]
        self.log(f"Found {len(urls)} courses", level="SUCCESS")
        return urls

    def download_all_courses(self, courses_url):
        """Download all courses from platform"""
        self.log("Starting download of all courses")
        courses_urls = self.get_all_courses_links(courses_url)

        try:
            enable_cookies_button = WebDriverWait(self.driver, self.MIN_WAIT_TIME).until(
                EC.element_to_be_clickable((By.ID, "c-p-bn"))
            )
            enable_cookies_button.click()
            self.log("Cookies banner accepted")
        except:
            pass

        for index, url in enumerate(courses_urls, start=1):
            course_name = url.split('/')[-1]
            self.log(f"Course {index}/{len(courses_urls)}: {course_name}")
            self.download_course(url)
            time.sleep(1)
        
        self.log("All courses download completed!", level="SUCCESS")

# ------------------- USAGE -------------------

scraper = CourseScraper()
scraper.login("https://padrepauloricardo.org/entrar")
scraper.get_class_material('https://padrepauloricardo.org/aulas/as-universidades')
# scraper.download_all_courses('https://padrepauloricardo.org/cursos')
scraper.log("Process finished", level="SUCCESS")
scraper.log("="*80)
time.sleep(5)