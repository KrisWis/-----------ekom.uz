import requests
from bs4 import BeautifulSoup

URL = 'https://ekom.uz/'
HEADERS = {'accept': '*/*',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.5.715 Yowser/2.5 Safari/537.36'}


def get_html(url, params=''):

    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_categories(html):

    soup = BeautifulSoup(html, 'html.parser')

    items = soup.find_all('li', class_='ty-menu__item cm-menu-item-responsive first-lvl')

    categories = []

    for item in items:
        categories.append({
                "category": item.find('a', class_='ty-menu__item-link a-first-lvl').find("span", class_="menu-lvl-ctn exp-wrap").bdi.text,
                "link": item.find("a", class_="ty-menu__item-link a-first-lvl").get("href")
                #'image':item.find('a', class_="item__thumbnail").find('img').get('src'),
                #'code':item.find('button',class_='code').get('data-target'),
                #'author':item.find('div', class_='item__details').find('a').get_text('href',strip=True)
        }
        )

    categories[0]["link"] += "/"
    return categories


def get_items(html, link):
    html = get_html(link)
    soup = BeautifulSoup(html.text, 'html.parser')
    items = soup.find_all('div', class_='ty-column3')
    item_list = []
    for item in items:
        try:
            item_list.append({
                "name": item.find("a", class_="product-title").text,
                "link": item.find("a", class_="product-title").get('href'),
                "photo": item.find("div", class_="ut2-gl__image").img.get("src"),
                "availability": item.find("div", class_="ut2-gl__amount").span.get_text(strip=True),
                "price": item.find("span", class_="ty-no-price").text if item.find("span", class_="ty-price-num") is None else item.find("span", class_="ty-price-num").text + " сум"

            }
            )
        except:
            pass

    return item_list


html = get_html(URL)
categories = get_categories(html.text)