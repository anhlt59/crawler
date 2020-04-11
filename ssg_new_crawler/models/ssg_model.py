# -*- coding: utf-8 -*-
import time
from sqlalchemy import Column, Integer, String, Unicode, Text
from sqlalchemy import or_, and_

from ssg_new_crawler.models import Base
from ssg_new_crawler.utils import strmd5


class News(Base):
    __tablename__ = 'news'

    new_id = Column(Integer, primary_key=True, autoincrement=True)
    new_status = Column(Integer)
    new_hot = Column(Integer)
    new_category_id = Column(Integer)
    new_source_id = Column(Integer)
    new_type = Column(Integer)
    new_spider_name =  Column(Unicode(255))
    # cat
    new_source_url = Column(Unicode(255))
    # detail
    new_title = Column(Unicode(255))
    new_image = Column(Unicode(255))
    new_content = Column(Text)
    new_description = Column(Text)
    new_title_md5 = Column(Unicode(255))
    # auto generate
    new_create_time = Column(Integer, default=time.time)
    new_update_time = Column(Integer, onupdate=time.time)

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        title = kw.get('new_title', None)
        if title:
            self.new_title_md5 = strmd5(title)

    @classmethod
    def get(cls, spider_name, new_status=1, limit=100):
        return cls._session.query(cls).filter(and_(cls.new_spider_name==spider_name, cls.new_status==1))[:limit]

    @classmethod
    def exist(cls, item):
        new_source_url = item.get('new_source_url', '')
        if new_source_url and cls._session.query(cls).filter(cls.new_source_url==new_source_url).all():
            return True
        else:
            return False

    @classmethod
    def update(cls, item):
        data = cls(**item)
        cls._session.add(data)
        cls._session.commit()
        # new_id = item.get('new_id')
        # dict_data = {key:value for key, value in data.__dict__.items() if not key.startswith('_')}
        #
        # if not new_id:
        #     # update category if fail insert
        #     result = cls._session.query(cls).filter(cls.new_source_url==item.get('new_source_url')).update(dict_data)
        #     if not result:
        #         cls._session.add(data)
        #     cls._session.commit()
        # else:
        #     # update detail
        #     cls._session.query(cls).filter(cls.new_id==new_id).update(dict_data)
        #     cls._session.commit()


class CrawlerNews(Base):
    __tablename__ = 'crawler_news'

    crn_id = Column(Integer, primary_key=True, autoincrement=True)
    crn_type = Column(Integer)
    crn_status = Column(Integer)
    crn_spider_name =  Column(Unicode(255))
    crn_url = Column(Unicode(255))
    crn_create_time = Column(Integer, default=time.time)

    @classmethod
    def get(cls, spider_name):
        return cls._session.query(cls).filter(cls.crn_spider_name==spider_name).all()
