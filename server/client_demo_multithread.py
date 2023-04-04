import requests
from requests.auth import HTTPBasicAuth
import concurrent.futures
import constants
import time
import tldextract

from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import base64


def multithread_crawler(worker_id):
    page_available = True
    while page_available:
        try:
            print_from_thread(worker_id, "INFO", "Getting next page")
            response = requests.get(
                'http://127.0.0.1:8000/db/get_next_page_url',
                auth=HTTPBasicAuth(constants.USERNAME, constants.PASSWORD))
            if response.status_code == 200:
                if response.json()["url"]:
                    print_from_thread(worker_id, "INFO", "Got next page: " + str(response.json()))

            if response.status_code == 200:
                if response.json()["url"] is not None:
                    url = response.json()["url"]
                    page_id = response.json()["id"]
                    print_from_thread(worker_id, "PARSING", url)

                    # TODO: parse page and check for duplicate
                    new_urls, new_images_urls, html_content = parse_page(page_id, url)
                    # Store canonicalized URLs only!
                    print_from_thread(worker_id, "INFO", "New URLs: " + str(new_urls))

                    # insert images from the page to db
                    if new_images_urls:
                        insert_page_images(page_id, new_images_urls)

                    # insert new urls to to the frontier
                    if new_urls:
                        for new_url in new_urls:
                            try:
                                insert_page_if_allowed(new_url, page_id, worker_id)
                            except Exception as err:
                                print("ERROR on [Thread " + str(worker_id) + "]: ", err)

                    # update page status to parsed
                    update_parse_status(url, constants.PARSE_STATUS_PARSED)
                    print_from_thread(worker_id, "PARSED", url)
                # else:
                    # page_available = False
                    # print(worker_id , ": No pages available")

            else:
                print('Get request failed with status code:', response.status_code)

        except Exception as err:
            print("ERROR on [Thread " + str(worker_id) + "]: ", err)
            time.sleep(1)


def print_from_thread(worker_id, status_string, message):
    num_of_colors = len(constants.TERMINAL_COLORS)
    print(f"{constants.TERMINAL_COLORS[worker_id % num_of_colors]}"
          "[Thread " + str(worker_id) + f"]{constants.END_COLOR} - " + status_string + ": " + message)


def is_duplicate_url(new_url, html_content):
    response = requests.post(
        'http://127.0.0.1:8000/db/is_duplicate',
        auth=HTTPBasicAuth(constants.USERNAME, constants.PASSWORD),
        json={
            "url": new_url,
            "html_content": html_content,
        })

    if response.status_code != 200:
        raise Exception('Finding duplicate failed with status code: ' + str(response.status_code))
    return response.json()['duplicate_found']


