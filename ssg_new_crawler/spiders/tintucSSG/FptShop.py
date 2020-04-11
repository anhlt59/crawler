# -*- coding: utf8 -*-
from scrapy.http import JsonRequest, Request
from scrapy.selector import Selector
from bs4 import BeautifulSoup
import urllib
import json

from ssg_new_crawler.spiders.tintucSSG import SSGSpider
from ssg_new_crawler.utils import download_img


class FptShop(SSGSpider):
    name = "FptShop"
    headers = {
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
    }
    params = {'page': 1, 'category': 'giai-tri'}
    url = 'https://fptshop.com.vn/tin-tuc/Ajax/Home/ViewMoreHome'
    limit = 30

    def create_request(self, item, data, *a, **kw):
        return JsonRequest(f'{self.url}?{urllib.parse.urlencode(self.params)}', headers=self.headers, callback=self.parse, errback=self.fail, meta={'item': item})

    def parse(self, response):
        item = response.meta.get('item')
        data = json.loads(response.body)
        selector = Selector(text=data['view'])

        # extract cat_link and image
        for element in selector.css('div.fs-ne2-it'):
            self.crawler.stats.inc_value(f'{self.name}/total')
            new_source_url=element.css("a.fs-ne2-tit::attr(href)").extract_first()
            new_image=element.css("a.fs-ne2-img img::attr(src)").extract_first()

            if new_source_url and new_image:
                detail_item = item.copy() # create detail_item base on item
                # update item
                detail_item.update(
                    new_source_url=f'https://fptshop.com.vn{new_source_url}',
                    new_image=f'https:{new_image}' #download_img(new_image)
                )
                # check item exist in databse
                if not self.model.exist(detail_item):
                    # goto parse_detail
                    yield Request(detail_item['new_source_url'], callback=self.parse_detail, errback=self.fail, meta={'item': detail_item})

        # nextpage
        if self.crawler.stats.get_value(f'{self.name}/total') < self.limit:
            self.params['page'] += 1
            yield JsonRequest(f'{self.url}?{urllib.parse.urlencode(self.params)}',
                              headers=self.headers, callback=self.parse_category, errback=self.fail, meta={'item': item})

    def parse_detail(self, response):
        item = response.meta.get('item')

        # extract title, description, content
        title = response.css('h1.fs-newsdt-tit::text').extract_first()
        description = response.css('h2.fs-newsdt-des::text').extract_first()

        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.select_one('body .fs-newsdt-cten')

        for tag in content.select('p img'):
            # soup.new_tag() create new image tag
            new_tag = soup.new_tag('img', src=tag['data-original']) # soup.new_tag('img', src=download_img(tag['data-original']))
            # replaces tag with new_tag
            tag.replace_with(new_tag)

        # update item
        item.update(
            new_title=title,
            new_description=description,
            new_content=str(content)
        )
        yield item
        self.logger.info(f"url: {response.url} done, "\
                         f"category: {self.crawler.stats.get_value(f'{self.name}/total')}, "\
                         f"saved: {self.crawler.stats.get_value(f'{self.name}/saved')}")
