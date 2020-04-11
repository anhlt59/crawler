# -*- coding: utf-8 -*-
from scrapy import signals
from scrapy.exceptions import DontCloseSpider, CloseSpider

import logging


logger = logging.getLogger(__name__)


class ScheduleRequestMiddleware:
    """ If spider.start_request() is not empty schedule new request"""
    logger = logger.getChild('schedule')

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_idle, signal=signals.spider_idle)
        return s

    def spider_idle(self, spider):
        empty = True
        reqs = spider.start_requests()

        # Create new request
        for req in reqs:
            spider.crawler.engine.crawl(req, spider)
            if empty:
                empty = False

        # Check start_request is empty
        if not empty:
            raise DontCloseSpider
            # self.logger.info(f'{spider.name} request more data')
        else:
            self.logger.info(f'Data is empty. Stop {spider.name}')
            # raise CloseSpider(f'Data is empty. Stop {spider.name}')
