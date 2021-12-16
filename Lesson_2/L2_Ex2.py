
import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import json

post = input(f'Введите ключевое слово в названии должности >>>  ')

url = 'https://spb.superjob.ru'
full_url = 'https://spb.superjob.ru/vacancy/search/'
# page = 1

params = {'keywords': post,
          'geo%5Bt%5D%5B0%5D': '14'
          }
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}

vacancies = []

while True:

    response = requests.get(full_url, params=params, headers=headers)
    soup = bs(response.text, 'html.parser')
    vacancies_list = soup.find_all('span', attrs={'class': '_1e6dO _1XzYb _2EZcW'})
    # pprint(vacancies_list)
    # print(len(vacancies_list))

    if not vacancies_list or not response.ok:
        break

    for vacancy in vacancies_list:
        vacancy_data = {}
        vacancy_info = vacancy.find('a', attrs={'target': '_blank'})
        vacancy_name = vacancy_info.text
        link = url + vacancy_info.get('href')
        # print(link)
        vacancy_wedge = vacancy.next_sibling.text

        if vacancy_wedge:

            wedge_amount = vacancy_wedge.replace('\xa0', ' ')
            wedge_amount = wedge_amount.split()
            # pprint(wedge_amount)
            try:
                wedge_currency = wedge_amount[-1].split('.')
                wedge_currency = wedge_currency[-2]
            except:
                wedge_currency = None
                # pprint(wedge_currency)
    #
            if wedge_amount[0] == 'от':
                vacancy_wedge_min = int(wedge_amount[1] + wedge_amount[2])
                vacancy_wedge_max = None

            elif wedge_amount[0] == 'до':
                vacancy_wedge_max = int(wedge_amount[1] + wedge_amount[2])
                vacancy_wedge_min = None

            elif wedge_amount[0].isnumeric() and wedge_amount[2] == '-':
                vacancy_wedge_min = int(wedge_amount[0] + wedge_amount[1])
                vacancy_wedge_max = int(wedge_amount[3] + wedge_amount[4])

            elif wedge_amount[0].isnumeric():
                vacancy_wedge_min = int(wedge_amount[0] + wedge_amount[1])
                vacancy_wedge_max = int(wedge_amount[0] + wedge_amount[1])

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

    next_page = soup.find('a', attrs={'class': "icMQ_ bs_sM _3ze9n _1M2AW f-test-button-2 f-test-link-2"})

    if next_page:
        next_page = next_page.get('href')
        full_url = url + next_page
        print(full_url)
    else:
        break

with open('vacancies_superjob_search.json', 'w') as v:
    json.dump(vacancies, v)
    json_list = json.dumps(vacancies)

print(f'Всего найдено ', len(vacancies), ' вакансий')
pprint(vacancies)

