# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join

from ssg_new_crawler.utils import strmd5, strstrip, mapcompose


class NewsItem(scrapy.Item):
    new_id = scrapy.Field()
    new_hot = scrapy.Field()
    new_category_id = scrapy.Field()
    new_status = scrapy.Field()
    new_type = scrapy.Field()
    new_source_id = scrapy.Field()
    new_spider_name = scrapy.Field()
    new_create_time = scrapy.Field()
    new_update_time = scrapy.Field()
    # cat
    new_source_url = scrapy.Field()
    new_image = scrapy.Field(input_processor=MapCompose(remove_tags, str.strip()))
    # detail
    new_title = scrapy.Field(input_processor=MapCompose(strstrip))
    new_content = scrapy.Field(input_processor=MapCompose(strstrip))
    new_description = scrapy.Field(input_processor=MapCompose(strstrip))
    new_title_md5 = scrapy.Field()
