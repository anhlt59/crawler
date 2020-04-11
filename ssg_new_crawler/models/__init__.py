# -*- coding: utf-8 -*-
from scrapy.utils.project import get_project_settings
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import scoped_session, sessionmaker
import sqlalchemy as sa


mysql_uri = get_project_settings().get('MYSQL_URI')

engine = sa.create_engine(mysql_uri, encoding='utf-8', pool_recycle=3)
Session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))

Base = declarative_base(metadata=sa.MetaData())
Base._session = Session
