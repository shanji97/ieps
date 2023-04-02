import requests
from requests.auth import HTTPBasicAuth
import constants

username = "fri"
password = "fri-pass"

response = requests.post(
    'http://127.0.0.1:8000/db/insert_page_images',
    auth=HTTPBasicAuth(username, password),
    json={
        "page_id": 143,
        "images_urls": [
           "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png",
           "https://f4n3x6c5.stackpathcdn.com/UploadFile/40e97e/content-type-as-metadata-frequently-asked-questions/Images/Content-Type-as-Metadata.jpg",
        ]
    })

# response = requests.get(
#     'http://127.0.0.1:8000/db/get_next_page_url',
#     auth=HTTPBasicAuth(username, password))

if response.status_code == 200:
    print(response.json())
else:
    print('Get request failed with status code:', response.status_code)
