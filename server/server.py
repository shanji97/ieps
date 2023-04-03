import datetime
import logging
import validators
from base64 import b64decode
import imghdr

from sqlalchemy import or_, and_, extract, text

from crawldb_model import *
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, request
from flask import jsonify
from flask_httpauth import HTTPBasicAuth
import tldextract
import constants
import socket
import threading

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

app = Flask(__name__)
basic_auth = HTTPBasicAuth()

session = scoped_session(
    sessionmaker(
        bind=engine
    ))

lock = threading.Lock()


@basic_auth.verify_password
def verify_password(username, password):
    if password == constants.PASSWORD and username == constants.USERNAME:
        return username
    else:
        return None


@basic_auth.error_handler
def basic_auth_error(status):
    return jsonify({"success": False, "message": "Wrong credentials!"}), status


@app.errorhandler(404)
def not_found_error(_):
    return jsonify({"success": False, "message": "Object not found!"}), 404


@app.errorhandler(500)
def internal_error(_):
    return jsonify({"success": False, "message": "Server error!"}), 500


@app.route('/db/get_next_page_url', methods=['GET'])
@basic_auth.login_required
def get_next_page_url():
    with lock:
        current_time = datetime.datetime.now()

        # select non parsed pages and pages that have been parsing for more than 5 minutes
        to_parse_url = session.query(Page, Site, Ip) \
            .order_by(Page.parse_status, Page.parse_status_change_time) \
            .filter(Page.site_id == Site.id, Ip.domain == Site.domain,
                    extract('epoch', current_time) - extract('epoch', Ip.last_time_accessed) >= Ip.crawl_delay,
                    or_(Page.parse_status == constants.PARSE_STATUS_NOT_PARSED,
                        and_(Page.parse_status == constants.PARSE_STATUS_PARSING,
                            extract('epoch', current_time) - extract('epoch', Page.parse_status_change_time) >= constants.OLDER_THAN_SECONDS_WHEN_PARSING))).first()

        if not to_parse_url:
            return jsonify({"url": None}), 200

        session.query(Ip).filter(Ip.ip == to_parse_url.Ip.ip).update({'last_time_accessed': current_time})
        session.query(Page).filter(Page.id == to_parse_url.Page.id)\
            .update({'parse_status': constants.PARSE_STATUS_PARSING, "parse_status_change_time": current_time})
        session.commit()

    return jsonify({"url": to_parse_url.Page.url, "ip": to_parse_url.Ip.ip, "id": to_parse_url.Page.id}), 200


@app.route('/db/update_parse_status', methods=['POST'])
@basic_auth.login_required
def update_parse_status():
    request_json = request.json
    current_time = datetime.datetime.now()
    session.query(Page).filter(Page.url == request_json["url"]).update({'parse_status': request_json["parse_status"],  "parse_status_change_time": current_time})
    session.commit()

    return jsonify({"success": True, "message": "Parse status updated"}), 200


@app.route('/db/insert_page_unparsed', methods=['POST'])
@basic_auth.login_required
def insert_page_unparsed():
    with lock:
        request_json = request.json

        url = request_json["url"]
        robots_content = request_json["robots_content"]
        sitemap_content = request_json["sitemap_content"]
        from_page_id = request_json["from_page_id"]
        crawl_delay = request_json["crawl_delay"]

        site_url_extract = tldextract.extract(url)
        domain = site_url_extract.subdomain + "." + site_url_extract.domain + "." + site_url_extract.suffix
        try:
            ip = socket.gethostbyname(domain)
        except socket.gaierror:
            ip = None

        print("insert_page_unparsed")

        # Add site if it doesn't exist
        site = get_or_create_site(session, domain, robots_content, sitemap_content)
        if not site:
            return jsonify({"success": False, "message": "Site add failed!"}), 500

        _ = get_or_create_ip(session, ip, domain, crawl_delay)
        print("insert_page_unparsed1")

        # Add page
        page = create_or_create_page(
            session=session,
            site_id=site.id,
            page_type_code=constants.PAGE_TYPE_HTML,
            url=url,
            html_content=None,
            http_status_code=0,
            accessed_time=datetime.datetime.now())
        if not page:
            return jsonify({"success": False, "message": "Page add failed!"}), 500

        print("insert_page_unparsed2")

        # Add link
        link = get_or_create_link(session, from_page_id, page.id)
        if not link:
            return jsonify({"success": False, "message": "Link add failed!"}), 500

        site.last_time_accessed = datetime.datetime.now()
        session.commit()

    return jsonify({"success": True, "message": "Page added!", "added_page_id": page.id}), 200


@app.route('/db/update_page_info', methods=['POST'])
@basic_auth.login_required
def update_page_info():
    request_json = request.json

    page_id = request_json["page_id"]
    html_content = request_json["html_content"]
    page_type_code = request_json["page_type_code"]
    session.query(Page).filter(Page.id == page_id).update({
        "html_content": html_content,
        "page_type_code": page_type_code
    })
    session.commit()

    return jsonify({"success": True, "message": "Page updated!"}), 200


@app.route('/db/insert_page_data', methods=['POST'])
@basic_auth.login_required
def insert_page_data():
    request_json = request.json

    page_id = request_json["page_id"]
    data_type_code = request_json["data_type_code"]
    data = request_json["data"]

    page_data = create_page_data(session, page_id, data_type_code, data)

    if not page_data:
        return jsonify({"success": False, "message": "Page data add failed!"}), 500

    return jsonify({"success": True, "message": "Page data added!"}), 200


