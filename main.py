from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os

class CourseScraper:
    def __init__(self):
        self.MAX_WAIT_TIME = 30
        self.driver = webdriver.Chrome()
        self.cookies_file = "cookies.json"

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
        print("Cookies saved.")

    def load_cookies(self):
        # Check if cookies exist
        if not os.path.exists(self.cookies_file):
            return False
        
        # Load cookies and add them to the driver
        with open(self.cookies_file, 'r', encoding='utf-8') as file:
            cookies = json.load(file)

        for cookie in cookies:
            self.driver.add_cookie(cookie)

        print("Cookies loaded.")
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
                print("Logged in using cookies.")
                return
            else:
                print("Cookies invalid. Logging in manually.")

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

# ------------------- USAGE -------------------

scraper = CourseScraper()
scraper.login("https://padrepauloricardo.org/entrar")
time.sleep(5)
