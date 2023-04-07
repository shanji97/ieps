import os

import requests
from requests.auth import HTTPBasicAuth
from sqlalchemy.orm import scoped_session, sessionmaker
import constants

import constants
from crawldb_model import *


session = scoped_session(
    sessionmaker(
        bind=engine
    ))

all_pages = session.query(Page).all()

pages_with_links = []
page_datas = []
for page in all_pages:
    _, ext = os.path.splitext(str(page.url))
    if ext in [".doc", ".DOC", ".DOCX", ".docx", ".ppt", ".pptx", ".PPT", ".PPTX", ".PDF"] and page.page_type_code != constants.PAGE_TYPE_BINARY:
        pages_with_links.append(page)
        page.page_type_code = constants.PAGE_TYPE_BINARY
        page_datas.append(PageData(page_id=page.id, data_type_code=ext[1:].upper(), data=str.encode("")))
session.commit()

print(len(page_datas))
print(page_datas[0].data_type_code)
print(len(pages_with_links))
print(pages_with_links[0].url)
