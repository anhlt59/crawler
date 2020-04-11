# -*- coding: utf8 -*-
from scrapy.http import JsonRequest, Request
from scrapy.selector import Selector
from bs4 import BeautifulSoup

from ssg_new_crawler.spiders.tintucSSG import SSGSpider
from ssg_new_crawler.utils import download_img


class Techz(SSGSpider):
    name = "Techz"
    url = 'https://www.techz.vn/category-more-dien-thoai-{page}'
    page = 1
    limit = 30

    def create_request(self, item, data, *a, **kw):
        return Request(self.url.format(page=self.page), callback=self.parse, errback=self.fail, meta={'item': item})

    def parse(self, response):
        item = response.meta.get('item')

        # extract catlink and image
        cat_link = [f'https://www.techz.vn{x}' for x in response.css(".media .media-body > a::attr(href)").extract()]
        imgs = response.css('.media img::attr(src)').extract()

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
        self.page += 1
        yield Request(self.url.format(page=self.page), callback=self.parse, errback=self.fail, meta={'item': item})

    def parse_detail(self, response):
        item = response.meta.get('item')

        # extract title, description, content
        title = response.css('h1::text').extract_first()
        description = response.css('h2::text').extract_first()

        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.select_one('.content-detail-right')

        # remove h2 and tag contain .inner-article
        remove_tags = content.select('h2') + content.select('.inner-article')
        for tag in remove_tags:
            tag.decompose()
        # replace img
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
        # yield item
        import pdb; pdb.set_trace()
        self.logger.info(f"url: {response.url} done, "\
                         f"category: {self.crawler.stats.get_value(f'{self.name}/total')}, "\
                         f"saved: {self.crawler.stats.get_value(f'{self.name}/saved')}")
