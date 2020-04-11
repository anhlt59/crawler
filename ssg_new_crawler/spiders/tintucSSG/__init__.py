# -*- coding: utf8 -*-
from scrapy.http import Request
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import CloseSpider, NotConfigured

from ssg_new_crawler.spiders.common.spiders import BaseSpider
from ssg_new_crawler.models.ssg_model import News, CrawlerNews
from ssg_new_crawler.items.ssg_item import NewsItem


class SSGSpider(BaseSpider):
    # base spider
    name = 'SSGSpider'
    model = News
    custom_settings = {
        **get_project_settings(),
        # config mysql
        'MYSQL_URI': 'mysql+mysqldb://root:12345678@localhost/db_ssg?charset=utf8',
        # Configure item pipelines
        'ITEM_PIPELINES': {
           'ssg_new_crawler.pipelines.ssg_pipelines.MySQLPipeline': 300,
        },
    }

    def start_requests(self):
        if not hasattr(self, 'bdata'):
            # get data from table crawler_news
            self.bdata = self.get_data_from_db()
        # create requests
        if getattr(self, 'bdata', None):
            data = self.bdata.pop()
            item = self.load_item_from_data(data)
            yield self.create_request(item, data)

    def get_data_from_db(self):
        """Get data from crawler_news"""
        return CrawlerNews.get(self.spider_name)

    def load_item_from_data(self, data):
        item = NewsItem()
        # set default attribute
        item.setdefault('new_status', 1)
        item.setdefault('new_spider_name', data.crn_spider_name)
        item.setdefault('new_source_id', data.crn_id)
        item.setdefault('new_type', data.crn_type)
        return item

    def create_request(self, item, data, *a, **kw):
        return Request(data.crn_url, callback=self.parse, errback=self.fail, meta={'item': item, 'data': data})

    def parse(self, response):
        pass

    def parse_detail(self, response):
        pass






#
