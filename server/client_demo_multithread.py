import requests
from requests.auth import HTTPBasicAuth
import concurrent.futures
#import threading

username = "fri"
password = "fri-pass"
#lock = threading.Lock()


def multithread_crawler(worker_id):
    page_available = True
    while page_available:
        try:
            response = requests.get(
            'http://127.0.0.1:8000/db/get_next_page_url',
            auth=HTTPBasicAuth(username, password))
            
            if response.status_code == 200:
                if response.json()["url"] is not None:
                    print(worker_id, response.json())
                    url = response.json()["url"]
                    # TODO: parse page
                    data = parse_page(url)
                    # TODO: add data to db
                    # TODO: change status to parsed
                else:
                    page_available = False
                    print(worker_id , ": No pages available")

            else:
                print('Get request failed with status code:', response.status_code)

        except Exception as err:
            print(worker_id, err)
            

def parse_page(url):
    # TODO
    return None

max_workers = 3
with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    for i in range(max_workers):
        f = executor.submit(multithread_crawler, i)