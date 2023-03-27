import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

conn_str = "postgresql+psycopg2://orglce:5loFzWry6ZwC@ep-falling-block-598917.eu-central-1.aws.neon.tech/neondb"

Base = sqlalchemy.orm.declarative_base()
engine = create_engine(conn_str, connect_args={'options': '-csearch_path={}'.format('crawldb')})
Base.metadata.reflect(engine)


class DataType(Base):
    __table__ = Base.metadata.tables['data_type']


class Image(Base):
    __table__ = Base.metadata.tables['image']


class Link(Base):
    __table__ = Base.metadata.tables['link']


class Page(Base):
    __table__ = Base.metadata.tables['page']


class PageData(Base):
    __table__ = Base.metadata.tables['page_data']


class PageType(Base):
    __table__ = Base.metadata.tables['page_type']


class Site(Base):
    __table__ = Base.metadata.tables['site']


class Ip(Base):
    __table__ = Base.metadata.tables['ip']


class Counters(Base):
    __table__ = Base.metadata.tables['counters']
