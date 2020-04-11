# -*- coding: utf8 -*-
from scrapy.http import JsonRequest, Request
from scrapy.selector import Selector
from bs4 import BeautifulSoup

from ssg_new_crawler.spiders.tintucSSG import SSGSpider
from ssg_new_crawler.utils import download_img


class Genk(SSGSpider):
    name = "Genk"
    url = 'http://genk.vn/ajax-cate/page-{page}-c{zoneid}/{excluid}.chn'
    headers = {
    'Connection': 'keep-alive',
    'Accept': 'text/html, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
    }
    page = 1
    limit = 30

    # def create_request(self, item, data, *a, **kw):
    #     return Request(data.crn_url, callback=self.parse, errback=self.fail, meta={'item': item, 'data': data})

    def parse(self, response):
        item = response.meta.get('item')

        self.zoneid = response.css('#hdZoneId::attr(value)').extract_first()
        self.excluid = response.css('#hdExcluId::attr(value)').extract_first()

        url = self.url.format(
            page=self.page,
            zoneid=self.zoneid,
            excluid=self.excluid
        )
        yield JsonRequest(url, headers=self.headers, callback=self.parse_api, errback=self.fail,
                          dont_filter=True, meta={'item': item})

    def parse_api(self, response):
        item = response.meta.get('item')
        selector = Selector(text=response.text)

        # extract catlink and image
        cat_link = [f'http://genk.vn{x}' for x in selector.css('h4 a.visit-popup::attr(href)').extract()]
        imgs = selector.css('img::attr(src)').extract()

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

        # nextpage
        if self.crawler.stats.get_value(f'{self.name}/total') < self.limit:
            self.page += 1
            url = self.url.format(
                     page=self.page,
                     zoneid=self.zoneid,
                     excluid=self.excluid
                  )
            yield JsonRequest(url, headers=self.headers, callback=self.parse_api, errback=self.fail, meta={'item': item})

    def parse_detail(self, response):
        item = response.meta.get('item')

        # extract title, description, content
        title = response.css('h1::text').extract_first()
        description = response.css('h2::text').extract_first()

        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.select_one('#ContentDetail')

        for tag in content.select('img'):
            # soup.new_tag() create new image tag
            new_tag = soup.new_tag('img', src=tag['src']) # soup.new_tag('img', src=download_img(tag['data-original']))
            # replaces tag with new_tag
            tag.replace_with(new_tag)

        # update item
        item.update(
            new_title=title,
            new_description=description,
            new_content=str(content)
        )
        yield item
        # import pdb; pdb.set_trace()
        self.logger.info(f"url: {response.url} done, "\
                         f"category: {self.crawler.stats.get_value(f'{self.name}/total')}, "\
                         f"saved: {self.crawler.stats.get_value(f'{self.name}/saved')}")
