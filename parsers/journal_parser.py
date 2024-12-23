import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

import pandas as pd



def get_full_links(base_url, articles):
    links = []
    for article in articles:
        link_tag = article.find("a", class_=re.compile(r"_link"))
        if link_tag and "href" in link_tag.attrs:
            links.append(base_url + link_tag["href"].lstrip("/"))
    return links


def fetch_article_details(article_url):
    response = requests.get(article_url)
    if response.status_code != 200:
        print(f"Не удалось загрузить статью: {article_url}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    title_tag = soup.find("h1", class_=re.compile(r"_articleTitle"))
    title = title_tag.get_text(strip=True) if title_tag else "Без заголовка"

    subtitle_tag = soup.find("div", class_=re.compile(r"_articleSubtitle"))
    subtitle = subtitle_tag.get_text(strip=True) if subtitle_tag else "Без подзаголовка"

    content_div = soup.find("div", class_=re.compile(r"_articleView"))
    content = []
    if content_div:
        for tag in content_div.find_all(["p", "h2"], recursive=True):
            content.append(tag.get_text(strip=True))

    full_content = "\n".join(content)

    d, m, y = soup.find("div", class_=re.compile(r"_dateWrapper")).find("time").text.split('.')
    
    article_date = datetime(2000 + int(y), int(m), int(d))

    tags_links = soup.find('div', class_=re.compile(r"_subscriptionAndTags")).find_all('a')
    
    if tags_links:
        article_tags = '; '.join(link.find("span").text for link in tags_links)
    else:
        article_tags = ''

    return {
        "title": title,
        "subtitle": subtitle,
        "content": full_content,
        "date": article_date,
        "tags": article_tags
    }

def scrape_best_articles(end_date, page_type):
    base_url = "https://journal.tinkoff.ru/"
    page_num = 1
    res_path = './data/df_articles.csv'

    if os.path.exists(res_path):
        df_articles = pd.read_csv(res_path)
        df_articles['date'] = pd.to_datetime(df_articles['date'])
    else:
        df_articles = pd.DataFrame([], columns=['title', 'subtitle', 'content', 'date', 'tags'])

    headers = {"User-Agent": "Mozilla/5.0"}

    while True:
        best_url = f"{base_url}/flows/invest/{page_type}/page/{page_num}/"
        df_to_add = pd.DataFrame([], columns=['title', 'subtitle', 'content', 'date', 'tags'])

        response = requests.get(best_url, headers=headers)
        if response.status_code != 200:
            print("Ошибка при загрузке страницы лучших статей.")
            return

        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.find_all("div", class_=re.compile(r"_card"))
        article_links = get_full_links(base_url, articles)

        for article_url in article_links:
            try:
                article_data = fetch_article_details(article_url)
                df_to_add.loc[len(df_to_add)] = article_data.values()
            except Exception as e:
                print(e)
                continue

        df_to_add['date'] = pd.to_datetime(df_to_add['date'])

        data_above_end_time = df_to_add[df_to_add['date'] < end_date]
        df_articles = pd.concat([df_articles, df_to_add])
        if len(data_above_end_time) == len(df_to_add):
            df_articles[df_articles['date'] >= end_date].drop_duplicates().to_csv(res_path, index=False)
            break
        else:
            df_articles[df_articles['date'] >= end_date].drop_duplicates().to_csv(res_path, index=False)
        
        print(f'Page {page_num} was processed')
        page_num += 1

for page_type in ('best', 'new', 'posts'):
    scrape_best_articles("2024-11-01", page_type)