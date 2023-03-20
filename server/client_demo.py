import requests
from requests.auth import HTTPBasicAuth

username = "fri"
password = "fri-pass"

response = requests.post(
    'http://127.0.0.1:8000/db/insert_page_unparsed',
    auth=HTTPBasicAuth(username, password),
    json={
        "url": "https://www.google.com/",
        "from_page_id": 0,
        "robots_content": "",
        "sitemap_content": "",
    })

if response.status_code == 200:
    print(response.json())
else:
    print('Get request failed with status code:', response.status_code)
