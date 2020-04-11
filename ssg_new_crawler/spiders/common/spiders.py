# -*- coding: utf8 -*-
from scrapy import Spider
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import CloseSpider, NotConfigured
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet import reactor, defer
from twisted.internet.error import TimeoutError, TCPTimedOutError
import logging
import re


class Splash(Spider):
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_splash.SplashCookiesMiddleware': 723,
            'scrapy_splash.SplashMiddleware': 725,
            },
        'SPIDER_MIDDLEWARES': {
            'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
        },
    }
    script = """
    function main(splash, args)
      assert(splash:go(args.url))
      assert(splash:wait(1))
      return splash:html()
    end
    """
    # def ...


class Selenium(Spider):
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'ssg_new_crawler.middlewares.selenium.SeleniumMiddleware': 800,
        }
    }


class SeleniumWire(Spider):
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'ssg_new_crawler.middlewares.selenium.SeleniumWireMiddleware': 800,
        }
    }


class BaseSpider(Spider):

    name = "BaseSpider"
    model = None
    custom_settings = {
        **get_project_settings(),
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'ssg_new_crawler.middlewares.scheduler.ScheduleRequestMiddleware': 100,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
        },
    }

    def __init__(self, *a, **kw):
        # load config lưu lại trong self.config
        self.settings = get_project_settings()
        # config logging
        configure_logging(install_root_handler=False,)
        logging.config.fileConfig(self.settings.get('LOGCONF'), disable_existing_loggers=False)
        super().__init__(*a, **kw)
        # get spider_name
        sname = self.name.lower()
        self.spider_name = re.sub(r'(cat|detail)$', '', sname) # AgodaDetail >> spider_name = agoda

    @classmethod
    def update_settings(cls, settings):
        """Load custom_settings from another subclass"""
        custom_settings = {}
        DOWNLOADER_MIDDLEWARES = {}
        SPIDER_MIDDLEWARES = {}

        # update DOWNLOADER_MIDDLEWARES and SPIDER_MIDDLEWARES, overwrite a nother setting attributes
        for cl in cls.mro():
            cls_settings =  cl.custom_settings or {} if 'custom_settings' in dir(cl) else {}
            DOWNLOADER_MIDDLEWARES.update(cls_settings.pop('DOWNLOADER_MIDDLEWARES', {}))
            SPIDER_MIDDLEWARES.update(cls_settings.pop('SPIDER_MIDDLEWARES', {}))
            custom_settings.update(cls_settings)

        custom_settings.update(
            DOWNLOADER_MIDDLEWARES=DOWNLOADER_MIDDLEWARES,
            SPIDER_MIDDLEWARES=SPIDER_MIDDLEWARES
        )
        settings.setdict(custom_settings, priority='spider')

    def success(self, response):
        self.logger.info(f' post result {response.text} - {response.url}')

    def fail(self, failure):
        # callback if failures
        if failure.check(HttpError):
            response = failure.value.response
            status = response.status
            self.logger.error(f"HttpError occurred on {response.url} - got {status}")

            if status == 504:
                self.logger.info('Waiting for Splash restart - 10s')
                request = failure.request
                d = defer.Deferred()
                reactor.callLater(10.0, d.callback, request)
                return d

        elif failure.check(DNSLookupError):
            self.logger.error(f"DNSLookupError occurred on {failure.request.url}")
            raise CloseSpider("DNSLookupError")

        elif failure.check(TimeoutError, TCPTimedOutError):
            self.logger.error(f"TimeoutError occurred on {failure.request.url}")
            raise CloseSpider(f"TimeoutError")
        # self.logger.error(repr(failure))

    def start_requests(self):
        if not hasattr(self, 'bdata'):
            # get data from table crawler_news
            self.bdata = self.get_data_from_db()
        # create requests
        if getattr(self, 'bdata', None):
            data = self.bdata.pop()
            item = self.load_item_from_data(data)
            yield self.create_request(item, data)

    def create_request(self, item, data, *a, **kw):
        """return Request or SplashRequest or SeleniumRequest..."""
        # url = ''
        # return Request(url, callback=self.parse, errback=self.fail, meta={'item': item, 'data': data})
        pass

    def get_data_from_db(self):
        """return list data"""
        # return CrawlerNews.get(self.spider_name)
        pass

    def load_item_from_data(self, data):
        """return Item"""
        # set default attribute
        pass


# use splash and SeleniumWire
# class SampleSpider(BaseSpider, Splash, Selenium):
#     name = 'SampleSpider'
#     ...
