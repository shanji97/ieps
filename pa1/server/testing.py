import requests
from requests.auth import HTTPBasicAuth
import constants

response = requests.post(
        'http://127.0.0.1:8000/db/insert_page_data',
        auth=HTTPBasicAuth(constants.USERNAME, constants.PASSWORD),
        json={
            "page_id": 504,
            "data_type_code": constants.DATA_TYPE_PDF,
            "data": "",
        })

if response.status_code == 200:
    raise Exception('Updating html content failed with status code: ' + str(response.status_code))