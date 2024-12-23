from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm


def get_all_courses_links(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(3)
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    links = driver.find_elements(By.XPATH, "//a[contains(@class, 'Link-module__link')]")
    courses_links = [link.get_attribute("href") for link in links]

    driver.quit()
    return courses_links

def get_lesson_links(url):
    base_url = 'https://www.tbank.ru'

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    links = [base_url + a['href'] for a in soup.find_all('a', class_=re.compile(r"Link-module__link"))]

    return links

def get_common_card_texts(url):
    driver = webdriver.Chrome()
    driver.get(url)
    
    try:
        WebDriverWait(driver, 4).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'CommonCard')]"))
        )

        header = driver.find_element(By.XPATH, "//*[contains(@class, 'LessonMainCoverCard')]")

        common_cards = driver.find_elements(By.XPATH, "//*[contains(@class, 'CommonCard')]")

        texts = [card.text.strip() for card in common_cards if card.text.strip()]
        result = "\n".join(texts)
        return header.text + '\n' + result

    except Exception as e:
        return ""

    finally:
        driver.quit()

courses_url = "https://www.tbank.ru/invest/education/courses/"
courses_links = get_all_courses_links(courses_url)

print(f"Найдено {len(courses_links)} курсов:")

lesson_content = []
for link in tqdm(courses_links):
    lesson_links = get_lesson_links(link)

    for lesson_link in lesson_links:
        lesson_content.append(get_common_card_texts(lesson_link))

with open('./data/courses.txt', 'w') as f:
    f.write('\n\n\n\n'.join(lesson_content))


