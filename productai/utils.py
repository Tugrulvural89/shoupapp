import requests
from bs4 import BeautifulSoup
import time
import random


def scrape_product_info(url):
    if not url.startswith("https://"):
        print("URL must start with https://")
        return
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive',
    }

    response = requests.get(url, headers=headers)

    # 503 hatasını aşmak için istek tekrarları
    retries = 5
    while response.status_code == 503 and retries > 0:
        time.sleep(random.uniform(2, 10))  # Rastgele bekleme süresi
        response = requests.get(url, headers=headers)
        retries -= 1



    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Dinamik olarak HTML yapısında veri arama
    title = soup.find(['h1', 'h2', 'title'])
    images = soup.find_all('img')
    all_text_body = soup.find('body').get_text(separator=' ', strip=True)
    all_text_header = soup.find('body').get_text(separator=' ', strip=True)

    # Tüm img etiketlerindeki src bilgilerini liste olarak alma ve filtreleme
    # image_urls = [
    #     img['src'] for img in images if 'src' in img.attrs and (
    #             img['src'].endswith('.png') or img['src'].endswith('.jpg') or img['src'].endswith('.jpeg')
    #     )
    # ]

    image_urls = [
        img['src'] for img in images if 'src' in img.attrs
    ]

    product_info = {
        'title': title.text if title else 'Title not found',
        'image_urls': image_urls if image_urls else ['Image not found'],
        'all_text_body': all_text_body,
        'all_text_header': all_text_header,
        'page_url': url
    }
    return product_info




