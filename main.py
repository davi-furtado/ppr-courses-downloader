from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

import time
import json
import os

class CourseScraper:
    def __init__(self):
        self.MAX_WAIT_TIME = 10
        self.MIN_WAIT_TIME = 3
        self.DEBUG_MODE = True

        self.driver = webdriver.Chrome()
        self.cookies_file = "cookies.json"

    def log(self, msg, exception=None):
        if self.DEBUG_MODE:
            if exception:
                print(f'=> {msg} [{exception}]')
            else:
                print(f'-> {msg}')

    def load_login_data(self, credentials_file='credentials.json'):
        # Load email and password from JSON file
        with open(credentials_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.email = data["email"]
            self.password = data["password"]

    def save_cookies(self):
        # Store cookies to a JSON file
        with open(self.cookies_file, 'w', encoding='utf-8') as file:
            json.dump(self.driver.get_cookies(), file)
        self.log("Cookies saved")

    def load_cookies(self):
        # Check if cookies exist
        if not os.path.exists(self.cookies_file):
            return False
        
        # Load cookies and add them to the driver
        with open(self.cookies_file, 'r', encoding='utf-8') as file:
            cookies = json.load(file)

        for cookie in cookies:
            self.driver.add_cookie(cookie)

        self.log("Cookies loaded")
        return True

    def login(self, login_url):
        self.load_login_data()

        self.driver.get(login_url)
        self.driver.maximize_window()

        # Try login using cookies (if valid)
        if self.load_cookies():
            self.driver.get(login_url)
            time.sleep(3)
            if "entrar" not in self.driver.current_url.lower():
                self.log("Logged in using cookies")
                return
            else:
                self.log("Cookies invalid. Logging in manually")

        # Manual login
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
        print("Manual login completed.")

    def download_class_audio(self):
        try:
            WebDriverWait(self.driver, self.MAX_WAIT_TIME).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Áudio da aula')]"))
            )
            audio = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Áudio da aula')]")
            audio.click()
        except Exception as e:
            self.log('Couldnt find audio', e)

    def download_class_summary(self):
        try:
            WebDriverWait(self.driver, self.MAX_WAIT_TIME).until(
                EC.presence_of_element_located((By.ID, 'print-button'))
            )
            print_button = self.driver.find_element(By.ID, 'print-button')
            print_button.click()
        except Exception as e:
            self.log('Couldnt find print button', e)

        try:
            select_element = WebDriverWait(self.driver, self.MAX_WAIT_TIME).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'select.md-select'))
            )
            dropdown = Select(select_element)
            dropdown.select_by_value("Save as PDF/local/")
        except Exception as e:
            self.log('Couldnt find Save as PDF option', e)

        try:
            WebDriverWait(self.driver, self.MAX_WAIT_TIME).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'Save'))
            )
            print_button = self.driver.find_element(By.ID, 'Save')
            print_button.click()
        except Exception as e:
            self.log('Couldnt find Salvar button', e)

    def get_class_material(self, class_url, firstTime=False):
        self.driver.get(class_url)

        if not firstTime:
            try:
                review = WebDriverWait(self.driver, self.MIN_WAIT_TIME).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".course-review__ask-later"))
                )
                review.click()
            except:
                pass

            # TODO move to class listing
            try:
                enable_cookies = WebDriverWait(self.driver, self.MIN_WAIT_TIME).until(
                    EC.element_to_be_clickable((By.ID, "c-p-bn"))
                )
                enable_cookies.click()
            except:
                pass

        self.download_class_audio()
        # TODO self.download_class_summary()

    def get_all_class_links(self, course_url):
        self.driver.get(course_url)

        # wait until lessons load
        WebDriverWait(self.driver, self.MAX_WAIT_TIME).until(
            EC.presence_of_all_elements_located((By.ID, "course-classes"))
        )

        links = self.driver.find_elements(By.CSS_SELECTOR, "a.class")
        urls = [link.get_attribute("href") for link in links]
        self.log(f"Found {len(urls)} lessons")
        return urls
    
    def download_course(self, course_url):
        class_urls = self.get_all_class_links(course_url)

        for index, url in enumerate(class_urls, start=1):
            self.log(f"Downloading lesson {index}/{len(class_urls)}")
            if index == 1:
                self.get_class_material(url, firstTime=True)
            else:
                self.get_class_material(url, firstTime=False)
            time.sleep(2)

# ------------------- USAGE -------------------

scraper = CourseScraper()
scraper.login("https://padrepauloricardo.org/entrar")
#scraper.get_class_material('https://padrepauloricardo.org/aulas/o-que-e-ser-homem')
scraper.download_course('https://padrepauloricardo.org/cursos/os-sete-sacramentos')
time.sleep(5)
