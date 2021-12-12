

import requests
from pprint import pprint
import json


my_params = {
    'v': 5.54,
    'user_id': '1532750',
    'token': 'token'
}
url = "https://api.vk.com/method/groups.get"

response = requests.get(url, params=my_params)
j_data = response.json()
pprint(j_data)

# search_results = []
# for elem in j_data.get("items"):
#     volume_info = elem.get('volumeInfo', None)
#     title = volume_info.get('title')
#     author = volume_info.get('authors')
#     results = dict({'Книга': title, 'Автор(ы)': author})
#     search_results.append(results)
#     pprint(f'Книга: {title} - Автор(ы): {author}')