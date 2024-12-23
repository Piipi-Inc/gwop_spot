from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import locale
import time

import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import pandas as pd


locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

driver = webdriver.Chrome()

def get_articles():
    url = "https://www.tbank.ru/invest/research/all/"
    driver.get(url)
    time.sleep(3)

    articles_data = []
    six_months_ago = datetime.now() - timedelta(days=180)
    count_pages = 0
    while True:
        try:
            show_more_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'Button-module__button')]"))
            )
            show_more_button.click()
            count_pages += 1
            time.sleep(2)
        except Exception as e:
            print("Кнопка 'Показать еще' больше не доступна или произошла ошибка:", e)
            break
    print('Общее ко-во статей примерно: ', count_pages * 30)
    articles = driver.find_elements(By.XPATH, "//div[starts-with(@class, 'ResearchCatalogNews')]")
    count_articles = 0
    for article in articles:
        try:
            link_element = article.find_element(By.XPATH, ".//a[starts-with(@class, 'Link-module')]")
            title = link_element.text
            link = link_element.get_attribute("href")

            date_element = article.find_element(By.XPATH, ".//div[contains(@class, 'date')]")
            date_text = date_element.text
            article_date = datetime.strptime(date_text, "%d %B %Y")

            count_articles += 1

            if article_date >= six_months_ago:
                articles_data.append({"title": title, "date": article_date, "link": link})
        except Exception as e:
            print(f"Ошибка при обработке статьи: {e}")
    print("Общее кол-во статей: ", count_articles)
    return articles_data

def parse_article(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    if '/research/' in url:
        paragraphs = soup.find_all('p')
        return '\n'.join(p.text for p in paragraphs)
    else:
        postpages = soup.find_all("div", class_=re.compile(r"pulse-postpage"))
        
        max_idx = 0
        max_val = 0
        for i, post in enumerate(postpages):
            val = len(post.find_all('p'))
            if val > max_val:
                max_val = val 
                max_idx = i
        post = postpages[max_idx]
        return post.text

try:
    articles = get_articles()

    for i, article in tqdm(enumerate(articles)):
        if article['content']:
            continue
        try:
            article['content'] = parse_article(article['link'])
        except Exception as e:
            article['content'] = ''
        articles[i] = article
    
    df_articles_analytics = pd.DataFrame(articles)
    df_articles_analytics.to_csv('./data/df_articles_analytics.csv')
finally:
    driver.quit()

