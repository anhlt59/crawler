# -*- coding: utf-8 -*-
from scrapy.exceptions import CloseSpider
from rotating_proxies.middlewares import RotatingProxyMiddleware
import logging


logger = logging.getLogger(__name__)


class RotatingProxyMiddleware(RotatingProxyMiddleware):
    logger = logger.getChild('rotating_proxy')

    def process_request(self, request, spider):
        # Adding handle splash request

        if 'proxy' in request.meta and not request.meta.get('_rotating_proxy'):
            return None

        proxy = self.proxies.get_random()
        if not proxy:
            if self.stop_if_no_proxies:
                raise CloseSpider("no_proxies")
            else:
                logger.warn("No proxies available; marking all proxies as unchecked")
                self.proxies.reset()
                proxy = self.proxies.get_random()
                if proxy is None:
                    logger.error("No proxies available even after a reset.")
                    raise CloseSpider("no_proxies_after_reset")

        if isinstance(request, SplashRequest):
            request.meta['splash']['proxy'] = proxy
        else:
            request.meta['proxy'] = proxy
        request.meta['download_slot'] = self.get_proxy_slot(proxy)
        request.meta['_rotating_proxy'] = True