def render_page_and_extract(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(5)

    html_content = driver.page_source
    http_status_code = -1  # TODO get http status code

    # Get all 'a' tags:
    links = driver.find_elements(By.TAG_NAME, 'a')
    valid_links = []

    for link in links:
        url = link.get_attribute('href')
        # Get only gov si links 
        if url and 'gov.si' in url:
            if url and 'gov.si/#' not in url:
                valid_links.append(url)

    images = driver.find_elements(By.TAG_NAME, 'img')
    valid_images = []
    for img_element in images:
        # Get the value of the src attribute
        src = img_element.get_attribute('src')
        if src:
            if src.startswith('data:image/'):
                # This is a base64-encoded image
                # Decode the base64 data and save it to a file
                encoded_data = src.split(',', 1)[1]
                valid_images.append(encoded_data)

            else:
                # This is an image with a URL
                valid_images.append(src)

    return valid_links, valid_images, html_content, http_status_code


def parse_page(page_id, url):
    # Check content type: if not html, change data_type and add entry in
    # table page_data with page_id equal to from page id, else go on and parse html page
    is_html_code, extension = is_html(url)
    html_content = ""

    if is_html_code:
        valid_links, valid_images, html_content, http_status_code = render_page_and_extract(url)
        duplicate_id = is_duplicate(url, html_content)
        if duplicate_id == -1:
            update_page_info(page_id, html_content, constants.PAGE_TYPE_HTML, http_status_code)
            return valid_links, valid_images, html_content
        else:
            # Change page_type to DUPLICATE, update (Link) attribute from_page to
            # duplicate_id (create functions on server and send post request)
            return None, None, None
    else:
        # Change page_type to Binary and add entry in table page_data with page_id
        # equal to from page id and appropriate data_type  (.pdf, .doc, .docx, .ppt and .pptx and other types)
        update_page_info(page_id, html_content, constants.PAGE_TYPE_BINARY, 200)
        insert_page_data(page_id, extension)
        return None, None, None


def is_html(url):
    parsed_url = urlparse(url)
    if parsed_url.path.endswith('.html'):
        return (True, None)
    else:
        extensions = [
            'pdf', 'odt', 'odp', 'fodt', 'ods', 'fods', 'odg', 'fogd', 'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc',
            'docx', 'docm', 'rtf', 'csv', 'tsv', 'xlsx',
            'xlsm', 'xlsb', 'xltx', 'ppt', 'pptx', 'ppsx', 'pst', 'zip', '7z', 'pdf/a'
        ]

        for extension in extensions:
            if parsed_url.path.endswith(f'.{extension}'):
                print(f'Parsed URL contains extension: {extension}')
                return (False, extension)
            return (True, None)


def is_duplicate(url, html_content):
    # TODO
    # select pages from db with html_content equal to html_content of new page: if 0 results return -1 else return id of match
    # (send request to server + add function on server that sends query)
    id = -1
    return id


def insert_page_data(page_id, data_type_code, data=""):
    """
    If the page is not HTML, insert its data to the database.

    Input:
    * page_id: id of the page
    * data_type_code: extension of the file found on page
    * data: the file content
    """
    insert = True
    extension = ""
    if data_type_code == 'pdf':
        extension = constants.DATA_TYPE_PDF
    elif data_type_code == 'doc':
        extension = constants.DATA_TYPE_DOC
    elif data_type_code == 'docx':
        extension = constants.DATA_TYPE_DOCX
    elif data_type_code == 'ppt':
        extension = constants.DATA_TYPE_PPT
    elif data_type_code == 'pptx':
        extension = constants.DATA_TYPE_PPTX
    else:
        insert = False

    if insert:
        response = requests.post(
            'http://127.0.0.1:8000/db/insert_page_data',
            auth=HTTPBasicAuth(constants.USERNAME, constants.PASSWORD),
            json={
                "page_id": page_id,
                "data_type_code": extension,
                "data": data,
            })

        if response.status_code != 200:
            raise Exception('Updating html content failed with status code: ' + str(response.status_code))

def update_page_info(page_id, html_content, page_type_code, http_status_code):
    """
    Update page html content.

    Input:
    * page_id: id of the page
    * html_content: html content to add to page
    * page_type_code: type of page (html, binary, duplicate)
    * http_status_code: http status code of the page
    """
    response = requests.post(
        'http://127.0.0.1:8000/db/update_page_info',
        auth=HTTPBasicAuth(constants.USERNAME, constants.PASSWORD),
        json={
            "page_id": page_id,
            "html_content": html_content,
            "page_type_code": page_type_code,
            "http_status_code": http_status_code
        })

    if response.status_code != 200:
        raise Exception('Updating html content failed with status code: ' + str(response.status_code))


def insert_page_images(page_id, images_urls):
    """
    Insert images in db.

    Input:
    * page_id: id of the page
    * images_urls: list of images urls
    """
    response = requests.post(
        'http://127.0.0.1:8000/db/insert_page_images',
        auth=HTTPBasicAuth(constants.USERNAME, constants.PASSWORD),
        json={
            "page_id": page_id,
            "images_urls": images_urls,
        })

    if response.status_code != 200:
        raise Exception('Inserting images failed with status code: ' + str(response.status_code))


def update_parse_status(url, status):
    """
    Update parse status of page.

    Input:
    * url: url
    * status: parse status
    """
    response = requests.post(
        'http://127.0.0.1:8000/db/update_parse_status',
        auth=HTTPBasicAuth(constants.USERNAME, constants.PASSWORD),
        json={
            "url": url,
            "parse_status": status,
        })

    if response.status_code == 200:
        print(response.json())
    else:
        raise Exception('Update parse status request failed with status code: ' + str(response.status_code))


def insert_page_if_allowed(url, from_page_id, worker_id):
    """
    Insert page in frontier if allowed by robots.txt.

    Input:
    * url: new url
    * from_page_id: Id of page on which the url was found
    """
    # TODO: allow only sites with domain gov.si
    # Get robots.txt content if site exists id db
    robots_content = get_robots_content(url)
    if robots_content == -1:
        # New site (no robots.txt)
        # extract domain from url
        site_url_extract = tldextract.extract(url)
        domain = site_url_extract.subdomain + "." + site_url_extract.domain + "." + site_url_extract.suffix
        try:
            # request robots.txt
            robots_response = requests.get("https://" + domain + "/robots.txt")
            if robots_response.status_code == 200:
                robots_content = robots_response.text
                # Extract data from robots.txt
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
                # request sitemap
                sitemap_response = requests.get(sitemap)
                if sitemap_response.status_code == 200:
                    sitemap_content = sitemap_response.text
            except Exception as e:
                print(e)
                sitemap_content = None
        if is_page_allowed(url, disallowed, allowed):
            insert_page_unparsed(url, robots_content, sitemap_content, from_page_id, crawl_delay, worker_id)
    elif robots_content is not None and len(robots_content) != 0:
        # Robots.txt exists
        disallowed, allowed, crawl_delay, sitemap = parse_robots_content(robots_content)  # change if stored in db
        if is_page_allowed(url, disallowed, allowed):
            insert_page_unparsed(url, robots_content, sitemap, from_page_id, crawl_delay, worker_id)
    else:
        # No robots.txt
        insert_page_unparsed(url, None, None, from_page_id, constants.DEFAULT_CRAWL_DELAY_SECONDS, worker_id)


def insert_page_unparsed(url, robots_content, sitemap_content, from_page_id, crawl_delay, worker_id):
    """
    Send post request to server to insert unparsed page.
    """
    response = requests.post(
        'http://127.0.0.1:8000/db/insert_page_unparsed',
        auth=HTTPBasicAuth(constants.USERNAME, constants.PASSWORD),
        json={
            "url": url,
            "robots_content": robots_content,
            "sitemap_content": sitemap_content,
            "from_page_id": from_page_id,
            "crawl_delay": crawl_delay
        })
    if response.status_code == 200:
        if not response.json()["already_exists"]:
            print_from_thread(worker_id, "INFO", "Inserted page: " + url)
    else:
        raise Exception('Insert page unparsed request failed with status code: ' + str(response.status_code))


def get_robots_content(url):
    """
    Send post request to server to get robots content.
    """
    response = requests.post(
        'http://127.0.0.1:8000/db/get_robots_content',
        auth=HTTPBasicAuth(constants.USERNAME, constants.PASSWORD),
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
    """
    Parse robots.txt (User-agent, Allow, Disallow, Crawl-delay and Sitemap), only for user-agent: *

    Input: 

    * robots_content: content of robots.txt
    """
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
    """
    Check if page is allowed based on allowed and disallowed from robots.txt

    Input:

    * url: page url

    * disallowed: array of disallowed paths

    * allowed: array of allowed paths
    """
    for d_page in disallowed:
        if match_pattern(d_page, url):
            for a_page in allowed:
                if match_pattern(a_page, url) and a_page.count("/") > d_page.count("/"):
                    return True
            return False
    return True


def match_pattern(pattern, url):
    """
    Return True if pattern matches the url.

    Wildcard characters:
        \* designates 0 or more instances of any valid character.
        
        $ designates the end of the URL.

    Input:

    * pattern: url pattern

    * url: page url
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


max_workers = 8
with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    for i in range(max_workers):
        f = executor.submit(multithread_crawler, i)
