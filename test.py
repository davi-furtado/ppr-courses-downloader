
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'MINHA CONTA'))
)

cookies = driver.get_cookies()
with open("cookies.json", "w") as f:
    json.dump(cookies, f)

driver.get("https://padrepauloricardo.org/aulas/o-que-e-ser-homem")

option = WebDriverWait(driver, 50).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".course-review__ask-later"))
)
option.click()

WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'Áudio da aula (mp3)'))
)
audio = driver.find_element(By.PARTIAL_LINK_TEXT, 'Áudio da aula (mp3)')
audio.click()

time.sleep(5)

print("Página acessada com sessão mantida!")