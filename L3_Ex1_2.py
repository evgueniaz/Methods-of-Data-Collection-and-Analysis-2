
from pprint import pprint
from bs4 import BeautifulSoup as bs
import json
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke
import requests
import xml.etree.ElementTree as ET
import datetime


post = input(f'Введите ключевое слово в названии должности >>>  ')
pages = input(f'Введите количество страниц с вакансиями или нажмите клавишу Enter, чтобы вывести все страницы >>>  ')
if pages.isnumeric():
    x = int(pages)
else:
    x = None

url = 'https://spb.hh.ru'
full_url = 'https://spb.hh.ru/search/vacancy/'

params = {'text': post,
          'area': '2',
          'items_on_page': '20'}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}

vacancies = []
i = 0

client = MongoClient('127.0.0.1', 27017)
db = client['hh']
positions_mongo = db.positions_mongo

while True:
    response = requests.get(full_url, params=params, headers=headers)
    soup = bs(response.text, 'html.parser')

    vacancies_list = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})

    if not vacancies_list or not response.ok:
        break

    for vacancy in vacancies_list:
        vacancy_data = {}
        vacancy_info = vacancy.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})
        vacancy_name = vacancy_info.text

        vacancy_link = vacancy.find('a', attrs={'href': True})
        link = vacancy_link.get('href')

        vacancy_wedge = vacancy.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
        if vacancy_wedge:
            wedge_amount = vacancy_wedge.text
            wedge_amount = wedge_amount.replace('\u202f', '')
            wedge_amount = wedge_amount.split()
            wedge_currency = wedge_amount[-1]

            if wedge_amount[0] == 'от':
                vacancy_wedge_min = int(wedge_amount[1])
                vacancy_wedge_max = None
            if wedge_amount[0] == 'до':
                vacancy_wedge_max = int(wedge_amount[1])
                vacancy_wedge_min = None
            if wedge_amount[0].isnumeric():
                vacancy_wedge_min = int(wedge_amount[0])
                vacancy_wedge_max = int(wedge_amount[2])

        else:
            vacancy_wedge_max = None
            vacancy_wedge_min = None
            wedge_currency = None

        vacancy_data['vacancy_name'] = vacancy_name
        vacancy_data['link'] = link
        vacancy_data['min_wedge'] = vacancy_wedge_min
        vacancy_data['max_wedge'] = vacancy_wedge_max
        vacancy_data['wedge_currency'] = wedge_currency
        vacancy_data['vacancy_site'] = url

        vacancies.append(vacancy_data)

        try:
            positions_mongo.insert_one(vacancy_data)
            positions_mongo.create_index('link', unique=True)
        except dke:
            continue

    i += 1
    next_page = soup.find('a', attrs={'data-qa': "pager-next"})
    if x == None:
        if next_page:
            full_url = url + next_page.get('href')
        else:
            break

    else:
        if i < x:
            if next_page:
                full_url = url + next_page.get('href')
            else:
                break
        else:
            break


url = 'http://www.cbr.ru/scripts/XML_daily.asp'
response = requests.get(url)
data = response.content
tree = ET.fromstring(data)

date = tree.attrib
rate_date = date['Date']
rate_date = datetime.datetime.strptime(rate_date, "%d.%m.%Y").date()
print(f'Exchange rate at {rate_date}')

def currency_rates(currency_code):
    i = 0
    value = None
    for code in tree.iter('CharCode'):
        if code.text == currency_code.upper():
            value = tree[i][4].text
            value = float(value.replace(',', '.'))
        i += 1
    return value


salary_request = int(input(f'Введите желаемую заплату в рублях >>>  '))
list_of_currencies = {'USD': 0, 'EUR': 0, 'руб.': 1}

wished_usd_wedge = salary_request / currency_rates('USD')
wished_eur_wedge = salary_request / currency_rates('EUR')

suitable_vacancies = []

n = 0
for item in positions_mongo.find(
        {'$or': [
            {'wedge_currency': 'USD', '$and': [{'$or': [{'min_wedge': {'$gte': wished_usd_wedge}}, {'max_wedge': {'$gte': wished_usd_wedge}}]}]},
            {'wedge_currency': 'EUR', '$and': [{'$or': [{'min_wedge': {'$gte': wished_eur_wedge}}, {'max_wedge': {'$gte': wished_eur_wedge}}]}]},
            {'wedge_currency': 'руб.', '$and': [{'$or': [{'min_wedge': {'$gte': salary_request}}, {'max_wedge': {'$gte': salary_request}}]}]}
            ]}):
    n += 1
    print(f'Вакансия, соответствующая указанной зарплате:  ')
    pprint(item)
print(f'Всего найдено  {n}  вакансий, соответствующих указанной зарплате')