@app.route('/db/is_duplicate', methods=['POST'])
@basic_auth.login_required
def is_duplicate():
    request_json = request.json

    url = request_json["url"]
    html_content = request_json["html_content"]
    all_pages = session.query(Page).all()
    all_pages_urls = [page.url for page in all_pages]
    print(all_pages_urls)
    print(url)
    if url in all_pages_urls:
        print("Duplicate found: " + url)
        return jsonify({"success": True, "duplicate_found": True}), 200

    return jsonify({"success": True, "duplicate_found": False}), 200


@app.route('/db/insert_page_images', methods=['POST'])
@basic_auth.login_required
def insert_page_images():
    request_json = request.json

    page_id = request_json["page_id"]
    images_urls = request_json["images_urls"]

    images_to_add = []
    for image_url in images_urls:
        real_url = ""
        base64_string = ""
        content_type = ""
        insert_image = True
        if validators.url(image_url):
            if len(image_url) > 255:
                print("Image url too long: " + image_url)
                insert_image = False
            else:
                real_url = image_url
                # content_type, base64_string = download_image(image_url)
        else:
            base64_string = image_url
            decoded_string = b64decode(base64_string)
            content_type = imghdr.what(None, h=decoded_string)

        if insert_image:
            images_to_add.append(Image(
                page_id=page_id,
                filename=real_url,
                content_type=content_type,
                data=str.encode(base64_string),
                accessed_time=datetime.datetime.now()))

    session.bulk_save_objects(images_to_add)
    session.commit()

    return jsonify({"success": True, "message": "Page images added!"}), 200


@app.route('/db/get_robots_content', methods=['POST'])
@basic_auth.login_required
def get_robots_content():
    request_json = request.json
    url = request_json["url"]
    site_url_extract = tldextract.extract(url)
    domain = site_url_extract.subdomain + "." + site_url_extract.domain + "." + site_url_extract.suffix
    site = session.query(Site).filter(Site.domain == domain).first()
    if not site:
        return jsonify({"success": False, "message": "Site not found"}), 200
    return jsonify({"success": True, "message": "Site found", "robots_content": site.robots_content}), 200


@app.route('/db/clear_database', methods=['POST'])
@basic_auth.login_required
def clear_database():
    session.flush()
    session.execute(text(
        '''truncate table 
            crawldb.page_data, 
            crawldb.ip, 
            crawldb.page, 
            crawldb.site, 
            crawldb.link, 
            crawldb.site 
            CASCADE''').execution_options(autocommit=True))
    dummmy_page = Page(id=-1)
    session.add(dummmy_page)
    session.commit()
    return jsonify({"success": True, "message": "Frontier filled!"}), 200


def download_image(image_url):
    # TODO download image and get content type
    return "", ""


def create_page_data(session, page_id, data_type_code, data):
    page_data = PageData(
        page_id=page_id,
        data_type_code=data_type_code,
        data=str.encode(data))
    session.add(page_data)
    session.commit()
    return page_data


def get_or_create_site(session, domain, robots_content, sitemap_content):
    site = session.query(Site).filter(Site.domain == domain).first()
    if not site:
        try:
            site = Site(
                domain=domain,
                robots_content=robots_content,
                sitemap_content=sitemap_content)
            session.add(site)
            session.commit()
            logging.info("Site added: {}".format(site.domain))
            return site
        except Exception as e:
            session.rollback()
            session.close()
            logging.error("Site add failed: {}".format(e))
            return None
    return site


def get_or_create_ip(session, ip, domain, crawl_delay):
    ip_object = session.query(Ip).filter(Ip.ip == ip, Ip.domain == domain).first()
    if not ip_object:
        try:
            ip_object = Ip(
                ip=ip,
                domain=domain,
                last_time_accessed=datetime.datetime.now(),
                crawl_delay=crawl_delay)
            session.add(ip_object)
            session.commit()
            logging.info("IP added: {}".format(ip_object.ip))
            return ip_object
        except Exception as e:
            session.rollback()
            session.close()
            logging.error("IP add failed: {}".format(e))
            return None
    return ip_object


def create_or_create_page(session, site_id, page_type_code, url, html_content, http_status_code, accessed_time):
    page = session.query(Page).filter(Page.url == url).first()
    if not page:
        try:
            page = Page(
                site_id=site_id,
                page_type_code=page_type_code,
                url=url,
                html_content=html_content,
                http_status_code=http_status_code,
                accessed_time=accessed_time)
            session.add(page)
            session.commit()
            logging.info("Page added: {}".format(url))
            return page
        except Exception as e:
            session.rollback()
            session.close()
            logging.error("Page add failed: {}".format(e))
            return None
    else:
        return page


def get_or_create_link(session, from_page_id, to_page_id):
    link = session.query(Link).filter(Link.from_page == from_page_id, Link.to_page == to_page_id).first()
    if not link:
        try:
            link = Link(
                from_page=from_page_id,
                to_page=to_page_id)
            session.add(link)
            session.commit()
            logging.info("Link added: {} -> {}".format(from_page_id, to_page_id))
            return link
        except Exception as e:
            session.rollback()
            session.close()
            logging.error("Link add failed: {}".format(e))
            return None
    else:
        return link


if __name__ == "__main__":
    app.run(port=8000, debug=True)
