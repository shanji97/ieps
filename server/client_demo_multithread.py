import requests
from requests.auth import HTTPBasicAuth
import concurrent.futures
import constants
import time
import tldextract

username = "fri"
password = "fri-pass"


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
                    new_urls = []
                    for new_url in new_urls:
                        insert_page_if_allowed(new_url, response.json()["id"])
                    #update_parse_status(url, constants.PARSE_STATUS_PARSED)
                else:
                    page_available = False
                    print(worker_id , ": No pages available")

            else:
                print('Get request failed with status code:', response.status_code)

        except Exception as err:
            print(worker_id, err)
            time.sleep(1)
            

def parse_page(url):
    # TODO
    return None

def update_parse_status(url, status):
    response = requests.post(
     'http://127.0.0.1:8000/db/update_parse_status',
     auth=HTTPBasicAuth(username, password),
     json={
         "url": url,
         "parse_status": status,
     })

    if response.status_code == 200:
        print(response.json())
    else:
        raise Exception('Update parse status request failed with status code: ' + str(response.status_code))
    
def insert_page_if_allowed(url, from_page_id):
    robots_content = get_robots_content(url)
    if robots_content == -1:
        # New site
        site_url_extract = tldextract.extract(url)
        domain = site_url_extract.subdomain + "." + site_url_extract.domain + "." + site_url_extract.suffix
        try:
            robots_response = requests.get("https://" + domain + "/robots.txt")
            if robots_response.status_code == 200:
                robots_content = robots_response.text
                disallowed, allowed, crawl_delay, sitemap = parse_robots_content(robots_content)
        except Exception as e:
            print(e)
            robots_content = None
            sitemap_content = None
            disallowed = []
            allowed = []
            sitemap = None
        if sitemap:
            try:
                sitemap_response = requests.get(sitemap)
                if sitemap_response.status_code == 200:
                    sitemap_content = sitemap_response.text
            except Exception as e:
                print(e)
                sitemap_content = None
        if is_page_allowed(url, disallowed, allowed):
            insert_page_unparsed(url, robots_content, sitemap_content, from_page_id)
    elif robots_content is not None and len(robots_content) != 0:
        # Robots.txt exists
        disallowed, allowed, crawl_delay, sitemap = parse_robots_content(robots_content) # change if stored in db
        if is_page_allowed(url, disallowed, allowed):
            insert_page_unparsed(url, robots_content, sitemap, from_page_id)
    else:
        # No robots.txt
        insert_page_unparsed(url, None, None, from_page_id)

def insert_page_unparsed(url, robots_content, sitemap_content, from_page_id):
    response = requests.post(
    'http://127.0.0.1:8000/db/insert_page_unparsed',
    auth=HTTPBasicAuth(username, password),
    json={
        "url": url,
        "robots_content": robots_content,
        "sitemap_content": sitemap_content,
        "from_page_id": from_page_id
    })
    if response.status_code == 200:
        print(response.json())
    else:
        raise Exception('Insert page unparsed request failed with status code: ' + str(response.status_code))

def get_robots_content(url):
    response = requests.post(
        'http://127.0.0.1:8000/db/get_robots_content',
        auth=HTTPBasicAuth(username, password),
        json={
        "url": url
        })
    if response.status_code == 200:
        if response.json()["success"]:
            return response.json()["robots_content"]
        else:
            return -1
    else:
        raise Exception('Get robots content request failed with status code: ' + str(response.status_code))

def parse_robots_content(robots_content):
    user_agent_found = False
    disallowed_pages = []
    allowed_pages = []
    crawl_delay = None
    sitemap = None
    for line in robots_content.split("\n"):
        split_line = line.strip().lower().split(" ")
        if len(split_line) == 2:
            if user_agent_found:
                if split_line[0] == "user-agent:" and split_line[1] != "*":
                    user_agent_found = False
                elif split_line[0] == "disallow:":
                    disallowed_pages.append(split_line[1])
                elif split_line[0] == "allow:":
                    allowed_pages.append(split_line[1])
                elif split_line[0] == "crawl-delay:" and split_line[1].isnumeric():
                    crawl_delay = int(split_line[1])
                elif split_line[0] == "sitemap:":
                    sitemap = split_line[1]       
            elif split_line[0] == "user-agent:" and split_line[1] == "*":
                user_agent_found = True
    return (disallowed_pages, allowed_pages, crawl_delay, sitemap)

def is_page_allowed(url, disallowed, allowed):
    for d_page in disallowed:
        if match_pattern(d_page, url):
            for a_page in allowed:
                if match_pattern(a_page, url) and a_page.count("/") > d_page.count("/"):
                    return True
            return False
    return True

def match_pattern(pattern, url):
    """
    Wildcard characters:
        \* designates 0 or more instances of any valid character.
        
        $ designates the end of the URL.
    """
    parts = []
    if pattern[-1] == "$":
        parts = pattern[:-1].split("*")
        if not url.endswith(parts[-1]):
            return False
        parts = parts[:-1]
    else:
        parts = pattern.split("*")
    
    for part in parts:
        if url.find(part) == -1:
            return False
    return True

max_workers = 3
with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    for i in range(max_workers):
        f = executor.submit(multithread_crawler, i)