import requests
from requests.auth import HTTPBasicAuth
import constants

seed_urls = [
    "https://www.gov.si/",
    "https://spot.gov.si/spot/drzavljani/zacetna.evem",
    "https://e-uprava.gov.si/",
    "https://www.e-prostor.gov.si/"]

# clear database and insert dummy page
response = requests.post('http://127.0.0.1:8000/db/clear_database',
                         auth=HTTPBasicAuth(constants.USERNAME, constants.PASSWORD))

if response.status_code == 200:
    print("Database cleared\n------")
else:
    raise Exception("Database not cleared")

# insert unparsed initial pages
for url in seed_urls:
    response_insert = requests.post(
        'http://127.0.0.1:8000/db/insert_page_unparsed',
        auth=HTTPBasicAuth(constants.USERNAME, constants.PASSWORD),
        json={
            "url": url,
            "robots_content": "",
            "sitemap_content": "",
            "from_page_id": -1,
            "crawl_delay": 5})  # TODO change back to constants.DEFAULT_CRAWL_DELAY_SECONDS
    if response_insert.status_code == 200:
        print("Seed page inserted: " + url)
    else:
        raise Exception("Page not inserted: " + url)
