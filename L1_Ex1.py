
# 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

# https://api.github.com/users/evgueniaz/repos

import json
import requests
from pprint import pprint
user_login = 'evgueniaz'
url = "https://api.github.com/users/" + user_login + "/repos"

response = requests.get(str(url))
j_data = response.json()
# pprint(j_data)
with open('my_file.jsn', 'a+') as f:
    json.dump(j_data, f)

for elem in j_data:
    repo_name = elem.get('name', None)
    pprint(repo_name)



