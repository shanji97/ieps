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
                    # TODO: parse page and check for duplicate
                    data = parse_page(url)
                    # Store canonicalized URLs only!
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
    # fetch and render page (selenium)
    #Check content type: if not html, change data_type and add entry in table page_data with page_id equal to from page id, else go on and parse html page
    if is_html(url):
        html_content = None
        duplicate_id = is_duplicate(html_content)
        if is_duplicate(html_content) == -1:
            # Extract links (attribute href, onlcick javascript events) and images (img tag, where src points to url) (selenium)
            ...
        else:
            # Change page_type to DUPLICATE, update (Link) attribute from_page to duplicate_id (create functions on server and send post request)
            ...
    else:
        # Change page_type to Binary and add entry in table page_data with page_id equal to from page id and appropriate data_type  (.pdf, .doc, .docx, .ppt and .pptx) 
        #(create functions on server and send post request)
        ...
       
    # Return links and images
    return None

def is_html(url):
    # TODO
    # Check if content is html
    return True


def is_duplicate(html_content):
    # TODO
    # select pages from db with html_content equal to html_content of new page: if 0 results return -1 else return id of match
    # (send request to server + add function on server that sends query)
    id = -1
    return id

def update_parse_status(url, status):
    """
    Update parse status of page.

    Input:
    * url: url
    * status: parse status
    """
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
                #Extract data from robots.txt
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
    """
    Send post request to server to insert unparsed page.
    """
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
    """
    Send post request to server to get robots content.
    """
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

max_workers = 3
with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    for i in range(max_workers):
        f = executor.submit(multithread_crawler, i)