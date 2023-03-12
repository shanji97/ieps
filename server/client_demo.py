import requests
from requests.auth import HTTPBasicAuth

username = "fri"
password = "fri-pass"

response = requests.get('http://127.0.0.1:8000/db/get_data_types', auth=HTTPBasicAuth(username, password))

if response.status_code == 200:
    print(response.json())
else:
    print('Get request failed with status code:', response.status_code)
