import requests
from requests.auth import HTTPBasicAuth
import constants

username = "fri"
password = "fri-pass"

response = requests.post(
    'http://127.0.0.1:8000/db/insert_page_data',
    auth=HTTPBasicAuth(username, password),
    json={
        "page_id": 143,
        "data_type_code": constants.DATA_TYPE_DOC,
        "data": "drek"
    })

# response = requests.get(
#     'http://127.0.0.1:8000/db/get_next_page_url',
#     auth=HTTPBasicAuth(username, password))

if response.status_code == 200:
    print(response.json())
else:
    print('Get request failed with status code:', response.status_code)
