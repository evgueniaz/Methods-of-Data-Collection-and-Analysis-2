from pprint import pprint
from lxml import html
import requests
import pymongo
from pymongo import MongoClient


url = 'https://news.mail.ru/?_ga=2.90596378.1604719935.1640122142-1809438773.1631561525'
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'}

response = requests.get(url, headers=header)
dom = html.fromstring(response.text)

main_news = []


items = dom.xpath(
                "//span[@class = 'photo__captions'] | "
                "//li[@class = 'list__item list__item_height_fixed_primary'] | "
                "//li[@class = 'list__item'] | "
                "//span[@class='cell'] ")

for item in items:
    piece = {}
    names = item.xpath(".//span[contains(@class, 'photo__title photo__title_new')]/text() | "
                       ".//a[@class = 'list__text']/text() | "
                       ".//span[@class = 'link__text']/text() | "
                       ".//span[@class='newsitem__title-inner']/text()  "
                       )[0]
    links = item.xpath(".//ancestor::div[contains(@class, 'daynews__item')]/a/@href | "
                       ".//a[@class = 'list__text']/@href | "
                       ".//a[contains(@class, 'link')]/@href | "
                       ".//a[contains(@class, 'newsitem__title')]/@href "
                       )
    for link in links:
        resp = requests.get(link, headers=header)
        d = html.fromstring(resp.text)
        source = d.xpath("//a[@class='link color_gray breadcrumbs__link']/span[@class='link__text']/text()")[0]
        publishing_time = d.xpath("//span[@datetime]/text()")[0]
        piece['source'] = source
        piece['publishing_time'] = publishing_time

    piece['name'] = names
    piece['link'] = links[0]
    main_news.append(piece)

pprint(len(main_news))
pprint(main_news)

client = MongoClient('127.0.0.1', 27017)

db = client['news_mailru']
news = db.news
news.insert_many(main_news)

for doc in news.find({}):
    pprint(doc)
