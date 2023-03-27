import datetime
import logging
import time

from sqlalchemy import or_, and_, func, extract

from crawldb_model import *
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, request
from flask import jsonify
from flask_httpauth import HTTPBasicAuth
import tldextract
import constants
import socket

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

app = Flask(__name__)
basic_auth = HTTPBasicAuth()

session = scoped_session(
    sessionmaker(
        autoflush=True,
        autocommit=False,
        bind=engine
    ))

USERNAME = "fri"
PASSWORD = "fri-pass"

SECOND_BETWEEN_IP_REQUESTS = 5
OLDER_THAN_SECONDS = 5 * 60


@basic_auth.verify_password
def verify_password(username, password):
    if password == PASSWORD and username == USERNAME:
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
    current_time = datetime.datetime.now()

    # select non parsed pages and pages that have been parsing for more than 5 minutes
    to_parse_url = session.query(Page, Site, Ip) \
        .order_by(Page.parse_status, Page.parse_status_change_time) \
        .filter(Page.site_id == Site.id, Ip.domain == Site.domain,
                extract('epoch', current_time) - extract('epoch', Ip.last_time_accessed) >= SECOND_BETWEEN_IP_REQUESTS,
                or_(Page.parse_status == constants.PARSE_STATUS_NOT_PARSED,
                    and_(Page.parse_status == constants.PARSE_STATUS_PARSING,
                         extract('epoch', current_time) - extract('epoch', Page.parse_status_change_time) >= OLDER_THAN_SECONDS))).first()

    if not to_parse_url:
        return jsonify({"url": None}), 200

    session.query(Ip).filter(Ip.ip == to_parse_url.Ip.ip).update({'last_time_accessed': current_time})
    session.commit()

    return jsonify({"url": to_parse_url.Page.url, "ip": to_parse_url.Ip.ip}), 200


@app.route('/db/insert_page_unparsed', methods=['POST'])
@basic_auth.login_required
def insert_page_unparsed():
    request_json = request.json

    url = request_json["url"]
    robots_content = request_json["robots_content"]
    sitemap_content = request_json["sitemap_content"]
    from_page_id = request_json["from_page_id"]

    site_url_extract = tldextract.extract(url)
    domain = site_url_extract.domain + "." + site_url_extract.suffix
    try:
        ip = socket.gethostbyname(domain)
    except socket.gaierror:
        ip = None

    # Add site if it doesn't exist
    site = get_or_create_site(session, domain, robots_content, sitemap_content)
    if not site:
        return jsonify({"success": False, "message": "Site add failed!"}), 500

    _ = get_or_create_ip(session, ip, domain)

    # Add page
    page = create_page(
        session=session,
        site_id=site.id,
        page_type_code=constants.PAGE_TYPE_HTML,
        url=url + str(time.time()),  # for testing purposes so that every url is different
        html_content=None,
        http_status_code=0,
        accessed_time=datetime.datetime.now())
    if not page:
        return jsonify({"success": False, "message": "Page add failed!"}), 500

    # Add link
    link = create_link(session, from_page_id, page.id)
    if not link:
        return jsonify({"success": False, "message": "Link add failed!"}), 500

    site.last_time_accessed = datetime.datetime.now()
    session.commit()

    return jsonify({"success": True, "message": "Page added!", "added_page_id": page.id}), 200


@app.route('/db/insert_page', methods=['POST'])
@basic_auth.login_required
def insert_page():
    request_json = request.json

    url = request_json["url"]
    site_url_extract = tldextract.extract(url)
    domain = site_url_extract.domain + "." + site_url_extract.suffix
    try:
        ip = socket.gethostbyname(domain)
    except socket.gaierror:
        ip = None

    # Add site if it doesn't exist
    site = get_or_create_site(session, domain, request_json["robots_content"], request_json["sitemap_content"])
    if not site:
        return jsonify({"success": False, "message": "Site add failed!"}), 500

    _ = get_or_create_ip(session, ip, domain)

    # Add page
    page = create_page(
        session=session,
        site_id=site.id,
        page_type_code=request_json["page_type_code"],
        url=url + str(time.time()),
        html_content=request_json["html_content"],
        http_status_code=request_json["http_status_code"],
        accessed_time=request_json["accessed_time"])
    if not page:
        return jsonify({"success": False, "message": "Page add failed!"}), 500

    # Add link
    link = create_link(session, request_json["from_page_id"], page.id)
    if not link:
        return jsonify({"success": False, "message": "Link add failed!"}), 500

    site.last_accessed_time = datetime.datetime.now()
    session.commit()

    return jsonify({"success": True, "message": "Page added!", "added_page_id": page.id}), 200


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


def get_or_create_ip(session, ip, domain):
    ip_object = session.query(Ip).filter(Ip.ip == ip, Ip.domain == domain).first()
    if not ip_object:
        try:
            ip_object = Ip(
                ip=ip,
                domain=domain,
                last_time_accessed=datetime.datetime.now())
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


def create_page(session, site_id, page_type_code, url, html_content, http_status_code, accessed_time):
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


def create_link(session, from_page_id, to_page_id):
    try:
        link = Link(
            from_page=to_page_id,  # TODO replace with request_json["from_page_id"]
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


if __name__ == "__main__":
    app.run(port=8000, debug=True)
