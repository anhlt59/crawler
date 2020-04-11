# -*- coding: utf8 -*-
from scrapy.http import JsonRequest, Request
from scrapy.selector import Selector
from bs4 import BeautifulSoup
import requests

from ssg_new_crawler.spiders.tintucSSG import SSGSpider
from ssg_new_crawler.utils import download_img


class Thegioididong(SSGSpider):
    name = "Thegioididong"
    url = 'https://www.thegioididong.com/tin-tuc/aj/Home/Box'
    headers = {
        'authority': 'www.thegioididong.com',
        'accept': '*/*',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
    }
    data = {'ID': 1169, 'Size': 10, 'Index': 1}
    page = 1
    limit = 30

    # def create_request(self, item, data, *a, **kw):
    #     return Request(data.crn_url, callback=self.parse, errback=self.fail, meta={'item': item, 'data': data})

    def parse(self, response):
        item = response.meta.get('item')

        # extract catlink and image
        cat_link = [f'https://www.thegioididong.com{x}' for x in response.css('.newslist > li[data-id] > a::attr(href)').extract()]
        imgs = response.css('.newslist > li[data-id] > a img::attr(data-original)').extract()

        while len(cat_link) < self.limit:
            res = requests.post(self.url, headers=self.headers, data=self.data)
            selector = Selector(text=res.text)
            # extract cat link
            cat_link.extend([f'https://www.thegioididong.com{x}' for x in selector.css('li[data-id] a::attr(href)').extract()])
            imgs.extend([selector.css('li[data-id] a img::attr(data-original)').extract()])

        for url, img in list(zip(cat_link, imgs)):
            self.crawler.stats.inc_value(f'{self.name}/total')
            detail_item = item.copy()
            detail_item.update(
                new_source_url=url,
                new_image=img # download_img(img)
            )
            if not self.model.exist(detail_item):
                yield Request(url, callback=self.parse_detail, errback=self.fail, meta={'item': detail_item})

    def parse_detail(self, response):
        item = response.meta.get('item')

        # không lấy tin khuyến mãi
        if response.xpath(".//a[contains(text(),'Tin Khuyến Mãi')]/@class").extract_first() == 'actmenu':
            self.logger.info(f'Tin khuyen mai: {response.url}')
            return None

        # extract title, description, content
        title = response.css('h1.titledetail::text').extract_first()
        description = ''

        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.select_one('article')

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
        content = str(content).replace('<article>', '').replace('</article>', '')

        # update item
        item.update(
            new_title=title,
            new_description=description,
            new_content=content
        )
        # yield item
        import pdb; pdb.set_trace()
        self.logger.info(f"url: {response.url} done, "\
                         f"category: {self.crawler.stats.get_value(f'{self.name}/total')}, "\
                         f"saved: {self.crawler.stats.get_value(f'{self.name}/saved')}")
