# -*- coding: utf8 -*-
from scrapy.http import JsonRequest, Request
from scrapy.selector import Selector
from bs4 import BeautifulSoup
import requests

from ssg_new_crawler.spiders.tintucSSG import SSGSpider
from ssg_new_crawler.utils import download_img


class Trangcongnghe(SSGSpider):
    name = "Trangcongnghe"
    limit = 30

    # def create_request(self, item, data, *a, **kw):
    #     return Request(data.crn_url, callback=self.parse, errback=self.fail, meta={'item': item, 'data': data})

    def parse(self, response):
        item = response.meta.get('item')

        # extract catlink and image
        imgs = response.css('.item img::attr(data-src)').extract()
        cat_link = response.css('.item h3 a::attr(href)').extract()

        for url, img in list(zip(cat_link, imgs)):
            self.crawler.stats.inc_value(f'{self.name}/total')
            detail_item = item.copy()
            detail_item.update(
                new_source_url=url,
                new_image=img # download_img(img)
            )
            # check item exist in database
            if not self.model.exist(detail_item):
                yield Request(url, callback=self.parse_detail, errback=self.fail, meta={'item': detail_item})

        #  nextpage
        nextpage_abs = response.css('.pagination_n ::attr(href)').extract_first()
        if nextpage_abs:
            yield Request(nextpage_abs, callback=self.parse, dont_filter=True, meta={'item': item})

    def parse_detail(self, response):
        item = response.meta.get('item')

        # extract title, description, content
        title = response.css('h1::text').extract_first()

        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.select_one('#noidung')

        description_tag = content.select_one('*')
        description = description_tag.text
        description_tag.decompose()

        remove_tags = []
        # remove title
        remove_tags.extend(content.select('h1'))
        # remove user profile
        remove_tags.extend(content.select('.userdetail'))
        # remove tag youtube
        remove_tags.extend(content.select('.youtube'))
        # remove tag info product
        remove_tags.extend(content.select('.titledetail'))
        for tag in remove_tags:
            tag.decompose()

        # replace images
        for tag in content.select('img'):
            # soup.new_tag() create new image tag
            new_tag = soup.new_tag('img', src=tag['data-original']) # soup.new_tag('img', src=download_img(tag['data-original']))
            # replaces tag with new_tag
            tag.replace_with(new_tag)

        # remove all tag sau tag xem them
        remove = False
        for tag in content.select('*'):
            if tag.text == 'Xem thêm:':
                remove = True
            if remove:
                tag.decompose()
        # content = str(content).replace('<article>', '').replace('</article>', '')

        # update item
        item.update(
            new_title=title,
            new_description=description,
            new_content=content
        )
        yield item
        # import pdb; pdb.set_trace()
        self.logger.info(f"url: {response.url} done, "\
                         f"category: {self.crawler.stats.get_value(f'{self.name}/total')}, "\
                         f"saved: {self.crawler.stats.get_value(f'{self.name}/saved')}")
