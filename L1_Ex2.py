

import requests
from pprint import pprint
import json

key = 'mystic'
my_params = {
    'q': key,
    'appid': 'Password'
}
url = "https://www.googleapis.com/books/v1/volumes"

response = requests.get(url, params=my_params)
j_data = response.json()
# pprint(j_data)

search_results = []
for elem in j_data.get("items"):
    volume_info = elem.get('volumeInfo', None)
    title = volume_info.get('title')
    author = volume_info.get('authors')
    results = dict({'Книга': title, 'Автор(ы)': author})
    search_results.append(results)
    pprint(f'Книга: {title} - Автор(ы): {author}')

pprint(search_results)

with open('book_search_results.json', 'w', encoding='utf-8') as bsr:
    json.dump(search_results, bsr, ensure_ascii=False, indent=4)