from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

import time
import json
import os
import re

class CourseScraper:
    def __init__(self):
        self.MAX_WAIT_TIME = 4
        self.MIN_WAIT_TIME = 3
        self.DEBUG_MODE = True

        self.base_download_dir = os.path.abspath("downloads")

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
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Áudio da')]"))
            )
            audio = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Áudio da')]")
            audio.click()
        except Exception as e:
            self.log('Couldnt find audio', e)

    def sanitize_filename(self, filename):
        """Remove caracteres inválidos do nome do arquivo"""
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = filename.strip()
        return filename[:200]  # Limita o tamanho do nome

    def download_class_summary(self):
        try:
            # Espera a div lesson-content__text carregar
            WebDriverWait(self.driver, self.MAX_WAIT_TIME).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'lesson-content__text'))
            )
            
            # Pega o HTML da página
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Encontra a div lesson-content__text
            lesson_content = soup.find('div', class_='lesson-content__text')
            
            if not lesson_content:
                self.log('Couldnt find lesson-content__text div')
                return
            
            # Extrai o título da aula
            title_elem = lesson_content.find('h2', class_='lesson-text__title')
            title = title_elem.get_text(strip=True) if title_elem else 'aula_sem_titulo'
            
            # Extrai o tema
            theme_elem = lesson_content.find('span', class_='lesson-text__theme')
            theme = theme_elem.get_text(strip=True) if theme_elem else ''
            
            # Extrai a descrição
            description_elem = lesson_content.find('div', class_='lesson-text__description')
            description = description_elem.get_text(strip=True) if description_elem else ''
            
            # Extrai o conteúdo do artigo
            article = lesson_content.find('article', class_='editor')
            
            if not article:
                self.log('Couldnt find article content')
                return
            
            # Remove scripts e estilos
            for script in article(['script', 'style']):
                script.decompose()
            
            # Pega todo o texto formatado
            paragraphs = article.find_all('p')
            content_text = '\n\n'.join([p.get_text(strip=True) for p in paragraphs])
            
            # Monta o texto final
            full_text = f"{theme}\n\n"
            full_text += f"{title}\n"
            full_text += "=" * len(title) + "\n\n"
            
            if description:
                full_text += f"{description}\n\n"
                full_text += "-" * 80 + "\n\n"
            
            full_text += content_text
            
            # Cria o nome do arquivo
            filename = self.sanitize_filename(f"{title}.txt")
            filepath = os.path.join(self.base_download_dir, filename)
            
            # Salva o arquivo
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            self.log(f'Texto salvo em: {filepath}')
            
        except Exception as e:
            self.log('Error downloading class summary', e)

    def get_class_material(self, class_url, firstTime=False):
        self.driver.get(class_url)

        if firstTime:
            try:
                review = WebDriverWait(self.driver, self.MIN_WAIT_TIME).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".course-review__ask-later"))
                )
                review.click()
            except:
                pass

        # self.download_class_audio()
        self.download_class_summary()

    def get_all_classes_links(self, course_url):
        self.driver.get(course_url)

        # wait until lessons load
        WebDriverWait(self.driver, self.MAX_WAIT_TIME).until(
            EC.presence_of_all_elements_located((By.ID, "course-classes"))
        )

        links = self.driver.find_elements(By.CSS_SELECTOR, "a.class")
        urls = [link.get_attribute("href") for link in links]
        self.log(f"Found {len(urls)} lessons")
        return urls
    
    def download_course(self, course_url: str):
        course_name = course_url.split('/')[-1]
        course_dir = os.path.join(self.base_download_dir, course_name)
        os.makedirs(course_dir, exist_ok=True)

        print(course_dir)

        # muda pasta de download do Chrome em tempo de execução
        self.driver.execute_cdp_cmd(
            "Page.setDownloadBehavior",
            {
                "behavior": "allow",
                "downloadPath": course_dir
            }
        )

        class_urls = self.get_all_classes_links(course_url)

        for index, url in enumerate(class_urls, start=1):
            self.log(f"Downloading lesson {index}/{len(class_urls)}")
            self.get_class_material(url, firstTime=(index == 1))
            time.sleep(1)

    def get_all_courses_links(self, courses_url):
        self.driver.get(courses_url)

        # wait until lessons load
        WebDriverWait(self.driver, self.MAX_WAIT_TIME).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "course-card"))
        )

        links = self.driver.find_elements(By.CLASS_NAME, "course-card")
        urls = [link.get_attribute("href") for link in links]
        self.log(f"Found {len(urls)} courses")
        return urls

    def download_all_courses(self, courses_url):
        courses_urls = self.get_all_courses_links(courses_url)

        try:
            enable_cookies = WebDriverWait(self.driver, self.MIN_WAIT_TIME).until(
                EC.element_to_be_clickable((By.ID, "c-p-bn"))
            )
            enable_cookies.click()
        except:
            pass

        for index, url in enumerate(courses_urls, start=1):
            self.log(f"Downloading course {index}/{len(courses_urls)}: {url.split('/')[-1]}")
            self.download_course(url)
            time.sleep(1)

# ------------------- USAGE -------------------

scraper = CourseScraper()
scraper.login("https://padrepauloricardo.org/entrar")
scraper.get_class_material('https://padrepauloricardo.org/aulas/as-universidades')
# scraper.download_all_courses('https://padrepauloricardo.org/cursos')
time.sleep(5)
