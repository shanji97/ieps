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


@app.route('/db/get_counter_values', methods=['GET'])
@basic_auth.login_required
def fl_get_values():
    results = session.query(Counters).all()
    results = [{
        "id": r.counter_id,
        "value": r.value
    } for r in results]
    return jsonify(results)


@app.route('/db/reset_counter_values', methods=['POST'])
@basic_auth.login_required
def fl_restart():
    session.query(Counters).update({'value': 0})
    session.commit()
    return jsonify({"success": True})


@app.route('/db/get_data_types', methods=['GET'])
@basic_auth.login_required
def get_data_types():
    results = session.query(DataType).all()
    return jsonify([d.code for d in results])


@app.route('/db/get_next_page_url', methods=['GET'])
@basic_auth.login_required
def get_next_page_url():
    current_time = datetime.datetime.now()

    # select non parsed and pages that have been parsing for more than 5 minutes
    to_parse_url = session.query(Page) \
        .order_by(Page.parse_status, Page.parse_status_change_time) \
        .filter(or_(Page.parse_status == constants.PARSE_STATUS_NOT_PARSED,
                    and_(Page.parse_status == constants.PARSE_STATUS_PARSING,
                         extract('epoch', current_time) - extract('epoch', Page.parse_status_change_time) >= 5 * 60))).first()

    if not to_parse_url:
        return jsonify({"url": None}), 200

    return jsonify({"url": [to_parse_url.url, to_parse_url.parse_status_change_time, to_parse_url.parse_status]}), 200


@app.route('/db/insert_page_unparsed', methods=['POST'])
@basic_auth.login_required
def insert_page_unparsed():
    print("neki")
    request_json = request.json

    url = request_json["url"]
    robots_content = request_json["robots_content"]
    sitemap_content = request_json["sitemap_content"]
    from_page_id = request_json["from_page_id"]

    site_url_extract = tldextract.extract(url)
    domain = site_url_extract.domain + "." + site_url_extract.suffix

    # Add site if it doesn't exist
    site = get_or_create_site(session, domain, robots_content, sitemap_content)
    if not site:
        return jsonify({"success": False, "message": "Site add failed!"}), 500

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

    return jsonify({"success": True, "message": "Page added!", "added_page_id": page.id}), 200


@app.route('/db/insert_page', methods=['POST'])
@basic_auth.login_required
def insert_page():
    request_json = request.json

    url = request_json["url"]
    site_url_extract = tldextract.extract(url)
    domain = site_url_extract.domain + "." + site_url_extract.suffix

    # Add site if it doesn't exist
    site = get_or_create_site(session, domain, request_json["robots_content"], request_json["sitemap_content"])
    if not site:
        return jsonify({"success": False, "message": "Site add failed!"}), 500

    # Add page
    page = create_page(
        session,
        site.id,
        request_json["page_type_code"],
        url + str(time.time()),
        request_json["html_content"],
        request_json["http_status_code"],
        request_json["accessed_time"])
    if not page:
        return jsonify({"success": False, "message": "Page add failed!"}), 500

    # Add link
    link = create_link(session, request_json["from_page_id"], page.id)
    if not link:
        return jsonify({"success": False, "message": "Link add failed!"}), 500

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
