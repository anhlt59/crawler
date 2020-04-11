# -*- coding: utf-8 -*-
import logging


logger = logging.getLogger(__name__)
logger.setLevel('INFO')


class MySQLPipeline:
    # stats_name = 'mysql_pipeline'

    def __init__(self, crawler):
        self.stats = crawler.stats
        self.model = crawler.spider.model
        self.name = crawler.spider.name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def close_spider(self, spider):
        pass

    def __del__(self):
        self.model._session.close()

    def process_item(self, item, spider):
        try:
            self.model.update(item)
            self.stats.inc_value(f'{self.name}/saved') # collect stats
            # logger.info(f'{self.name}: Saved item {item} done')
        except Exception as e:
            self.model._session.rollback()
            self.stats.inc_value(f'{self.name}/error')
            logger.exception(f'{self.name}: Saved item {item} fail: {repr(e)}')
        return item
